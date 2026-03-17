# Results Draft

The results are organized around slice-level comparisons rather than package-level
bookkeeping totals. We use the frozen Block A closure as the umbrella evidence source
and use the prompt-only, runtime-only, cross-family, and harder-task summaries only
where they sharpen a specific comparison. Throughout, the main question is whether
prompt/interface structure and runtime validation change execution outcomes in the
tested setup, not how many runs were merged into the paper package. [Fig: main condition ordering]
[Table: final closure result summary]

## Main Prompt x Runtime Effect

The main effect is a stable qualitative ordering across the covered Block A slices.
Across navigation easy, manipulation easy, navigation harder, and the current harder
manipulation slice, the weakest condition is consistently `P0/R0`. The same frozen
package also shows the same recovery pattern whenever the weakest prompt is paired
with runtime validation: `P0/R1` succeeds where `P0/R0` fails, and the successful
conditions remain `P1/R0`, `P1/R1`, `P2/R0`, and `P2/R1`. This ordering is the core
result because it appears in the main easy cross-family comparisons and survives both
harder slices rather than depending on a single narrow task subset.

The same results also show that prompt/interface structure and runtime validation play
different roles. In the easy cross-family summary, both navigation and manipulation
assign all invalid-action failures to the `P0` cells, while the structured prompt
conditions `P1` and `P2` eliminate invalid actions in those shared easy comparisons.
Within the successful structured conditions, `P2` is not weaker than `P1` on success
but it uses fewer planner/tool calls in both families. The easy cross-family summary
shows this efficiency gap directly: in navigation, average planner/tool calls drop
from `4.875/4.875` under `P1` to `3.875/3.875` under `P2`; in manipulation, they
drop from `10.0/10.0` to `8.0/8.0`. The broader frozen closure therefore supports a
compact reading of the main effect: the bare minimal interface is fragile, runtime
validation can recover that fragility, and the brief self-check can lower workload
once a structured interface is already in place. [Fig: planner/tool overhead]

## Prompt-only and Runtime-only Ablations

### Runtime-only ablation

The runtime-only ablation shows that runtime validation has independent recovery value
when prompt structure is held fixed. With `P1` fixed across two navigation tasks and
two manipulation tasks, moving from `R0` to `R1` raises success from `2/4` to `4/4`.
The mechanism is important: the improvement is not caused by fewer invalid attempts.
Invalid-action runs remain `2` under both runtimes, but successful invalid-action
recoveries rise from `0` to `2` once validation and a single retry are enabled. The
same direction appears in each family separately, with navigation rising from `0.5`
to `1.0` success and manipulation rising from `0.5` to `1.0`. This slice therefore
supports a specific interpretation of `R1`: its value in the current study is
recovery of fragile but recoverable executions, not a broad proof that runtime design
dominates prompting in all settings. [Fig: invalid actions and recovery]
[Table: focused ablation summary]

### Prompt-only ablation

The prompt-only ablation shows that prompt/interface structure has independent value
when the runtime is held fixed at `R0`. Under the minimal direct-action prompt,
`P0/R0` fails on all `4/4` evaluated tasks and accumulates `4` total invalid actions.
Under the structured tool-call conditions, both `P1/R0` and `P2/R0` succeed on `4/4`
tasks and reduce invalid actions to zero. This means that the structured interface
itself changes the failure mode: the failures seen in the weakest condition do not
persist once the planner is required to produce dispatchable tool calls.

The same prompt-only slice also isolates the efficiency role of `P2`. While `P1/R0`
and `P2/R0` share the same success profile, average planner/tool calls fall from
`7.5/7.5` under `P1` to `6.0/6.0` under `P2`. The family-level breakdown preserves
the same relation: navigation drops from `5.0/5.0` to `4.0/4.0`, and manipulation
drops from `10.0/10.0` to `8.0/8.0`. In this controlled slice, the brief self-check
does not create a new success regime; instead, it makes the already strong structured
interface more execution-efficient. [Fig: invalid actions and recovery]
[Fig: planner/tool overhead] [Table: focused ablation summary]

## Cross-family Consistency

The cross-family evidence shows that the direction of the effects is consistent across
navigation and manipulation within the covered scope. In the shared easy slice, both
families exhibit the same success ordering: `P0/R0` fails, `P0/R1` recovers, and all
structured conditions remain successful. Both families also locate invalid actions in
the `P0` conditions rather than in `P1` or `P2`. The absolute workload differs by
family, with manipulation requiring more planner/tool calls than navigation, but the
qualitative ranking remains aligned.

The focused ablations repeat that pattern instead of contradicting it. In the
prompt-only slice, both families move from invalid-action failures under `P0/R0` to
full success under `P1/R0` and `P2/R0`, and both show lower planner/tool calls for
`P2` than for `P1`. In the runtime-only slice, both families move from `0.5` to
`1.0` success when `R1` is added to fixed `P1`, with the gain again coming from
recovery of invalid-first-action probes. These replications matter because they show
that the paper's main claims do not depend on only one task family. At the same time,
the claim should remain narrow: the paper establishes consistency across the covered
navigation and manipulation slices, not across arbitrary domains or embodiments.
[Table: final closure result summary]

## Harder-task Robustness

The harder-task slices increase planner/tool workload without changing the condition
ordering. In the navigation harder slice summarized in the frozen package, the same
success ranking as the easy slice is preserved, but every successful cell except
`P0/R0` requires more planner/tool calls than its easy counterpart. The master
summary reports a uniform increase of `2.931818` planner calls and `2.931818` tool
calls for the successful navigation cells when moving from the easy to the harder
slice. This pattern argues against a rank-reversal story and instead supports a
cost-amplification reading.

The harder manipulation slice shows the same behavior with direct family-specific
evidence. `P0/R0` remains the worst cell and fails on all `3/3` harder manipulation
tasks. `P0/R1` recovers those tasks and succeeds on `3/3`, using three retries across
the slice. `P1` and `P2` remain fully successful under both runtimes. The workload,
however, rises relative to the easy manipulation pilot, and `P2` keeps its efficiency
edge over `P1` under both runtimes: average planner/tool calls fall from
`11.666667/11.666667` for `P1` to `9.666667/9.666667` for `P2`. Taken together, the
current harder navigation and harder manipulation slices support the same conclusion:
harder tasks amplify execution burden, but they do not change the qualitative ordering
of prompt/runtime conditions in the tested setup. [Fig: planner/tool overhead]
[Table: final closure result summary]
