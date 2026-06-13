---
name: mimiciv-dataset
description: How to identify any patient cohort in MIMIC-IV (+ MIMIC-IV-ED) — where each kind of signal (diagnosis, procedure, medication, device, lab/vital) lives and how to match it, including resolving numeric ids through dictionaries (d_items, d_labitems, d_icd_diagnoses). Use when building or filtering a MIMIC cohort, finding the itemid/code behind a concept, or writing a MIMIC patient-identification notebook. Read clinical-icu-datasets first. Feature extraction is covered briefly at the end.
---

# MIMIC-IV — patient identification

## High-level overview

MIMIC-IV is a deep single-center critical-care database (Beth Israel Deaconess, Boston,
~2008–2019; PhysioNet credentialed). **Relational and modular:** `hosp/` (hospital-wide EHR)
and `icu/` (high-resolution ICU data); add-on **MIMIC-IV-ED** (emergency dept). The defining
trait: most signals are stored as a **numeric id resolved through a dictionary** — so
identification is usually *"search the dictionary for the id, then filter the fact table by
id."* **Real timestamps** (date-shifted), not offsets. Files are often `.csv.gz`.

**ID hierarchy:** `subject_id` (patient) → `hadm_id` (hospital admission) → `stay_id`
(ICU stay in `icustays`; also ED stay in `edstays`).

## Where each signal lives (the identification map)

| Signal kind | Dictionary → fact table | Match on |
|---|---|---|
| Diagnosis (coded) | `d_icd_diagnoses` → `diagnoses_icd.csv.gz` | `icd_code` (+ `icd_version` 9/10) |
| Procedure (coded) | `d_icd_procedures` → `procedures_icd.csv.gz` | `icd_code` (+ version) |
| ED chief complaint (text) | — → `triage.csv.gz` | `chiefcomplaint` |
| ED diagnosis | — → ED `diagnosis.csv.gz` | `icd_code` |
| ICU procedure / device / ventilation | `d_items` → `procedureevents.csv.gz` | `itemid` (e.g. ventilation, lines, CRRT) |
| Medication (continuous infusion) | `d_items` → `inputevents.csv.gz` | `itemid` |
| Medication (orders / admin) | — → `prescriptions.csv.gz` / `emar.csv.gz` | `drug` / `medication` (text) |
| Lab value | `d_labitems` → `labevents.csv.gz` ⚠⚠ | `itemid` + `valuenum` |
| Vital / score / device setting | `d_items` → `chartevents.csv.gz` ⚠⚠⚠ | `itemid` + `valuenum`/`value` |

Demographics/outcomes for filters: `patients.csv.gz` (`anchor_age`, `gender`),
`admissions.csv.gz` (`admission_type`, `edregtime`, `hospital_expire_flag`, `deathtime`),
`icustays.csv.gz` (`intime`/`outtime`, defines "had an ICU stay" and time zero).

```python
HOSP, ICU, ED = DATA_DIR+"hosp/", DATA_DIR+"icu/", ED_DIR+"ed/"   # configure
read = lambda f, **k: pd.read_csv(f, compression="gzip", **k)     # files are .csv.gz
```

## The generic matching methods

**Coded signal** — look up codes by name in the dictionary, match both ICD versions:
```python
d_icd = read(HOSP + "d_icd_diagnoses.csv.gz")
codes = d_icd[d_icd.long_title.str.contains("<keyword>", case=False, na=False)].icd_code
dx = read(HOSP + "diagnoses_icd.csv.gz", dtype={"icd_code": str})
ids = dx[dx.icd_code.str.strip().isin(codes)].hadm_id.unique()
# explicit prefix families across versions:
def bucket(frame, p9, p10):
    return frame[((frame.icd_version==9)  & frame.icd_code.str.startswith(p9)) |
                 ((frame.icd_version==10) & frame.icd_code.str.startswith(p10))]
```

**Id-based signal** (procedure / infusion / device / vital) — find the `itemid`(s) in
`d_items`, then filter the (big) event table by `itemid`:
```python
d_items = read(ICU + "d_items.csv.gz")
item_ids = d_items[d_items.label.str.contains(r"<keyword|regex>", case=False, regex=True, na=False)].itemid
hits = []
for ch in read(ICU + "<eventtable>.csv.gz", chunksize=500_000,
               usecols=["stay_id","itemid","starttime"]):       # cols vary by table
    hits.append(ch[ch.itemid.isin(item_ids)])
ids = pd.concat(hits).stay_id.unique()
```
This single pattern covers procedures (`procedureevents`), continuous meds/fluids/blood
(`inputevents`), and device/vital/setting signals (`chartevents`). For a *presence* cohort
take the unique ids; for an *amount/intensity* cohort keep `starttime`+`amount`, offset from
ICU `intime`, aggregate, and threshold (optionally with `max_in_window`).

**Text-name medication** (hospital-wide) — `prescriptions`/`emar` carry drug names directly:
```python
presc = read(HOSP + "prescriptions.csv.gz", usecols=["hadm_id","drug"])
ids = presc[presc.drug.str.contains("<keyword>", case=False, na=False)].hadm_id.unique()
```

**ED chief complaint (text)** — match `triage.chiefcomplaint`, link to `hadm_id` via
`edstays` (ED `stay_id` ≠ ICU `stay_id`).

**Threshold signal** — stream `labevents`/`chartevents` filtered to itemid + cohort, take
min/max within a window, apply the cutoff.

**Combine & finalize:** intersect/union the id sets; apply filters (`anchor_age >= 18`,
require a row in `icustays`, restrict `admission_type`, ED-vs-direct pathway); de-duplicate
to one admission/stay per subject; save the `subject_id`/`hadm_id`/`stay_id` list.

## Exploratory recipe — find the id behind a concept

Search the dictionaries first (the core MIMIC move):
```python
d_items[d_items.label.str.contains(r"<keyword|regex>", case=False, regex=True, na=False)][["itemid","label","param_type"]]
d_lab = read(HOSP + "d_labitems.csv.gz"); d_lab[d_lab.label.str.contains("<frag>", case=False, na=False)]
d_icd[d_icd.long_title.str.contains("<frag>", case=False, na=False)]
```
Then stream the event table filtered on **both** `subject_id.isin(cohort)` and the `itemid`,
and check coverage: `ev[ev.itemid==<id>].subject_id.nunique()`.

## MIMIC identification gotchas

- **ICD-9 and ICD-10 coexist** — match both via `icd_version`.
- `chartevents`/`labevents`/`inputevents` are huge — filter by `itemid` (and ids) inside a
  chunk loop; never load whole.
- ED `stay_id` ≠ ICU `stay_id`; join through `edstays` to get `hadm_id`.
- Death: `hospital_expire_flag`, `admissions.deathtime`, or `patients.dod`.
- `anchor_age` is binned for ≥91; dataset version (2.2 vs 3.1) changes paths/compression.

## Next: building the analysis dataset (brief)

After identification, set time zero (ICU `intime`, ED `intime`, or event time), stream
`chartevents`/`labevents` filtered to the cohort, compute `offset = (charttime − intime)`
minutes, merge to `d_items`/`d_labitems` for labels, and summarize per stay
(`window_features`) or per day/hour bucket. Defer until the cohort is settled. For *which*
variable lives where (GCS/mGCS itemids, discharge status, ICU days, demographics, vitals,
labs, …), see the **icu-feature-identification** skill.
