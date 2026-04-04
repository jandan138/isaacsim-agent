# Core Claim

## Working paper identity

This paper is a controlled systems study of planner-to-executor contract design and
runtime validation for embodied-agent execution in a lightweight simulator setup.
The main factorial uses a deterministic reference backend; a minimal Isaac Sim slice
provides qualitative cross-backend validation. Its scope is limited to how
action-interface specification and lightweight runtime handling affect invalid
actions, recovery, success, and planner/tool overhead in the current Block A task
matrix.

## Core claim

Within the tested Block A simulator setup (lightweight reference backend + Isaac Sim
validation slice), planner-to-executor contract design and runtime validation show
consistent execution effects:

- the under-specified direct-action contract (`P0`) is the weakest condition in the
  covered slices
- typed tool-call contracts (`P1`, `P2`) reduce invalid actions relative to `P0`
  and keep the execution profile strong in the tested tasks
- runtime validation with a single retry (`R1`) recovers fragile runs that would
  otherwise terminate on contract-violating first actions
- within the structured contract conditions, the brief self-check in `P2` is
  associated with lower planner/tool overhead than `P1` in the covered slices
- the same qualitative ordering persists across the covered navigation and
  manipulation tasks, including the current harder slices

## Evidence lock

Use these processed outputs to support the claim:

- primary freeze:
  `results/processed/block_a_final_closure/block_a_final_closure_summary.{json,csv,md}`
- action-interface ablation support:
  `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}`
- runtime-validation support:
  `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.{json,md}`
- harder manipulation support:
  `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.{json,md}`
- cross-family and harder-navigation context:
  `results/processed/block_a_master_summary/block_a_master_summary.{json,md}` and
  `results/processed/block_a_cross_family_summary/cross_family_summary.json`

## What this claim is not

This claim is not a new-model claim, a benchmark-supremacy claim, or a universal
claim about other simulators, robots, or later roadmap axes.

## Usage note

If a sentence in a draft cannot be justified from the sources above, move it to
discussion, future work, or remove it.
