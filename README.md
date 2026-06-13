# icu_analysis_skills

Claude Code [skills](https://docs.claude.com/en/docs/claude-code/skills) for **machine-
learning and statistical analysis on critical-care (ICU) EHR datasets**. They capture how
to identify patient cohorts, locate clinical variables, and engineer time-windowed
features in the major ICU databases, so an assistant can pick up dataset structure and the
exploratory workflow without re-deriving them each time.

The skills are dataset-focused and analysis-agnostic — useful for any predictive modeling,
causal inference, phenotyping, or descriptive study built on these data.

## Skills

| Skill | Use it when |
|---|---|
| **clinical-icu-datasets** | Starting any ICU-data analysis. Overview of the datasets, the shared event-table/dictionary/index-time mental model, a reusable cohort → time-windowed-feature → matrix workflow, naming conventions, and exploration recipes. Routes to the per-dataset skills. |
| **eicu-dataset** | Building an eICU-CRD cohort or finding/extracting a variable (flat CSVs keyed by `patientunitstayid`, inline variable names, integer time offsets). |
| **mimiciv-dataset** | Building a MIMIC-IV (+ ED) cohort or finding an `itemid` / ICD code (relational `hosp`/`icu` modules, real timestamps, `d_items`/`d_labitems`/`d_icd_diagnoses` dictionaries). |
| **pmap-dataset** | Building a cohort or finding a flowsheet `meas_id` / lab `proc_id` in a PMAP-style institutional **Epic Clarity** export (measure/procedure dictionaries; units often Fahrenheit). |

Each skill is a directory under `skills/` containing a `SKILL.md` with YAML frontmatter
(`name`, `description`). Claude auto-loads the relevant one based on the `description`.

## Install (symlink into your Claude skills dir)

Skills must live in `~/.claude/skills/` (or a project's `.claude/skills/`) to be picked
up. This repo stays the single source of truth; `install.sh` symlinks each skill into
your skills directory:

```bash
git clone https://github.com/michelraskin/icu_analysis_skills.git
cd icu_analysis_skills
./install.sh
```

This creates symlinks like `~/.claude/skills/eicu-dataset -> .../icu_analysis_skills/skills/eicu-dataset`.
Re-run after pulling updates (it's idempotent). To install elsewhere, set
`CLAUDE_SKILLS_DIR` (e.g. project-local):

```bash
CLAUDE_SKILLS_DIR=/path/to/project/.claude/skills ./install.sh
```

To uninstall, remove the symlinks:
`rm ~/.claude/skills/{clinical-icu-datasets,eicu-dataset,mimiciv-dataset,pmap-dataset}`.

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
