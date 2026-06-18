---
name: lcicm-cluster
description: Operating context for running ICU EHR analyses on the LCICM lab cluster — where the eICU / MIMIC-IV / PMAP CSVs live on disk, the file format and access conventions, how to run the analysis notebooks, and the layout shared across the lab's analysis repos. Use when writing or running a notebook against these datasets on the cluster, setting a DATA_DIR, or needing the on-disk path for a dataset. Pairs with clinical-icu-datasets and the per-dataset skills.
---

# LCICM cluster — ICU data operating context

Environment notes for the JHU critical-care (LCICM) group's analysis cluster. The
*scientific* "where does each variable live" knowledge is in **clinical-icu-datasets**,
**eicu-dataset**, **mimiciv-dataset**, **pmap-dataset**, and **icu-feature-identification**.
This skill is the *operational* layer: where the bytes are and how to run.

## Where the datasets live

Datasets are stored as **plain `.csv` (uncompressed — not `.csv.gz`)** under
`/projects/LCICM/`. Set the notebook CONFIG `DATA_DIR` to one of:

| Dataset | `DATA_DIR` | Layout |
|---|---|---|
| eICU-CRD | `/projects/LCICM/eICU/` | flat CSVs (`patient.csv`, `infusionDrug.csv`, `nurseCharting.csv`, `respiratoryCare.csv`, …) |
| MIMIC-IV **v2.2** | `/projects/LCICM/mimic-iv-2.2/` | relational `hosp/` + `icu/` subdirs (`icu/chartevents.csv`, `icu/d_items.csv`, `hosp/d_icd_diagnoses.csv`, …) |
| PMAP (Epic Clarity export) | under `/projects/LCICM/` (confirm subfolder) | raw Clarity tables + dictionaries |

> The per-dataset skills sometimes show `.csv.gz` and `read(...,compression="gzip")` — on
> **this** cluster the files are uncompressed, so use plain `pd.read_csv(path)`.

```python
import os, pandas as pd
DATA_DIR = "/projects/LCICM/eICU"            # or /projects/LCICM/mimic-iv-2.2
def path(name): return os.path.join(DATA_DIR, name)
read = lambda f, **k: pd.read_csv(path(f), **k)
```

## Access conventions

- **Stream the big tables.** `chartevents` / `nurseCharting` / `labevents` / `inputevents`
  are huge — read with `chunksize=1_000_000` and filter to itemids/cohort inside the loop;
  never load whole.
- **The user runs notebooks on the cluster**, not the assistant's machine. Write notebooks
  so they are runnable as-is there (DATA_DIR preset to the cluster path, outputs written
  relative to the notebook). Don't expect to execute them locally.
- Headless figures: `import matplotlib; matplotlib.use("Agg")` if running via nbconvert.

Run a notebook on the cluster:
```bash
jupyter nbconvert --to notebook --execute <nb>.ipynb \
  --output <nb>.ipynb --ExecutePreprocessor.timeout=-1
```

## Repo layout shared across the lab's analyses

Analysis repos (e.g. `~/Documents/GitHub/ttmhte`, `~/Documents/GitHub/causal_sedation`)
share a convention: **one subdirectory per dataset** (`eICU/`, `mimiciv/`, `pmap/`), each
holding its notebooks + a `*Util.py`. Notebooks set `database_folder = '/projects/LCICM/...'`
in a CONFIG cell. Cohort-identification notebooks follow the
`clinical-icu-datasets` template (signal → filter → de-duplicate → persist → describe) with a
`step(label, ids)` attrition logger.

Generating notebooks programmatically: build the `.ipynb` with a small `_build_notebook.py`
(uses `nbformat`) kept next to the notebook, and **edit the builder, not the JSON**.

## Active work using this context

- **causal_sedation** — Dynamic Causal Model of ICU sedation (Aim 1 IDA); cohort = adult,
  invasively ventilated, continuously sedated. Started on eICU.

## Source of truth / install

These skills live in `~/Documents/GitHub/icu_analysis_skills/skills/`, symlinked into
`~/.claude/skills/` (run `./install.sh` after pulling). This file is the single place to
update cluster paths — change it here, not in scattered notebooks.
