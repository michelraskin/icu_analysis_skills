# icu_analysis_skills

Claude Code [skills](https://docs.claude.com/en/docs/claude-code/skills) for analysis on
critical-care (ICU) EHR datasets, focused on **patient (cohort) identification** and
**feature identification**. They give a fresh Claude session enough context to understand a
dataset, identify a new cohort of patients via a notebook, run an initial descriptive
analysis, and locate the variables an analysis needs — without re-deriving any of it.

The skills are dataset-focused and analysis-agnostic — useful for any predictive modeling,
causal inference, phenotyping, or descriptive study built on these data.

## Skills

| Skill | Use it when |
|---|---|
| **clinical-icu-datasets** | Starting any ICU-data analysis. Overview of the datasets, the event-table/dictionary/index-time mental model, the patient-identification recipe and signal taxonomy, and a bundled **cohort-identification notebook template** (`cohort_identification_template.py`) + initial-analysis playbook. Routes to the others. |
| **eicu-dataset** | Identifying an eICU-CRD cohort — where each signal lives (inline name strings, ICD-9, no dictionary) and how to match it. Keyed by `patientunitstayid`; integer time offsets. |
| **mimiciv-dataset** | Identifying a MIMIC-IV (+ ED) cohort — resolving signals through `d_items`/`d_labitems`/`d_icd_diagnoses` (relational `hosp`/`icu` modules; ICD-9 **and** ICD-10; real timestamps). |
| **pmap-dataset** | Identifying a cohort in a PMAP-style institutional **Epic Clarity** export (flowsheet `meas_id` / lab `proc_id` dictionaries; units often Fahrenheit). |
| **icu-feature-identification** | Locating/extracting a specific variable across all three datasets — GCS & motor GCS (mGCS), discharge status/mortality, ICU & hospital length of stay, demographics, weight/height/BMI, vitals, labs, ventilation, vasopressors, sedation, urine output, severity scores, comorbidities. Includes the default "baseline covariates" block. |
| **lcicm-cluster** | Operating context for the LCICM lab cluster — on-disk paths for the eICU / MIMIC-IV / PMAP CSVs under `/projects/LCICM/`, file format & chunked-read conventions, how to run the notebooks, and the shared per-dataset repo layout. The operational layer beneath the scientific dataset skills. |
| **cluster-jobs** | Submitting, monitoring, interpreting and collecting SLURM batch jobs from a repo's `jobs/` directory — runner vs submitter, per-account runners, `INPUT_DIRS`/`LATEST:` resolution, PROBE timing runs, `finished_utc`, and the traps that kill a job in four seconds. Sits on top of **lcicm-cluster**. |
| **iteration-framework** | Running a unit of work end to end: specify → build → run → review → record, who owns correctness, when to stop, and the two documents that must stay current — an agent-facing `HANDOFF.md` with an experiment table, and a human-readable status doc. |
| **plain-words** | Every human-facing output: replies back to you as well as reports and READMEs. Result first, short sentences, compact tables, figure-led narrative, a one-paragraph interpretation; keeps AI handoffs operationally precise. |

Each skill is a directory under `skills/` containing a `SKILL.md` with YAML frontmatter
(`name`, `description`); some bundle helper files. Claude auto-loads the relevant one based
on the `description`.

## Install (symlink into your Claude and Codex skills dirs)

Skills must live in `~/.claude/skills/` (or a project's `.claude/skills/`) for Claude Code,
and `~/.codex/skills/` for Codex. Both tools select a skill from the same `SKILL.md`
frontmatter. This repo stays the single source of truth; `install.sh` symlinks each skill
into **both** directories:

```bash
git clone https://github.com/michelraskin/icu_analysis_skills.git
cd icu_analysis_skills
./install.sh
```

This creates symlinks like `~/.claude/skills/eicu-dataset -> .../icu_analysis_skills/skills/eicu-dataset`
and the matching `~/.codex/skills/eicu-dataset`. Re-run after pulling updates — it is idempotent,
and it prunes links left dangling by a renamed skill. Override either destination, or set one to
an empty string to skip that tool:

```bash
CLAUDE_SKILLS_DIR=/path/to/project/.claude/skills ./install.sh   # project-local Claude install
CODEX_SKILLS_DIR= ./install.sh                                   # Claude only
```

To uninstall, remove the symlinks from both directories:
`rm ~/.claude/skills/<name> ~/.codex/skills/<name>`.

## Updating the skills

Edit the `SKILL.md` files in `skills/`. Because they're symlinked, changes take effect
immediately — no reinstall needed. Keep each `description` specific (it's what Claude uses
to decide when to load the skill), and prefer copy-paste-ready snippets over prose.

## Data access

These skills describe dataset *structure* only and contain **no patient data**. You must
obtain the data yourself through the appropriate channel:
- **eICU-CRD** and **MIMIC-IV** — credentialed access via [PhysioNet](https://physionet.org/)
  (CITI training + signed data-use agreement).
- **Institutional Epic Clarity exports (PMAP-style)** — through your institution's data-use
  agreement / IRB. Keep raw exports out of version control; share only derived,
  de-identified feature tables.

## Citing

If these skills help your work, please cite this repository (see `CITATION.cff`):

> Raskin, M. *icu_analysis_skills: Claude Code skills for ML analysis of ICU EHR
> datasets.* GitHub repository, https://github.com/michelraskin/icu_analysis_skills

Please **also cite the underlying datasets** per their own requirements — e.g. the
eICU-CRD and MIMIC-IV PhysioNet publications and the PhysioNet platform. Check each
dataset's PhysioNet page for the exact citation and version.
