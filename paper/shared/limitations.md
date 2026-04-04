# Limitations

This file captures the study boundaries that should remain stable across
versions. Use it to keep the paper honest without turning the prose into a list
of repeated reviewer prompts.

## Study scope limitations

- The evidence is simulator-based. The majority of the evaluation matrix runs on
  a lightweight deterministic reference backend; Isaac Sim serves as a small
  qualitative validation slice. No real-robot execution is included.
- The paper covers Block A only and studies two execution-design axes:
  planner-to-executor contract variants and runtime validation variants.
- The paper covers two task families only: navigation and tabletop
  manipulation.
- Difficulty coverage is limited to the current easy/shared slices plus the
  present harder navigation and harder manipulation slices.

## Experimental limitations

- The focused interface-only, runtime-only, and harder-manipulation slices are
  compact mechanism checks rather than broad benchmark sweeps.
- Backend coverage differs across slices, so claims should remain tied to the
  covered task matrix rather than extended to arbitrary deployments.
- The runtime-only ablation is built around recoverable invalid-first-action
  probes, so it isolates recovery value rather than a full runtime taxonomy.

## Framing limitations

- This is a controlled systems paper about execution architecture, not a
  new-model, broad benchmark, or sim-to-real paper.
- The study does not cover later roadmap axes such as memory, context
  management, tool abstraction, or domain randomization.
- The paper should argue for bounded execution-design lessons under controlled
  conditions.

## Paper-asset limitations

- Existing packaged figures and tables under
  `results/processed/block_a_master_summary/` are legacy templates, not the
  final frozen evidence package.
- A later writing task still needs to regenerate final paper figures and tables
  from the correct final-closure sources.

## Safe conclusion wording

The safest conclusion is:

Within the current controlled simulator study, planner-to-executor contract design,
lightweight runtime validation, and a brief self-check meaningfully affect
reliability and planner/tool overhead.
