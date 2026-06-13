---
name: icu-feature-identification
description: Cross-dataset catalogue of where common ICU clinical variables live and how to extract them in eICU-CRD, MIMIC-IV, and PMAP/Epic Clarity exports — GCS and motor GCS (mGCS), discharge status / mortality, ICU and hospital length of stay (days), demographics, vitals, labs, ventilation, vasopressors, sedation, urine output, severity scores, comorbidities. Use after a cohort is identified, when locating or extracting a specific feature/variable, or building the analysis dataset. Pairs with the patient-identification skills eicu-dataset / mimiciv-dataset / pmap-dataset.
---

# ICU feature identification (cross-dataset)

A lookup table for the variables analyses repeatedly need. For each variable it gives the
**locator in each dataset** — the table, the column/`itemid`/`meas_id`, and any extraction
note. Use it once a cohort exists (see the patient-identification skills) to assemble
features.

How locators work per dataset (recap):
- **eICU** — no dictionary; match the inline **name string** (e.g. `nursingchartcelltypevalname == 'Motor'`) or read a fixed column. Times are integer `*offset` (minutes from unit admit).
- **MIMIC-IV** — find the **`itemid`** in `d_items` (ICU) / `d_labitems` (hosp labs) by label, then filter the event table. **Verify itemids in `d_items`** — labels below are search terms; the numeric ids listed are the common MetaVision ones but confirm in your version. Times are timestamps → compute offsets.
- **PMAP** — find the **`meas_id`** in `d_flo_measures` (flowsheet) or **`proc_id`** in `CLARITY_EAP` (labs) by name. Times are timestamps. ⚠ temps usually °F.

`KEY` = the grain id (`patientunitstayid` / `stay_id` / `osler_id`).

## Baseline covariates — include in (almost) every analysis

Pull this standard block by default for any cohort, before the analysis-specific variables.
It anchors descriptive tables, adjustment/confounding control, and subgroup definitions:

- **Demographics:** age, sex, race/ethnicity
- **Anthropometrics:** weight (kg), height (cm), **BMI** (compute `weight/(height/100)**2`
  when not stored)
- **Admission context:** admission type/source, admission diagnosis/reason
- **Severity at baseline:** GCS / motor GCS, an acuity score (APACHE where native), a
  baseline SOFA if feasible
- **Outcomes/exposure-time:** discharge status (mortality), ICU length of stay (days),
  hospital length of stay

The locators for each are in the tables below (demographics/anthropometrics in *Identifiers,
demographics*; status & LOS in *Admission / discharge / length of stay*).

## Identifiers, demographics

| Variable | eICU | MIMIC-IV | PMAP |
|---|---|---|---|
| Patient / stay id | `patient.patientunitstayid` (+ `uniquepid`, `patienthealthsystemstayid`) | `subject_id` / `hadm_id` / `stay_id` | `osler_id` / `pat_enc_csn_id` |
| Age | `patient.age` (string; `'> 89'`→90) | `patients.anchor_age` | from `accm_patient.birth_date` vs `hosp_admsn_time` |
| Sex | `patient.gender` | `patients.gender` (`M`/`F`) | `accm_patient.gender` |
| Weight | `patient.admissionweight` (kg) | chartevents *admission/daily weight* (search `d_items` "weight"; e.g. 226512/224639) or `inputevents.patientweight` | flowsheet `meas_id == 14` |
| Height | `patient.admissionheight` (cm) | chartevents "height" (search `d_items`; e.g. 226730) or `omr` "Height (Inches)" | flowsheet `meas_id == 11` |
| BMI | compute: `weight/(height/100)**2` | `omr` "BMI (kg/m2)" or compute | compute |
| Race / ethnicity | `patient.ethnicity` | `admissions.race` | institutional field |

## Admission / discharge / length of stay  ← (status at discharge, days in ICU)

| Variable | eICU | MIMIC-IV | PMAP |
|---|---|---|---|
| **Discharge status (mortality)** | `patient.hospitaldischargestatus == 'Expired'` (hosp); `patient.unitdischargestatus == 'Expired'` (ICU) | `admissions.hospital_expire_flag` (hosp); ICU death = `admissions.deathtime` within `icustays.intime…outtime`; also `patients.dod` | `accm_inpatient.disch_disp_c` (a specific code = expired — **verify the code**) |
| Discharge location/disposition | `patient.hospitaldischargelocation` | `admissions.discharge_location` | `accm_inpatient.disch_disp_c` |
| **ICU length of stay (days)** | `patient.unitdischargeoffset / 1440` | `icustays.los` (already days) or `(outtime − intime).days` | `(core_icustay.out_time − in_time)` in days |
| Hospital length of stay (days) | `patient.hospitaldischargeoffset / 1440` | `(admissions.dischtime − admittime)` | `(accm_inpatient.hosp_disch_time − hosp_admsn_time)` |
| Admission type / source | `patient.apacheadmissiondx`, `hospitaladmitsource` | `admissions.admission_type`, `admission_location` | `accm_inpatient.hosp_admsn_type_c`, `admit_source_c` |
| ICU readmission / stay seq | `patienthealthsystemstayid` groups stays | `icustays` rows per `hadm_id` | `core_icustay.seq` |

## Neurologic — GCS and motor GCS (mGCS)

| Variable | eICU | MIMIC-IV | PMAP |
|---|---|---|---|
| **GCS total** | `nurseCharting` where `nursingchartcelltypevalname == 'GCS Total'` | chartevents GCS components; total often = eye+verbal+motor (search `d_items` "GCS") | flowsheet: search `d_flo_measures` "glasgow"/"gcs" |
| **Motor GCS (mGCS)** | `nurseCharting` where `nursingchartcelltypevalname == 'Motor'` | chartevents **`itemid == 223901`** (GCS-Motor) | flowsheet **`meas_id in {30405069, 160302}`** |
| GCS eye / verbal | names `'Eyes'` / `'Verbal'` | eye ≈ 220739, verbal ≈ 223900 (verify) | search `d_flo_measures` |
| Pupils | `nurseCharting` name contains `'pupil'` | search `d_items` "pupil" | search `d_flo_measures` "pupil" |

**First/last mGCS in window** (the common neuro-outcome construction): sort the variable's
rows by offset within the cohort, take the min-offset (first) and max-offset (last) value per
stay. A "good" motor outcome is often `last motor GCS == 6`.

**Defining "comatose" (e.g. for a post-arrest cohort).** Coma is conventionally **GCS total
≤ 8** (or motor GCS ≤ 4 / not following commands). Two cautions when using GCS as a coma
*signal* rather than just a feature: (1) **sedation confounds it** — a low GCS while the
patient is on propofol/midazolam/dexmedetomidine/fentanyl (see *Organ support → Sedation*) is
sedation, not neurologic coma; prefer an off-sedation assessment, or take the **worst (min)
GCS in a window** and note sedation exposure rather than a single sedated reading. (2) Clean
the eICU `'Unable to score'`/non-numeric GCS strings before thresholding. Pair this with a
cardiac-arrest signal (diagnosis/text) and a sensible time anchor — see the post-arrest
timing note in **clinical-icu-datasets**.

## Vital signs

| Variable | eICU | MIMIC-IV | PMAP |
|---|---|---|---|
| Heart rate | `vitalPeriodic.heartrate`; `nurseCharting` `'Heart Rate'` | chartevents HR (≈220045) | flowsheet (search "pulse"/"heart rate") |
| Systolic / diastolic / mean BP | `vitalPeriodic.systemicsystolic/diastolic/mean`; `nurseCharting` `'Non-Invasive BP …'` | chartevents ABP 220050/051/052 (invasive), NBP 220179/180/181 | flowsheet `meas_val_type_c == 4` (BP, split `sys/dia`) |
| SpO2 | `vitalPeriodic.sao2`; `'O2 Saturation'` | chartevents SpO2 (≈220277) | flowsheet (search "spo2"/"o2 sat") |
| Respiratory rate | `vitalPeriodic.respiration` | chartevents RR (≈220210) | flowsheet (search "resp rate") |
| Temperature | `vitalPeriodic.temperature`; `'Temperature (C)'` (°C) | chartevents temp F≈223761 / C≈223762 | flowsheet `meas_val_type_c == 7` or `meas_id in {6, 304301490}` (**°F**) |

## Laboratory values

| eICU | MIMIC-IV | PMAP |
|---|---|---|
| `lab.csv` → match `labname` (e.g. `'Hgb'`, `'lactate'`, `'creatinine'`, `'platelets x 1000'`, `'PT - INR'`, `'sodium'`, `'glucose'`, `'total bilirubin'`, `'pH'`, `'paO2'`, `'paCO2'`, `'Base Excess'`, `'bicarbonate'`, `'WBC x 1000'`, `'Hct'`); value = `labresult`, time = `labresultoffset` | `labevents` (hosp) via `d_labitems` label, value = `valuenum`; some bedside labs also in `chartevents` via `d_items` | `accm_labs.ord_value` joined to `CLARITY_EAP` `proc_name` (keep `data_type == 'Number'`); search the proc dictionary by name |

Common labs to look up by name: hemoglobin/hematocrit, WBC, platelets, lactate, creatinine,
BUN, sodium, potassium, glucose, bilirubin, INR/PT/PTT, fibrinogen, pH, paO2, paCO2, base
excess, bicarbonate, troponin, albumin.

## Organ support & interventions

| Variable | eICU | MIMIC-IV | PMAP |
|---|---|---|---|
| Mechanical ventilation | `respiratoryCare` (`ventstartoffset`>0 /`ventendoffset`, `airwaytype`), `respiratoryCharting` (`respchartvaluelabel`); `treatment` string; `apacheApsVar.intubated`/`vent` (day-1 cross-check) — union, no single flag | `procedureevents` invasive vent ≈225792 / NI ≈225794; chartevents vent mode | flowsheet measures (search "ventilator"/"vent mode"/"o2 device") |
| PEEP / FiO2 | `respiratoryCharting` (`respchartvaluelabel` "peep"/"fio2") | chartevents PEEP≈220339, FiO2≈223835 | flowsheet (search "peep"/"fio2") |
| Vasopressors | `infusionDrug.drugname` (norepinephrine/epinephrine/dopamine/dobutamine/vasopressin/phenylephrine) | `inputevents` via `d_items` vasopressor labels | `accm_med_admin.generic_name` |
| Sedation / analgesia | `infusionDrug`/`medication` `drugname` (propofol/midazolam/dexmedetomidine/fentanyl/ketamine) | `inputevents` via `d_items`; `prescriptions.drug` | `accm_med_admin.generic_name` |
| Urine output / fluid balance | `intakeOutput` (`celllabel`/`cellpath` "urine"; `intaketotal`/`outputtotal`/`nettotal`) | `outputevents` urine itemids | flowsheet I/O measures |
| RRT / dialysis | `treatment` string "dialysis"/"CRRT"; `infusionDrug` | `procedureevents`/`inputevents` CRRT itemids (search `d_items` "dialysis"/"CRRT") | flowsheet / `accm_med_admin` |

## Severity scores & comorbidities

| Variable | eICU | MIMIC-IV | PMAP |
|---|---|---|---|
| APACHE score / predicted mortality | `apachePatientResult` (`apachescore`, `predictedhospitalmortality`; pick IVa), `apacheApsVar` | not native — compute | not native — compute |
| SOFA | compute from components | compute from components | compute from components |
| Comorbidities / past history | `pastHistory.pasthistorypath` | `diagnoses_icd` (Elixhauser/Charlson from ICD) | `accm_encounter_dx` |

**SOFA components** (worst value per window/day; standard cut-points): respiration
(PaO2/FiO2), coagulation (platelets), liver (bilirubin), cardiovascular (MAP +
vasopressor doses), CNS (GCS total), renal (creatinine + urine output). Score each 0–4 and
sum; report how many components were observed (missingness is common).

## Extraction notes

- **Numeric summary in a window:** for any numeric variable, after restricting to
  `0 ≤ offset ≤ window`, summarize per stay as `first`/`last`/`min`/`max`/`mean` (see
  `window_features` in clinical-icu-datasets). `first`/`last` = earliest/latest by offset.
- **Find the locator** when unsure: search the dataset's dictionary / distinct names with the
  exploratory snippet in the per-dataset skill, and **check coverage**
  (`series.notna().mean()`) before relying on a variable.
- **Units & sentinels:** confirm units (°C vs °F, kg vs lbs, mg/dL vs mmol/L) and clean
  sentinels (eICU `'> 89'`, "Unable to score" GCS strings) before casting/aggregating.
- **Verify MIMIC itemids** in `d_items`/`d_labitems` for your version rather than trusting a
  remembered number; confirmed-from-source ids here: mGCS `223901`, temperature-management/
  cooling `225052`, CPR procedure `225466`.
