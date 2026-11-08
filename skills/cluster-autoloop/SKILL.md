---
name: cluster-autoloop
description: "Closing the loop between a SLURM cluster and an assistant that cannot log in: SLURM e-mail on every sbatch (MAIL_USER / MAIL_TYPE through one shared helper), a 30-minute scrontab job that writes a status snapshot (every chain's job states, a Failures section with log tails, an ALERT file, the Dice of finished arms) and pushes it to the repository, an automatic results zip committed at quiet points, and a submission queue of chain lines in the repository that the cron dry-runs and runs once. Use when a lab repo needs runs to be monitored, archived, fixed and resubmitted without anyone pasting terminals, or when porting the pattern from domain_adaptation_topology to another repo. Pairs with cluster-jobs (how jobs are built) and lcicm-cluster (site facts)."
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
| auto-zip | same cron, at a quiet point | the repo's `zip_results.sh` bundle copied into `results_archive/` and committed (each part ≤ 95 MB, GitHub's limit), marker `cluster_status/last_auto_zip.txt` | `AUTO_ZIP=0` |
| submission queue | same cron | `jobs/queue/pending/<stamp>_<name>.sh` → dry-run preflight → real run → `jobs/queue/done/<name>.{log,ids}` → commit `queue: ran <name>` | `QUEUE=0`, a tracked `jobs/queue/STOP` file, `QUEUE_MAX=2` per cycle |

A quiet point is: no job of any tracked chain is RUNNING or PENDING, and at least one tracked job
ended after the newest archive's stamp. Tracked chains are the `jobs/runs/*/chain.tsv` written in
the last 7 days; the owner's unrelated jobs (dashboards, editors) never block a quiet point.

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
| `# WHEN=quiet` | run when the tracked chains are all finished (one quiet item per cycle) |
| `# WHEN=after:<id>[,<id>]` | run when every listed job is terminal per `sacct` |
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
| finish | cron | auto-zip committed at the quiet point |
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
