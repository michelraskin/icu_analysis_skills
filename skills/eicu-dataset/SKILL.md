---
name: eicu-dataset
description: How to identify any patient cohort in the eICU Collaborative Research Database (eICU-CRD) — where each kind of signal (diagnosis, procedure, medication, fluid/device, lab/vital) lives and how to match it. Use when building or filtering an eICU cohort, finding which table/column carries a concept, or writing an eICU patient-identification notebook. Read clinical-icu-datasets first for shared conventions. Feature extraction is covered briefly at the end.
---

# eICU-CRD — patient identification

## High-level overview

eICU-CRD is a multi-center US critical-care database (Philips eICU telehealth + MIT-LCP,
PhysioNet credentialed): ~200,000 ICU unit stays across 200+ hospitals (~2014–2015).
Multi-center → coding and available variables **vary by hospital**, so search broadly. Flat
denormalized CSVs; **variable names are stored inline as strings** (there is no central item
dictionary); **time is an integer offset in minutes** from unit admission (columns ending in
`offset`).

**ID hierarchy:** `uniquepid` (patient) → `patienthealthsystemstayid` (hospital stay) →
**`patientunitstayid`** (ICU stay — the usual cohort grain).

## Where each signal lives (the identification map)

To identify a cohort, decide what *kind* of signal defines it, then match the corresponding
field. In eICU the signal is almost always a **code** (`icd9code`) or a **text/name string**
matched with a case-insensitive substring/regex.

| Signal kind | Table → field to match | Notes |
|---|---|---|
| Diagnosis (coded) | `diagnosis.csv` → `icd9code` | comma-list; split & take first; match by prefix or substring |
| Diagnosis (text) | `diagnosis.csv` → `diagnosisstring` | pipe-`\|` hierarchy; substring search works on the path |
| Admission reason | `patient.csv` → `apacheadmissiondx` | free text |
| Procedure / intervention | `treatment.csv` → `treatmentstring` | pipe hierarchy |
| Medication | `medication.csv` / `infusionDrug.csv` → `drugname` | infusionDrug also has `drugrate` |
| Fluid / blood / device (I/O) | `intakeOutput.csv` → `cellpath`, `celllabel` | `cellvaluenumeric` has volumes |
| Respiratory support / ventilation | `respiratoryCare.csv` (`ventstartoffset`/`ventendoffset`), `respiratoryCharting.csv` | no single flag — union these |
| Lab value | `lab.csv` ⚠ → `labname` + `labresult` | for threshold cohorts |
| Vital / score | `nurseCharting.csv` ⚠ → `nursingchartcelltypevalname` + `nursingchartvalue` | also `vitalPeriodic.csv` (vitals as columns) |
| Comorbidity / history | `pastHistory.csv` → `pasthistorypath` | pre-existing conditions |

Demographics & outcomes for inclusion filters live in `patient.csv`: `gender`, `age`
(string; `'> 89'`), `hospitaldischargestatus` (`'Expired'`), `unitdischargeoffset/status`.

```python
DATA_DIR = "/path/to/eicu/"   # configure
```

## The generic matching methods

**Coded signal** (ICD-9) — by prefix family or substring:
```python
dx = pd.read_csv(DATA_DIR + "diagnosis.csv")
dx["icd9_first"] = dx.icd9code.astype(str).str.split(",").str[0].str.strip()
ids = dx[dx.icd9_first.str[:3].isin(["XXX","YYY"])].patientunitstayid.unique()   # fill prefixes
```

**Text / name signal** — case-insensitive substring or regex on the relevant string field:
```python
field = some_df["<text_or_name_col>"].astype(str).str.lower()
ids = some_df[field.str.contains(r"<keyword|regex>", regex=True, na=False)].patientunitstayid.unique()
```
For diagnosis/complaint text, pair INCLUDE with EXCLUDE patterns (history-of / neonatal /
wrong-site) — see the shared regex helper in clinical-icu-datasets.

**Exposure signal** (a drug, fluid, device, or procedure the patient *received*) — all use
the same shape: match the name field → take `patientunitstayid.unique()` for a *presence*
cohort. If the cohort needs an **amount/intensity** (not just "any"), keep the offset and
value, restrict to a time window, aggregate per stay, and threshold — optionally with the
`max_in_window` rolling-window helper (clinical-icu-datasets) for "X amount within N hours".

**Threshold signal** (lab/vital crossing a cutoff in a window):
```python
lab = pd.read_csv(DATA_DIR + "lab.csv")
s = lab[lab.labname.str.contains("<labname>", case=False, na=False)].copy()
s["labresult"] = pd.to_numeric(s.labresult, errors="coerce")
s = s[(s.labresultoffset >= 0) & (s.labresultoffset < WINDOW_MIN)]
ids = s.groupby("patientunitstayid").labresult.min().pipe(lambda x: x[x < CUTOFF].index.values)
```

**Combine & finalize:** `np.intersect1d` (AND) / `np.union1d` (OR) the id sets, apply
inclusion filters (e.g. `age >= 18` after `replace("> 89","90")`), de-duplicate to the
grain, and persist: `pd.Series(cohort, name="patientunitstayid").to_csv("cohort_ids.csv", index=False)`.

## Exploratory recipe — which column carries a concept? (no dictionary)

The distinct values of the name columns *are* the dictionary:
```python
some_df["<name_col>"].value_counts().head(50)                                   # what exists
sorted({x for x in lab.labname.unique() if "<frag>" in str(x).lower()})          # fuzzy match
dx[dx.diagnosisstring.str.contains("<frag>", case=False, na=False)].diagnosisstring.value_counts()
```
Peek at a large table without loading it whole: `next(pd.read_csv(path, chunksize=1_000_000))`.

## eICU identification gotchas

- `age` is a **string** with `'> 89'` — coerce before numeric filters.
- `icd9code` can be a comma-separated list — split and take the first for prefix matching.
- Multi-center spelling variation — the same concept appears under several names; search
  broadly and union.
- Offsets can be negative (pre-ICU) — usually require `offset >= 0`.

## Next: building the analysis dataset (brief)

After identification, filter `lab`/`nurseCharting` (chunked) to the cohort and summarize per
stay with the shared `window_features` helper (`type_col='labname'` /
`'nursingchartcelltypevalname'`, `value_col='labresult'` / `'nursingchartvalue'`,
`time_col='*offset'`); daily/hourly panels bucket the offset (`offset // 1440`). Defer until
the cohort is settled. For *which* variable lives where (GCS/mGCS, discharge status, ICU
days, demographics, vitals, labs, …), see the **icu-feature-identification** skill.
