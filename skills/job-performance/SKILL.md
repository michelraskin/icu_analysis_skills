---
name: job-performance
description: "Performance requirements for any batch job, audit script, preprocessing pass, or training run in the lab's analysis repos — how to size processes and threads to the hardware, keep every core or GPU busy, keep memory below the swap line, avoid oversubscription, and keep the edit-run-look loop short with probes, smoke modes, caching and resumable outputs. Use when writing or reviewing a script that loops over many files, patients, folds or models; when a job runs slower than its probe predicted; when workers show low CPU; when choosing --workers, --cpus-per-task, thread counts or batch size; or when a delegate's build must be checked for utilisation. Pairs with cluster-jobs (submission mechanics) and lcicm-cluster (site hardware)."
---

# Job performance

The rule: **a job is correctly parallel only when its measured utilisation says so.** A script that
launches N workers has not "been made parallel" until a probe shows those workers near 100 % CPU
each, the machine not swapping, and wall time close to CPU time divided by N. Report utilisation
in the run manifest, or the job is not done.

## Hard requirements

| # | requirement | why |
|---|---|---|
| 1 | Probe before the full run, on the **largest** inputs, and report seconds per unit and peak RSS per worker | small-input probes underestimate by 10× on skewed datasets |
| 2 | Size workers from memory as well as cores: `workers = min(cores − 1, floor(0.6 × free RAM / peak RSS per worker))` | a swapping worker runs at 5–25 % CPU; six of them are slower than one |
| 3 | One BLAS/OpenMP thread per process worker (`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `torch.set_num_threads(1)` in the pool initializer) | otherwise N workers × 8 threads oversubscribe the cores and thrash caches |
| 4 | Total threads ≤ granted cores: `workers × threads_per_worker ≤ SLURM_CPUS_PER_TASK` (or `os.cpu_count()` locally) | twice the cores is contention, not speed |
| 5 | Stream, do not slurp: load one unit (slice, chunk, patient) at a time, `float32` unless the maths needs `float64`, `dataobj` slicing for NIfTI, chunked reads for CSV | peak memory is what limits worker count |
| 6 | Return small results; write big ones: each worker writes its own CSV/npz/parquet to a per-run temp dir and returns the path plus a small dict | pickling large arrays through the pool serialises the job on the parent |
| 7 | Order work largest-first and use `chunksize=1` or `imap_unordered` | the last big unit otherwise runs alone while other workers idle |
| 8 | Progress lines with a stable prefix every K units: `[job] <i>/<n> elapsed=<s> rate=<units/s> rss_max=<MB>`; a final line with `wall`, `cpu_seconds`, `utilisation = cpu_seconds / (wall × workers)` | the number that tells a reviewer the parallelism worked |
| 9 | Fail fast, never fall back silently: if a requested GPU or core count is unavailable, raise | a silent CPU fallback burns hours and misreports |
| 10 | Record `workers`, `threads_per_worker`, `cpu_count`, `peak_rss_mb`, `wall_seconds`, `cpu_seconds`, `utilisation`, `device` in the run manifest | provenance of the allocation, not just of the code |

## Sizing procedure

| step | do | output |
|---|---|---|
| 1 | Pick the unit of parallelism: the largest independent thing (patient, image, fold, model), not the smallest | one task per unit |
| 2 | `--probe-largest 8`: run the 8 largest units with `--workers 1`, measure `time.perf_counter()` per unit and `resource.getrusage(RUSAGE_SELF).ru_maxrss` | `s/unit`, `peak RSS` |
| 3 | Compute `workers` from requirement 2; compute predicted wall = `n_units × s/unit / workers` | print both before starting |
| 4 | Run the full set; compare achieved wall to predicted; if > 1.5× predicted, stop and diagnose with the table below | utilisation line |
| 5 | For GPU work: measure `nvidia-smi --query-gpu=utilization.gpu` every 30 s in the log; target ≥ 80 %; if lower, raise batch size, add `DataLoader(num_workers, pin_memory=True, persistent_workers=True)`, or move preprocessing off the training loop | GPU utilisation series in the log |

## Diagnosing a slow job from `ps` / `top`

| symptom | cause | fix |
|---|---|---|
| every worker at 5–30 % CPU, swap in use (`vm.swapusage`, `free -g`) | memory thrashing | fewer workers, float32, stream per slice, requirement 5 |
| every worker at 5–30 % CPU, no swap, disk busy | I/O bound (gz decompression is CPU, so gz is usually not it) | read once, cache preprocessed units under `PREPROCESSED_ROOT`, use local scratch on the cluster |
| workers at 100 % but total > cores | thread oversubscription | requirement 3 |
| one worker busy, the rest idle near the end | tail from unordered sizes | requirement 7 |
| parent process at 100 %, workers idle | results pickled back and concatenated in the parent | requirement 6 |
| all workers idle, parent idle | pool deadlock (a worker died, a lock in a forked C library) | use `spawn` context on macOS, `max_tasks_per_child`, catch and log per-task exceptions |
| GPU utilisation < 50 % | data loading or Python-side augmentation on the critical path | DataLoader workers, pre-tensorised cache, larger batches, mixed precision |

## Keep iteration time short

| practice | rule |
|---|---|
| Smoke mode | every script has `--limit K` (evenly sampled) and every trainer `--smoke` (few subjects, 1–2 epochs); a smoke run finishes in under two minutes on the laptop |
| Cache preprocessing once | write per-unit `.npz`/parquet with a manifest hash; downstream scripts read the cache, never the raw data |
| Resumable outputs | per-unit output files plus a final concatenation; a rerun skips units whose output exists unless `--force` |
| Fail in the first minute | validate paths, labels, dtypes, partition rules and device before the loop starts |
| Separate compute from plotting | notebooks read persisted CSVs; heavy computation lives in scripts with the rules above |
| Background long runs | `nohup … > log &` under `RESULTS_ROOT`, and poll the log; never block an agent turn for more than a few minutes |
| Probe on the largest units | see sizing procedure; a probe on the smallest units is a false promise |

## Reference skeleton (process pool)

```python
import os, time, resource
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

def _init_worker():
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[var] = "1"

def _work(unit):                      # runs in the worker
    t0 = time.perf_counter()
    out_path = process_and_write(unit)   # streams input, writes its own file, float32
    rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 if os.uname().sysname == "Linux" else 1024**2)
    return {"unit": unit.name, "path": out_path, "seconds": time.perf_counter() - t0, "rss_mb": rss_mb}

def run(units, workers):
    units = sorted(units, key=lambda u: u.nbytes, reverse=True)   # largest first
    t0 = time.perf_counter(); cpu = 0.0; rss_max = 0.0
    ctx = mp.get_context("spawn")
    with ProcessPoolExecutor(workers, mp_context=ctx, initializer=_init_worker) as pool:
        for i, r in enumerate(pool.map(_work, units, chunksize=1), 1):
            cpu += r["seconds"]; rss_max = max(rss_max, r["rss_mb"])
            if i % 25 == 0 or i == len(units):
                el = time.perf_counter() - t0
                print(f"[job] {i}/{len(units)} elapsed={el:.0f}s rate={i/el:.2f}/s rss_max={rss_max:.0f}MB", flush=True)
    wall = time.perf_counter() - t0
    print(f"[job] DONE wall={wall:.0f}s cpu={cpu:.0f}s workers={workers} utilisation={cpu/(wall*workers):.2f}", flush=True)
    return {"wall_seconds": wall, "cpu_seconds": cpu, "workers": workers, "peak_rss_mb": rss_max,
            "utilisation": cpu / (wall * workers)}
```

Threads instead of processes only when the hot loop releases the GIL (numpy/scipy/torch ops on
large arrays, I/O). Pure-Python loops over small arrays need processes.

## SLURM mapping

| local decision | SLURM flag |
|---|---|
| `workers × threads_per_worker` | `--cpus-per-task` |
| `peak RSS per worker × workers / cpus_per_task` (+30 %) | `--mem-per-cpu` (it multiplies by cores) |
| GPUs actually used by concurrent processes | `--gres=gpu:N`, one process per GPU, `CUDA_VISIBLE_DEVICES` per process |
| predicted wall × 2 | `--time` |

On `gpu110` (see lcicm-cluster): 32 threads and four T4s; at most four GPU processes with eight
threads each; CPU-only stages may use all 32.

## Review checklist for a delegate's job script

| check | pass when |
|---|---|
| probe on largest units reported with s/unit and peak RSS | numbers in the report |
| workers derived from memory, not just cores | formula printed at start |
| thread env vars set in the initializer | visible in the code |
| big results written by workers, not returned | no arrays in the returned dicts |
| final utilisation line ≥ 0.7 | in the log and the manifest |
| smoke mode exists and finishes in < 2 min | run in the report |
| fails, not falls back, when the allocation is missing | test or log line |
