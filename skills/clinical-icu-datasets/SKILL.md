---
name: clinical-icu-datasets
description: Overview and router for working with critical-care EHR datasets (eICU-CRD, MIMIC-IV, and institutional Epic Clarity exports such as PMAP) in machine-learning and statistical analyses. Use when starting any ICU-data analysis, defining a patient cohort, locating a clinical variable, engineering time-windowed features, or writing an exploratory notebook. Routes to the per-dataset skills eicu-dataset, mimiciv-dataset, pmap-dataset.
---

# Critical-care (ICU) EHR datasets for ML

Shared mental model and reusable workflow for analyzing intensive-care electronic health
record (EHR) datasets. These notes are dataset-agnostic; the per-dataset skills
(**eicu-dataset**, **mimiciv-dataset**, **pmap-dataset**) give the concrete table names,
ID columns, dictionaries, and gotchas.

## What these datasets are

ICU EHR datasets are de-identified (or institutional) dumps of everything recorded during
a critical-care stay: demographics, admission/discharge info, vital signs, laboratory
results, medications, fluid intake/output, procedures, diagnoses (ICD), and nursing
assessments (e.g. Glasgow Coma Scale). They are **longitudinal and irregularly sampled** —
each clinical measurement is its own timestamped row, and different patients have wildly
different numbers of rows. Turning them into an ML-ready matrix is most of the work.

| Dataset | Source / population | Access | Shape |
|---|---|---|---|
| **eICU-CRD** | ~200k ICU stays, 200+ US hospitals (Philips eICU telehealth), MIT-LCP | PhysioNet, credentialed | Flat denormalized CSVs; times are integer **offsets** (minutes from unit admission) |
| **MIMIC-IV** | Single academic center (Boston), 2008–2019; + ED/Note/CXR add-ons | PhysioNet, credentialed | Relational `hosp`/`icu` modules; real (date-shifted) **timestamps**; values via dictionaries |
| **PMAP / Epic Clarity export** | Institutional EHR (Epic Clarity/Caboodle) | Private / DUA | Raw Clarity tables; flowsheets + labs resolved via measure/procedure dictionaries |

## The common mental model

Despite different schemas, all three share the same structure:

1. **An ID hierarchy** — patient → hospital admission → ICU/ED stay. Pick the grain your
   analysis lives at (usually one row per ICU stay or per admission) and key everything to it.
2. **Event tables** — long tables of `(id, time, variable, value)`. Vitals, labs, meds,
   I/O, charted observations all follow this shape.
3. **Dictionaries** — most datasets store a numeric `itemid`/`meas_id`/`proc_id` in the
   event table and the human-readable name in a separate dictionary table. Finding a
   variable = searching the dictionary for the id, then filtering the event table by id.
   (eICU is the exception: the variable name is stored inline.)
4. **A reference / index time ("time zero")** — the instant features are measured relative
   to (unit admission, ED arrival, or an event time). All event times become **offsets** =
   `event_time − time_zero` in minutes.

## A reusable ML workflow on ICU data

1. **Define the cohort.** Select stays by ICD diagnosis code, procedure, chief complaint
   text, admission type, age, or any combination. Persist the selected id list so every
   downstream step filters to the same patients.
2. **Choose time zero and a feature window.** A common choice is the first **6 hours**
   (`window = 6*60` minutes) after admission/index for predictors, with outcomes measured
   later. Restrict events to `0 <= offset <= window` to avoid leaking the future.
3. **Engineer time-windowed features** — for each numeric variable, summarize within the
   window as `first`, `last`, `min`, `max`, `mean` (see helper below). One-hot categorical/
   binary items (presence within window). This collapses the long event tables into one
   row per stay.
4. **Assemble** a single wide table (one row per id, columns = features + outcome[s] +
   treatment/exposure), check coverage/missingness, then model.

### Reusable helpers (copy & adapt)

Read a large CSV in chunks, keeping only your cohort:

```python
def read_filtered(path, id_col, ids, chunksize=1_000_000, **kw):
    parts = []
    for chunk in pd.read_csv(path, chunksize=chunksize, **kw):
        parts.append(chunk[chunk[id_col].isin(ids)])
    return pd.concat(parts, ignore_index=True)
```

Summarize a long event table into first/last/min/max/mean per variable, in-window:

```python
def window_features(df, id_col, time_col, type_col, value_col, window):
    d = df[(df[time_col] >= 0) & (df[time_col] <= window)].copy()
    d['_v'] = pd.to_numeric(d[value_col], errors='coerce')
    g = d.groupby([id_col, type_col])
    first = d.loc[g[time_col].idxmin()][[id_col, type_col, '_v']]
    last  = d.loc[g[time_col].idxmax()][[id_col, type_col, '_v']]
    agg   = g['_v'].agg(['min', 'max', 'mean']).reset_index()
    # pivot each to wide, prefix the columns, and join on id_col -> one row per id
    return first, last, agg
```

Suggested column naming: `{source}_{first|last|min|max|mean}_{variable}` (e.g.
`lab_min_lactate`, `vital_first_heart_rate`). Keep it consistent so downstream feature
selection can pattern-match.

## Exploratory recipe — finding a variable

1. Load the dataset's **dictionary** (or, for eICU, the distinct values of the variable
   column).
2. Fuzzy-search it: `dict[dict.label.str.contains('lactate', case=False, na=False)]` →
   note the id / exact label string.
3. Pull just that variable from the (cohort-filtered) event table, compute offsets,
   restrict to the window.
4. **Check it's usable before committing:** `s.notna().mean()` (fraction of stays with the
   value) and `s.nunique()` (constant columns are useless). Look at the distribution and
   units.

## Cross-cutting pitfalls

- **Units differ** across and within datasets (°C vs °F, lbs vs kg, mg/dL vs mmol/L).
  Always confirm units before combining or thresholding.
- **Time representation differs**: eICU gives offsets directly; MIMIC/PMAP give timestamps
  you must subtract. Negative offsets = recorded before time zero — usually drop them.
- **Granularity / leakage**: don't let post-outcome or treatment-defining measurements
  into the feature window, and de-duplicate to one row per chosen grain.
- **Missingness is informative but heavy**: many variables are present for <5% of stays.
  Filter by coverage and decide imputation deliberately.
- **De-identification artifacts**: shifted dates, ages capped (e.g. eICU `'> 89'`,
  MIMIC anchor-age binning). Handle the sentinel strings before casting to numeric.

See the per-dataset skills for concrete schemas, dictionaries, ID columns, and example
cohort/variable lookups.
