---
name: mimiciv-dataset
description: How to identify patients (cohorts) and find/extract variables in MIMIC-IV (+ MIMIC-IV-ED) for machine-learning analysis. Use when building a MIMIC cohort, finding a MIMIC itemid / ICD code / clinical variable, resolving event tables through dictionaries (d_items, d_labitems, d_icd_diagnoses), computing time offsets, or writing a MIMIC exploratory notebook. Read clinical-icu-datasets first for shared conventions.
---

# MIMIC-IV

## High-level overview

MIMIC-IV is a large, single-center critical-care database from an academic medical center
in Boston (Beth Israel Deaconess), covering ~2008–2019, released on PhysioNet under
credentialed access. Compared with eICU it is **deeper but narrower**: one hospital, richly
detailed, and **relational** — measurements store a numeric id that you resolve through a
dictionary table.

Key design facts:
- **Modular.** Core data splits into `hosp/` (hospital-wide EHR) and `icu/` (high-resolution
  ICU data from the MetaVision clinical information system). Optional add-on modules ship
  separately: **MIMIC-IV-ED** (emergency department), MIMIC-IV-Note (free text),
  MIMIC-CXR (chest X-rays).
- **Real timestamps, not offsets.** Times are de-identified by a per-patient random date
  shift but remain internally consistent. You compute offsets yourself as
  `(event_time − time_zero)`.
- **Dictionaries.** ICU events reference `d_items`; hospital labs reference `d_labitems`;
  diagnoses/procedures reference `d_icd_diagnoses` / `d_icd_procedures`.

## ID hierarchy

```
subject_id        # the patient
└─ hadm_id        # one hospital admission
   └─ stay_id     # one ICU stay (icustays)  — also one ED stay (edstays)
```
Analyses are keyed on `subject_id`, `hadm_id`, or `stay_id` depending on grain.

## Folder / module layout

```
mimic-iv/
├─ hosp/   # hospital-wide
└─ icu/    # ICU (MetaVision)
mimic-iv-ed/ed/   # ED add-on (gzipped .csv.gz)
```

| Module | File | Key columns |
|---|---|---|
| hosp | `patients.csv` | `subject_id`, `gender`, `anchor_age`, `anchor_year`, `dod` (date of death) |
| hosp | `admissions.csv` | `hadm_id`, `admittime`, `dischtime`, `deathtime`, `admission_type` (`ELECTIVE`, `EW EMER.`, …), `edregtime`, `hospital_expire_flag` (in-hospital death) |
| hosp | `diagnoses_icd.csv` ⚠ | `hadm_id`, `icd_code`, `icd_version`, `seq_num` |
| hosp | `d_icd_diagnoses.csv` | `icd_code`, `long_title` — **ICD dictionary** |
| hosp | `procedures_icd.csv` / `d_icd_procedures.csv` | procedures + dictionary |
| hosp | `labevents.csv` ⚠⚠ | `itemid`, `valuenum`, `value`, `charttime` |
| hosp | `d_labitems.csv` | `itemid`, `label`, `fluid`, `category` — **lab dictionary** |
| hosp | `emar.csv` / `pharmacy.csv` / `prescriptions.csv` ⚠ | medication administration / orders |
| hosp | `omr.csv` | outpatient measurements: `result_name` (`Height (Inches)`, `Weight (Lbs)`, `BMI (kg/m2)`, BP), `result_value`, `chartdate` |
| icu | `icustays.csv` | `stay_id`, `intime`, `outtime`, `first_careunit` |
| icu | `chartevents.csv` ⚠⚠⚠ | `itemid`, `value`, `valuenum`, `charttime` (vitals, GCS, settings) |
| icu | `d_items.csv` | `itemid`, `label`, `abbreviation`, `category`, `param_type`, `unitname` — **ICU item dictionary** |
| icu | `outputevents.csv`, `inputevents.csv`, `procedureevents.csv`, `datetimeevents.csv` ⚠ | I/O, infusions, procedures, dated events |
| ed | `edstays.csv.gz` | `subject_id`, `hadm_id`, `stay_id`, `intime`, `outtime`, `disposition` |
| ed | `triage.csv.gz` | `chiefcomplaint`, vitals at triage |
| ed | `diagnosis.csv.gz` | `icd_code`, `icd_title` |

`d_items.param_type` tells you how to treat an ICU item: `Numeric` / `Numeric with tag`
→ numeric features; `Checkbox` → binary; `Text` → categorical/one-hot. Read large tables
(`chartevents`, `labevents`, `diagnoses_icd`, the event tables, ED `.csv.gz`) in chunks
filtered on `subject_id`; ED files are gzip (`compression='gzip'`).

## Identifying a cohort

Combine any of these signals (persist the id list afterward):

```python
hosp = DATA_DIR + "hosp/"; icu = DATA_DIR + "icu/"; ed = ED_DIR + "ed/"

# 1) by ICD diagnosis — search the dictionary, then the fact table
d_icd = pd.read_csv(hosp + "d_icd_diagnoses.csv")
codes = d_icd[d_icd.long_title.str.contains("sepsis", case=False, na=False)].icd_code
dx = read_filtered(hosp + "diagnoses_icd.csv", "subject_id", all_ids)
cohort = dx[dx.icd_code.isin(codes)].hadm_id.unique()

# 2) by ED chief complaint (free text)
triage = pd.read_csv(ed + "triage.csv.gz", compression="gzip")
ed_ids = triage[triage.chiefcomplaint.str.contains("chest pain", case=False, na=False)].stay_id

# 3) by ICU procedure (itemid from d_items) e.g. an intervention time
proc = read_filtered(icu + "procedureevents.csv", "subject_id", all_ids)
proc_ids = proc[proc.itemid == <itemid>].hadm_id.unique()

# typical filters: anchor_age >= 18; require a recorded ICU stay (icustays);
# admission_type not in {'ELECTIVE','SURGICAL SAME DAY ADMISSION'} for emergent cohorts;
# de-duplicate to one admission/stay per subject.
```

## Reference time and offsets

Pick `time_zero` per stay (ICU `intime`, ED `intime`, or an event time), then:

```python
ev["charttime"] = pd.to_datetime(ev["charttime"], errors="coerce")
ev = ev.merge(stays[["subject_id", "time_zero"]], on="subject_id")
ev["offset"] = (ev["charttime"] - ev["time_zero"]).dt.total_seconds() / 60
ev = ev[(ev.offset >= 0) & (ev.offset <= window)]
```

## Feature extraction

Merge `chartevents` / `labevents` with their dictionary to get a `label`, lower-case +
underscore it, then split by `param_type` / type:
- **Numeric** (chartevents Numeric, labevents) → shared `window_features` with
  `type_col='label'`, `value_col='valuenum'`, `time_col='offset'`; prefixes `chart` / `lab`.
- **Checkbox / binary** → pivot max per `(subject_id, label)`.
- **Text / categorical** → `MultiLabelBinarizer` (split multi-valued cells on `;`).
- **Meds** (`emar`/`prescriptions`) → one-hot presence per subject (`med_*`).
- **Other diagnoses** → one-hot `dx_*` from `diagnoses_icd` long titles.

## Exploratory recipe — finding a variable

Search the **dictionaries** first (this is the core MIMIC skill):

```python
d_items = pd.read_csv(icu + "d_items.csv")
d_items[d_items.label.str.contains("glasgow|gcs|motor", case=False, na=False)][
    ["itemid", "label", "abbreviation", "param_type", "unitname"]]

d_lab = pd.read_csv(hosp + "d_labitems.csv")
d_lab[d_lab.label.str.contains("lactate", case=False, na=False)][["itemid", "label", "fluid"]]
```
Then pull just that `itemid` from the event table (filter inside the chunk loop on both
`subject_id.isin(cohort)` **and** `itemid == <id>`), compute offsets, and check coverage:
`ev[ev.itemid == <id>].subject_id.nunique()`.

## Gotchas specific to MIMIC-IV

- `chartevents` is enormous — always filter by `itemid` (and ids) inside the chunk loop;
  never load it whole.
- `value` (string) vs `valuenum` (numeric): use `valuenum` for numeric features.
- The **same concept lives in two places**: bedside labs may appear in `chartevents`
  (icu) *and* `labevents` (hosp) under different itemids — decide which source to trust.
- Units come from `d_items.unitname` / `d_labitems`; the same itemid can mix units —
  inspect before aggregating.
- `anchor_age` is the age at `anchor_year`; ages ≥ 91 are grouped. Death can be read from
  `hospital_expire_flag`, `admissions.deathtime`, or `patients.dod`.
