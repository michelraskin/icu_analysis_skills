---
name: pmap-dataset
description: How to identify patients (cohorts) and find/extract variables in PMAP-style institutional Epic Clarity EHR exports (flowsheets, labs, med administrations) for machine-learning analysis. Use when building a cohort, resolving flowsheet meas_id / lab proc_id through measure/procedure dictionaries, computing time offsets from raw timestamps, or writing an exploratory notebook on an Epic Clarity export. Note temperatures are typically in Fahrenheit. Read clinical-icu-datasets first for shared conventions.
---

# PMAP — institutional Epic Clarity export

## High-level overview

PMAP is a representative **institutional EHR export** drawn from **Epic Clarity/Caboodle**
(the relational reporting layer behind the Epic electronic medical record). Unlike eICU
and MIMIC, it is **not a public research database** — it is a raw operational export
governed by a data-use agreement, so schemas, snapshot dates, and column names reflect the
source institution rather than a curated standard. The patterns below generalize to most
Epic Clarity ICU extracts.

Key design facts:
- **Snapshot-dated.** Files live under a date-stamped folder (a point-in-time extract);
  re-pulls land in new dated folders.
- **Two grains:** a stable **patient identifier** and an **encounter id** (Epic "CSN",
  contact serial number). Here: `osler_id` (patient) and `pat_enc_csn_id` (encounter).
- **Flowsheets** hold most bedside data (vitals, GCS, temps, scores). Each row is a
  measurement with a numeric `meas_id` resolved through a **measure dictionary**.
- **Labs** carry a `proc_id` resolved through a **procedure dictionary** (Epic `CLARITY_EAP`).
- **Real timestamps** (not offsets) — you compute offsets relative to admission yourself.

> ⚠ **Units follow the institution's charting**, which for Epic in the US is often
> **Fahrenheit** for temperature and **lbs/inches** for weight/height. Confirm units in the
> data before thresholding (e.g. 96.8 °F = 36 °C, 77 °F = 25 °C).

## Folder / file layout (typical)

```
<root>/
├─ <YYYY-MM-DD>/                         # dated snapshot of Clarity tables
│  ├─ dbo.accm_patient.csv               # patients
│  ├─ dbo.accm_inpatient.csv             # encounters / admit-discharge
│  ├─ dbo.accm_encounter_dx.csv          # encounter diagnoses (dx_name, ICD)
│  ├─ dbo.accm_labs.csv                  # lab results (ord_value, proc_id)
│  ├─ dbo.accm_med_admin.csv             # medication administrations
│  └─ <EAP/proc dictionary>.csv          # PROC_ID -> PROC_NAME
├─ <flowsheet folder>/
│  ├─ Flowsheet_part*.csv                # flowsheet measurements (often headerless!)
│  └─ d_flo_measures.csv                 # flo_meas_id -> flo_meas_name (measure dictionary)
└─ core_icustay_*.csv                    # ICU stay windows (in_time/out_time)
```

| File | Key columns |
|---|---|
| `accm_patient` | `osler_id`, `gender`, `birth_date` |
| `accm_inpatient` | `pat_enc_csn_id`, `hosp_admsn_time`, `hosp_disch_time`, `admit_source_c`, `hosp_admsn_type_c`, `ed_visit_yn`, `disch_disp_c`, `hospital_service` |
| `core_icustay` | `pat_enc_csn_id`, `in_time`, `out_time`, `seq`, `icu`, `origin` |
| `accm_encounter_dx` | `dx_name`, `icd10_code`, `icd9_code`, `primary_dx_yn`, `dx_ed_yn`, `annotation` |
| flowsheet | `osler_id`, `pat_enc_csn_id`, `recorded_time`, `meas_value`, `meas_id`, `meas_val_type_c` |
| `d_flo_measures` | `flo_meas_id`→`meas_id`, `flo_meas_name`→`meas_name` (**measure dictionary**) |
| `accm_labs` | `ord_value`, `proc_id`, `specimen_taken_time`, `data_type` |
| proc dictionary (`CLARITY_EAP`) | `PROC_ID`→`proc_id`, `PROC_NAME`→`proc_name` (**lab/procedure dictionary**) |
| `accm_med_admin` | `generic_name`, `medication_name`, `taken_time` |

**Headerless flowsheets:** some exports ship flowsheet CSVs with no header row — assign
column names after reading (read with `header=None`, then set `df.columns = [...]`). Read
big tables in chunks; some lab files need `on_bad_lines="skip"`.

Coded columns (Epic `_c` category codes) are institution-specific integers — confirm their
meaning against a code table or by cross-tabbing. Common ones observed: `hosp_admsn_type_c`
(admission type, e.g. elective vs emergent), `disch_disp_c` (discharge disposition, e.g. a
specific code for expired/death), `origin` (`'init'` = admitted directly to ICU).

## Identifying a cohort

```python
SNAP = ROOT + "2024-08-15/"     # configure to your snapshot
dx = read_filtered(SNAP + "dbo.accm_encounter_dx.csv", "osler_id", all_ids)

# by diagnosis text or ICD (combine icd9 + icd10 then match)
dx["icd"] = dx.icd9_code.fillna("") + " " + dx.icd10_code.fillna("")
cohort = dx[dx.dx_name.str.contains("sepsis", case=False, na=False) |
            dx.icd.str.contains(r"\bA41", case=False, na=False)].pat_enc_csn_id.unique()

# typical filters: compute age from birth_date vs hosp_admsn_time and keep >= 18;
# restrict to first ICU stay (seq == 1); use ed_visit_yn / origin for the care pathway;
# drop patients with multiple qualifying encounters.
```
Compute `age` from `birth_date` and `hosp_admsn_time`; derive outcomes from `disch_disp_c`
(disposition) and discharge times. Persist the `osler_id` / `pat_enc_csn_id` lists.

## Reference time and offsets

Time zero is usually `hosp_admsn_time` (or ICU `in_time`). Offsets in minutes:

```python
fs["recorded_time"]   = pd.to_datetime(fs.recorded_time, errors="coerce")
fs = fs.merge(enc[["osler_id", "hosp_admsn_time", "hosp_disch_time"]], on="osler_id")
fs["offset"] = (fs.recorded_time - pd.to_datetime(fs.hosp_admsn_time)).dt.total_seconds() / 60
fs = fs[(fs.offset >= 0) & (fs.offset <= window) & (fs.recorded_time <= fs.hosp_disch_time)]
```

## Feature extraction

- Join flowsheet to `d_flo_measures` on `meas_id` to get `meas_name`; route by
  `meas_val_type_c` (the value-type code): numeric measures → shared `window_features`
  (`type_col='meas_name'`, `value_col='meas_value'`, `time_col='offset'`, prefix `flo`);
  blood-pressure measures are stored as `"sys/dia"` strings → split on `/`; multi-select /
  custom measures → split on `;` and one-hot.
- Labs: join `accm_labs` to the procedure dictionary on `proc_id` → `proc_name`; keep
  numeric (`data_type == 'Number'`) → `lab_*` features.
- Meds: normalize `generic_name` (fallback `medication_name`; strip parenthetical detail
  and vendor `zzz` prefixes) → one-hot `med_*`.
- Diagnoses: split `dx_name` and one-hot, collapsing synonymous variants.

## Exploratory recipe — finding a variable

Search the **two dictionaries**:

```python
meas = pd.read_csv(FLOW + "d_flo_measures.csv").rename(
    columns={"flo_meas_id": "meas_id", "flo_meas_name": "meas_name"})
meas[meas.meas_name.str.contains("glasgow|gcs|temperature", case=False, na=False)]   # -> meas_id

eap = pd.read_csv(SNAP + "<proc dictionary>.csv").rename(
    columns={"PROC_ID": "proc_id", "PROC_NAME": "proc_name"})
eap[eap.proc_name.str.contains("lactate", case=False, na=False)]                     # -> proc_id
```
Then filter the flowsheet/lab table to that id, compute offsets, and check coverage
(`df[df.meas_id == <id>].osler_id.nunique()`). For categorical flowsheet items, drop rare
ones first (e.g. require ≥ N patients via `groupby('meas_id')['osler_id'].nunique()`).

## Gotchas specific to Epic Clarity exports

- **No standard vocabulary** — the same concept can appear under several `meas_id`s and
  free-text spellings; search broadly and union.
- **Coded `_c` columns are institution-specific integers**; never assume a code's meaning,
  verify it.
- **Snapshot drift**: ids and code meanings can change between dated extracts — pin the
  snapshot you analyzed.
- **Units are charted, not standardized** — temperature often °F, weight lbs, height
  inches; convert explicitly.
- **PHI**: these exports are sensitive; keep raw files out of version control and share
  only derived, de-identified feature tables.
