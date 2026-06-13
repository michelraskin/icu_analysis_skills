# %% [markdown]
# # Cohort identification — <COHORT NAME>
#
# Template for identifying a patient cohort in an ICU EHR dataset and running an initial
# descriptive analysis. Fill every `TODO`. Cells are delimited with `# %%` so this opens as
# a notebook in Jupyter/VS Code (or convert: `jupytext --to notebook this_file.py`, or
# `nbformat`).
#
# **Pick the dataset** and read the matching skill (eicu-dataset / mimiciv-dataset /
# pmap-dataset) for the exact tables, id columns, and dictionaries. The flow is identical
# across datasets: match signal(s) → filter → de-duplicate → persist → describe.

# %%
import numpy as np
import pandas as pd

# ---- CONFIG -----------------------------------------------------------------
DATASET   = "eicu"          # TODO: "eicu" | "mimiciv" | "pmap"
DATA_DIR  = "/path/to/data" # TODO: dataset root (see the per-dataset skill)
COHORT    = "my_cohort"     # TODO: short name; used for output filenames
WINDOW_MIN = 6 * 60         # feature/threshold window (minutes from time zero)

# Per-dataset grain + helper columns (see the per-dataset skill).
ADAPTER = {
    "eicu":    dict(id="patientunitstayid", age="age", gender="gender",
                    death="hospitaldischargestatus"),       # death == 'Expired'
    "mimiciv": dict(id="stay_id",           age="anchor_age", gender="gender",
                    death="hospital_expire_flag"),
    "pmap":    dict(id="osler_id",          age="age",     gender="gender",
                    death="disch_disp_c"),                  # a specific code == expired
}
ID = ADAPTER[DATASET]["id"]

# Track cohort attrition so the analysis can print a CONSORT-style flow.
attrition = []
def step(label, ids):
    ids = np.asarray(pd.unique(pd.Series(ids)))
    attrition.append((label, len(ids)))
    print(f"{label:45s}: {len(ids):,}")
    return ids

# %% [markdown]
# ## 1. Locate the signal(s)
# Define the cohort in words first, then find where each signal lives.
# - eICU: search the distinct values of the relevant name column (no dictionary).
# - MIMIC: search `d_items` / `d_labitems` / `d_icd_diagnoses` for the id/code.
# - PMAP: search `d_flo_measures` / `CLARITY_EAP` for the `meas_id` / `proc_id`.
#
# TODO: use the exploratory snippet from the per-dataset skill to confirm the exact
# column / itemid / code, and check coverage before committing.

# %%
# TODO: load the table(s) you need. Read big tables in chunks filtered to candidate ids.
# Example (adapt table/column names to your dataset + signal):
#   src = pd.read_csv(f"{DATA_DIR}/<table>.csv")
#   field = src["<text_or_name_col>"].astype(str).str.lower()

# %% [markdown]
# ## 2. Build candidate id sets — one per signal
# Use the matching method that fits each signal (see clinical-icu-datasets):
#  - coded:     prefix/`isin` on ICD codes (match BOTH icd9 & icd10 in MIMIC)
#  - text:      INCLUDE regex AND-NOT EXCLUDE regex on a name/text field
#  - id-based:  dictionary lookup → filter event table by itemid/meas_id/proc_id
#  - exposure:  presence (any matching event) OR amount-in-window (threshold)
#  - threshold: aggregate a lab/vital in [0, WINDOW_MIN] and apply a cutoff

# %%
import re
INCLUDE = [r"TODO"]          # TODO: inclusion regexes
EXCLUDE = [r"history|hx|h/o", r"neonatal", r"newborn"]   # extend as needed
def text_match(text):
    t = str(text).lower()
    return any(re.search(p, t) for p in INCLUDE) and not any(re.search(p, t) for p in EXCLUDE)

# signal_ids = step("signal: <describe>", <ids matching the signal>)   # TODO

# Optional rolling-window threshold for amount-based exposure cohorts:
def max_in_window(times, units, window_min):
    j = csum = best = 0.0
    for i in range(len(times)):
        csum += units[i]
        while times[i] - times[j] > window_min:
            csum -= units[j]; j += 1
        best = max(best, csum)
    return best

# %% [markdown]
# ## 3. Inclusion filters + combine + de-duplicate
# Typical filters: age ≥ 18; require an ICU stay; restrict admission type; care pathway.
# Combine signals with intersection (AND) or union (OR), then keep one row per grain.

# %%
# adults = step("age >= 18", <adult ids>)                           # TODO
# cohort = step("after combining signals", np.intersect1d(signal_ids, adults))
# TODO: de-duplicate to one row per `ID` (e.g. keep first qualifying stay/encounter)
# TODO: set time zero per stay if features are time-relative (admission/ED/event time)

# %%
# ## 4. Persist the cohort (ids [+ index time / exposure flags])
# cohort_df = pd.DataFrame({ID: cohort})
# cohort_df.to_csv(f"{COHORT}_ids.csv", index=False)
# print(f"saved {COHORT}_ids.csv  n={len(cohort_df):,}")

# %% [markdown]
# ## 5. Initial cohort analysis (descriptive)
# Goal: confirm the cohort is sensible and report who's in it. Adapt column names via
# ADAPTER / the per-dataset skill.

# %%
# 5a. Attrition / selection flow
print("=== cohort selection flow ===")
for label, n in attrition:
    print(f"  {label:45s}: {n:,}")

# %%
# 5b. Demographics + outcomes  (TODO: load demographics for the cohort and fill columns)
# demo = <patient/demographics table restricted to cohort>
# print(f"n = {len(demo):,}")
# print(f"age   median={demo[ADAPTER[DATASET]['age']].median():.0f}")
# print(f"male  {(demo[ADAPTER[DATASET]['gender']].str.lower().str.startswith('m')).mean():.1%}")
# print(f"death {<death flag>.mean():.1%}")
# print(f"ICU LOS median (days) = {<los>.median():.1f}")

# %%
# 5c. Top diagnoses in the cohort (sanity check the phenotype)
# dx_cohort = <diagnoses restricted to cohort>
# (dx_cohort.drop_duplicates([ID, "<code_or_title>"])
#           .groupby("<code_or_title>").size().sort_values(ascending=False).head(20))

# %%
# 5d. Key-variable coverage (decide what's usable downstream)
# for col in [<candidate feature columns>]:
#     print(f"{col:30s}: present for {series.notna().mean():.1%} of cohort")

# %%
# 5e. (optional) quick plots: age distribution, mortality by subgroup, time-to-event, etc.
# import matplotlib.pyplot as plt
# demo[ADAPTER[DATASET]['age']].plot(kind="hist", bins=30); plt.title("Age"); plt.show()

# %% [markdown]
# ## Next steps
# With `{COHORT}_ids.csv` saved, move to dataset creation: restrict event tables to these
# ids, compute offsets from time zero, and build the modeling table (per-stay features or a
# longitudinal panel). See the "building the analysis dataset" note in the per-dataset skill.
