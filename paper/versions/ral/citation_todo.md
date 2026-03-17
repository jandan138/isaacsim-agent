# Citation Grounding Log for `full_draft_v1.md`

This file records the verified replacement of the former `[RW*]` placeholders
in `paper/versions/ral/full_draft_v1.md` and
`paper/versions/ral/related_work_draft.md`.

Source policy for this pass:

- prefer arXiv abstract pages for papers
- use official documentation only where it is the authoritative source
  (`design.ros2.org`, `behaviortree.dev`)
- avoid forcing weak one-to-one replacements when a single placeholder span is
  better supported by a small, tightly related citation cluster

## Replacement summary

- Status:
  all former placeholders `[RW1]` through `[RW17]` have been removed from the
  drafts and replaced with grounded citations.
- Draft state:
  `full_draft_v1.md` and `related_work_draft.md` now use verified literature
  directly in prose.
- Remaining unresolved placeholders:
  none.

## Former placeholder groups and grounded replacements

### `[RW1]`-`[RW5]` Embodied / LLM-based robot planning

- Inner Monologue: Embodied Reasoning through Planning with Language Models
  (Huang et al., 2022)
  Source: https://arxiv.org/abs/2207.05608
- PaLM-E: An Embodied Multimodal Language Model (Driess et al., 2023)
  Source: https://arxiv.org/abs/2303.03378
- RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic
  Control (Brohan et al., 2023)
  Source: https://arxiv.org/abs/2307.15818
- VoxPoser: Composable 3D Value Maps for Robotic Manipulation with Language
  Models (Huang et al., 2023)
  Source: https://arxiv.org/abs/2307.05973
- OK-Robot: What Really Matters in Integrating Open-Knowledge Models for
  Robotics (Liu et al., 2024)
  Source: https://arxiv.org/abs/2401.12202
- Category:
  embodied planning / embodied execution pipelines
- Why these were chosen:
  together they cover feedback-based planning, embodied multimodal modeling,
  vision-language-action control, model-based grounding, and systems-first
  integration without shifting the paper back to prompt-first framing.

### `[RW6]`-`[RW8]` Representative named systems

- Do As I Can, Not As I Say: Grounding Language in Robotic Affordances
  (Ahn et al., 2022)
  Source: https://arxiv.org/abs/2204.01691
- Code as Policies: Language Model Programs for Embodied Control
  (Liang et al., 2022)
  Source: https://arxiv.org/abs/2209.07753
- ProgPrompt: Generating Situated Robot Task Plans using Large Language Models
  (Singh et al., 2022)
  Source: https://arxiv.org/abs/2209.11302
- Category:
  language-conditioned skill selection, code-generating control, and
  program-like planning
- Why these were chosen:
  these are the exact exemplars named by the draft and the expert review.

### `[RW9]`-`[RW12]` Execution architecture / middleware / behavior trees

- Robot Operating System 2: Design, architecture, and uses in the wild
  (Macenski et al., 2022)
  Source: https://doi.org/10.1126/scirobotics.abm6074
- ROS 2 actions design article
  (Biggs, Perron, and Loretz, 2019/2020)
  Source: https://design.ros2.org/articles/actions.html
- PlanSys2: A Planning System Framework for ROS2 (Martin et al., 2021)
  Source: https://arxiv.org/abs/2107.00376
- Behavior Trees in Robotics and AI: An Introduction
  (Colledanchise and Ogren, 2018)
  Source: https://arxiv.org/abs/1709.00084
- BehaviorTree.CPP documentation
  Source: https://www.behaviortree.dev/docs/intro/
- Category:
  action interfaces, plan dispatch, guarded execution, and robotics middleware
- Note:
  the final prose uses a citation cluster here rather than a strict four-slot
  mapping because the paragraph now grounds middleware, action semantics,
  plan-dispatch frameworks, and behavior-tree tooling separately.

### `[RW13]`-`[RW14]` TAMP / planning-to-execution interface

- PDDLStream: Integrating Symbolic Planners and Blackbox Samplers via
  Optimistic Adaptive Planning (Garrett et al., 2020)
  Source: https://arxiv.org/abs/1802.08705
- Integrated Task and Motion Planning (Garrett et al., 2021)
  Source: https://arxiv.org/abs/2010.01083
- Category:
  task-and-motion planning and planning-to-execution interfaces
- Why these were chosen:
  they directly support the paper's argument that symbolic plans require an
  explicit grounding interface before execution.

### `[RW15]`-`[RW17]` Broader embodied evaluations used for positioning

- EmbodiedBench: Comprehensive Benchmarking Multi-modal Large Language Models
  for Vision-Driven Embodied Agents (Yang et al., 2025)
  Source: https://arxiv.org/abs/2502.09560
- IS-Bench: Evaluating Interactive Safety of VLM-Driven Embodied Agents in
  Daily Household Tasks (Lu et al., 2025)
  Source: https://arxiv.org/abs/2506.16402
- Mind and Motion Aligned: A Joint Evaluation IsaacSim Benchmark for Task
  Planning and Low-Level Policies in Mobile Manipulation
  (Kitchen-R; Kachaev et al., 2025)
  Source: https://arxiv.org/abs/2508.15663
- Category:
  broader embodied-agent evaluations and integrated planning/control studies
- Note:
  Section 2.3 was lightly rewritten so these citations now position the paper
  against broader evaluation-style work, while the controlled-study claim is
  carried by the paper's own methodology and not outsourced to weakly matched
  references.
