# Discussion and Limitations Draft

## Discussion

The clearest lesson from Block A is that planner-to-executor contract design is
a systems lever in its own right. The failure traces show that the weakest
condition is not dominated by a diffuse planning collapse. Instead, it fails
through a narrow contract-violation mode: the planner emits tool names such as
`move_to_goal` or `move_object` that are semantically plausible for the task
but not callable by the executor. That is an architecture-level failure. The
planner is not failing to recognize the task family; it is failing to speak the
executor's language. Explicit action interfaces matter because they move that
burden from ad hoc post hoc interpretation to a declared contract.

The runtime-only ablation shows the complementary role of runtime validation.
With `P1` fixed, `R1` raises success from `2/4` to `4/4` even though
invalid-action runs remain `2`. The benefit comes from intercepting a contract
violation, returning the validation error, and allowing one repair attempt. For
robotics execution stacks, that is a useful architectural pattern: lightweight
checking at the dispatch boundary can add robustness without collapsing planner
and executor into one module. The same idea is compatible with middleware-style
action interfaces, action-server boundaries, and behavior-tree-like guard
conditions, where execution-time validation protects the system from a bad
first emission without pretending to solve the entire planning problem.

`P2` suggests a second, narrower lesson. Once the planner is already bound to an
explicit tool vocabulary, a small planner-side self-check can reduce
planner/tool overhead without changing the success profile in the covered
slices. That pattern does not support a broad efficiency claim, but it does
suggest that some execution improvements come from refining the planner-side
contract rather than only adding downstream runtime machinery.

Taken together, the study argues for a layered view of embodied execution
architecture: specify the callable action interface clearly, validate emitted
actions before dispatch, and keep recovery lightweight but explicit. In
robotics terms, planner/executor separation is not just an implementation
convenience; it is a place where reliability can be designed.

## Limitations

The conclusions are bounded to a controlled Isaac Sim study. The evidence comes
from Block A only, covers two task families, and is limited to the current
easy/shared and harder slices. The paper therefore supports
execution-architecture lessons under controlled conditions, not broad claims
about other simulators, robots, or deployment settings.

The focused interface-only, runtime-only, and harder-manipulation slices are
small mechanism checks rather than broad surveys, and backend coverage differs
across slices because the package combines broader family summaries with
targeted controlled ablations. The runtime-only ablation is also centered on
recoverable first-step contract violations, so its strongest interpretation is
about lightweight repair at that specific boundary.

These limits do not remove the main result, but they do define where it should
travel next. The most useful follow-on work would extend the same
contract-and-validation study across additional backends, scenes, and execution
stacks while keeping the planner/executor boundary explicit.
