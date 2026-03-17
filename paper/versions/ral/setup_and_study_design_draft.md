# Experimental Setup and Study Design Draft

## Experimental Setup

This paper studies embodied-agent execution in a controlled Isaac Sim setting rather
than as a broad agent benchmark. The environment is fixed to the current Block A task
matrix, and the paper asks how two execution-stack design axes, planner-to-executor
contract design and lightweight runtime validation, affect invalid actions, recovery,
success, and planner/tool overhead under that shared setup.

The study covers two task families. The navigation family contains language-driven
mobile-goal tasks in indoor scenes. The manipulation family contains tabletop
pick-and-place tasks that require object identification, grasping, transfer, and
placement. We use `manipulation` as the paper-facing family name even where raw
artifacts store the family as `pick_place`. The easy/shared slice provides the
cleanest cross-family comparison, while the current harder navigation and harder
manipulation slices test whether increased task burden changes the ordering or mainly
amplifies workload.

All conditions share the same high-level execution architecture:

1. the planner receives the task state plus the currently exposed tool set
2. the planner emits an action request
3. the runtime checks whether that request matches the active contract
4. the executor dispatches only requests that satisfy the contract

The dispatch vocabulary is family-specific but explicit. Navigation exposes
`get_robot_state`, `get_goal_state`, and `navigate_to`. Manipulation exposes
`get_gripper_state`, `get_object_state`, `get_target_state`, and
`scripted_pick_place_step`. This separation matters because the paper is not asking
whether the planner can describe the task in natural language. It is asking whether
the planner can hand the executor a dispatchable request under a specified
interface.

An `invalid action` is an emitted action or tool call that violates the active
contract and therefore cannot be dispatched as issued. A `recovery` is a run that
contains an invalid action but still ends successfully after runtime handling.
Success rate is the primary task outcome. Invalid actions localize failures at the
planner/executor boundary. Retries capture the extra repair work used in `R1`.
Planner calls and tool calls together define `planner/tool overhead`, which is the
paper's efficiency proxy. [Table: experimental design summary]

## Study Design

The variant inventory is intentionally compact and is best treated as a design table
rather than as long-form prose:

| Axis | Variant | Paper-facing label | System meaning |
| --- | --- | --- | --- |
| Contract | `P0` | under-specified direct-action contract | planner outputs a task-level next action without being forced into the executor's exposed tool namespace |
| Contract | `P1` | typed tool-call contract | planner must choose one exposed tool and provide dispatchable arguments |
| Contract | `P2` | typed tool-call contract with a brief self-check | same dispatch contract as `P1`, plus a short planner-side check before emission |
| Runtime | `R0` | bare dispatch runtime | no pre-dispatch validation and no repair path |
| Runtime | `R1` | validate-and-retry runtime | runtime checks the emitted request against the active contract and allows one planner retry on failure |

`P0`, `P1`, and `P2` are still the same experimental conditions used in the
existing artifacts; the reframing here changes the paper language, not the
underlying experiment. The main difference across `P0` versus `P1/P2` is therefore
not merely prompt style. It is whether the planner is allowed to speak in loose
task-level action names or is required to speak in the executor's dispatchable tool
vocabulary.

`R0` and `R1` are runtime validation policy variants. `R0` leaves the handoff
unchecked. `R1` validates the emitted request against the active contract before
dispatch. If the request is invalid, `R1` returns the validation error to the
planner and allows one retry. This makes the runtime axis architecturally distinct
from the contract axis: contract design can prevent invalid actions at the source,
while runtime validation can recover some contract violations that still slip
through.

The evidence is organized into three analysis blocks. First, the main effect uses the
final Block A closure to establish the stable qualitative ordering across navigation,
manipulation, and the current harder slices. Second, the ablations isolate the two
design axes: fixed `P1` for runtime-only recovery value, and fixed `R0` for
action-interface value plus the efficiency role of the `P2` self-check. Third, the
harder-task comparisons test whether increasing task burden changes condition
ordering or mainly increases workload. This setup should be read as a controlled
systems study of execution architecture, not as a claim about a general embodied
agent stack.
