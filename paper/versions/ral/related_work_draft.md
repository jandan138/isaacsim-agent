# Related Work Draft

Placeholder citation note: citation markers such as `[RW1]` and `[RW2]` are
intentional placeholders only. They must be replaced with verified references in a
later literature-check pass and should not be treated as already confirmed
bibliography entries.

## Embodied-agent execution context

Recent work on language-conditioned and embodied-agent systems studies how agents
plan and act in simulated or robotic environments, often with increasing emphasis on
broader task suites, richer capability taxonomies, or larger benchmark packages
`[RW1]`, `[RW2]`, `[RW3]`, `[RW4]`. Related benchmark-oriented efforts similarly
highlight persistent brittleness in embodied execution, especially when planning must
be translated into executable actions under environment and tool constraints
`[RW5]`, `[RW6]`, `[RW7]`. That literature motivates the present paper, but it is
not the target shape of our contribution. We do not introduce a new model or a broad
benchmark. Instead, we hold the Isaac Sim setting fixed and ask a narrower systems
question: how much do prompt/interface structure and runtime validation change
invalid actions, recovery, success, and planner/tool overhead in a controlled task
matrix?

## Runtime checking, validation, and execution reliability

A second relevant line of work studies execution reliability, action validation, and
safety-adjacent runtime checks for embodied or robotic systems `[RW8]`, `[RW9]`,
`[RW10]`, `[RW11]`. The shared intuition is that planner outputs should not be
treated as executable by default; some contract is needed between generation and
dispatch. Our paper is closest to that execution-boundary view. However, the runtime
layer studied here is intentionally lightweight. `R1` performs runtime validation
against the active action or tool-call contract and allows a single retry after a
validation failure. The contribution is therefore evidence about a compact recovery
mechanism in a controlled simulator setting, not a claim of a full safety framework,
policy shield, or deployment-ready runtime stack.

## Controlled empirical design studies

This paper is also aligned with empirical systems studies that isolate a small number
of design axes instead of maximizing coverage breadth `[RW12]`, `[RW13]`, `[RW14]`.
That methodological choice matters for the present evidence base. By fixing the task
families and comparing only prompt/interface structure and runtime validation, the
study can directly attribute differences in invalid actions, recovery, success, and
planner/tool overhead to those execution-design choices within the covered slices.
This narrower scope complements larger embodied-agent evaluations rather than trying
to replace them. In that sense, the paper should be read as a controlled empirical
study of embodied-agent execution design in Isaac Sim: it uses a simulator-bounded
setting to extract specific system-design lessons, rather than to claim a generally
best agent or a universal benchmark ordering.
