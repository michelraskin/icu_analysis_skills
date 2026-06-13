---
name: eicu-dataset
description: How to identify patients and find/extract variables in the eICU Collaborative Research Database for the ttmhte/transfusionhte projects. Use when building an eICU cohort, locating an eICU clinical variable (lab, vital, treatment, diagnosis), or writing an eICU exploratory notebook. Read clinical-icu-datasets first for shared conventions.
---

# eICU dataset

Multi-center US ICU database (eICU-CRD). Flat CSV tables, one row per measurement/event,
all keyed by **`patientunitstayid`** (one ICU stay = one patient row in `myPredictorsDf`).
Reference notebook: `ttmhte/eICU/eICU.ipynb` (cohort + features in a single notebook).
`transfusionhte/eICU/eICU.ipynb` is the same pattern with a trauma cohort.

## Location & loading

```python
database_folder = '/projects/LCICM/eICU/'      # ttmhte (server)
# transfusionhte: mount_s_drive(subfolder='LCICM/Databases/eICU'); '/home/idies/workspace/SAFE/'
myHours = 60 * 6                                # 6-hour feature window
```
Small tables load directly with `pd.read_csv`. **Big tables** (`nurseCharting.csv`,
`lab.csv`) must be read in chunks and filtered to your ids:

```python
df_chunks = []
for chunk in pd.read_csv(database_folder+'nurseCharting.csv', chunksize=1e6):
    df_chunks.append(chunk[chunk['patientunitstayid'].isin(myIds.patientunitstayid)])
nurse_charting_df = pd.concat(df_chunks, ignore_index=True)
```

## Key tables and the columns that matter

| Table | Key columns | What it holds |
|---|---|---|
| `patient.csv` | `gender`, `age` (string, `'> 89'`), `apacheadmissiondx`, `admissionheight`, `admissionweight`, `hospitaladmittime24`, `hospitaladmitsource`, `hospitaldischargestatus` (`'Expired'` = death) | demographics & admission |
| `treatment.csv` | `treatmentstring` (pipe-`|`-delimited path), `treatmentoffset` | interventions incl. hypothermia |
| `diagnosis.csv` | `diagnosisstring` (pipe path), `icd9code`, `diagnosisoffset` | diagnoses |
| `nurseCharting.csv` ⚠ big | `nursingchartcelltypevalname` (the variable), `nursingchartvalue`, `nursingchartoffset`, `nursingchartentryoffset` | vitals, GCS, etc. |
| `lab.csv` ⚠ big | `labname`, `labresult`, `labresultoffset` | labs |
| `infusionDrug.csv` | `drugname` | infusions (blood products for transfusion) |
| `intakeOutput.csv` | `cellpath`, `celllabel` | I/O incl. blood/PRBC |

Note: in `patient.csv`, `age` is a string with `'> 89'` for old patients → replace with
`89` before `astype(int)`. `bmi = admissionweight / (admissionheight/100)**2`.

## Cohort identification

- **Cardiac arrest (ttmhte):** `apacheadmissiondx` contains `'Cardiac arrest'`, or
  `diagnosis.icd9code` contains `427.5`. Filter `age >= 18`. Cohort ids are persisted as
  `patient_ids.csv` and re-used by `eICU.ipynb`.
- **Trauma / intracranial injury (transfusionhte):** `diagnosis.icd9code` first 3 chars in
  `{'850','851','852','853','854'}`.
- **Transfusion exposure (transfusionhte):** `treatmentstring` contains `transfusion`; or
  `intakeOutput.cellpath`/`celllabel` contains `blood`/`prbc` (excluding `loss`); or
  `infusionDrug.drugname` contains `blood`/`prbc`/`platelets`/`plasma`.

## Treatment / outcome definitions

- **Hypothermia (treatment):** two independent signals, combined into `both_hypothermia`:
  1. `treatment_hypothermia` — `treatmentstring` contains `'hypothermia'`.
  2. `Hypothermia` — from `nurseCharting` Temperature (C): within first 48 h
     (`nursingchartentryoffset < 2880`), temp `< 36`, **>12** sub-36 readings, min temp
     `> 25`, and the sub-36 span (`max-min offset`) `> 720` min (12 h).
- **Death:** `DeathAtDischarge = (hospitaldischargestatus == 'Expired')`.
- **Neuro outcome `LastMGCSPositive`:** built from the Motor GCS (`Motor`) first/last
  values within window (`FirstMGCS`/`LastMGCS`); positive when `LastMGCS == 6`.

## Pipe-delimited strings → one-hot

`treatmentstring` and `diagnosisstring` are hierarchical pipe paths. Expand them:

```python
def getOneHotConditions(aDf, aColumn, aPrefix):
    aDf['conditions'] = aDf[aColumn].str.split('|')
    one_hot = aDf['conditions'].explode().str.get_dummies().groupby(level=0).sum()
    return aDf.drop(columns=['conditions']).join(one_hot.add_prefix(aPrefix)), one_hot.add_prefix(aPrefix)
```
Then aggregate per patient within `myHours` and binarize (`!= 0`).

## Numeric feature extraction

`nurseCharting` and `lab` are long tables → use the shared helpers with these arguments:

```python
# nurseCharting:  typeCol='nursingchartcelltypevalname', valueCol='nursingchartvalue', timeCol='nursingchartoffset'
# lab:            typeCol='labname',                      valueCol='labresult',        timeCol='labresultoffset'
g,b,e,a = getFeaturesFromDf(nurse_charting_df, 'nursingchartoffset', 'nursingchartcelltypevalname', 'nursingchartvalue')
myPredictorsDf = mergeFeaturesInDf(myPredictorsDf, b, e, a, 'nurse', 'nursingchartcelltypevalname', 'num_values')
```
Produces `nurse_first_*`, `nurse_last_*`, `nurse_{max,min,mean}_*`, `lab_first_*`, etc.

Common `nursingchartcelltypevalname` values: `Temperature (C)`, `GCS Total`, `Motor`,
`Heart Rate`, `O2 Saturation`, `Non-Invasive BP Systolic/Diastolic/Mean`, `QTc`.
GCS first/last are extracted separately (sort by offset, take min/max offset per patient).

## Exploratory recipes — finding a variable

eICU has **no dictionary table**; the "dictionary" is the distinct values of the type
column. Load a sample (or the cohort-filtered table) and search:

```python
# what vitals/charted items exist?
nurse_charting_df['nursingchartcelltypevalname'].value_counts().head(50)
# fuzzy find a lab
sorted({x for x in lab_df['labname'].unique() if 'lact' in str(x).lower()})
# which treatments mention a keyword?
treatment_df[treatment_df.treatmentstring.str.contains('transfus', case=False, na=False)].treatmentstring.value_counts()
# coverage of a candidate feature across the cohort
(nurse_charting_df[nurse_charting_df.nursingchartcelltypevalname=='Temperature (C)']
   .patientunitstayid.nunique())
```
Tip: to explore without loading the whole big table, read one chunk
(`next(pd.read_csv(path, chunksize=1e6))`) and inspect its `*name` columns.
