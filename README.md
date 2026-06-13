# icu_analysis_skills

Claude Code [skills](https://docs.claude.com/en/docs/claude-code/skills) that capture how
to **identify patients and find/extract variables** in the ICU research datasets used by
the `ttmhte` (targeted temperature management HTE) and `transfusionhte` (transfusion HTE)
projects. The goal: when you start a new analysis, Claude can pick up dataset structure,
cohort logic, variable locations, and the exploratory workflow without re-deriving them.

## Skills

| Skill | Use it when |
|---|---|
| **clinical-icu-datasets** | Starting any analysis on these datasets. Overview of the projects, the shared `myPredictorsDf` pipeline, naming conventions, data locations, and how to write an exploratory notebook. Routes to the per-dataset skills. |
| **eicu-dataset** | Building an eICU cohort or finding/extracting an eICU variable (flat CSV tables keyed by `patientunitstayid`). |
| **mimiciv-dataset** | Building a MIMIC-IV (+ ED) cohort or finding an `itemid`/ICD code (long event tables + `d_items`/`d_icd_diagnoses` dictionaries). |
| **pmap-dataset** | Building an ACCM PMAP cohort or finding a flowsheet `meas_id`/lab `proc_id` (Epic Clarity export keyed by `osler_id`; temperatures in °F). |

Each skill is a directory under `skills/` containing a `SKILL.md` with YAML frontmatter
(`name`, `description`). Claude auto-loads the relevant one based on the `description`.

## Install (symlink into your Claude skills dir)

Skills must live in `~/.claude/skills/` (or a project's `.claude/skills/`) to be picked
up. This repo stays the single source of truth; `install.sh` symlinks each skill into
your skills directory:

```bash
git clone <this-repo-url> icu_analysis_skills
cd icu_analysis_skills
./install.sh
```

This creates symlinks like `~/.claude/skills/eicu-dataset -> .../icu_analysis_skills/skills/eicu-dataset`.
Re-run after pulling updates (it's idempotent). To install somewhere else, set
`CLAUDE_SKILLS_DIR`, e.g. project-local:

```bash
CLAUDE_SKILLS_DIR=/path/to/project/.claude/skills ./install.sh
```

To uninstall, just remove the symlinks: `rm ~/.claude/skills/{clinical-icu-datasets,eicu-dataset,mimiciv-dataset,pmap-dataset}`.

## Updating the skills

Edit the `SKILL.md` files in `skills/`. Because they're symlinked, changes take effect
immediately — no reinstall needed. Commit and push to share. Keep the `description`
frontmatter specific (it's what Claude uses to decide when to load the skill), and
prefer copy-paste-ready snippets over prose.
