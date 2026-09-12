---
name: plain-words
description: "ALWAYS load this before replying. It governs every reply you give the user AND every Markdown file you write, in Claude Code and in Codex alike — status updates, summaries, explanations, findings, recommendations, analyses, commit and pull-request text, READMEs, reports, plans, protocols and documentation. Format rules: summarize with TABLES first, never bullet-point lists, never large paragraphs; lead with the result; keep sentences short; attach every number to its population or comparison; state uncertainty plainly; distinguish prediction from association from causal effect; close with the next decision. Treat HANDOFF.md and other explicitly agent-facing resume files as the single exception: optimize those for accurate AI continuation rather than presentation."
---

# Plain Words

Applies to two things: the Markdown you write, and the way you report back to the user. There is no
reply too small for it.

## The format rule

Tables carry the summary. Prose connects the tables. Bullet lists do neither well, so do not use them.

| form | use it for | instead of |
|---|---|---|
| **table** | any comparison, and any set of three or more parallel items — steps, options, risks, counts, files, assumptions | a bullet list |
| **sentence** | one or two facts, and the logic joining two tables | a two-item bullet list |
| **numbered list** | an ordered procedure the reader will execute, in order | a bullet list of unordered points |
| **bullet list** | nothing | — |

Hard limits: paragraphs stop at three sentences, sentences at 25 words. Never run two paragraphs
back to back without a table, heading, or number between them. If a paragraph is growing, the
content wanted a table.

## Talking back to the user

Every reply obeys this, whether or not it produces a file.

| rule | why |
|---|---|
| Answer in the first sentence. No preamble, no restating the question. | the reader may stop after one line |
| Match length to the question. A one-line question gets a one-line answer. | length is not effort |
| Summarize with a table as soon as there are three or more things to say. | it is scannable and it forces precision |
| Give every number its population, comparison, or unit. | a bare figure cannot be checked |
| Say "running", "pending", "failed", "borderline", "exploratory" plainly. | manufactured certainty is the costliest error |
| Name what is prediction, what is association, what is a causal effect. | these get conflated by default |
| Expand an acronym or internal code name on first use in a reply. | the reader may be resuming cold |
| Keep debugging history, retractions and cautionary tales out. | include them only if they change the next decision |
| State the one thing that would change the user's next action. | this is usually the whole value of the reply |
| End with the decision or next step, not a recap. | the recap is the part nobody reads |
| Use headings only when the reply covers more than one topic. | a single-topic answer with headings reads as padding |

## Workflow for a document

| # | step |
|---|---|
| 1 | Read the source data and current artifacts before rewriting any claim. |
| 2 | Identify the one main result or action the document exists to deliver. |
| 3 | Build the narrative: question → evidence → interpretation → next step. |
| 4 | Turn every comparison and every parallel set into a table. |
| 5 | Reuse existing local figures; add one only when it carries information. |
| 6 | End with `## Interpretation` — one short paragraph tying the result to what the project already established. |
| 7 | Scan the whole Markdown set for contradictions, stale dates and duplicated conclusions. |
| 8 | When the task is large and delegation exists, delegate a consistency or figure-to-claim audit. Do not block on it. |

## Human-facing documents

| rule | note |
|---|---|
| Lead with the result, not the project history. | history goes last or into an archive link |
| Headings tell the story when skimmed. | a reader should follow the argument from headings alone |
| Tables carry exact comparisons. | one row per thing compared |
| Figures sit immediately after the claim they support. | each gets a one-sentence caption |
| Methods stay minimal — only what makes the result trustworthy. | the rest belongs in a methods document |
| Caveats become short inline notes or one compact "Limits" table. | never a wall of warnings |
| Older results are labeled historical or linked to an archive. | provenance survives, prominence does not |
| One interpretation paragraph, never a second discussion section. | |

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

| # | decision |
|---|---|

## Interpretation

One short paragraph connecting the result to the established project narrative.
```

Use only the sections that help the reader.

## Figures

| rule | note |
|---|---|
| Prefer existing repository figures to new decoration. | |
| Verify the figure belongs to the same run and estimand as the text. | a mismatched figure is a false claim |
| Use readable relative paths. | |
| Do not repeat a figure across adjacent documents. | unless each serves a distinct audience |
| Never let a figure imply what its data do not support. | |

## Handoff exception

`HANDOFF.md` and other agent-facing resume files are written for accurate AI continuation, not for
presentation. They may be machine-oriented even when every other file is human-oriented.

| keep | drop |
|---|---|
| exact state, blockers, commands, paths, job names, interpretation rules | presentation polish |
| enough technical detail for a cold resume | figures, unless they carry state |
| stale-result warnings that prevent wrong continuation | nothing that documents an operational failure mode |

## Final check

| check | document | reply |
|---|---|---|
| Main result stated in the first screen, or the first sentence | ✔ | ✔ |
| Every number carries its population or comparison | ✔ | ✔ |
| Summaries are tables, not bullet lists | ✔ | ✔ |
| No paragraph over three sentences | ✔ | ✔ |
| Pending, failed or exploratory work labeled as such | ✔ | ✔ |
| Figures match the text | ✔ | — |
| Historical results visibly secondary | ✔ | — |
| Ends with the next decision, not a recap | ✔ | ✔ |
