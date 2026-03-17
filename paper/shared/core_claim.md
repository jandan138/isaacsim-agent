# Core Claim

## Working paper identity

This paper is a controlled systems study of embodied-agent execution in Isaac Sim.
Its scope is limited to how prompt/interface structure and lightweight runtime
validation affect invalid actions, recovery, success, and execution overhead in the
current Block A task matrix.

## Core claim

Within the tested Block A Isaac Sim setup, prompt/interface structure and runtime
validation materially shape execution outcomes:

- structured tool-oriented prompting reduces invalid actions relative to the weakest direct-action prompt
- lightweight runtime validation with a single retry recovers fragile executions that would otherwise fail
- a brief self-check can preserve the strong success profile of structured prompting while lowering planner/tool calls in the tested setup
- these qualitative trends persist across the covered navigation and manipulation tasks, including the current harder slices

## Evidence lock

Use these processed outputs to support the claim:

- primary umbrella evidence: `results/processed/block_a_final_closure/block_a_final_closure_summary.{json,csv,md}`
- prompt-only support: `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}`
- runtime-only support: `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.{json,md}`
- harder manipulation support: `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.{json,md}`
- earlier cross-family and harder-navigation context: `results/processed/block_a_master_summary/block_a_master_summary.{json,md}` and `results/processed/block_a_cross_family_summary/cross_family_summary.json`

## What this claim is not

This claim does not say that:

- the paper introduces a new model
- the paper establishes a generally strongest embodied agent
- the conclusions cover memory, context compression, tool abstraction, safety, or sim-to-real transfer
- the observed ordering is universal across backends, environments, or robot embodiments

## Usage note

If a sentence in a draft cannot be justified from the sources above, move it to
discussion, future work, or remove it.
