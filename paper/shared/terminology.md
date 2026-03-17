# Terminology Conventions

Use the terms below consistently across all versions. This prevents drift when the
paper is compressed for RA-L or expanded for another venue.

## Core study terms

- `prompt/interface structure`
  Fixed meaning: how the planner is instructed to emit actions or tool calls, including output typing and any required self-check field.
  Use for: the paper's first design axis.
  Avoid: loosely swapping between `prompting`, `formatting`, `schema`, and `interface` unless the sentence really needs the distinction.
- `runtime validation`
  Fixed meaning: checking the emitted action or tool call against the runtime contract before execution.
  Use for: the paper's second design axis.
  Avoid: calling it `safety layer` or `policy shield`, which would overstate the setup.
- `single retry`
  Fixed meaning: one planner retry after a validation failure in `R1`.
  Avoid: vague phrases like `iterative repair loop`.
- `invalid action`
  Fixed meaning: an emitted action or tool call that violates the executor/runtime contract and cannot be dispatched as issued.
  Avoid: treating every task failure as an invalid action.
- `recovery`
  Fixed meaning: a run that contains an invalid action but still succeeds after runtime handling.

## Variant labels

- `P0`
  Preferred prose label: `minimal direct-action prompt`
- `P1`
  Preferred prose label: `structured tool-call prompt`
- `P2`
  Preferred prose label: `structured tool-call prompt with a brief self-check`
- `R0`
  Preferred prose label: `bare runtime with no validation and no retry`
- `R1`
  Preferred prose label: `runtime validation with a single retry`

Keep the symbolic labels in tables and figures. Use the prose labels when first
introducing them in text.

## Metric terms

- `planner call`
  Fixed meaning: one call to the planner backend.
- `tool call`
  Fixed meaning: one dispatched tool execution attempt.
- `planner/tool overhead`
  Fixed meaning: planner-call and tool-call counts, not a general compute-cost claim.
- `success rate`
  Fixed meaning: successful runs divided by summarized runs for the stated slice.

## Task terms

- `task family`
  Use only for `navigation` and `manipulation`.
- `manipulation`
  Preferred prose label for the raw output family sometimes named `pick_place`.
  Rule: write `manipulation` in paper text unless quoting a raw artifact key.
- `easy/shared slice`
  Fixed meaning: the easy conditions used for the shared family-level comparisons.
- `harder slice`
  Fixed meaning: the current harder navigation or harder manipulation evaluations already present in processed results.

## Framing terms

- `controlled study`
  Use when describing the whole paper.
- `design principle`
  Use only in discussion/conclusion for evidence-backed takeaways.
- `controlled systems study of embodied-agent execution`
  Preferred short identity for the manuscript.

## Terms to avoid

- `state of the art`
- `general embodied intelligence`
- `safety guarantee`
- `complete framework`
- `universal best`
- `real-world readiness`
