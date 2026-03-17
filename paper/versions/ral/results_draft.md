# Results Draft

Across the covered Block A slices, the same execution ordering recurs: `P0/R0` is
the weakest condition, `P0/R1` recovers, and the structured-contract conditions
remain strong. The result is best read as an execution-architecture effect rather
than as package bookkeeping. [Fig: main condition ordering]
[Table: final closure result summary]

## Main Effect

The main effect is a stable qualitative ordering across navigation easy,
manipulation easy, navigation harder, and the current harder manipulation slice.
`P0/R0` is consistently the weakest condition. Pairing the same weak contract with
runtime validation changes the outcome: `P0/R1` succeeds where `P0/R0` fails, and
the strong conditions remain `P1/R0`, `P1/R1`, `P2/R0`, and `P2/R1`. This ordering
is the core result because it appears in both task families and survives the harder
slices rather than depending on one narrow subset.

The same comparison also separates the roles of contract design and runtime
validation. In the shared easy cross-family view, invalid-action failures are
concentrated in the `P0` cells, while the typed tool-call conditions `P1` and `P2`
remove those failures. Within the successful structured conditions, `P2` is not
weaker than `P1` on success and shows lower planner/tool overhead on the shared easy
slice. That pattern is not large enough to support a broad efficiency claim, but it
is consistent across the covered slices in which `P1` and `P2` are directly
compared. [Fig: planner/tool overhead]

The direction is also consistent across navigation and manipulation. Both families
place invalid actions in the weak contract condition, both recover under `P0/R1`,
and both preserve the `P2` lower-overhead pattern relative to `P1` on the covered
easy slice.

## Ablations

### Runtime-only ablation

The runtime-only ablation shows that runtime validation has independent recovery
value when the action interface is held fixed. With `P1` fixed across two navigation
tasks and two manipulation tasks, moving from `R0` to `R1` raises success from
`2/4` to `4/4`. The mechanism matters. The gain is not caused by fewer invalid
attempts: invalid-action runs remain `2` under both runtimes, but successful
invalid-action recoveries rise from `0` to `2` once validation and a single retry
are enabled. The same direction appears in each family separately, with navigation
and manipulation both moving from `0.5` to `1.0` success. This slice supports a
specific interpretation of `R1`: its value in the current study is recovery of
fragile but recoverable contract violations. [Fig: invalid actions and recovery]
[Table: focused ablation summary]

### Action-interface ablation

The fixed-`R0` action-interface ablation shows that contract design has independent
value even without runtime repair. Under the under-specified direct-action contract,
`P0/R0` fails on all `4/4` evaluated tasks and accumulates `4` total invalid
actions. Under the typed tool-call conditions, both `P1/R0` and `P2/R0` succeed on
`4/4` tasks and reduce invalid actions to zero. The failure mode therefore changes
at the architecture boundary: once the planner is required to emit dispatchable tool
calls, the invalid-action failures that dominate `P0` disappear in this slice.

The same slice also isolates the efficiency role of `P2`. While `P1/R0` and
`P2/R0` share the same success profile, average planner/tool calls fall from `7.5`
to `6.0`. In this controlled comparison, the brief self-check does not create a new
success regime; it lowers planner/tool workload within an already strong structured
contract. [Fig: invalid actions and recovery]
[Fig: planner/tool overhead] [Table: focused ablation summary]

### Failure-case analysis

The invalid actions in `P0` are not arbitrary. Existing run summaries and traces
show the same family-specific contract mismatches repeatedly. In navigation, failing
`P0` runs emit the unsupported dispatch name `move_to_goal`. In manipulation,
failing `P0` runs emit `move_object`. Both outputs are semantically plausible task
verbs, but neither belongs to the executor's exposed tool set, which expects
`navigate_to` in navigation and `scripted_pick_place_step` in manipulation. The
architectural issue is therefore under-specification at the planner/executor
boundary: the planner expresses task intent in its own vocabulary, while the
executor only accepts a named tool interface.

The runtime-only probe traces show why `R1` helps. In both families, the first
unsupported tool name is caught before dispatch, the runtime returns a validation
error, and the retry produces a valid exposed tool such as `get_robot_state` or
`get_object_state`, after which the run proceeds to success. `R1` does not remove
the initial contract violation; it converts what would be a dispatch-time
termination into a recoverable handoff. This is why the runtime-only gain is best
understood as execution-time repair value rather than as a general replacement for a
well-specified interface.

## Harder-task Robustness

The harder-task slices increase planner/tool workload without changing the condition
ordering. In the harder navigation slice, the same success ranking as the easy slice
is preserved, but successful cells require roughly three additional planner/tool
calls per run. The harder manipulation slice shows the same behavior with direct
family-specific evidence: `P0/R0` fails on all `3/3` harder tasks, `P0/R1` recovers
them with three retries across the slice, and `P1` and `P2` remain fully
successful under both runtimes.

The efficiency relation between `P1` and `P2` also survives the harder manipulation
setting. `P2` remains lower-overhead than `P1` by about two planner/tool calls per
run under both runtimes. Taken together, the current harder navigation and harder
manipulation slices support the same conclusion: harder tasks amplify execution
burden, but they do not change the qualitative ordering of contract and runtime
conditions in the tested setup. [Fig: planner/tool overhead]
[Table: final closure result summary]
