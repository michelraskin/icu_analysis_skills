---
name: plan-and-delegate
description: "Environment-generic workflow for implementation/build tasks: the planning and reviewing primary agent owns the specification and correctness, while a host-appropriate build delegate writes production code. Use for building, implementing, writing, editing, or refactoring code or notebooks in Claude or Codex environments."
---

# Plan and delegate implementation work

Division of labor for any implementation task. **The planning and reviewing primary agent owns the
specification and correctness; a build delegate writes the production code.**

1. **Plan (primary agent).** Produce a concrete, unambiguous spec before delegating: exact files to
   create/edit, section/function breakdown, input/output schema, conventions to follow, and
   acceptance/validation criteria. Reuse existing patterns; name exact paths. Resolve fuzziness
   (read code, ask the user) before delegating.

2. **Delegate the build.** One focused deliverable per delegation. The delegate starts cold — pass
   the FULL spec (paths, schemas, repo conventions, exact validation command). Choose the
   host-specific delegate:

   **a) Claude host/agent — Sonnet build delegate (in-harness, tracked, returns to you):**
   Agent tool, `model: "sonnet"`, `subagent_type: "general-purpose"`, `run_in_background: false`
   when you need the result before continuing. Tell it to self-validate, report results, not commit.

   **b) Codex host/agent — Codex CLI (external, OpenAI account via `codex exec`) — runs on model `gpt-5.6-luna`
   ("luna"):** run as a SINGLE Bash command (no `&&`/`cd` chains — they hit `_safe_eval`; use `-C`
   for the working dir), passing a long spec via stdin so quoting stays clean:
   ```
   codex exec -C <workdir> -m gpt-5.6-luna -s workspace-write --skip-git-repo-check --color never \
     -o <workdir>/.codex_last.txt - < <specfile>
   ```
   (Or pass the spec as the final quoted arg instead of `- < specfile`.) It writes files in-place,
   streams progress + a final message to stdout, and writes the final message to the `-o` file.
   `-m gpt-5.6-luna` pins the luna model (it is also the `~/.codex/config.toml` default; siblings:
   `gpt-5.6-sol`, `gpt-5.6-terra`). Use `-s danger-full-access` only if it must write outside the
   workspace. Codex is authenticated via the user's existing login (`~/.codex/auth.json`) — do not
   pass API keys. Do not substitute the Claude/Sonnet delegate for this Codex-host invocation.

3. **Review (primary agent).** Read what the delegate produced and the diff. Verify it meets the spec, check
   its validation actually ran, fix or re-delegate as needed. **The primary agent owns correctness** — never
   relay "done" without confirming.

### Modeling acceptance criterion: persistent parameters

For modeling work, parameter persistence is an acceptance criterion. Every predictive or learned
preprocessing fit must be represented in a machine-readable manifest that is initialized once and
saved incrementally and atomically after each successful fit. Manifests must preserve the seed,
split context, exact features, hyperparameters, fitted metadata such as best iteration, and
software versions; coefficient tables or serialized model artifacts are separate outputs. Future
delegates must validate that every `.fit` and `.fit_transform` site has a nearby recorder call,
including repeated, ablation, fallback, and classical-statistical fits.

### LCICM compute allocation

On `gpu110`, modeling builds should request 32 total CPU threads and all four T4 GPUs when enough
independent GPU-capable fits exist. Record the resolved allocation and each model's device. A
single LightGBM fit uses one GPU; distribute independent folds/horizons/models across devices 0–3
with at most four processes and eight CPU threads per concurrent worker. CPU-only stages may use
all 32 threads. Do not oversubscribe 32 aggregate CPU threads or silently fall back to CPU/fewer
GPUs; fail clearly and document any approved reduced allocation.

### Statistical-inference acceptance criterion

For notebooks that report p-values, confidence intervals, feature-selected coefficients, or model
performance comparisons, also apply `icu-statistical-analysis`. Require patient/stay-grouped
cross-validation or cross-fitting over all eligible patients, fold-contained preprocessing and selection, cluster-aware
uncertainty, and saved fold metadata. Cross-validation may use all eligible observations more
efficiently but must never be described or implemented as increasing the number of independent
patients. Prefer exactly one pooled OOF prediction per eligible observation over a fixed holdout,
unless an external/temporal confirmatory set is explicitly required. Reject stacked repeated-fold
rows, row-wise random CV of ICU bins, and ordinary p-values after same-sample feature selection.

### Reusable-code acceptance criterion

Delegates and reviewers must search for existing helpers before adding new ones. Centralize
deterministic logic used by two or more builders/notebooks—such as progress logging, chunk-scan
reporting, preprocessing/CV orchestration, or manifest persistence—in one importable, tested
module; do not copy/paste it or embed divergent code strings. Keep analysis-specific targets,
covariates, plots, and narrative local; do not abstract one-off code merely for abstraction's sake.

Make dependencies explicit. If a generated notebook imports a repo-local shared module, ensure the
module accompanies the notebook when shared, and make imports work from every supported execution
directory. Treat this as a review acceptance criterion: keep one source implementation, have all
consumers import it, regenerate and validate all consumers, and add a direct smoke/unit test for
the shared utility.

Require progress observability for long clinical-data pipelines: use a stable structured prefix
with the notebook/analysis and stage; emit START/DONE/ERROR or scan/model/fold events; include
elapsed time; flush output; report chunks periodically, not per row; and never log PHI, IDs, or
secrets.

## Notebook-builder repos (e.g. causal_sedation) — pass these to the delegate
- Notebooks are generated by `_build_*.py` builders (nbformat, `md()`/`code()` helpers).
  **Edit the builder, never the `.ipynb`.** Mirror the structure of existing builders.
- Cannot run vs cluster data locally — validate by building + compiling every cell:
  `python3 -c "import os,runpy,nbformat; os.chdir('<dir>'); runpy.run_path('<builder>.py'); nb=nbformat.read('<nb>.ipynb',4); nbformat.validate(nb); [compile(c.source,'<c>','exec') for c in nb.cells if c.cell_type=='code']; print('VALID',len(nb.cells))"`
- Bash `&&`/`cd` chains fail in this environment (`_safe_eval`) — use `python3 -c` with `os.chdir`.
- Users run the notebooks on the LCICM cluster; builders read `sedation_*` dataset parquet outputs.
