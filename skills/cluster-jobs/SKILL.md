---
name: cluster-jobs
description: "How to submit, monitor, interpret and collect SLURM batch jobs in the lab's analysis repos (causal_sedation and siblings) — the two-layer jobs/ design of a generic per-account notebook runner plus per-analysis wrapper submitters, which runner belongs to which account, --export and INPUT_DIRS/LATEST: syntax, the pre-flight traps that kill a job in four seconds, PROBE timing runs before a long submit, how to tell a finished run from a partial one, and the zip_*.sh collectors. Use when submitting or re-running a notebook on the cluster, writing a new job script, reading a run_manifest.txt or job log, deciding whether a run's outputs can be trusted, or diagnosing a job that failed instantly or produced an empty archive. Pairs with lcicm-cluster, which holds the dataset paths and the site's SLURM facts."
---

# Cluster jobs

The rule that prevents most of the damage: **a run is finished only when its `run_manifest.txt`
contains `finished_utc`.** A directory full of CSVs without that line is a partial run, and every
input resolver in these repos enforces the same predicate. Do not read results from a run that
cannot pass it.

Dataset paths, `--mem-per-cpu` semantics, partitions and the account flag live in
**lcicm-cluster**. This skill is the layer above: the repo's own `jobs/` scripts.

## The two layers

| layer | file | what it does |
|---|---|---|
| runner | `jobs/run_*_notebook.sh` | the actual `#SBATCH` job. Copies the notebook and `aim2_shared.py` into a fresh run directory, links inputs, writes the manifest, executes, appends `finished_utc` |
| submitter | `jobs/run_<analysis>.sh` | no `#SBATCH` of its own. Runs pre-flight checks, resolves `INPUT_DIRS`, then `sbatch`es a runner with the right resources and env |

Never add `#SBATCH` lines to a submitter, and never put analysis logic in a runner. A submitter
that needs different resources passes them as `sbatch` CLI flags, which override the runner's
`#SBATCH` block.

## Pick the runner by account

The `#SBATCH --output`/`--error` paths are hardcoded per home directory and are parsed before any
shell expansion, so the wrong runner dies instantly with nothing written to explain why. Check
`whoami` first.

| account | MIMIC-IV notebooks | eICU notebooks | collectors |
|---|---|---|---|
| `mbaz1` | `jobs/run_mimiciv_aim2_notebook.sh` | `jobs/run_eicu_aim2_notebook.sh`, `jobs/run_eicu_aim2.sh` | `jobs/zip_eicu_aim2.sh` |
| `mbranda1` | `jobs/run_aim2_notebook.sh` and every wrapper that calls it | `jobs/run_eicu_notebook.sh`, `jobs/run_eicu_readiness.sh` | `jobs/zip_cate.sh`, `zip_diagnostics.sh`, `zip_phase5.sh`, `zip_phase6.sh`, `zip_eicu.sh` |

Run once per account, before the first submit — SLURM opens the log files before the script body,
so a `mkdir` inside the script is too late:

```bash
mkdir -p ~/causal_sedation/mimiciv/runs/logs
mkdir -p ~/causal_sedation/eICU/runs/logs
```

## Submitting

```bash
sbatch --export=ALL,NOTEBOOK=<stem>,AIM2_FOO=bar,INPUT_DIRS="LATEST:<nb>/<sub>" \
  jobs/run_mimiciv_aim2_notebook.sh
```

- `NOTEBOOK` is the stem, no `.ipynb`.
- `--export` is one comma-separated list. A value containing a comma breaks it; quote and avoid.
- Analysis configuration travels as `AIM2_*` env vars, which the manifest records verbatim.
- Resource overrides go on the `sbatch` line: `--partition`, `--cpus-per-task`, `--mem-per-cpu`,
  `--time`, `--gres`.

## INPUT_DIRS and `LATEST:`

`INPUT_DIRS` is a space-separated list of specs. Each is symlinked into the run directory under its
own basename, so the notebook finds it relative to the working directory.

| spec | resolves to | link name in the run dir |
|---|---|---|
| `/abs/path/to/dir` | itself | `dir` |
| `LATEST:<notebook>` | newest **completed** run of that notebook | `<notebook>_<ts>_<jobid>` |
| `LATEST:<notebook>/<subpath>` | that subpath inside the newest completed run | `basename(subpath)` |

Two things to know. `LATEST:` resolves when the job **starts**, not when you submit, so two jobs
submitted together can read different inputs — pin an absolute path for any controlled comparison.
And a `LATEST:` spec that resolves to nothing calls `sys.exit` inside a command substitution under
`set -euo pipefail`, which kills the job, not the submit step. That is the four-second failure.

A pre-flight check in a submitter must use the **same predicate** as the resolver — a completed run
whose subpath exists — not merely "a directory matching the glob exists". Testing existence alone
is how an incomplete upstream run turns a warning into a hard kill.

## Probe before a long run

Any job that might approach the 72 h ceiling gets a short timing run first.

```bash
PROBE=1 ./jobs/run_trim_stability.sh
PROBE=1 PROBE_CELL=propofol:target ./jobs/run_trim_stability.sh
```

A probe measures per-fit wall time at reduced fidelity. It is **not** a result: its split and
bootstrap counts are far below production, and it cannot produce a verdict. Re-derive the
per-unit cost from the probe's logged timings, then budget the production run from that. A
wall-clock estimate printed at submit time is a guess until a probe replaces it.

## Reading a finished run

```bash
squeue -u "$USER"
cat <run_dir>/run_manifest.txt
```

Check, in order:

1. `finished_utc` present, and no fatal traceback in the `.out` log.
2. The resolved input paths — confirm the run read what you intended, not `LATEST:` drift.
3. `git_sha` **and** `git_dirty`. A SHA with uncommitted files does not identify the code that ran.
4. `cpus_per_task` against any thread budget the analysis sets. Twice the granted cores is
   contention, not speed.
5. `gres`. SLURM does not export `SLURM_JOB_GRES` for a `--gres=gpu:N` request, so the runner falls
   back through other signals and labels the source. `gres = none (source=unreported)` with a
   populated `cuda_visible` means a GPU was granted; do not chase it.

## Collecting outputs

```bash
./jobs/zip_phase6.sh        # or zip_diagnostics.sh, zip_cate.sh, zip_eicu.sh
```

Collectors find files with `find`, never a multi-level glob. A pattern like `"$d"*/"$sub"/*.csv`
matches nothing when any one component fails, bash leaves it literal, and a trailing `|| true`
swallows the error — producing an archive that looks like a run with no results. Match the job
name in a collector against the submitter's actual `--job-name`, or the log silently goes missing
from the archive.

## Failure triage

| symptom | cause |
|---|---|
| job dies in seconds, empty log | wrong account's runner, or missing `runs/logs` directory |
| job dies in ~4 s, log mentions the resolver | a `LATEST:` input with no completed run |
| runs on CPU despite a GPU request | `##SBATCH` — a doubled hash is a comment |
| OOM hours in | `--mem-per-cpu` multiplies by CPU count |
| archive has a manifest and nothing else | the job was zipped while still running |
| results shift between folds for no reason | the repo was `git pull`ed while an interactive notebook ran; use a runner, or a `git worktree` |

## Writing a new submitter

1. Pre-flight the notebook: it exists, and it contains whatever guard string this analysis needs.
   A stale generated notebook is the most common silent failure — edit `_build_*.py`, regenerate,
   test, then submit.
2. Resolve `INPUT_DIRS` with the resolver's own predicate. Warn, do not block, when an optional
   input is missing — and say in the warning what the fallback branch will do to the result.
3. Echo the resolved inputs and the resource choice before submitting.
4. `sbatch --parsable`, capture the job id, fail loudly if it is empty.
5. Print the watch command, the matching collector, and the decision the run drives.

## Interpretation

The jobs layer exists so that a result can be traced back to the exact code, inputs and allocation
that produced it. Most of its rules are scar tissue from runs that looked finished and were not —
which is why `finished_utc`, the resolved input list, and the dirty-file count matter more than any
convenience the scripts offer.
