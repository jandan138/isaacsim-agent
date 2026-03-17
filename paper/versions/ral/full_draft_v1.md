# A Controlled Study of Planner-to-Executor Contract Design and Runtime Validation for Embodied-Agent Execution in Isaac Sim

## Abstract

We present a controlled systems study of embodied-agent execution in Isaac Sim
that isolates two design axes at the planner/executor boundary:
planner-to-executor contract design and lightweight runtime validation. Across
navigation and tabletop manipulation tasks, we compare an under-specified
direct-action contract (`P0`), a typed tool-call contract (`P1`), and the same
typed contract with a brief self-check (`P2`), under either bare dispatch
(`R0`) or validation with a single retry (`R1`). In the fixed-runtime
action-interface ablation, `P0/R0` fails on all four evaluated tasks, while
`P1/R0` and `P2/R0` succeed on all four and eliminate invalid actions. In the
fixed-contract runtime-only ablation, adding validation and one retry raises
success from `2/4` to `4/4` by converting invalid-first-action runs into
successful recoveries. Across the broader evaluation slices, the same ordering
remains stable: `P0/R0` is weakest, `P0/R1` recovers, `P1` and `P2` remain
strong, and `P2` is associated with lower planner/tool overhead than `P1` in
the covered comparisons. The contribution is controlled empirical evidence
that explicit action interfaces and lightweight runtime checks are meaningful
systems levers for embodied-agent execution in the tested Isaac Sim setting.

## 1. Introduction

Embodied-agent systems often fail at the boundary between planning and
execution. A planner can identify the right task-level intention and still emit
an action name or argument structure that the executor cannot dispatch. When
that happens, the failure is not only a high-level planning error. It is also
an architectural failure of the planner-to-executor contract, of the action
interface that mediates the handoff, and of the runtime policy that decides
whether a bad first emission should terminate the run or be repaired.

This execution boundary is easy to overlook in current embodied-agent
literature, where broader benchmarks, richer capability taxonomies, and
stronger models often dominate the narrative. Those directions matter, but they
also make it hard to isolate execution-stack design from model quality or task
coverage. We therefore ask a narrower robotics-systems question: when the
simulator setting and task families are held fixed, how much do
planner-to-executor contract design and lightweight runtime validation affect
invalid actions, recovery, success, and planner/tool overhead?

We study two task families in Isaac Sim: language-conditioned navigation and
tabletop manipulation. The matrix compares three contract variants: an
under-specified direct-action contract (`P0`), a typed tool-call contract
(`P1`), and the same typed contract with a brief self-check (`P2`). It also
compares two runtime variants: bare dispatch (`R0`) and validation with a
single retry (`R1`). These variants are implemented through different planner
instructions, but the manipulated system variables are the executable interface
presented to the executor and the runtime policy applied before dispatch.

The findings are stable across the covered slices. `P0/R0` is consistently the
weakest condition; adding runtime validation to that weak contract recovers
fragile invalid-first-action failures; explicit contracts `P1` and `P2`
eliminate the invalid-action failure mode in the fixed-`R0` slice; and `P2` is
associated with lower planner/tool overhead than `P1` in the covered
comparisons. Harder tasks increase planner and tool activity without reversing
that ordering. The paper is limited to this controlled simulator study and
argues for bounded execution-design lessons rather than a new model or benchmark
claim.

This paper makes three contributions:

1. It presents a controlled Isaac Sim study that isolates two execution-design
   axes, planner-to-executor contract design and lightweight runtime
   validation, across navigation and tabletop manipulation tasks.
2. It provides evidence that typed tool-call contracts reduce invalid actions
   relative to an under-specified direct-action contract, while runtime
   validation with a single retry converts recoverable invalid first actions
   into successful executions in both covered task families.
3. It extracts a compact architectural lesson from the tested setup: contract
   design, runtime validation, and a brief planner-side self-check are separate
   systems levers that shape reliability and planner/tool overhead without
   changing the underlying task matrix.

## 2. Related Work

### 2.1 Embodied and LLM-Based Robot Planning

Recent embodied and language-conditioned robot-planning work studies how
high-level language intent is translated into executable robot behavior in
simulation or on robots, including closed-loop language feedback, embodied
multimodal models, vision-language-action policies, model-based language
grounding, and systems-first integration pipelines such as Inner Monologue
(Huang et al., 2022), PaLM-E (Driess et al., 2023), RT-2 (Brohan et al.,
2023), VoxPoser (Huang et al., 2023), and OK-Robot (Liu et al., 2024). This
includes language-conditioned skill selection, code-generating control, and
program-like robot planning directions exemplified by SayCan (Ahn et al.,
2022), Code as Policies (Liang et al., 2022), and ProgPrompt (Singh et al.,
2022). That literature makes planner quality visible, but it often leaves less
room to isolate what happens at the boundary between planner output and
dispatch. Our paper is narrower: it holds the Isaac Sim setting fixed and
studies how planner-to-executor contract design changes invalid actions,
recovery, success, and planner/tool overhead.

### 2.2 Execution Contracts, Runtime Validation, and Robotics Middleware

A second line of work addresses execution architecture rather than only planner
quality. Relevant threads include ROS 2 middleware and action semantics
(Macenski et al., 2022; Biggs et al., 2019/2020), planning frameworks such as
PlanSys2 (Martin et al., 2021), behavior-tree execution stacks and libraries
such as BehaviorTree.CPP (Colledanchise and Ogren, 2018;
BehaviorTree.CPP documentation), and task-and-motion planning interfaces such
as PDDLStream and the broader TAMP literature (Garrett et al., 2020; Garrett
et al., 2021). The shared intuition is that planner outputs should not
be treated as executable by default; they need an explicit interface to the
execution stack. The present study is closest to that execution-boundary view.
Its runtime layer is intentionally lightweight: `R1` validates an emitted
action or tool call against the active contract and allows one repair attempt.
The contribution is therefore evidence about a small validation-and-retry
mechanism in a controlled simulator setting, not a claim of a complete
middleware stack or end-to-end safety case.

### 2.3 Controlled Design Studies and Broader Evaluations

Methodologically, the paper favors a small controlled matrix over benchmark
breadth. Broader embodied-agent evaluations such as EmbodiedBench, IS-Bench,
and the Isaac Sim-based Mind and Motion Aligned benchmark are valuable because
they expose long-horizon execution difficulty, safety failures, or integrated
planning-and-control behavior across larger task sets or evaluation matrices
(Yang et al., 2025; Lu et al., 2025; Kachaev et al., 2025). By varying only
the action interface and runtime validation policy within a fixed Isaac Sim
setting, we instead use a narrower study design to attribute differences in
invalid actions, recovery, success, and planner/tool overhead to explicit
execution-design choices. This complements broader embodied-agent evaluations
rather than competing with them.

## 3. Study Design and Experimental Setup

### 3.1 Controlled Isaac Sim Setting

The study uses a common Isaac Sim execution architecture across navigation and
tabletop manipulation. The navigation family contains language-driven
mobile-goal tasks in indoor scenes. The manipulation family contains tabletop
manipulation tasks that require object identification, grasping, transfer, and
placement. The main comparison uses a shared easy slice across both
families, with additional harder navigation and harder manipulation slices to
test whether increased task burden changes the qualitative ordering or mainly
amplifies planner/tool overhead.

All conditions share the same high-level handoff:

1. The planner receives the current task state and the exposed tool set.
2. The planner emits an action request.
3. Under `R0`, the request is dispatched as issued; under `R1`, the runtime
   validates it against the active contract and allows one repair attempt on
   failure.
4. The executor runs only requests that satisfy the active dispatch interface.

The dispatch vocabulary is family-specific but explicit. Navigation exposes
`get_robot_state`, `get_goal_state`, and `navigate_to`. Tabletop manipulation
exposes `get_gripper_state`, `get_object_state`, `get_target_state`, and
`scripted_pick_place_step`. This distinction matters because the study is not
asking whether the planner can describe the task in natural language. It is
asking whether the planner can hand the executor a dispatchable request under a
specified interface.

### 3.2 Contract and Runtime Variants

The controlled matrix is summarized in [Table: experimental design summary].
`P0` uses an under-specified direct-action contract, allowing the planner to
emit a task-level next action without binding it to the executor's tool
namespace. `P1` uses a typed tool-call contract, requiring the planner to
choose one exposed tool and provide dispatchable arguments. `P2` keeps the same
typed tool-call contract and adds a brief planner-side self-check before
emission.

`R0` is a bare-dispatch runtime: it does not perform pre-dispatch validation or
offer a repair path. `R1` is a validate-and-retry runtime: it checks the
emitted request against the active contract and, on failure, returns the
validation error to the planner and allows one retry. Contract and runtime
therefore play distinct roles. Contract design can prevent invalid actions at
the source, while runtime validation can recover some contract violations that
still slip through.

### 3.3 Metrics and Evaluation Protocol

Success rate is the primary task outcome. An `invalid action` is an emitted
action or tool call that violates the active contract and therefore cannot be
dispatched as issued. A `recovery` is a run that contains an invalid action but
still ends successfully after runtime handling. Retries capture the extra
repair work used in `R1`. Planner calls and tool calls together define
`planner/tool overhead`, which is the paper's efficiency proxy.

The paper draws its quantitative comparisons from the main factorial results
plus targeted runtime-only, action-interface-only, and harder-task summaries.
The final closure summary provides the canonical aggregate view, while the
slice-specific summaries support the ablations and the failure-case
interpretation. [Table: final closure result summary]

## 4. Results

Across the aggregated evaluation slices, the same contract x runtime ordering
recurs:
`P0/R0` is the weakest condition, `P0/R1` recovers, and the explicit-contract
conditions remain strong.

### 4.1 Main Contract x Runtime Effect

The main effect is a stable qualitative ordering across navigation easy,
tabletop manipulation easy, harder navigation, and harder manipulation. In each
slice, `P0/R0` is the weakest cell. Pairing the same under-specified contract
with `R1` changes the outcome: `P0/R1` succeeds where `P0/R0` fails, while
`P1/R0`, `P1/R1`, `P2/R0`, and `P2/R1` remain strong. This repeated pattern
holds across both task families and persists as tasks become harder. [Fig: main
condition ordering]
[Table: final closure result summary]

The same comparison separates the roles of contract design and runtime
validation. Invalid-action failures are concentrated in the `P0` cells, showing
that loose task-level verbs are brittle at the planner/executor boundary. Once
the planner is forced into a typed tool namespace, the dominant failure mode
disappears in the covered fixed-`R0` slice. Within the successful structured
conditions, `P2` matches `P1` on success while showing lower planner/tool
overhead on the shared easy slice and the harder manipulation slice. We
interpret that pattern as an efficiency association within already-strong
contracts, not as evidence of a new success regime. [Fig: planner/tool
overhead]

The direction is also consistent across families. Navigation and tabletop
manipulation both place the weakest behavior in `P0/R0`, both recover under
`P0/R1`, and both preserve the lower-overhead `P2` pattern where `P1` and
`P2` are directly compared.

### 4.2 Action-Interface and Runtime-Only Ablations

The targeted ablations use different easy-task subsets: the runtime-only slice
deliberately includes recoverable invalid-first-action probes under fixed `P1`,
whereas the action-interface slice compares clean easy tasks under fixed `R0`.
Together they isolate the two design axes without changing the overall
execution-design framing.

With the contract fixed at `P1`, moving from `R0` to `R1` raises success from
`2/4` to `4/4` across two navigation tasks and two tabletop manipulation tasks.
The mechanism is recovery, not suppression: invalid-action runs remain `2`
under both runtimes, but successful invalid-action recoveries rise from `0` to
`2` once validation and one retry are enabled. The same direction appears in
each family separately, with navigation and manipulation each moving from
`0.5` to `1.0` success in this slice. [Fig: invalid actions and recovery]
[Table: focused ablation summary]

With runtime fixed at `R0`, `P0/R0` fails on all `4/4` evaluated tasks and
accumulates `4` total invalid actions, whereas `P1/R0` and `P2/R0` succeed on
all `4/4` tasks and reduce invalid actions to zero. This establishes an
independent contract effect: once the planner must emit dispatchable tool
calls, the invalid-action failures that dominate the under-specified interface
disappear in this slice. The same comparison also shows the narrower `P2`
effect: `P1/R0` and `P2/R0` have the same success profile, but average planner
and tool calls each fall from roughly `7.5` to `6.0`. [Fig: invalid actions
and recovery] [Fig: planner/tool overhead] [Table: focused ablation summary]

The failure traces explain what goes wrong under `P0`. In navigation, failing
`P0` runs repeatedly emit the unsupported tool name `move_to_goal`; in
tabletop manipulation, they emit `move_object`. Both are semantically plausible
task verbs, but the executor accepts `navigate_to` and
`scripted_pick_place_step` instead. `R1` helps because the runtime catches the
unknown tool before dispatch, returns a validation error, and allows a
corrected retry. The runtime does not erase the contract violation; it turns a
terminating handoff failure into a recoverable one.

### 4.3 Harder-Task Robustness

The harder-task slices increase planner/tool overhead without changing the
condition ordering. In harder navigation, the same ranking as the easy slice is
preserved, while successful cells require roughly three additional planner or
tool calls per run. In harder tabletop manipulation, `P0/R0` fails on all
`3/3` tasks, `P0/R1` recovers all `3/3` with one retry per task, and `P1/P2`
remain fully successful under both runtimes. [Table: final closure result
summary]

The `P1` versus `P2` efficiency relation also survives the harder manipulation
setting. `P2` remains about two planner calls and two tool calls per run below
`P1` under both runtimes while maintaining the same success profile. The harder
slices therefore look like cost amplification rather than rank reversal: tasks
become busier, but the contract and runtime ordering stays intact. [Fig:
planner/tool overhead]

## 5. Discussion and Limitations

### 5.1 Discussion

The clearest lesson is that planner-to-executor contract design is a systems
lever, not a presentation detail. Under the under-specified contract, the
planner often knows the task family but still speaks in a vocabulary the
executor cannot dispatch. Explicit contracts move that ambiguity out of ad hoc
interpretation and into a declared interface.

Runtime validation plays a complementary role. It does not replace a
well-specified contract, but it can intercept a bad first emission, surface a
concrete error, and recover the run with minimal additional machinery. That
pattern matters for embodied execution stacks that preserve
planner/executor separation, including middleware-style action interfaces and
guarded execution policies.

At a higher level, the studied boundary maps cleanly onto execution
architectures already familiar in robotics. The contract specifies the form of
a dispatchable request in much the same way that ROS 2 actions expose explicit
goal, feedback, and result semantics, while runtime validation decides whether
a malformed request should be rejected before execution (Biggs et al.,
2019/2020; Macenski et al., 2022; Martin et al., 2021). The same separation
appears in behavior-tree and TAMP systems: contract checks act like
precondition guards on callable nodes or operators, and runtime validation acts
like an execution guard that determines whether a proposed action can continue
to the executor interface (Colledanchise and Ogren, 2018;
BehaviorTree.CPP documentation; Garrett et al., 2020; Garrett et al., 2021).

The `P2` pattern suggests a second, narrower lesson. In the covered slices, a
brief planner-side self-check leaves the success profile unchanged while
reducing planner/tool overhead. The bounded interpretation is not that
self-checks are universally best, but that contract design and runtime design
remain separable levers once the callable interface is explicit.

### 5.2 Limitations

The conclusions are bounded to a controlled Isaac Sim study. The evidence is
simulator-based, covers two task families, and is limited to the current easy
and harder slices rather than a broad execution benchmark.

The action-interface-only and runtime-only ablations are compact mechanism
checks rather than broad sweeps, and backend coverage differs across slices.
The runtime-only ablation is especially specific: it is designed around
recoverable invalid-first-action probes, so its strongest claim is about
lightweight repair at that boundary.

These limits still allow a concrete systems conclusion. In the tested setting,
planner-to-executor contracts and lightweight runtime safeguards materially
change invalid actions, recovery, and planner/tool overhead. The next empirical
extension should preserve the same explicit boundary while widening scenes,
backends, and execution stacks.

## 6. Conclusion

This paper presents a controlled systems study of planner-to-executor contract
design and runtime validation for embodied-agent execution in Isaac Sim. Across
navigation and tabletop manipulation tasks, the same qualitative ordering
remains stable: `P0/R0` is weakest, `R1` recovers fragile invalid-first-action
cases, and the explicit-contract conditions `P1` and `P2` remain strong across
the covered slices.

The failure analysis shows why. The dominant errors are contract violations
rather than generic task collapse. Explicit contracts prevent those failures at
the source, runtime validation repairs some of the ones that remain, and a
brief self-check can reduce planner/tool overhead within an already strong
contract. For embodied-agent execution stacks, the main lesson is straightforward:
contract design and lightweight runtime safeguards belong in the architecture,
not as afterthoughts.
