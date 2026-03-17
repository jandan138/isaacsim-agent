# Conclusion Draft

This paper presents a controlled systems study of embodied-agent execution in Isaac
Sim. Across navigation and tabletop manipulation tasks, the results show a stable
ordering: the weakest condition is the minimal direct-action prompt with the bare
runtime, runtime validation with a single retry recovers fragile executions that
would otherwise fail, and the structured tool-call conditions remain strong across
the covered slices.

The main design lesson is modest but useful. In the tested Block A setup,
prompt/interface structure affects whether planner outputs can be dispatched cleanly,
runtime validation affects whether invalid first attempts can be recovered, and a
brief self-check can lower planner/tool overhead once a structured interface is in
place. The current harder slices increase workload, but they do not change that
qualitative ordering.

These conclusions remain bounded to the present controlled study. The paper does not
claim a new model, a general embodied-agent benchmark, or real-robot deployment
evidence. Its contribution is controlled empirical evidence that small execution-
interface and runtime choices materially shape embodied-agent outcomes in the current
Isaac Sim setting.
