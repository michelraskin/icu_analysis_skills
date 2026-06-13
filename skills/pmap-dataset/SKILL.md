---
name: pmap-dataset
description: How to identify patients and find/extract variables in the ACCM PMAP (Johns Hopkins Epic Clarity) dataset for the ttmhte/transfusionhte projects. Use when building a PMAP cohort, finding a PMAP flowsheet meas_id / lab proc_id / clinical variable, or writing a PMAP exploratory notebook. Note PMAP temperatures are in Fahrenheit. Read clinical-icu-datasets first for shared conventions.
---

# PMAP dataset (ACCM PMAP — Johns Hopkins Epic Clarity export)

A local Epic Clarity export, snapshot-dated. Two id levels: **`osler_id`** (patient) and
**`pat_enc_csn_id`** (encounter). Predictors table is one row per `osler_id`.
Reference notebooks (`ttmhte/pmap/`): cohort = `OHCA.ipynb`; features =
`Feature_extraction.ipynb`; temperature work = `TemperatureMeas.ipynb`.

> ⚠ **Temperatures and some vitals are in Fahrenheit**, not Celsius — the hypothermia
> thresholds are `96.8°F` (=36°C) and `77°F` (=25°C). Don't reuse the eICU/MIMIC °C logic
> blindly.

## Location & loading

```python
database_folder = '/projects/LCICM/ACCMPMAP/'
snap = database_folder + '2024-08-15/'     # dated Clarity snapshot
myHours = 60 * 6
```
Big tables read in chunks. Some labs need `on_bad_lines="skip"`. Flowsheet files have
**no header** — columns are assigned manually (see below). `pip install pyarrow` is used
for parquet in some cells.

## Key tables

| File | Key columns |
|---|---|
| `2024-08-15/dbo.accm_patient.csv` | `osler_id`, `gender` (`'Male'`), `birth_date` |
| `2024-08-15/dbo.accm_inpatient.csv` | `pat_enc_csn_id`, `hosp_admsn_time`, `hosp_disch_time`, `admit_source_c`, `hosp_admsn_type_c` (`3.0` = elective), `ed_visit_yn` (`'Y'`), `disch_disp_c` (`20.0` = died/expired), `hospital_service`, `disch_disp_c` |
| `core_icustay_8_15_2024.csv` | `pat_enc_csn_id`, `in_time`, `out_time`, `seq`, `icu`, `origin` (`'init'` = admitted straight to ICU) |
| `2024-08-15/dbo.accm_encounter_dx.csv` | `dx_name`, `icd10_code`, `icd9_code`, `primary_dx_yn`, `dx_ed_yn`, `annotation` |
| `Isalis/Isalis_Flowsheet_part1.csv`, `_part2.csv`, `Isalis_Flowsheetdata.csv` ⚠ no header | flowsheet measurements (vitals, GCS, temp) |
| `Isalis/d_flo_measures.csv` | `flo_meas_id`→`meas_id`, `flo_meas_name`→`meas_name` (**flowsheet dictionary**) |
| `2024-08-15/dbo.accm_labs.csv` ⚠ | `ord_value`, `proc_id`, `specimen_taken_time`, `data_type` (`'Number'`) |
| `2024-08-15/PMAP_commons_dbo_CLARITY_EAP.csv` | `PROC_ID`→`proc_id`, `PROC_NAME`→`proc_name` (**lab/procedure dictionary**) |
| `2024-08-15/dbo.accm_med_admin.csv` ⚠ | `generic_name`, `medication_name`, `taken_time` |

Flowsheet header (assign after reading headerless CSV):
```python
chunk.columns = ['osler_id','pat_enc_csn_id','inpatient_data_id','recorded_time','meas_value',
  'meas_comment','meas_id','meas_row_type_c','meas_val_type_c','meas_template_id','meas_fsd_id',
  'meas_line','meas_occurance','rw_meas_id','ip_lda_id','rw_row_type_c','rw_val_type_c','meas_taken_user_id']
```

## Cohort identification (OHCA)

In `OHCA.ipynb`, using shared `nameSearchCardiacArrest` / `icdSearchCardiacArrest`
(PMAP combines `icd9_code + ' ' + icd10_code` before the ICD search; CA = ICD-10 `i46.`,
ICD-9 `427.5`):

1. CA encounters: `encounter_dx.dx_name` matches CA name regex **or** ICD search; drop
   `annotation == 'H/o cardiac arrest'`.
2. Merge patient + inpatient; compute `age` from `birth_date` vs `hosp_admsn_time`;
   keep `age >= 18` (cap `>100 → 89` to match eICU).
3. Filter to first ICU stay (`seq == 1` or no ICU), **non-elective**
   (`hosp_admsn_type_c != 3`), **through ED or straight to ICU**
   (`ed_visit_yn == 'Y'` or `origin == 'init'`), **dx seen in ED or straight to ICU**
   (`dx_ed_yn == 'Y'` or `origin == 'init'`); drop patients with multiple encounters.
4. Persist ids: `ohca_osler_ids.csv`, `ohca_pat_enc_ids.csv`, `ohca.csv` (and the
   ICU-only variants `icu_ohca_*`). `Feature_extraction.ipynb` reads these.

All event offsets are `(event_time - hosp_admsn_time)` in minutes, kept in `[0, myHours]`
and before `hosp_disch_time`.

## Treatment / outcome / key flowsheet ids

| Concept | How |
|---|---|
| **Death** | `disch_disp_c == 20.0` → `death_at_disch` |
| **mGCS** (neuro outcome) | flowsheet `meas_id in {30405069, 160302}`; first/last numeric value in window → `first_mGCS`/`last_mGCS`; `LastMGCSPositive = (last_mGCS == 6)` |
| **Hypothermia** (treatment, °F!) | temp flowsheet `meas_id in {6, 304301490}`, within first `1440` min; time-weighted mean temp `< 96.8°F` with min `>= 77°F` |
| **Height / Weight** | `meas_id == 11` (height), `meas_id == 14` (weight) |
| **Temp / BP / ED acuity** | `meas_val_type_c == 7` (temp), `== 4` (BP, split `systolic/diastolic`), `meas_id == 16054` (ED acuity) |

`meas_val_type_c` routes flowsheet handling: `1` Numeric, `2` String, `4` BP (split on
`/`), `7` Temperature, `8` Custom/multi-select (split on `;`, one-hot).

## Feature extraction

- Join flowsheet with `d_flo_measures` on `meas_id` to get `meas_name` (lower+underscore).
  Numeric/BP/temp/height/weight → shared `getFeaturesFromDf`/`mergeFeaturesInDf` with
  `typeCol='meas_name'`, `valueCol='meas_value'`, `timeCol='meas_offset'`, prefix `flo`.
- String/custom flowsheet values with ≥100 patients → one-hot (`flo_{meas_name}_{value}`).
- Labs: join `accm_labs` with `CLARITY_EAP` on `proc_id` → `proc_name`; numeric
  (`data_type=='Number'`) → `lab_*` features.
- Meds: `generic_name` (fallback `medication_name`), strip parenthetical/`zzz` prefixes →
  one-hot `med_*`.
- Diagnoses: `dx_name` split on `;`/`-` → `MultiLabelBinarizer`; CA subtypes collapsed
  (asystole, PEA, VF, etc.).

## Exploratory recipes — finding a variable

Search the **two dictionaries** (`d_flo_measures` for flowsheet, `CLARITY_EAP` for labs):

```python
meas = pd.read_csv(database_folder+'Isalis/d_flo_measures.csv').rename(
    columns={'flo_meas_id':'meas_id','flo_meas_name':'meas_name'})
meas[meas['meas_name'].str.contains('glasgow|gcs|motor', case=False, na=False)]   # → meas_id

eap = pd.read_csv(snap+'PMAP_commons_dbo_CLARITY_EAP.csv').rename(
    columns={'PROC_ID':'proc_id','PROC_NAME':'proc_name'})
eap[eap['proc_name'].str.contains('lactate', case=False, na=False)]               # → proc_id
```
Then filter the big flowsheet/lab table to that id, compute offsets, and check coverage
(`df[df.meas_id==<id>].osler_id.nunique()`). For categorical flowsheet items the
`>=100`-patient threshold (`groupby('meas_id')['osler_id'].nunique()`) is used to drop
rare items before one-hot.

## Mapping PMAP/observational features to the HYPERION RCT

`Feature_extraction.ipynb` also contains `FRENCH_CONCEPTS` (maps HYPERION `J0_*`/`BIO_*`
codes like `LACTAT`, `CREAT`, `GLASGOW` to substring keywords) and `EXCLUDE_TERMS` (drops
device/alarm/setting columns). Reuse these when aligning columns across datasets for a
pooled or cross-dataset analysis.
