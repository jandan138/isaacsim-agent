# Introduction Draft

Embodied-agent systems often fail at the boundary between planning and execution. A
planner can generate a sensible task-level intention while still emitting an action
name or argument structure that the executor does not know how to dispatch. In that
case, the failure is not only a high-level planning error. It is also an
architectural failure of the contract between planner and executor, of the action
interface that mediates the handoff, and of the runtime policy that decides whether
an invalid first action should terminate the run or be repaired.

This paper studies that execution boundary in a controlled Isaac Sim setting. Recent
embodied-agent and robot-planning work increasingly emphasizes stronger models,
broader benchmarks, or richer capability taxonomies. Those directions matter, but
they also make it easy to blur together model quality, environment coverage, and
execution-stack design. We instead ask a narrower systems question: when the
simulator setting and task families are held fixed, how much do planner-to-executor
contract design and lightweight runtime validation affect invalid actions, recovery,
success, and planner/tool overhead?

We evaluate two task families, navigation and tabletop manipulation, using the
current Block A task matrix in Isaac Sim. The study compares three contract
variants: an under-specified direct-action contract (`P0`), a typed tool-call
contract (`P1`), and the same typed contract with a brief self-check (`P2`). It also
compares two runtime variants: bare dispatch with no validation or retry (`R0`), and
runtime validation with a single retry (`R1`). These variants are implemented
through different planner instructions, but the manipulated system variables are the
action interface presented to the executor and the runtime policy applied before
dispatch.

The results show a stable and practically useful ordering. Across the covered
navigation and manipulation slices, `P0/R0` is consistently the weakest condition.
Adding runtime validation to that weak interface recovers runs that would otherwise
terminate on invalid actions. When runtime is held fixed, typed tool-call contracts
remove the invalid-action failures seen under the under-specified direct-action
condition. Within the structured contract conditions, the brief self-check in `P2`
preserves the strong success profile of `P1` while showing lower planner/tool
overhead in the covered efficiency slices. The same qualitative ordering remains
visible across both task families and the current harder-task evaluations, which
increase workload without reversing condition order. [Fig: main condition ordering]
[Fig: invalid actions and recovery] [Fig: planner/tool overhead]

The paper stays within a simulator-bounded Block A study of these contract and
runtime choices. Its contribution is not a new model or a broad benchmark, but
controlled empirical evidence that modest changes at the planner/executor boundary
change whether the same task specification is executed cleanly, recovered after a
bad first action, or completed with lower overhead.

This paper makes the following contributions:

1. It presents a controlled Isaac Sim study that isolates two embodied-agent
   execution design axes, planner-to-executor contract design and lightweight
   runtime validation, across navigation and tabletop manipulation tasks.
2. It provides evidence that typed action interfaces remove the invalid-action
   failures seen under an under-specified direct-action contract, while runtime
   validation with a single retry converts recoverable invalid first actions into
   successful executions in both covered task families.
3. It extracts an architectural lesson from the tested setup: contract design,
   runtime validation, and a brief planner-side self-check are separate systems
   levers that shape reliability and planner/tool overhead without changing the
   underlying task matrix.
