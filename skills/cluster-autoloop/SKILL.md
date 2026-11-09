---
name: cluster-autoloop
description: "Closing the loop between a SLURM cluster and an assistant that cannot log in: SLURM e-mail on every sbatch (MAIL_USER / MAIL_TYPE through one shared helper), a 30-minute scrontab job that writes a status snapshot (every chain's job states, a Failures section with log tails, an ALERT file, the Dice of finished arms) and pushes it to the repository, an eager automatic results zip committed as results appear (no quiet point), and a submission queue of chain lines in the repository that the cron dry-runs and runs once. Use when a lab repo needs runs to be monitored, archived, fixed and resubmitted without anyone pasting terminals, or when porting the pattern from domain_adaptation_topology to another repo. Pairs with cluster-jobs (how jobs are built) and lcicm-cluster (site facts)."
---

# Cluster auto-loop

The rule: **the repository is the only channel.** Nothing the cluster knows reaches the assistant
unless a job commits it; nothing the assistant decides reaches the cluster unless a commit carries
it. Every piece below is a file in Git plus a cron job that moves it.

Reference implementation: `domain_adaptation_topology` (`jobs/lib/mail_args.sh`, `jobs/status_push.sh`,
`scripts/cluster_status.py`, `cluster_status/`, `jobs/queue/`, `scripts/zip_results_index.py`,
`tests/test_cluster_status.py`, `tests/test_mail_args.py`). Agreed with the owner on 2026-11-07.

## The four pieces

| piece | where it runs | what it moves | switch |
|---|---|---|---|
| SLURM mail | every `sbatch` | `--mail-type=END,FAIL --mail-user=$MAIL_USER` on each job | `MAIL_USER` unset = silent; `MAIL_TYPE=FAIL` = failures only |
| status snapshot | scrontab, every 30 min, login account | `cluster_status/STATUS_CLUSTER.md` + `jobs.tsv`, a `## Failures` section with the last 15 lines of each failed job's `.err` and the first Python error of its `.out`, `cluster_status/ALERT` while any tracked job failed | always on |
| auto-zip | same cron, EAGER (since 2026-11-08; no quiet point) | per run, a results-only zip whenever its result files changed (≤ 1 per 30 min) and a full zip with logs once the run is idle, copied into `results_archive/` and committed (each ≤ 95 MB, GitHub's limit), state `cluster_status/<user>/zip_state.json` | `AUTO_ZIP=0`, `ZIP_MIN_INTERVAL_MIN` |
| submission queue | same cron | `jobs/queue/pending/<stamp>_<name>.sh` → dry-run preflight → real run → `jobs/queue/done/<name>.{log,ids}` → commit `queue: ran <name>` | `QUEUE=0`, a tracked `jobs/queue/STOP` file, `QUEUE_MAX=6` per cycle |

There is no global quiet point any more (retired 2026-11-08, see "Eager zips and per-run idle"
below). Tracked chains are the `jobs/runs/*/chain.tsv` (or run manifests) written in the last 7 days;
the owner's unrelated jobs (dashboards, editors) never count against a run.

## Mail through one helper

| rule | why |
|---|---|
| One function (`mail_args`) prints the sbatch words; every submit path calls it | a missed path is a silent job |
| `MAIL_USER` is exported once in `~/.bashrc` AND written on the scrontab line | scrontab does not source `.bashrc`, so queued submissions would otherwise go unmailed |
| SLURM cannot add mail to a job already submitted | the first mails arrive with the next submission, not the running round |
| Odd characters in the address or type give a warning and no mail, never a refused sbatch | a notification setting must not block a run |

## The status snapshot

| section | content | who reads it |
|---|---|---|
| counts line and commit subject `cluster status <stamp>: <running>/<pending>/<failed>` | state at a glance | `git log` alone |
| `## Failures` | chain, stage, job name, NEW flag, `.err` tail, first `.out` error lines | the assistant, to build the fix without a terminal paste |
| finished arms | run id, arm name, raw and connected-component Dice from `metrics_summary_target_test*.csv` | the assistant's round analysis |
| one table per chain | each job's state and elapsed time | both |
| Queue | pending items with their `WHEN` and `NOTE`, the last five handled, HALTED when STOP exists | both |

Git handling that keeps the clone healthy: `pull --ff-only` first and abort quietly on failure; a
lock directory stale after 60 minutes; commit only when the files changed (a clock line alone is
not a change); on a rejected push one `pull --rebase` and one retry, then leave the commit local
and log it. Everything is logged to `jobs/logs/status_push.log`, which is gitignored.

## The queue

A queued item is one file with a comment header and the chain line(s) exactly as the owner would
type them, using variables from a tracked `jobs/queue/env.sh` (results root, pools, selector
folders, hint strings, student words; never secrets).

| header | meaning |
|---|---|
| `# WHEN=now` | run in the next cycle |
| `# WHEN=after:<id>[,<id>]` | run when every listed job is terminal per `sacct` |
| `# WHEN=after:<item name>` | run when that earlier queue item has run and every id in its `done/<name>.ids` is terminal |
| `# WHEN=idle:<run>` | run when no tracked job of that run (a run directory or an `env.sh` variable name such as `RUN2`) is RUNNING or PENDING; different runs in one cycle, the same run one per cycle |
| `# WHEN=quiet` | RETIRED: runs as `now` |
| `# NOTE=<one line>` | shown in the status snapshot |

Safety comes from the chains' own `DRY_RUN=1` preflights, not from parsing the lines: a refused
preflight moves the item to `done/<name>.refused.log` and it is never retried; a failed real run is
not retried either. The queue is for fixes and rounds the owner agreed to, never for new experiments
the owner has not seen.

## The loop, end to end

| step | actor | mechanism |
|---|---|---|
| submit a round | owner, or assistant through the queue | chain lines; dry run first |
| monitor and notify | cron | snapshot commit every 30 min, mail per job |
| fail | cron | `## Failures` + `ALERT` in the next commit |
| fix | assistant | pull, read the log tail, fix, push, queue the resubmission with `WHEN=after:` or `now` |
| finish | cron | eager auto-zip committed as the results appear (full zip when the run is idle) |
| analyse | assistant | round row in STATUS, figure, ideas log; the owner reviews and picks the next round |

## Lessons from the first day (2026-11-08)

| what broke | why | the rule now |
|---|---|---|
| `scrontab` and `crontab` both refused | disabled by the site ("scrontab is disabled"; "not allowed to access crontab because of pam configuration") | a self-resubmitting SLURM job (`jobs/status_push_loop.sh`): each tick runs the snapshot and `sbatch --begin=now+N minutes` itself; a `STOP_LOOP` file ends it; a duplicate loop is refused by job name |
| a five-hour gap between ticks | the tick is a `cpu` job and waits in the queue like any other | the interval is a floor, not a period; read `sacct` end times, not tick times, and never conclude "nothing finished" from a missing tick |
| the queue's run logs never reached the repo | a global `*.log` rule in `.gitignore` | `!jobs/queue/done/*.log`; check `git check-ignore` on every machine-written path before trusting the push |
| two queued chains died after their seed job | the campaign refused a checkout "2 commits behind origin" because the owner pushed during the tick | the queue pulls again right before each item and runs it with `ALLOW_STALE=1`; a chain that submits in stages must tolerate the repo moving under it |
| rounds 2+ of every teacher lineage were invisible | `pseudo_chain.sh` wrote `chain.txt` only; the tracker read `chain.tsv` | every chain writes `chain.tsv`; the reader also parses `chain.txt`; a tracked-job set that is incomplete makes the quiet point wrong, not just the table |
| one-off `sbatch_once` jobs (seed votes) were untracked | no chain folder | the tracker reads `jobs/queue/done/*.log` and `*.ids` and makes a synthetic chain per queue item |
| `sbatch_once.sh` has no dry run | the queue preflight would have submitted for real | a queued one-off line starts with `[[ -z "${DRY_RUN:-}" ]] \|\| return 0 2>/dev/null \|\| exit 0` |
| 44 "failures" in the first snapshot | the 7-day window counted long-known failures | `FAIL_WINDOW_HOURS=48` for Failures and ALERT; older ones are one summary line |
| the Arms table could not show an arm's result | rows were per job | one row per arm name (rounds folded as `r1: a / b / c; r2: …`), mean Dice over finished students |

A self-resubmitting tick can die before it resubmits (2026-11-09: a tick FAILED after 5 s on its node and the loop stopped for an hour). Each tick therefore also submits a watchdog job three intervals out; the next tick cancels it, and if no tick is queued when the watchdog starts, it restarts the loop. Submit the successor and the fresh watchdog at the START of the tick, before any work: a tick killed at its time limit after it had cancelled the old watchdog left nothing behind (2026-11-09). Never run long housekeeping (copies, moves) inside the tick; submit it as its own one-at-a-time job.

Prefer `WHEN=after:<the item's own input jobs>`, `after:<item name>`, `idle:<run>` or `WHEN=now` over a global wait: a quiet point waits for every unrelated job too, and on 2026-11-08 five ready items sat idle for hours behind one running round. `quiet` no longer waits (it runs as `now`). Auto-zip likewise runs on every new result, not only at quiet points.

Two design facts worth repeating: the snapshot is only as good as the set of tracked jobs, so every new submission path must register itself (a chain.tsv row or a queue log line), and the queue is paced (`QUEUE_MAX` items per tick), so a batch of nine items takes several ticks — the Queue section of the snapshot says what is still pending.

## Installing on a cluster

| step | command |
|---|---|
| 1 | `echo 'export MAIL_USER=<address>' >> ~/.bashrc` |
| 2 | one manual run: `RESULTS_ROOT=<root> bash jobs/status_push.sh; tail jobs/logs/status_push.log` — confirm a `cluster status …` commit reached the remote |
| 3 | `scrontab -e`: `#SCRON --partition=cpu --time=00:45:00 --mem=4G --cpus-per-task=1 --job-name=status-push --output=/dev/null`, `#SCRON --open-mode=append`, `*/30 * * * * MAIL_USER=<address> RESULTS_ROOT=<root> bash /abs/path/repo/jobs/status_push.sh` |
| if `scrontab` is disabled | the login-node `crontab -e` form of the same line, `>/dev/null 2>&1` |
| if `crontab` is disabled too (our site) | `MAIL_USER=<address> RESULTS_ROOT=<root> sbatch jobs/status_push_loop.sh` once; `INTERVAL_MIN` (default 15) on the sbatch line; stop with `touch jobs/logs/STOP_LOOP`; check with `squeue -n da-topology-status-loop` (one PENDING tick with a start time ahead is healthy) |

Use a clone that only the cron commits to, or accept that the owner's own pushes from the same
clone go through the same `pull --ff-only` discipline.

## Porting checklist

| item | check |
|---|---|
| every `sbatch` call site calls `mail_args` (grep `sbatch ` and `"$SBATCH_BIN"`) | a test with a stubbed `SBATCH_BIN` shows the words on a campaign job and a once-key job |
| chains write `jobs/runs/<chain>_<stamp>/chain.tsv` with a numeric `job_id` column | the snapshot tracks only those |
| the metrics reader matches the repo's own results table reader | the same Dice in both |
| `zip_results.sh` prints a commit line and refuses parts over the repo limit | the auto-zip trusts that line |
| the tests use a temporary git repository with a bare remote | the real repo's git state is never touched by a test |

## Per-user scoping (added 2026-11-08, causal_sedation port)

When two accounts share one repository and one cluster (here `mbranda1` and `mbaz1`, a teammate), one
loop per account, and a loop never reads, writes or commits outside its own account's directories.

| rule | mechanism |
|---|---|
| the user tag is the account | `USER_TAG=${LOOP_USER:-$(whoami)}`; the runs root resolves by whoami as the job scripts do |
| every machine-written path is per user | `cluster_status/<user>/{STATUS_CLUSTER.md,jobs.tsv,ALERT,zip_state.json,auto_zip_status.txt,queue_skip.txt}`, `jobs/queue/<user>/{pending,done,STOP,env.sh}`, `results_archive/<user>/`, `jobs/logs/<user>/` |
| the tracked set is one account's jobs | `sacct -u <user>`, `squeue -u <user>`, run manifests under that account's runs root only |
| one loop per account | job name `a3-status-loop-<user>` (duplicate refusal by name); `MAIL_USER` per account |
| commits name the account | `cluster status [<user>] <stamp>: r/p/f`, `auto-zip [<user>]: ...`, `queue [<user>]: ran <name>` |
| two loops share one remote | `pull --ff-only`, one rebase retry; a loop never edits the other user's directory, so their commits never conflict |
| shared facts stay shared | recipe lists and other non-path constants in `jobs/queue/env.common.sh`; run paths in the per-user `env.sh` |

Tests: two fake users in one temporary repository; each loop commits only its own files, and one
user's Failures never appear in the other's snapshot.

## Eager zips and per-run idle (2026-11-08)

Asked by the project lead the same day: "zip immediately as new results are done, queue whenever possible", then "no quiet point rule, just run when we can so we utilise the cluster".

**Why.** A global quiet point (no job of the user RUNNING or PENDING) almost never occurs when several long chains run at once, so `WHEN=quiet` items waited for days and the auto-zip archived nothing. The old rule protected nothing: each item already depends on its own inputs.

| rule | mechanism |
|---|---|
| nothing waits for a global quiet point | `WHEN=quiet` is retired: treated as `now`, logged, and noted in the snapshot's Queue section |
| an item waits only for what it reads | `after:<ids>`, `after:<item name>` (the named item has run and all its `.ids` are terminal), `idle:<run>` (no tracked job of that run is RUNNING or PENDING; a run directory or an `env.sh` variable name such as `RUN2`) |
| several ready items per tick | `QUEUE_MAX` default 6; SLURM and each chain's `MAX_CPUS` throttle the cluster |
| different runs together, the same run in turn | idle items for different runs go out in one cycle; a run that got a job this cycle is busy for the `idle:` items behind it (the next cycle sees the new job ids) |
| a job belongs to a run through its manifest or the queue item that submitted it | `RESUME_RUN=$RUN2`, `RUN=$RUN2` or `idle:RUN2` in the item; a hand-submitted job that is still PENDING and in no manifest is not counted |
| the snapshot says why an item waits | Queue table column "Runs next cycle?": `RUN2 busy: 74 running`, `waiting for 7433407 running`, `<item> has not run yet`, `already ran` |
| results-only zip as results change | per run, hash of the result files (csv, md, json, png under `<run>/pooled/`, no unit / cache / plan folders, no logs) plus mtimes in `zip_state.json`; at most once per `ZIP_MIN_INTERVAL_MIN` (30); fixed name `<tree>_h<H>_<stamp>.zip`, overwritten, so the history keeps one blob per change |
| full zip with logs at the idle point | once per idle period of the run, `<name>_full.zip` via `jobs/zip_pooled_cv.sh` |
| a zip over 95 MB is not committed | the status table says so; no retry until the files change |
| an item runs once | skipped when `done/<name>.ids` (or `.sh`, `.log`) exists in the working tree or in the remote's `done/` |
| a lost queue commit heals itself | each tick first commits leftover `jobs/queue/<user>/` moves and logs (`queue [<user>]: recover ...`); the dirty-tree rule ignores the user's own queue, status and archive paths and names the offending paths in `queue_skip.txt`; commits that never reached the remote are pushed by the next tick |

Lesson behind the last row: on 2026-11-08 an item ran but its commit never reached the remote and the queue then stood still for hours because a rule meant for foreign edits blocked the loop's own leftovers. Treat the loop's own directories as its own, and make the reason for any skipped tick visible in the snapshot.
