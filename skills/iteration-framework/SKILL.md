---
name: iteration-framework
description: "How this project iterates on an experiment or a build, and what must be written down at the end of each cycle. Use when starting, resuming, or finishing a unit of work — a cluster run, an analysis, a code fix, a delegated build — and whenever the user asks what the status is, what to run next, or where things stand. Defines the five-step cycle (specify, build, run, review, record), who owns correctness, when to stop, and the two documents that must stay current: an agent-facing HANDOFF.md carrying an experiment table with one row per run, and a human-readable status document. Pairs with plan-and-delegate for the build step and cluster-jobs for the run step."
---

# Iteration framework

One rule above all: **a cycle is not finished when the code runs or the agent reports done. It is finished when the experiment table says what happened and what comes next.**

## The cycle

| # | step | owner | done when |
|---|---|---|---|
| 1 | **Specify** | you | exact files, schemas, conventions and acceptance criteria are written before any code is touched |
| 2 | **Build** | delegate, per `plan-and-delegate` | the delegate self-validates and reports real output, not a summary |
| 3 | **Run** | the cluster, per `cluster-jobs` | `run_manifest.txt` carries `finished_utc` |
| 4 | **Review** | you | you read the diff and the outputs yourself; a delegate's "done" is a claim, not evidence |
| 5 | **Record** | you | the experiment table and the status document both reflect the new state |

Never skip step 5 because the result was negative or the run failed. A failed run that nobody recorded gets re-run by the next person, or worse, quoted as if it had succeeded.

## Acceptance criteria before delegating

State them in the spec, not after seeing the result.

| criterion | test |
|---|---|
| the change does what was specified | read the diff, not the report |
| a new test would have caught the old bug | revert the fix; the test must fail |
| nothing else broke | the full local suite still passes at its known count |
| generated artifacts were regenerated | builders edited, notebooks rebuilt, cells compile |

## When to stop

| situation | action |
|---|---|
| acceptance criteria met | stop; record; move to the next question |
| a criterion fails on a known cause | re-delegate once with a corrected spec |
| the same criterion fails twice | stop delegating. The spec is wrong, not the build |
| the result is negative | stop and record it. A negative result is a result |
| the run revealed a defect | fix the defect, re-run, and keep the defective run in the table |

## The two documents

Both are updated at the end of every cycle that changed state. They serve different readers and must not be merged.

| document | reader | optimize for |
|---|---|---|
| `reports/HANDOFF.md` | an AI or a person resuming cold | exact state, job ids, paths, commands, blockers, interpretation rules |
| the human status document (for example `reports/aim2_status.md`) | a collaborator or supervisor | what is known, what it means, what happens next |

### The experiment table

`HANDOFF.md` carries one table with one row per run or experiment, newest first. It is the project's memory; prose around it is commentary.

| column | holds |
|---|---|
| experiment | the analysis or question, and its notebook stem |
| job / date | cluster job id and completion date, or "local" |
| status | complete, running, failed, invalid, superseded, not built |
| result | the finding in one line, with the number that matters |
| next action | the single next step, or "none — closed" |

Rules for the table: never delete a row, mark it `superseded` instead; a run whose method was later found defective is `invalid`, not `complete`; and a row with no next action must say so explicitly, so a reader can tell a closed question from a forgotten one.

### The status document

Human-readable, follows `plain-words`: lead with the result, summarize with tables, no bullet lists, close with the next decision. It says what the project now believes and how confident it is. It does not repeat the handoff's paths and commands.

## Resuming

Read `HANDOFF.md` first, then the experiment table, then the status document. Before acting on any row, verify its stated state still holds — a job may have finished, a file may have moved, a claim may have been withdrawn.
