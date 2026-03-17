# Findings Ledger

This file separates what is directly supported by current Block A evidence from
careful interpretation and from statements the paper should not make.

## Strong supported findings

These statements can be written as results, provided they cite the listed sources.

1. The weakest condition is consistently `P0/R0`.
   Support:
   `results/processed/block_a_master_summary/block_a_master_summary.md`,
   `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.md`,
   `results/processed/block_a_final_closure/block_a_final_closure_summary.md`
2. Runtime validation plus a single retry has independent value when the action
   interface is fixed at `P1`.
   In `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.md`,
   success rises from `2/4` to `4/4`, and the same `0.5 -> 1.0` trend appears in both navigation and manipulation.
3. The runtime-only gain is a recovery effect, not an invalid-attempt suppression effect.
   In the same runtime-only summary, invalid-action runs remain `2` vs `2`, while successful invalid-action recoveries rise from `0` to `2`.
4. Action-interface specification has independent value when runtime is fixed at
   `R0`.
   In `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.md`,
   `P0/R0` is `0/4`, while `P1/R0` and `P2/R0` are `4/4`, and invalid actions drop from `4` total under `P0` to `0` under `P1` and `P2`.
5. `P2` is more planner/tool-efficient than `P1` in the tested action-interface and
   harder-manipulation slices while keeping the same success profile.
   Support:
   `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.md`,
   `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.md`,
   `results/processed/block_a_final_closure/block_a_final_closure_summary.md`
6. The qualitative ordering is stable across the covered navigation and manipulation tasks.
   Support:
   `results/processed/block_a_cross_family_summary/cross_family_summary.json`,
   `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.md`,
   `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.md`,
   `results/processed/block_a_final_closure/block_a_final_closure_summary.md`
7. The current harder slices increase workload without changing the condition ordering.
   Support:
   `results/processed/block_a_master_summary/block_a_master_summary.md`,
   `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.md`,
   `results/processed/block_a_final_closure/block_a_final_closure_summary.md`

## Weaker or more careful claims

These belong in interpretation or discussion, not as over-strong headline results.

1. The current evidence suggests that planner-to-executor contract design matters
   primarily by preventing invalid actions before dispatch.
   Reason:
   this is an interpretation of the fixed-`R0` comparison and the cross-family
   pattern, not a separately manipulated mechanism study.
2. The dominant invalid actions in `P0` look like contract mismatches rather than
   arbitrary planner collapse.
   Reason:
   run summaries and traces repeatedly show semantically plausible but unsupported
   dispatch names such as `move_to_goal` and `move_object`, while the executor
   expects named tools such as `navigate_to` and `scripted_pick_place_step`.
3. The current evidence suggests that lightweight runtime support is most valuable
   for fragile executions that are still recoverable.
   Reason:
   the runtime-only slice was deliberately built around recoverable invalid-first-action probes.
4. The brief self-check in `P2` appears to reduce planner/tool overhead without
   harming success in the tested setup.
   Reason:
   the effect is stable in current slices, but the dataset is small and controlled.
5. Harder tasks currently look like cost amplification rather than rank reversal.
   Reason:
   this is supported only for the present harder navigation and harder manipulation slices, not for a broad difficulty benchmark.
6. Block A is closed enough to support a controlled systems paper.
   Reason:
   this is a paper-scoping judgment from the closure package, not itself a scientific result.

## Explicitly not claimed

These statements should not appear as claims in the paper.

1. The paper does not claim state of the art.
2. The paper does not claim a generally best embodied agent.
3. The paper does not claim broad generalization across models, simulators, or robots.
4. The paper does not claim broader roadmap findings about memory, context,
   tool abstraction, safety, or randomization.
5. The paper does not claim sim-to-real readiness or real-world safety.
6. The paper does not claim that the merged overall success rate of the final
   closure package is the main scientific result.

## Writing discipline

When drafting:

- use strong findings as result sentences
- use careful claims as discussion sentences
- move anything beyond those buckets to future work or remove it
