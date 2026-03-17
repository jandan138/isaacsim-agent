# RA-L Abstract Candidates

All three versions stay within the current Block A evidence boundary: a controlled
Isaac Sim study of prompt/interface structure and lightweight runtime validation.

## A. Most conservative version

We present a controlled systems study of embodied-agent execution in Isaac Sim. The
study isolates two design axes, prompt/interface structure and lightweight runtime
validation, across navigation and tabletop manipulation tasks. We compare a minimal
direct-action prompt, a structured tool-call prompt, and a structured tool-call
prompt with a brief self-check, under either a bare runtime or runtime validation
with a single retry. Results from the frozen Block A package show a stable ordering
across the covered slices: the weakest condition is the minimal direct-action prompt
without validation, runtime validation recovers fragile executions that would
otherwise fail, and the structured prompt variants remain successful while the
self-check variant reduces planner/tool workload relative to the structured baseline.
The same qualitative trends appear in both task families and remain unchanged on the
current harder slices, where workload increases but condition ordering does not. The
paper does not claim a new model or broad embodied generalization; it offers
controlled empirical evidence that interface structure and lightweight runtime checks
meaningfully affect embodied-agent reliability and execution overhead in the tested
Isaac Sim setting.

## B. Most finding-forward version

We study how prompt/interface structure and runtime validation affect embodied-agent
execution in a controlled Isaac Sim setting. Across navigation and tabletop
manipulation tasks, a fixed-runtime prompt-only ablation shows that the minimal
direct-action condition fails on all four evaluated tasks, while both structured
tool-call variants succeed on all four and eliminate invalid actions in that slice.
A fixed-prompt runtime-only ablation shows that adding validation with a single retry
raises success from `2/4` to `4/4`, with the gain coming from successful recovery of
invalid-first-action runs rather than fewer invalid attempts. In the broader frozen
Block A package, the same qualitative ordering remains visible across the covered
easy and harder slices: `P0/R0` is weakest, `P0/R1` recovers, `P1` and `P2` stay
strong, and `P2` uses fewer planner/tool calls than `P1` in the tested slices.
These results position the paper as a controlled systems study rather than a
new-model or benchmark-supremacy claim, and suggest that execution reliability in
embodied agents depends substantially on interface design and lightweight runtime
checks.

## C. Most robotics-relevance version

Embodied robots can fail at the boundary between planning and execution even when the
task itself is simple. We present a controlled Isaac Sim study of two design choices
at that boundary: how planner outputs are structured for execution, and whether the
runtime validates an emitted action before dispatch and allows a single retry. The
study covers navigation and tabletop manipulation under a unified execution contract,
with success, invalid actions, retries, and planner/tool calls as the primary
outcomes. We find that structured tool-call prompts remove the invalid-action
failures seen under a minimal direct-action prompt, that lightweight runtime
validation recovers otherwise failing but recoverable executions, and that a brief
self-check lowers planner/tool workload relative to the structured baseline without
changing the success profile in the tested setup. These effects remain qualitatively
consistent across both task families and the current harder slices, where workload
increases but ranking does not reverse. The contribution is controlled empirical
evidence for execution-interface design in simulation, not a claim of a general
embodied-agent system or a deployment claim.

## Current recommendation

Version A is the safest default for the next manuscript pass. Version B is useful if
the authors want the abstract to surface the independent prompt-only and runtime-only
ablations more explicitly.
