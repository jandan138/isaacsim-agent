# Conclusion Draft

This paper presents a controlled systems study of planner-to-executor contract
design and runtime validation for embodied-agent execution in Isaac Sim. Across
navigation and tabletop manipulation tasks, the same qualitative ordering
remains stable: the underspecified `P0/R0` condition is weakest, `R1` recovers
fragile invalid-first-action cases, and the explicit-interface conditions `P1`
and `P2` remain strong across the covered slices.

The failure analysis clarifies why. The dominant invalid actions are not generic
task failures but contract violations, where the planner emits plausible but
non-dispatchable tool names. Explicit action interfaces prevent those failures
at the source, while runtime validation catches and repairs recoverable
violations at execution time. `P2` further suggests that a brief planner-side
self-check can lower planner/tool overhead once the interface is explicit.

The contribution is a robotics-systems lesson for planner/executor separation
and execution stacks: in the tested Block A Isaac Sim setting, contract design
and lightweight runtime safeguards matter.
