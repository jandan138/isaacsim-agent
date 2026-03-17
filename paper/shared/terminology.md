# Terminology Conventions

Use the terms below consistently across the shared layer and the RA-L drafts. The
main goal of this update is to keep the science fixed while shifting the headline
framing from `prompt structure` to execution architecture.

## Preferred headline framing

- `planner-to-executor contract design`
  Fixed meaning: how the system specifies what kinds of planner outputs count as
  dispatchable actions or tool calls before execution.
  Use for: the paper's first design axis.
- `action interface specification`
  Fixed meaning: the concrete executable form expected at the planner/executor
  boundary, including tool names, required arguments, and any planner-side
  self-check field.
  Use for: section text, titles, abstracts, and figure captions when a shorter term
  than `planner-to-executor contract design` is helpful.
- `runtime validation and retry`
  Fixed meaning: checking an emitted action or tool call against the active
  contract before dispatch and, in `R1`, allowing one repair attempt.
  Use for: the paper's second design axis.
- `invalid action`
  Fixed meaning: an emitted action or tool call that violates the active contract
  and therefore cannot be dispatched as issued.
  Avoid: using it as a synonym for every unsuccessful run.
- `recovery`
  Fixed meaning: a run that contains an invalid action but still succeeds after
  runtime handling.

## Legacy-to-current mapping

The experimental definitions do not change. Only the paper-facing wording changes.

| Legacy term | Preferred current term | Usage rule |
| --- | --- | --- |
| `prompt structure` | `planner-to-executor contract design` or `action interface specification` | Use the legacy term only when discussing the implementation mechanism that realizes the contract variant. |
| `structured prompt` | `structured action interface` or `typed tool-call contract` | Prefer the current term in titles, abstracts, and result claims. |
| `prompt-only ablation` | `action-interface ablation` | `prompt-only ablation` may remain as a shorthand for the fixed-`R0` slice, but first mention should clarify that it is an action-interface comparison implemented through planner instructions. |
| `runtime policy` | `runtime validation policy` | Use the longer form when referring specifically to `R0` and `R1`. |

## Variant labels

Keep symbolic labels in figures and tables. Use the prose labels on first mention.

- `P0`
  Preferred prose label: `under-specified direct-action contract`
  Legacy correspondence: `minimal direct-action prompt`
- `P1`
  Preferred prose label: `typed tool-call contract`
  Legacy correspondence: `structured tool-call prompt`
- `P2`
  Preferred prose label: `typed tool-call contract with a brief self-check`
  Legacy correspondence: `structured tool-call prompt with a brief self-check`
- `R0`
  Preferred prose label: `bare dispatch runtime`
  Legacy correspondence: `bare runtime with no validation and no retry`
- `R1`
  Preferred prose label: `validate-and-retry runtime`
  Legacy correspondence: `runtime validation with a single retry`

## Metric terms

- `planner call`
  Fixed meaning: one call to the planner backend.
- `tool call`
  Fixed meaning: one dispatched tool execution attempt.
- `planner/tool overhead`
  Fixed meaning: planner-call and tool-call counts, not a general compute-cost
  claim.
- `success rate`
  Fixed meaning: successful runs divided by summarized runs for the stated slice.

## Task and slice terms

- `task family`
  Use only for `navigation` and `manipulation`.
- `manipulation`
  Preferred paper-facing label for the raw artifact family sometimes named
  `pick_place`.
- `easy/shared slice`
  Fixed meaning: the easy conditions used for the direct family-level comparison.
- `harder slice`
  Fixed meaning: the current harder navigation or harder manipulation evaluations
  already present in processed results.

## Writing rules

- Use `prompt` only when the sentence truly needs to talk about the textual
  instruction given to the planner.
- Use `contract`, `interface`, or `runtime validation` for the paper's main story.
- Use `controlled systems study` or `controlled empirical study of embodied-agent
  execution` for the manuscript identity.

## Terms to avoid as headline framing

- `prompt engineering study`
- `prompt ablation paper`
- `state of the art`
- `general embodied intelligence`
- `safety guarantee`
- `complete framework`
- `universal best`
- `real-world readiness`
