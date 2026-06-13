---
name: eicu-dataset
description: How to identify patients (cohorts) and find/extract variables in the eICU Collaborative Research Database (eICU-CRD) for machine-learning analysis. Use when building an eICU cohort, locating an eICU clinical variable (lab, vital, treatment, diagnosis, nursing chart), computing time offsets, or writing an eICU exploratory notebook. Read clinical-icu-datasets first for shared conventions.
---

# eICU Collaborative Research Database (eICU-CRD)

## High-level overview

eICU-CRD is a multi-center US critical-care database released by Philips Healthcare and
the MIT Laboratory for Computational Physiology (PhysioNet, credentialed access). It
covers roughly **200,000 ICU unit stays across 200+ hospitals** that participated in the
Philips eICU telehealth program (~2014–2015). Because it is multi-center, coding and
available variables **vary by hospital** — expect ragged coverage.

Key design facts:
- **Flat, denormalized CSVs.** One file per domain (patient, lab, treatment, …); no
  module subfolders. Most variable names are stored **inline** as strings, so there is no
  central item dictionary to look up (unlike MIMIC).
- **Time is an integer offset in minutes** relative to **unit admission** (`time zero`).
  Column names end in `offset` (e.g. `labresultoffset`, `nursingchartoffset`). Negative
  offsets mean recorded before ICU admission.

## ID hierarchy

```
uniquepid                 # the patient (can span multiple hospitalizations)
└─ patienthealthsystemstayid   # one hospital stay
   └─ patientunitstayid        # one ICU/unit stay  ← the usual analysis grain
```
Most analyses are keyed on **`patientunitstayid`** (one row per ICU stay).

## Folder / file layout

A download is a single folder of CSVs (often `.csv.gz`). The tables you will use most:

| File | Grain | Key columns |
|---|---|---|
| `patient.csv` | unit stay | `patientunitstayid`, `gender`, `age` (string; `'> 89'` sentinel), `admissionheight`, `admissionweight`, `apacheadmissiondx`, `unitadmittime24`, `hospitaladmitsource`, `hospitaldischargestatus` (`'Expired'` = died), `hospitaldischargeoffset` |
| `diagnosis.csv` | event | `diagnosisstring` (pipe-`|`-delimited hierarchy), `icd9code`, `diagnosisoffset` |
| `treatment.csv` | event | `treatmentstring` (pipe hierarchy), `treatmentoffset` |
| `lab.csv` ⚠ large | event | `labname`, `labresult`, `labresultoffset` |
| `nurseCharting.csv` ⚠ large | event | `nursingchartcelltypevalname` (the variable name), `nursingchartvalue`, `nursingchartoffset`, `nursingchartentryoffset` |
| `vitalPeriodic.csv` ⚠ large | event | high-frequency vitals (`heartrate`, `sao2`, `respiration`, `systemicsystolic`, …) as columns |
| `vitalAperiodic.csv` | event | intermittent vitals (cuff BP, etc.) |
| `infusionDrug.csv` | event | `drugname`, `infusionrate`, `infusionoffset` |
| `intakeOutput.csv` | event | `cellpath`, `celllabel`, `cellvaluenumeric`, `intakeoutputoffset` |
| `medication.csv` | event | `drugname`, `drugstartoffset` |
| `apacheApsVar.csv` / `apachePatientResult.csv` | unit stay | APACHE severity components & predicted mortality |
| `pastHistory.csv`, `physicalExam.csv`, `microLab.csv`, `respiratoryCharting.csv` | event | comorbidities, exam, cultures, vent settings |

Set the data location once and read; chunk the large tables filtered to your cohort:

```python
DATA_DIR = "/path/to/eicu/"     # configure for your environment
window   = 6 * 60               # example 6-hour feature window
labs = read_filtered(DATA_DIR + "lab.csv", "patientunitstayid", cohort_ids)
```

Demographic gotchas: `age` is a **string** with `'> 89'` for elderly patients → replace
with `89` before `astype(int)`. BMI is not stored: `bmi = admissionweight /
(admissionheight/100)**2`.

## Identifying a cohort

eICU has no single dictionary, so cohorts are built by **string/code matching** on the
diagnosis, treatment, or admission-reason fields:

```python
# by ICD-9 code prefix (e.g. select a diagnosis family)
dx = pd.read_csv(DATA_DIR + "diagnosis.csv")
ids = dx[dx.icd9code.astype(str).str.startswith(("850", "851"))].patientunitstayid.unique()

# by free-text in the APACHE admission diagnosis
pat = pd.read_csv(DATA_DIR + "patient.csv")
ids = pat[pat.apacheadmissiondx.str.contains("sepsis", case=False, na=False)].patientunitstayid

# by a treatment / exposure (treatmentstring is a pipe path)
tx = pd.read_csv(DATA_DIR + "treatment.csv")
exposed = tx[tx.treatmentstring.str.contains("transfusion", case=False, na=False)].patientunitstayid.unique()

# typical filters: age >= 18, first/qualifying unit stay only
```
Persist the resulting id list and reuse it to filter every event table.

## Hierarchical strings → one-hot features

`diagnosisstring` and `treatmentstring` are `|`-delimited hierarchical paths. Explode and
one-hot them, then aggregate per stay within the window:

```python
def one_hot_pipe(df, col, prefix):
    oh = df[col].str.split('|').explode().str.get_dummies().groupby(level=0).sum()
    return df.join(oh.add_prefix(prefix)), oh.add_prefix(prefix)
```

## Numeric feature extraction

`lab` and `nurseCharting` are long `(id, time, name, value)` tables → use the shared
`window_features` helper with:

| Table | `type_col` | `value_col` | `time_col` |
|---|---|---|---|
| `lab` | `labname` | `labresult` | `labresultoffset` |
| `nurseCharting` | `nursingchartcelltypevalname` | `nursingchartvalue` | `nursingchartoffset` |

Common `nursingchartcelltypevalname` values: `Temperature (C)`, `Heart Rate`,
`O2 Saturation`, `Non-Invasive BP Systolic/Diastolic/Mean`, `GCS Total`, `Motor`,
`Verbal`, `Eyes`, `QTc`. `vitalPeriodic` stores vitals as **columns** (not name/value), so
aggregate those columns directly per stay.

## Exploratory recipe — finding a variable (no dictionary)

The distinct values of the name columns *are* the dictionary:

```python
nc = read_filtered(DATA_DIR + "nurseCharting.csv", "patientunitstayid", cohort_ids)
nc.nursingchartcelltypevalname.value_counts().head(50)            # what's charted
sorted({x for x in lab.labname.unique() if 'lact' in str(x).lower()})   # fuzzy find a lab
tx[tx.treatmentstring.str.contains("vasopress", case=False, na=False)].treatmentstring.value_counts()
# coverage of a candidate feature across the cohort:
nc[nc.nursingchartcelltypevalname == "Temperature (C)"].patientunitstayid.nunique()
```
To peek without loading a whole large table, read one chunk:
`next(pd.read_csv(path, chunksize=1_000_000))`.

## Gotchas specific to eICU

- Multi-center → the same concept may appear under several `labname`/`drugname` spellings;
  search broadly and union them.
- Temperatures are usually in **°C** here (contrast with PMAP, which is °F).
- Offsets can be negative (pre-ICU) or implausibly large; clip to your window and sanity-
  check ranges.
- Use the offset columns directly — do **not** try to reconstruct wall-clock time.
