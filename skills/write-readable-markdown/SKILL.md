---
name: write-readable-markdown
description: "Create or rewrite Markdown documentation as simple, human-readable narrative with short sections, clear result-first structure, compact tables, and useful figures. Use for README files, reports, status pages, methods summaries, plans, and documentation cleanups where dense technical prose, long warning blocks, chronology, or duplicated detail should become an accessible visual story. Treat HANDOFF.md and other explicitly agent-facing resume files as an exception: optimize those for accurate AI continuation rather than presentation."
---

# Write Readable Markdown

## Workflow

1. Read the source data and current artifacts before rewriting claims.
2. Identify the one main result or action for each document.
3. Build a short narrative: question → evidence → interpretation → next step.
4. Reuse relevant local figures. Add a figure only when it carries information.
5. Replace long prose with a compact table, figure caption, or short bullets.
6. End every human-facing summary with `## Interpretation`: one short paragraph at most, connecting
   the result to relevant conclusions or decisions established earlier in the project.
7. Scan the full Markdown set for contradictions, stale dates, and duplicated conclusions.
8. When delegation tools are available and the task is large, delegate an independent consistency
   review or figure-to-claim audit. Do not block the work when delegation is unavailable.

## Human-facing documents

- Lead with the result, not project history.
- Prefer sentences under 25 words.
- Keep paragraphs to one to three sentences.
- Use descriptive headings that tell the story when skimmed.
- Use compact tables for exact comparisons.
- Place figures immediately after the claim they support.
- Give each figure a one-sentence caption or interpretation.
- Keep methods to the minimum needed to trust the result.
- Turn caveats into short inline notes or one compact “Limits” table.
- Remove cautionary tales, debugging history, and repeated retractions from the main narrative.
- Preserve provenance by labeling older results “historical” or linking to an archive.
- Do not manufacture certainty. State “running,” “pending,” or “exploratory” plainly.
- Add one small interpretation paragraph. Never turn it into a second discussion section.

## Narrative template

```markdown
# Title

One-sentence result.

## Why this matters

Two or three short sentences.

## Main result

| comparison | result |
|---|---:|

![Descriptive figure](path/to/figure.png)

One-sentence interpretation.

## What happens next

1. First decision.
2. Second decision.

## Interpretation

One short paragraph connecting the result to the established project narrative.
```

Use only the sections that help the reader.

## Figures

- Prefer existing repository figures over new decoration.
- Verify the figure belongs to the same run and estimand as the text.
- Use readable relative paths.
- Avoid repeating the same figure across several adjacent documents unless each document serves a
  distinct audience.
- Never use a figure to imply a result that its underlying data do not support.

## Handoff exception

For `HANDOFF.md` or another agent-facing resume file:

- prioritize exact state, blockers, commands, paths, job names, and interpretation rules;
- include enough technical detail for a cold resume;
- keep stale-result warnings when they prevent incorrect continuation;
- figures are optional;
- do not simplify away operational failure modes.

The handoff may be machine-oriented even when every other Markdown file is human-oriented.

## Final check

- Can a new reader state the main result after one screen?
- Does every number identify its population or comparison?
- Is the current primary analysis visually and verbally clear?
- Are historical results visibly secondary?
- Do figures match the text?
- Are next actions concrete?
- Is the interpretation section present and limited to one paragraph?
