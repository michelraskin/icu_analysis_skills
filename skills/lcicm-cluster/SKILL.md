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

Run a notebook on the cluster — **interactively** (fine for short, exploratory runs):
```bash
jupyter nbconvert --to notebook --execute <nb>.ipynb \
  --output <nb>.ipynb --ExecutePreprocessor.timeout=-1
```
For anything long, reproducible, or parallel, submit it as a **batch job** instead — see the
next section. Interactive runs have a specific hazard documented there (git operations
mid-run).

## Running notebooks as SLURM batch jobs (Discovery HPC / Open OnDemand)

The cluster runs **SLURM**, reachable from the OnDemand Job Composer (`Jobs → Job Composer`,
scripts under `~/ondemand/data/sys/myjobs/projects/`) or `sbatch` on a login node
(`rithpc-login02.cm.cluster`). Prefer batch for any run that is long, must be reproducible,
or can run alongside another.

**Why batch, beyond wall-clock:**
- **Provenance.** Stamp the git SHA, hostname, resolved allocation and package versions into
  a `run_manifest.txt` per run. Without this you *will* eventually analyse a stale output and
  not notice — the failure mode is silent, and re-deriving which code produced a zip costs
  more than the discipline does.
- **Parallelism.** Independent notebooks become independent jobs instead of serial cells in
  one kernel.
- **Unattended long runs** (dataset rebuilds, large sweeps).

**Site-specific SLURM facts (verified Aug 2026):**

| Setting | Value |
|---|---|
| Partitions | `cpu`, `gpu` |
| Account | `--account=LCICM` — **required**, jobs are rejected without it |
| Memory flag | `--mem-per-cpu=<MB>` — **per core, not total**; `--mem` is not the local convention |
| GPUs | `--gres=gpu:N` (plain count, no device-type token) |
| Max walltime | 72 h |
| Python | `module load python311` |

**Gotchas that cost real time:**
- **`#SBATCH` vs `##SBATCH`.** A doubled hash is a comment SLURM ignores. Commenting out
  `--gres` this way yields a job with zero GPUs that runs happily on CPU — you find out from
  the runtime, not an error.
- **The `--output`/`--error` directory must already exist.** SLURM opens those files *before*
  the script body runs, so a `mkdir -p` inside the script is too late; the job dies instantly
  with nothing written to explain why.
- **`#SBATCH` directives cannot reference shell variables** — they are parsed before any
  expansion. Paths in them are fixed. Conversely, **`sbatch` CLI flags override `#SBATCH`
  directives**, so one parameterized script can serve every job without editing the header.
- **`--mem-per-cpu` multiplies.** 40 cores × 1000 MB is 39 GB, not 1 GB — and 39 GB will OOM a
  large decision-table job hours in.

**Job-script pattern** (reference implementation: `causal_sedation/jobs/run_aim2_notebook.sh`):
1. Take the notebook stem and input directories as env vars (`--export=ALL,NOTEBOOK=…`).
2. `mkdir` a run directory keyed `{notebook}_{UTC}_{jobid}` so runs never overwrite.
3. **Copy the notebook and any repo-local shared module (`aim2_shared.py`, `*Util.py`) into
   the run dir and `cd` there.** This is what insulates a running job from git operations in
   the repo — see the hazard below.
4. Symlink declared input directories, and **fail fast if one is missing** rather than letting
   the notebook silently produce `unknown`/empty results.
5. Write `run_manifest.txt` (git SHA + dirty count, host, `SLURM_CPUS_PER_TASK`,
   `SLURM_MEM_PER_CPU`, gres, `CUDA_VISIBLE_DEVICES`, `nvidia-smi`, package versions, every
   analysis env override).
6. Execute with `jupyter nbconvert --to notebook --execute --inplace
   --ExecutePreprocessor.timeout=-1`. **Do not pass `--allow-errors`** — a failed cell must
   kill the job rather than leave a half-executed notebook that looks like a result.

**⚠ Never `git pull`/`rebase` in a tree an interactive notebook is running from.** Grouped-OOF
helpers use joblib **Loky, which spawns**; each new fold worker re-imports the shared module
*from disk*. Changing that file mid-run means early folds ran under one version of the code and
later folds under another, with no error raised. Either run via the job script (which works off
copies), or use a `git worktree` for edits while the running tree stays pinned:
```bash
git -C <repo> worktree add ../<repo>_dev -b wip   # edit here; the running tree never moves
```

Add the run-output root (e.g. `mimiciv/runs/`) to `.gitignore` before the first submit.

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

## Standard modeling allocation

On `gpu110`, modeling jobs should request 32 total CPU threads and all four Tesla T4 GPUs when the
workload has independent GPU-capable fits. Record the resolved allocation in the parameter
manifest. One LightGBM fit uses one GPU, so distribute folds, horizons, outcomes, or model fits
across devices 0–3 using at most four processes and eight CPU threads per concurrent worker.
CPU-only stages may use all 32 BLAS/OpenMP threads. Do not exceed 32 aggregate CPU threads or
silently fall back to CPU/fewer GPUs; fail clearly and document an approved reduced allocation.

On `gpu110`, `nvidia-smi` reports four Tesla T4 GPUs (16 GiB each), NVIDIA driver `570.124.06`,
and CUDA driver compatibility `12.8`. T4 compute capability is `7.5`; do not describe that as the
installed CUDA version. Use only scheduler-granted devices and record the resolved
`CUDA_VISIBLE_DEVICES`. Request all four for parallelizable work; if fewer are granted, stop or use
an explicitly approved reduced allocation rather than assuming every visible node GPU is usable.

## Source of truth / install

These skills live in `~/Documents/GitHub/icu_analysis_skills/skills/`, symlinked into
`~/.claude/skills/` (run `./install.sh` after pulling). This file is the single place to
update cluster paths — change it here, not in scattered notebooks.
