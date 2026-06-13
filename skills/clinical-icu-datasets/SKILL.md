---
name: clinical-icu-datasets
description: Overview and router for working with critical-care EHR datasets (eICU-CRD, MIMIC-IV, and institutional Epic Clarity exports such as PMAP), focused on PATIENT IDENTIFICATION — defining cohorts and locating the patients/stays for an analysis. Use when starting an ICU-data analysis, building or filtering a cohort, identifying an exposure or diagnosis group, or writing a patient-identification notebook. Routes to the per-dataset skills eicu-dataset, mimiciv-dataset, pmap-dataset.
---

# Critical-care (ICU) EHR datasets — patient identification

Shared mental model and reusable workflow for analyzing intensive-care electronic health
record (EHR) datasets, **centered on the first and most important step: identifying the
patients** (the cohort) for an analysis. The per-dataset skills (**eicu-dataset**,
**mimiciv-dataset**, **pmap-dataset**) give the concrete tables, id columns, code fields,
and dictionaries used to do this in each database.

## What these datasets are

ICU EHR datasets are de-identified (or institutional) dumps of everything recorded during
a critical-care stay: demographics, admissions, diagnoses (ICD), procedures, vital signs,
labs, medications, fluids, and nursing assessments. They are longitudinal — each
measurement is its own timestamped row.

| Dataset | Source / population | Access | Shape |
|---|---|---|---|
| **eICU-CRD** | ~200k ICU stays, 200+ US hospitals (Philips eICU), MIT-LCP | PhysioNet, credentialed | Flat denormalized CSVs; inline variable names; integer time **offsets** |
| **MIMIC-IV** | Single academic center (Boston), 2008–2019; + ED add-on | PhysioNet, credentialed | Relational `hosp`/`icu` modules; real **timestamps**; values via dictionaries |
| **PMAP / Epic Clarity export** | Institutional EHR (Epic Clarity/Caboodle) | Private / DUA | Raw Clarity tables; flowsheets + labs via measure/procedure dictionaries |

## The two stages of an ICU analysis

1. **Patient identification (the focus of these skills).** Decide *which stays are in the
   study*, and for each one *when time zero is*. Output: a de-duplicated list of cohort ids
   (+ optional index time / exposure flags), saved to disk.
2. **Analysis-dataset creation (downstream).** Restrict the event tables to the cohort and
   build the modeling table (cross-sectional features, a longitudinal panel, etc.). Covered
   briefly here and in the per-dataset skills; treat it as the step *after* identification.

## Patient identification — the mental model

Every cohort is built from one or more **signals**, then narrowed by **inclusion filters**,
then **de-duplicated** to the analysis grain. The same handful of signal types recur across
all three datasets:

| Signal | How it's expressed | Example |
|---|---|---|
| **Diagnosis code** | ICD-9 / ICD-10 codes, matched via a code dictionary or by prefix | TBI = ICD-9 `850–854` / ICD-10 `S06`; sepsis = `038*`, `A41*` |
| **Diagnosis / complaint text** | free-text diagnosis or ED chief-complaint, matched by regex | "cardiac arrest", "asystole", `\bpea\b` |
| **Procedure** | procedure events / procedure strings | CPR, ICP monitor, craniotomy, dialysis |
| **Exposure / treatment received** | a drug, fluid, device, or order the patient got | transfusion, vasopressors, therapeutic hypothermia |
| **Physiologic threshold** | a lab/vital crossing a cutoff within a window | min Hgb < 10 g/dL in first 7 days |
| **Demographics / admission** | age, admission type, care pathway | age ≥ 18, non-elective, came through ED |

### The standard identification recipe

1. **Match the primary signal** to get a candidate id set (see per-dataset skills for the
   exact tables/columns).
2. **Apply inclusion/exclusion filters** — e.g. `age >= 18`; require a recorded ICU stay;
   exclude history-of / intraoperative / neonatal mentions; restrict admission type.
3. **De-duplicate to the grain.** Pick one row per patient / admission / stay (e.g. keep the
   first qualifying stay; drop patients with multiple conflicting encounters).
4. **Set time zero** per stay (ICU admission, ED arrival, or an event time) if features will
   be measured relative to it.
5. **Persist** the id list (and index time / exposure flags) to a file so every downstream
   step filters to exactly the same patients.

### Reusable identification patterns

**Code-based cohort** — search a dictionary, then the fact table (or match by prefix):
```python
codes  = dx_dict[dx_dict.title.str.contains("sepsis", case=False, na=False)].code
cohort = dx[dx.code.isin(codes)].id.unique()
# or, by prefix family:
cohort = dx[dx.icd9.astype(str).str[:3].isin(["850","851","852","853","854"])].id.unique()
```

**Text / regex cohort** — with inclusion AND exclusion patterns (avoids false positives):
```python
import re
INCLUDE = [r'cardia.*rrest', r'\basystole', r'\bpea\b|pulseless elec']
EXCLUDE = [r'history|hx|h/o', r'neonatal', r'resp.*rrest']
def matches(text):
    t = str(text).lower()
    return (any(re.search(p, t) for p in INCLUDE)
            and not any(re.search(p, t) for p in EXCLUDE))
```

**Exposure cohort from events** (e.g. identify who received a product/intervention) —
extract events, classify them, optionally quantify, then threshold. This is how
"received transfusion" or "massive transfusion" cohorts are built:
```python
# 1) find the events (regex over a drug/fluid/order field, or dictionary itemids)
# 2) classify into types (e.g. PRBC vs plasma vs platelets) and estimate amount
# 3) aggregate per stay; flag exposure, or apply a rolling-window threshold:
def max_in_window(times, units, window_min):
    j = csum = best = 0.0
    for i in range(len(times)):
        csum += units[i]
        while times[i] - times[j] > window_min:
            csum -= units[j]; j += 1
        best = max(best, csum)
    return best   # e.g. massive transfusion = >=10 units in any 24h window
```

**Combine signals** with `np.intersect1d` (AND) or `np.union1d` / `pd.concat` (OR), then
de-duplicate.

## Writing a patient-identification notebook for a new cohort

When asked to identify a new cohort, produce a notebook from the bundled template
**`cohort_identification_template.py`** (in this skill's directory; `# %%` cell markers — opens
as a notebook in Jupyter/VS Code, or convert with `jupytext --to notebook` / `nbformat`).
Copy it next to the analysis, set the CONFIG block (dataset, paths, cohort name, window),
read the matching per-dataset skill for the exact tables/ids/dictionaries, and fill the
`TODO`s. The template enforces the recipe above and ends with an **initial cohort analysis**:

1. **Selection flow** — the `step(label, ids)` helper logs the id count after each signal and
   filter, so the notebook prints a CONSORT-style attrition table (how many patients survive
   each criterion). This is the first sanity check.
2. **Demographics + outcomes** — n, age, sex, mortality, ICU length of stay.
3. **Top diagnoses** — confirm the phenotype is what you intended.
4. **Key-variable coverage** — `series.notna().mean()` per candidate variable, to see what is
   actually usable downstream.
5. **Quick plots** — age distribution, subgroup mortality, time-to-event as relevant.

Always show the selection flow and at least one phenotype sanity check before declaring the
cohort done.

## Briefly: building the analysis dataset (downstream)

Once you have the cohort ids + time zero: read the big event tables in chunks filtered to
those ids, compute offsets (`event_time − time_zero` in minutes), keep `0 ≤ offset ≤
window`, and summarize per stay (`first/last/min/max/mean`) or per time-bucket (a daily or
hourly panel). The per-dataset skills note the table/value/time columns; expand this later.

To locate a *specific* variable (GCS / motor GCS, discharge status, ICU days, demographics,
weight/BMI, vitals, labs, ventilation, vasopressors, severity scores, …) in each dataset,
use the **icu-feature-identification** skill — a cross-dataset catalogue of where each common
variable lives and how to extract it. Pull its "baseline covariates" block (age, sex,
weight, height, BMI, admission context, baseline severity, mortality, LOS) by default in
nearly every analysis.

## Cross-cutting pitfalls (that affect identification)

- **ICD-9 vs ICD-10.** MIMIC-IV mixes both (`icd_version`); the same concept needs both code
  families. eICU is ICD-9-era; Epic exports carry both.
- **History-of / intraoperative / neonatal** mentions masquerade as the condition — always
  add exclusion patterns to text matches.
- **De-duplicate deliberately.** One patient can have many diagnoses, stays, and encounters;
  decide the grain and keep one row per unit.
- **Exposure cohorts can leak.** If the exposure defines the cohort, don't also use it (or
  things derived from it) as a predictor of the outcome.
- **De-identification artifacts**: age sentinels (eICU `'> 89'`), binned ages (MIMIC
  `anchor_age`), shifted dates — clean before filtering on them.
- **Post-arrest / post-event cohorts have no clean event timestamp.** Neither eICU nor
  MIMIC records a ROSC (return-of-circulation) time, so "after cardiac arrest" has no exact
  time zero. Anchor on a proxy — the **post-arrest ICU admission** (`intime` / unit-admit
  offset 0), or the offset of the arrest event/diagnosis if charted — and state the choice.
  Measure post-event status (e.g. coma) in a window *after* that anchor, and beware that
  early readings overlap sedation/peri-arrest instability (see the coma-definition note in
  **icu-feature-identification**).

See the per-dataset skills for the exact tables, code columns, dictionaries, and
copy-paste identification snippets.
