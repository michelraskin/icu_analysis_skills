---
name: plain-words
description: "Write in plain words. This governs BOTH the Markdown you produce AND every reply you give back to the user, in Claude Code and in Codex alike. Load it before writing or rewriting any README, report, status page, plan, methods summary, protocol, or documentation, and before answering with a status update, summary, explanation, set of findings, recommendation, commit message, or pull-request description. Applies to any output a human reads: lead with the result, keep sentences short, use compact tables and figures that carry information, attach every number to its population or comparison, state uncertainty plainly, distinguish prediction from association from causal effect, and close with the next decision. Treat HANDOFF.md and other explicitly agent-facing resume files as the single exception: optimize those for accurate AI continuation rather than presentation."
---

# Plain Words

Applies to two things: the Markdown you write, and the way you report back to the user.

## Talking back to the user

Use these rules in every reply, whether or not the reply produces a file. They cover chat answers,
status summaries, terminal output, and commit or pull-request text.

- Lead with the answer or the current state in the first sentence. No preamble, no recap of the question.
- Use plain words. Expand an acronym or an internal code name the first time it appears in a reply.
- Keep sentences under 25 words and paragraphs to one to three sentences.
- Match length to the question. A one-line question gets a one-line answer.
- Give every number its population, comparison, or unit. Never quote a bare figure.
- Use a compact table only when comparing several numbers. Two numbers belong in a sentence.
- Say "running", "pending", "failed", "borderline", or "exploratory" plainly. Do not manufacture certainty.
- Name what is prediction, what is association, and what is a causal effect, every time.
- Keep debugging history, retractions, and cautionary tales out of the reply unless the user needs
  them to make the next decision.
- Flag the one thing that would change the user's next action, and say what that action is.
- End with the decision or next step, not a summary of what you just said.
- Use headings in a reply only when it covers more than one topic.

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

For a conversational reply:

- Is the answer in the first sentence?
- Would a reader who knows the project but not this session follow it?
- Is every number attached to a population or comparison?
- Is uncertain work labeled as pending, failed, or exploratory?
- Does it end with the next decision rather than a recap?
