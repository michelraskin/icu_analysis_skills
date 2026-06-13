---
name: pmap-dataset
description: How to identify any patient cohort in PMAP-style institutional Epic Clarity EHR exports — where each kind of signal (diagnosis, encounter attributes, medication, device, flowsheet measure, lab) lives and how to match it, resolving flowsheet meas_id / lab proc_id through dictionaries. Use when building or filtering a cohort or writing a patient-identification notebook on an Epic Clarity export. Read clinical-icu-datasets first. Feature extraction is covered briefly at the end.
---

# PMAP — patient identification (Epic Clarity export)

## High-level overview

PMAP is a representative **institutional EHR export** from **Epic Clarity/Caboodle** — a raw
operational extract under a data-use agreement (schemas/column names reflect the source
institution, not a public standard); the patterns generalize to most Epic Clarity ICU
extracts. **Snapshot-dated** (point-in-time folders). **Two grains:** a stable patient id and
an encounter id (Epic "CSN") — here `osler_id` (patient) and `pat_enc_csn_id` (encounter).
Bedside data lives in **flowsheets** (numeric `meas_id` → measure dictionary); labs carry
`proc_id` (→ procedure dictionary, Epic `CLARITY_EAP`). **Real timestamps**.

> ⚠ Units follow institutional charting — temperature often **Fahrenheit**, weight lbs.

## Where each signal lives (the identification map)

| Signal kind | Dictionary → fact table | Match on |
|---|---|---|
| Diagnosis (text + coded) | — → `dbo.accm_encounter_dx.csv` | `dx_name`, `icd10_code`, `icd9_code` |
| Admission attributes / pathway | — → `dbo.accm_inpatient.csv` | `hosp_admsn_type_c`, `ed_visit_yn`, `disch_disp_c`, `admit_source_c` |
| ICU stay (require/define) | — → `core_icustay_*.csv` | `seq`, `origin`, `in_time` |
| Medication | — → `dbo.accm_med_admin.csv` ⚠ | `generic_name` / `medication_name` (text) |
| Flowsheet measure (vital/score/device/ventilation) | `d_flo_measures` → flowsheet (`Flowsheet_part*.csv`) ⚠ | `meas_id` + `meas_value` |
| Lab value | `CLARITY_EAP` → `dbo.accm_labs.csv` ⚠ | `proc_id` + `ord_value` |

Demographics/outcomes for filters: `dbo.accm_patient.csv` (`gender`, `birth_date` → age),
`dbo.accm_inpatient.csv` (`hosp_admsn_time`, `hosp_disch_time`, `disch_disp_c` → death).

```python
SNAP, FLOW = ROOT + "2024-08-15/", ROOT + "<flowsheet folder>/"   # configure to your snapshot
```
**Headerless flowsheets:** read with `header=None`, then assign column names (see feature
note). **Coded `_c` columns are institution-specific integers** — verify their meaning
(observed: `hosp_admsn_type_c` admission type, `disch_disp_c` disposition incl. a code for
expired, `origin == 'init'` direct ICU admit). Never assume a code's meaning.

## The generic matching methods

**Diagnosis (text + code on one table):**
```python
dx = read_filtered(SNAP + "dbo.accm_encounter_dx.csv", "osler_id", all_ids)
dx["icd"] = dx.icd9_code.fillna("") + " " + dx.icd10_code.fillna("")
ids = dx[dx.dx_name.str.contains("<keyword>", case=False, na=False) |
         dx.icd.str.contains(r"<icd9|icd10 regex>", regex=True, na=False)].pat_enc_csn_id.unique()
```
Pair INCLUDE/EXCLUDE regex (shared helper); `annotation` often flags "H/o ..." to exclude.

**Id-based flowsheet signal** (vital / score / device / ventilation) — find the `meas_id`(s)
in the measure dictionary, then flag any matching flowsheet row:
```python
meas = pd.read_csv(FLOW + "d_flo_measures.csv").rename(columns={"flo_meas_id":"meas_id","flo_meas_name":"meas_name"})
sig_ids = meas[meas.meas_name.str.contains(r"<keyword|regex>", case=False, regex=True, na=False)].meas_id
# stays with any flowsheet row whose meas_id in sig_ids → presence cohort;
# for thresholds keep meas_value + recorded_time, window, aggregate, cut off.
```

**Text-name medication:**
```python
meds = read_filtered(SNAP + "dbo.accm_med_admin.csv", "osler_id", all_ids)
name = meds.generic_name.fillna(meds.medication_name).str.lower()
ids = meds[name.str.contains(r"<keyword|regex>", regex=True, na=False)].osler_id.unique()
```

**Lab threshold:** look up `proc_id` in `CLARITY_EAP` by name, stream `accm_labs` filtered to
those proc_ids + cohort, coerce `ord_value`, take min/max in a window, threshold.

**Combine & finalize:** intersect/union id sets; compute `age` from `birth_date` vs
`hosp_admsn_time` and keep ≥ 18; apply pathway filters (`ed_visit_yn`, `origin`, `seq`,
non-elective via `hosp_admsn_type_c`); de-duplicate to one encounter per patient; save the
`osler_id` / `pat_enc_csn_id` lists.

## Exploratory recipe — find the id behind a concept

Search the two dictionaries:
```python
meas[meas.meas_name.str.contains(r"<keyword|regex>", case=False, regex=True, na=False)]   # meas_id
eap = pd.read_csv(SNAP + "<proc dictionary>.csv").rename(columns={"PROC_ID":"proc_id","PROC_NAME":"proc_name"})
eap[eap.proc_name.str.contains("<frag>", case=False, na=False)]                            # proc_id
```
Then filter the flowsheet/lab table to that id and check coverage
(`df[df.meas_id==<id>].osler_id.nunique()`).

## PMAP identification gotchas

- **No standard vocabulary** — concepts appear under several `meas_id`s / free-text
  spellings; search broadly and union.
- **Coded `_c` columns** are institution-specific integers; verify, never assume.
- **Snapshot drift** — ids/code meanings can change between dated extracts; pin the snapshot.
- **Units charted, not standardized** (temp °F, weight lbs) — relevant when thresholding.
- **PHI** — keep raw exports out of version control; share only derived id/feature tables.

## Next: building the analysis dataset (brief)

After identification, set time zero (`hosp_admsn_time` or ICU `in_time`), join flowsheet to
`d_flo_measures` (route by `meas_val_type_c`) and labs to the procedure dictionary, compute
offsets, and summarize per stay or per bucket. Defer until the cohort is settled. For *which*
variable lives where (GCS/mGCS `meas_id`, discharge status, ICU days, demographics, vitals,
labs, …), see the **icu-feature-identification** skill.
