# Discussion and Limitations Draft

## Discussion

The main value of the current results is that they make the execution boundary
itself visible as a robotics systems problem. In embodied tasks, failure does not
arise only from high-level planning quality. It also arises when the planner emits
an action or tool call that the executor cannot dispatch as issued. Within the
current Block A study, the weakest condition is consistently the minimal direct-
action prompt with the bare runtime, while structured tool-call prompting removes the
invalid-action failures seen in that weakest cell. For robotics and embodied-agent
systems, this matters because it shifts attention from model-only explanations toward
planner-to-executor interface design as an independent source of reliability.

The runtime-only ablation shows why runtime validation is a high-leverage design
point. When prompt/interface structure is held fixed at `P1`, adding runtime
validation with a single retry raises success from `2/4` to `4/4`, while the number
of invalid-action runs remains the same and successful recoveries rise from `0` to
`2`. In other words, the gain comes from catching and repairing fragile executions at
the point where they would otherwise terminate. That is a practically attractive
result for embodied systems: a small runtime contract check can add recovery value
without requiring a different planner, a larger runtime taxonomy, or a more complex
agent architecture. At the same time, the evidence is narrow by design. The study
supports runtime validation as a recovery mechanism for recoverable contract
violations in the tested setup; it does not justify broader safety or robustness
claims.

The `P2` condition suggests a complementary lesson. Once a structured tool-call
interface is already in place, a brief self-check can preserve the strong success
profile of `P1` while lowering planner/tool overhead in the tested slices. This is a
useful systems result because it indicates that some efficiency gains can come from a
small planner-side interface refinement rather than from a heavier downstream runtime
policy. The paper should still state that point conservatively. The current evidence
does not prove that self-checks are always beneficial, only that the brief self-
check used here lowered planner/tool overhead without harming success in the covered
navigation, manipulation, and harder-task slices.

Just as importantly, this paper is not a general embodied-agent benchmark or a
state-of-the-art comparison. The contribution is not a new model, not a full agent
framework covering the entire project roadmap, and not a claim that the current
ordering must hold across different simulators, backends, or robot embodiments.
Instead, the paper offers a controlled comparison that isolates two execution-design
axes and shows that both materially affect outcomes in the current Isaac Sim task
matrix. That narrower positioning is a strength of the study rather than a weakness:
it lets the results speak to concrete system design choices without pretending to
settle broader questions that the present evidence does not cover.

## Limitations

The limitations are substantial and should be stated plainly. First, the evidence is
simulator-bounded. All results come from a controlled Isaac Sim study, not from real-
robot execution, so the paper should not imply deployment readiness or real-world
safety. Second, the task scope is deliberately small. The study covers Block A only,
with two task families, navigation and tabletop manipulation, and only the current
easy/shared and harder slices already present in the processed summaries. Third, the
paper studies two design axes only: prompt/interface structure and runtime
validation. It does not evaluate later roadmap axes such as memory, context
management, tool abstraction, randomization, or other `M7+` extensions, and it
should not borrow claims from those broader themes.

There are also experimental limits inside the current evidence base. The focused
prompt-only, runtime-only, and harder-manipulation slices are intentionally small and
should be interpreted as directional controlled evidence rather than large-scale
inferential studies. The processed outputs do not support confidence intervals,
significance tests, or multi-seed robustness claims. Backend coverage is also mixed
across slices: some broader navigation evidence includes a minimal Isaac-backed
subset, while the newer focused ablations are toy-backed to isolate the tested
design axes. Finally, the runtime-only ablation was built around recoverable invalid-
first-action probes. That makes it useful for isolating recovery value, but it does
not establish a comprehensive taxonomy of runtime failure handling.

## Restrained Future Work

The most natural future work is to extend the same controlled-study logic before
widening the paper's claims. That could include testing the same prompt/runtime
questions across additional backends, more scenes, or richer runtime policies while
preserving explicit contracts and slice-level comparisons. Separate studies could
also examine memory, context policies, tool abstraction, or randomization, but those
axes should remain future work rather than being implied by the present paper.
Likewise, any claim about broader embodied generalization, safety, or real-robot
transfer would require new evidence rather than extrapolation from the current
simulator-bounded results.
