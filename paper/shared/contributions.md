# Reusable Contributions

These contribution bullets are written to survive venue changes. Keep them aligned
with `shared/core_claim.md` and `shared/findings.md`.

1. A controlled Isaac Sim study that isolates two embodied-agent execution design axes, prompt/interface structure (`P0`, `P1`, `P2`) and lightweight runtime validation (`R0`, `R1`), across navigation and tabletop manipulation tasks.
2. Evidence that structured prompt/interface design sharply reduces invalid actions and improves execution reliability relative to a minimal direct-action prompt in the tested Block A setup.
3. Evidence that runtime validation with a single retry has independent recovery value when prompt structure is held fixed, converting recoverable invalid-action runs into successful executions in both covered task families.
4. A compact design lesson from the tested setup: a brief self-check can retain the strong success profile of structured tool calls while reducing planner/tool workload, and harder tasks increase workload without changing the qualitative condition ordering.

## Not contribution bullets

Do not turn the paper contributions into any of the following:

- a claim of a new embodied foundation model
- a full-framework claim covering the whole roadmap in `plan.md`
- a state-of-the-art benchmark claim
- a claim that the paper solves general embodied planning
