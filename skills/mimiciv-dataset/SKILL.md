---
name: mimiciv-dataset
description: How to identify patients and find/extract variables in MIMIC-IV v2.2 (+ MIMIC-IV-ED) for the ttmhte/transfusionhte projects. Use when building a MIMIC cohort, finding a MIMIC itemid/ICD code or clinical variable, or writing a MIMIC exploratory notebook. Read clinical-icu-datasets first for shared conventions.
---

# MIMIC-IV dataset

Single-center (BIDMC) ICU + ED database, v2.2. Unlike eICU, values live in **long event
tables resolved through dictionaries** (`d_items`, `d_icd_diagnoses`). Three id levels:
**`subject_id`** (patient), **`hadm_id`** (hospital admission), **`stay_id`** (ICU or ED
stay). The predictors table is one row per `subject_id`.
Reference notebooks (`ttmhte/mimiciv/`): cohort = `CA_ED.ipynb` + `CA_time.ipynb`;
features = `Feature_extraction.ipynb`.

## Location & module layout

```python
database_folder = '/projects/LCICM/'
hosp = database_folder + 'mimic-iv-2.2/hosp/'        # hospital-wide
icu  = database_folder + 'mimic-iv-2.2/icu/'         # ICU module
ed   = database_folder + 'mimic-iv-ed-2.2/mimic-iv-ed-2.2/ed/'   # ED (.csv.gz)
myHours = 60 * 6
```
Big tables (`chartevents`, `diagnoses_icd`, `outputevents`, `inputevents`, `emar`,
`procedureevents`, ED `.csv.gz`) read in chunks, filtered on `subject_id`. ED files are
gzip: `pd.read_csv(path, compression='gzip')`.

## Key tables

| Module | File | Key columns |
|---|---|---|
| hosp | `patients.csv` | `subject_id`, `gender` (`'M'`/`'F'`), `anchor_age` |
| hosp | `admissions.csv` | `hadm_id`, `admittime`, `dischtime`, `admission_type` (`'ELECTIVE'`, `'SURGICAL SAME DAY ADMISSION'`…), `edregtime`, `hospital_expire_flag` (death) |
| hosp | `diagnoses_icd.csv` ⚠ | `hadm_id`, `icd_code`, `seq_num` |
| hosp | `d_icd_diagnoses.csv` | `icd_code`, `long_title` (ICD **dictionary**) |
| hosp | `emar.csv` ⚠ | `medication`, `charttime` (med administrations) |
| hosp | `omr.csv` | `result_name` (`Height (Inches)`, `Weight (Lbs)`, `BMI (kg/m2)`), `result_value`, `chartdate` |
| icu | `icustays.csv` | `stay_id`, `intime`, `outtime` |
| icu | `chartevents.csv` ⚠⚠ | `itemid`, `value`, `valuenum`, `charttime` (vitals/labs/GCS) |
| icu | `d_items.csv` | `itemid`, `label`, `abbreviation`, `param_type` (**item dictionary**) |
| icu | `outputevents.csv`, `inputevents.csv` ⚠ | `itemid`, `value`, `charttime`/`starttime` |
| icu | `procedureevents.csv` ⚠ | `itemid`, `starttime` |
| ed | `edstays.csv.gz` | `subject_id`, `hadm_id`, `stay_id`, `intime`, `outtime`, `disposition` |
| ed | `triage.csv.gz` | `chiefcomplaint` |
| ed | `diagnosis.csv.gz` | `icd_code` |

`d_items.param_type` routes feature handling: `Numeric` → numeric features;
`Numeric with tag` → labs; `Checkbox` → binary; `Text` → categorical/one-hot.

## Cohort identification (cardiac arrest)

Built from **two paths, then unioned** (see shared `nameSearchCardiacArrest` /
`icdSearchCardiacArrest`; CA ICD = ICD-10 `I46*`, ICD-9 `4275`):

1. **ED chief complaint** (`CA_ED.ipynb`): `triage.chiefcomplaint` matches the CA name
   regex → join `edstays` for `hadm_id` → keep `anchor_age >= 18`. Saved as `CA_ED.csv`.
2. **ICD diagnosis path** (`CA_ED.ipynb`): `diagnoses_icd` ∩ CA codes from
   `d_icd_diagnoses`, excluding `intraoperative`; require a recorded **ICU stay**,
   **non-elective** admission (`admission_type` not in `{SURGICAL SAME DAY ADMISSION,
   ELECTIVE}`), patient **went through ED or straight to ICU**, and CA **diagnosis also
   seen in ED**; drop subjects with multiple qualifying admissions.
3. **Procedure path** (`CA_time.ipynb`): `procedureevents.itemid == 225466` (the CPR /
   cardiac-arrest procedure) gives an arrest time. Saved as `CA_time.csv`.

`Feature_extraction.ipynb` unions the ids and sets each patient's **reference `time`** =
ED `intime` (ED path) or `max(arrest starttime, ICU intime)` (procedure path). All event
offsets are `(charttime - time)` minutes, kept in `[0, myHours]`.

## Treatment / outcome / key itemids

| Concept | How |
|---|---|
| **mGCS** (neuro outcome) | `chartevents.itemid == 223901` (GCS-Motor); first/last `valuenum` in window → `first_mGCS`/`last_mGCS`; `LastMGCSPositive = (last_mGCS == 6)` |
| **Hypothermia** (treatment) | `chartevents.itemid == 225052` (temperature-management / cooling status), `value == 'On'`; longest contiguous "On" run `>= 720` min within first `1440` min |
| **Death** | `admissions.hospital_expire_flag` |
| **Height/Weight/BMI** | `omr.csv` latest values on/before the event date |

## Feature extraction

Merge `chartevents`/`outputevents`/`inputevents` with `d_items[['itemid','label','param_type']]`
(lower-case + underscore the `label`), split by `param_type`, then:
- Numeric / labs → shared `getFeaturesFromDf` + `mergeFeaturesInDf` with
  `typeCol='label'`, `valueCol='value'`, `timeCol='chartoffset'`, prefixes `chart`/`lab`/`output`.
- Checkbox/binary → pivot max per `(subject_id, label)` → `chart_*`.
- Text/categorical → `MultiLabelBinarizer` (split on `;`).
- `inputevents`, `emar` (meds) → one-hot presence per subject (`input_*`, `med_*`).
- Other diagnoses → one-hot `dx_*` from `diagnoses_icd` ∩ non-CA `long_title`.

## Exploratory recipes — finding a variable

Search the **dictionaries** first (this is the main difference from eICU):

```python
d_items = pd.read_csv(icu+'d_items.csv')
# find the itemid for a charted variable
d_items[d_items['label'].str.contains('lactate', case=False, na=False)][['itemid','label','param_type','abbreviation']]

d_icd = pd.read_csv(hosp+'d_icd_diagnoses.csv')
# find ICD codes / titles for a condition
d_icd[d_icd['long_title'].str.contains('cardiac arrest', case=False, na=False)]
```
Then pull only that `itemid` from `chartevents` (filter inside the chunk loop on both
`subject_id.isin(cohort)` and `itemid == <id>`), compute offsets, and check coverage:
`chartevents_df[chartevents_df.itemid==<id>].subject_id.nunique()`.
For meds, search `emar.medication.value_counts()`; for procedures search `d_items` with
`param_type` ignored (procedure items share the dictionary).
