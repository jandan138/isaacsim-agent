# Experimental Setup and Study Design Draft

## Experimental Setup

This paper studies embodied-agent execution in a controlled Isaac Sim setting rather
than as a general agent benchmark. The environment is fixed to the current Block A
task matrix, and the paper asks how two design axes, prompt/interface structure and
lightweight runtime validation, affect execution outcomes under that shared setup.
The goal is not to maximize benchmark breadth. The goal is to isolate how planner
outputs and runtime handling change invalid actions, recovery, success, and
planner/tool workload when the surrounding task definition is held constant.

The study covers two task families. The navigation family includes language-driven
mobile-goal tasks in simple indoor scenes. The manipulation family includes tabletop
pick-and-place tasks that require object identification, grasping, transfer, and
placement. We use `manipulation` as the paper-facing family name even where raw
artifacts store the family as `pick_place`. Across these two families, the easy/shared
slice provides the cleanest direct family comparison because both families are
represented with matched prompt/runtime cells and the same measurement contract.

Difficulty is introduced through the slices already present in the frozen evidence
package. The easy/shared slice contains the main cross-family comparisons used for
the controlled study. The current harder navigation slice increases route length and
task burden without changing the task family. The current harder manipulation slice
reuses the same prompt x runtime matrix while increasing scripted sequence length via
fixed transfer waypoints. These harder slices are used to test whether more demanding
tasks change the qualitative condition ordering or mainly amplify workload. They do
not constitute a broad difficulty benchmark.

All conditions share a unified planner-to-executor contract. The planner emits either
a direct next action or a typed tool call, depending on the prompt/interface variant,
and the runtime dispatches only outputs that satisfy the contract for the active
condition. An `invalid action` is an emitted action or tool call that violates that
dispatch contract and cannot be executed as issued. A `recovery` is a run that
contains an invalid action but still ends successfully after runtime handling. This
shared contract is important because it lets the paper separate two failure modes:
invalid outputs generated at the planner interface, and recoverable invalid outputs
that can be repaired before execution.

The metrics are chosen to match that contract. We report success rate, invalid
actions, retries, planner calls, and tool calls throughout the draft. Success rate is
the main task outcome. Invalid actions reveal interface failures. Retries capture the
extra runtime handling used in `R1`. Planner calls and tool calls together represent
planner/tool overhead rather than a broader compute-cost claim. These metrics are
summarized in the frozen Block A closure package and in the slice-specific summaries
used for prompt-only, runtime-only, cross-family, and harder-task analysis.
[Table: experimental design summary]

The evidence package is intentionally finite. The frozen umbrella source is
`results/processed/block_a_final_closure/`, which integrates the earlier master
summary with the focused runtime-only, prompt-only, and harder-manipulation
additions. The broader easy navigation coverage includes a small Isaac-backed subset,
whereas the focused ablation slices are toy-backed to isolate the tested axes. This
mixed coverage is a study boundary, not a hidden implementation detail, and it is one
reason the paper argues for controlled design evidence rather than broad embodied
generalization.

## Study Design

The first study axis is prompt/interface structure. `P0` uses a minimal direct-action
prompt, which asks the planner for the next action without a typed tool-call schema.
`P1` uses a structured tool-call prompt, which requires the planner to select a tool
and provide typed arguments in a dispatchable form. `P2` keeps that structured
tool-call interface and adds a brief self-check before action emission. The role of
`P2` is not to introduce a larger runtime. Its purpose is to test whether a small
planner-side check can preserve the success profile of structured tool calls while
reducing unnecessary planner/tool work.

The second study axis is runtime handling. `R0` is a bare runtime with no validation
and no retry. `R1` adds runtime validation with a single retry. Runtime validation
checks the emitted action or tool call against the active contract before dispatch.
If validation fails, `R1` issues one planner retry; if the retried output satisfies
the contract, execution continues. This definition matters for interpretation. Prompt
variants can reduce invalid actions at the source, while the runtime variant can
convert some invalid outputs into successful executions after a failed first attempt.

The paper organizes the evidence into four analysis blocks. First, the main
prompt x runtime comparison uses the frozen Block A closure to establish the stable
qualitative ordering across the covered navigation and manipulation slices. Second,
the runtime-only ablation fixes prompt structure at `P1` and compares `R0` against
`R1` to measure the independent value of validation and retry. Third, the prompt-only
ablation fixes runtime at `R0` and compares `P0`, `P1`, and `P2` to measure the
independent value of interface structure and the efficiency effect of the brief
self-check. Fourth, the cross-family and harder-task views test whether those trends
remain aligned across navigation and manipulation and under higher task burden.

This setup should be read as a controlled systems study, not as a claim of a general
agent system. The task families are fixed, the condition matrix is explicit, the
runtime taxonomy stops at `R1`, and the study covers Block A only. The design claims
are therefore limited to what can be supported by the frozen summaries: prompt
structure affects invalid actions and success, runtime validation affects recovery and
success, a brief self-check can lower planner/tool overhead, and the observed
ordering persists across the covered task families and harder slices.
