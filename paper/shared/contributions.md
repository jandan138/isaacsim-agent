# Reusable Contributions

These contribution bullets are written to survive venue changes. Keep them aligned
with `shared/core_claim.md` and `shared/findings.md`.

1. A controlled Isaac Sim study that isolates two embodied-agent execution design
   axes, planner-to-executor contract design (`P0`, `P1`, `P2`) and lightweight
   runtime validation (`R0`, `R1`), across navigation and tabletop manipulation
   tasks.
2. Evidence that structured action interfaces sharply reduce invalid actions and
   improve execution reliability relative to an under-specified direct-action
   contract in the tested Block A setup.
3. Evidence that runtime validation with a single retry has independent recovery
   value when the action interface is held fixed, converting recoverable
   invalid-action runs into successful executions in both covered task families.
4. A compact design lesson from the tested setup: a brief self-check can retain the
   strong success profile of a typed tool-call contract while reducing planner/tool
   workload, and harder tasks increase workload without changing the qualitative
   condition ordering.

## Not contribution bullets

Do not turn the paper contributions into any of the following:

- a claim of a new embodied foundation model
- a full-framework claim covering the whole roadmap in `plan.md`
- a state-of-the-art benchmark claim
- a claim that the paper solves general embodied planning
