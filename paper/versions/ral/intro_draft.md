# Introduction Draft

Embodied agents often fail at the boundary between planning and execution. In
navigation and manipulation tasks, a planner can produce a seemingly plausible next
step while still emitting an action or tool call that the executor cannot dispatch as
issued. These failures are not only high-level reasoning errors; they also reflect
how the planner is asked to express actions, how the runtime checks those outputs,
and whether the system can recover from an invalid first attempt. For embodied-agent
systems, these interface and runtime decisions are practical design choices, but
their effects are often harder to isolate than model quality itself.

This paper focuses on that systems question in a controlled Isaac Sim setting. Recent
embodied-agent work increasingly emphasizes larger agents, broader benchmarks, or
richer capability taxonomies. Those directions are valuable, but they also make it
easy to blur together model capability, environment coverage, and execution-runtime
design. We instead study a narrower question: when the simulator setting and task
families are held fixed, how much do prompt/interface structure and lightweight
runtime validation affect invalid actions, recovery, success, and planner/tool
overhead?

We evaluate two task families, navigation and tabletop manipulation, using the
current Block A task matrix in Isaac Sim. The study compares three prompt/interface
variants: a minimal direct-action prompt (`P0`), a structured tool-call prompt
(`P1`), and a structured tool-call prompt with a brief self-check (`P2`). It also
compares two runtime variants: a bare runtime with no validation and no retry
(`R0`), and runtime validation with a single retry (`R1`). This scope is deliberate.
The paper does not attempt to cover later roadmap axes such as context policies,
memory, skill abstraction, randomization, or real-world deployment. Instead, it uses
a unified execution contract and a small set of consistent metrics to isolate two
design dimensions that directly govern whether planner outputs can be executed
reliably.

The results show a stable and practically meaningful ordering. Across the covered
navigation and manipulation slices, the weakest condition is consistently `P0/R0`.
Adding runtime validation to that fragile interface recovers runs that would
otherwise terminate on invalid actions. When runtime is held fixed, structured
tool-call prompting removes the invalid-action failures seen under the minimal
direct-action prompt. Within the structured variants, the brief self-check in `P2`
preserves the strong success profile of `P1` while reducing planner/tool calls in the
tested prompt-only and harder-manipulation slices. The same qualitative ordering
holds across both task families, and the current harder-task evaluations increase
planner/tool workload without reversing that ordering. [Fig: main condition ordering]
[Fig: invalid actions and recovery] [Fig: planner/tool overhead]

These findings support a controlled systems view of embodied-agent execution. The
paper does not claim a new model, benchmark supremacy, or broad generalization
across environments and robots. Instead, it argues that two modest design choices,
output structure at the planner interface and lightweight runtime validation before
dispatch, materially affect whether the same task specification is executed
cleanly, recovered after failure, or completed with lower overhead in the tested
setup.

This paper makes the following contributions:

1. It presents a controlled Isaac Sim study that isolates two embodied-agent
   execution design axes, prompt/interface structure and lightweight runtime
   validation, across navigation and tabletop manipulation tasks.
2. It provides evidence that structured prompt/interface design sharply reduces
   invalid actions and improves execution reliability relative to a minimal
   direct-action prompt in the current Block A setting.
3. It shows that runtime validation with a single retry has independent recovery
   value when prompt structure is held fixed, converting recoverable invalid-action
   runs into successful executions in both covered task families.
4. It identifies a compact design lesson from the tested setup: a brief self-check
   can retain the strong success profile of structured tool calls while reducing
   planner/tool workload, and harder tasks amplify workload without changing the
   qualitative condition ordering.
