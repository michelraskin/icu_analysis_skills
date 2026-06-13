---
name: clinical-icu-datasets
description: Overview and router for the cardiac-arrest / transfusion ICU research datasets (eICU, MIMIC-IV, PMAP, Hyperion) used in the ttmhte and transfusionhte projects. Use when starting any analysis on these datasets, building a cohort, locating a clinical variable, or writing an exploratory notebook. Routes to the per-dataset skills eicu-dataset, mimiciv-dataset, pmap-dataset.
---

# Clinical ICU datasets (ttmhte / transfusionhte)

Shared knowledge for two research projects that estimate **heterogeneous treatment
effects (HTE)** in critically ill patients across several ICU databases.

## The two projects

| Repo | Path | Question | Treatment | Cohort | Primary outcomes |
|---|---|---|---|---|---|
| **ttmhte** | `~/Documents/GitHub/ttmhte` | Does targeted temperature management (TTM / therapeutic hypothermia) help, and for whom? | `hypothermia` (a.k.a. `Hypothermia`, `treatment_hypothermia`) | Cardiac arrest patients | `LastMGCSPositive` (neuro recovery), `death_at_disch` / `DeathAtDischarge` |
| **transfusionhte** | `~/transfusionhte` | HTE of blood transfusion / massive transfusion | transfusion (PRBC / plasma / platelets / blood products) | Trauma — intracranial injury (ICD-9 `850`–`854`) | death, neuro |

Both projects reuse the **same databases and the same code pattern**, just with a
different cohort definition, treatment column, and outcome.

## The datasets (one sub-folder per database in each repo)

- **eICU** — eICU Collaborative Research Database (multi-center US ICU). Wide CSV
  tables keyed by `patientunitstayid`. → see **eicu-dataset** skill.
- **mimiciv** — MIMIC-IV v2.2 + MIMIC-IV-ED. Keyed by `subject_id` / `hadm_id` /
  `stay_id`; values live in long event tables resolved through dictionaries. → see **mimiciv-dataset** skill.
- **pmap** — ACCM PMAP (Johns Hopkins Epic Clarity export). Keyed by `osler_id` /
  `pat_enc_csn_id`; flowsheets + labs resolved through dictionaries. → see **pmap-dataset** skill.
- **hyperion** (ttmhte only) — the French HYPERION RCT. A single pre-formatted table
  with `J0_*` / `V0_*` / `BIO_*` columns and `CPC` outcome; no cohort building needed.
  Mappings to the observational datasets live in the `FRENCH_CONCEPTS` dict in
  `pmap/Feature_extraction.ipynb`.

## The universal pipeline pattern

Every dataset follows the same two-stage flow:

1. **Cohort + feature extraction notebook(s)** build a one-row-per-patient table called
   `myPredictorsDf` and save it to a CSV:
   - eICU → `eICUPredictorsDiag.csv` (cohort+features in one notebook, `eICU.ipynb`)
   - MIMIC → `MIMIC_Predictors*.csv` (cohort in `CA_ED.ipynb` + `CA_time.ipynb` → features in `Feature_extraction.ipynb`)
   - PMAP → `PMAP_Predictors*.csv` (cohort in `OHCA.ipynb` → features in `Feature_extraction.ipynb`)
2. **Analysis notebooks + `*Util.py`** load that CSV via `getTrainTestFunctions(...)` and
   run the modeling (`*AnalysisDML`, `*AnalysisBART`, `*AnalysisClassif`,
   `*AnalysisNeural`, regression, unsupervised, etc.).

`<dataset>Util.py` / `MIMICUtil.py` / `PMAPUtil.py` all expose the same entry point:

```python
getTrainTestFunctions(aPredictedColumn='LastMGCSPositive',
                      aTreatmentColumn='hypothermia',   # 'Hypothermia' in eICU
                      aTestSize=0.3, aTreatmentSplit=False,
                      aDropColumns=[], aSkipTemp=True)
# returns (myPredictorsDf, X_train, X_test, [T_train, T_test,] y_train, y_test)
```
It reads the predictors CSV, drops highly-treatment-correlated columns
(`top_correlations.csv`, |corr|>0.7), drops rare binaries (<15 positives), drops
temperature-derived columns when `aSkipTemp` (to avoid leaking the treatment), and
stratifies the split on outcome × treatment.

## Conventions that hold across ALL datasets

- **Time window:** `myHours = 60*6` → features use only the **first 6 hours** after the
  reference time (admission / arrest). Hypothermia detection uses 24 h (`1440`) or 48 h
  (`2880`) windows.
- **Offsets** are minutes from the reference time. In eICU they're columns in the data
  (`*offset`); in MIMIC/PMAP you compute them: `(event_time - reference_time)` in minutes,
  then keep `0 <= offset <= myHours`.
- **Feature column naming:** `{prefix}_{first|last|max|min|mean}_{variable}`.
  Prefixes: `nurse`, `lab`, `chart`, `output`, `input`, `med`, `flo`, `dx`, `diagnosis`,
  `treatment`. `first`/`last` = earliest/latest value in the window; `max`/`min`/`mean`
  = aggregates.
- **Two shared helper functions** appear in every feature-extraction notebook:
  - `getFeaturesFromDf(df, timeCol, typeCol, valueCol)` → `(group, begin, end, agg)`
  - `mergeFeaturesInDf(predictorsDf, begin, end, agg, prefix, typeCol, valueCol)` → wide df
  Copy these from any existing `Feature_extraction.ipynb` rather than rewriting them.
- **Cardiac-arrest identification** uses two shared regex functions,
  `nameSearchCardiacArrest(text)` (matches cardiac/cardio/circulatory arrest, asystole,
  PEA, post-arrest; excludes history/neonatal/respiratory) and
  `icdSearchCardiacArrest(text)` (ICD-10 `I46*`, ICD-9 `4275`/`427.5`). They are
  duplicated in CA_ED.ipynb, CA_time.ipynb, OHCA.ipynb — reuse verbatim for consistency.
- **mGCS outcome:** the neuro outcome is the *motor* component of GCS. `LastMGCSPositive`
  = (`last_mGCS` == 6). Patients who died are forced to `last_mGCS = 1`. Rows where first
  and last mGCS times are equal (single measurement) are filtered out.

## Where the data lives

- ttmhte (current, server): `database_folder = '/projects/LCICM/'`
  (eICU under `/projects/LCICM/eICU/`, MIMIC under `/projects/LCICM/mimic-iv-2.2/` and
  `/projects/LCICM/mimic-iv-ed-2.2/`, PMAP under `/projects/LCICM/ACCMPMAP/`).
- transfusionhte (older, SciServer): mounted via
  `from mount_drive import mount_s_drive; mount_s_drive(subfolder='LCICM/Databases/eICU')`
  to `/home/idies/workspace/SAFE/`. Original network share is `S:\LCICM\Databases`.
- Raw clinical CSVs are **not in the repos** (git-ignored, PHI). Notebooks read from the
  mounted data folder; only derived `*Predictors*.csv` / cohort id files are produced.

## Writing a new exploratory notebook (general recipe)

1. `import pandas as pd, numpy as np, re, math`; set `myHours = 60*6` and `database_folder`.
2. Load the dictionary table for the dataset (eICU: distinct values of the type column;
   MIMIC: `d_items` / `d_icd_diagnoses`; PMAP: `d_flo_measures` / `CLARITY_EAP`).
3. **Find a variable** by fuzzy search on the dictionary/label, e.g.
   `dict_df[dict_df['label'].str.contains('lactate', case=False, na=False)]` — note the
   id (`itemid` / `meas_id` / `proc_id`) or the exact label string.
4. Read big tables in chunks filtered to your cohort ids (`read_by_chunks` pattern), keep
   only the columns you need, compute offsets, restrict to the time window.
5. Inspect coverage before committing a feature:
   `series.notna().mean()` (fraction of patients with the value) and `series.nunique()`.
6. Add the variable to the feature-extraction step using `getFeaturesFromDf` /
   `mergeFeaturesInDf` (numeric) or one-hot encoding (categorical/binary).

See the per-dataset skills for the exact table names, id columns, key item ids, and
copy-paste search snippets.
