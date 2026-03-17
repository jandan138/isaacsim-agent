# Failure Case Notes

This file is an internal writing workbench for the RA-L revision pass. It is not an
appendix draft. Its job is to keep the failure-case prose aligned to existing
artifacts without inventing new analysis.

## Evidence basis

- `results/processed/block_a_prompt_only_ablation/run_summary.jsonl`
- `results/processed/block_a_runtime_only_ablation/run_summary.jsonl`
- `results/processed/block_a_final_closure/run_summary.jsonl`
- `results/block_a_prompt_only_ablation/runs/block-a-prompt-only-ablation-prompt-nav-short-forward-easy-empty-stage-a-p0-r0-s0/artifacts/planner_trace.json`
- `results/block_a_navigation_prompt_runtime_expanded/runs/block-a-navigation-prompt-runtime-expanded-toy-nav-short-forward-easy-empty-stage-a-p0-r1-s0/artifacts/planner_trace.json`
- `results/block_a_manipulation_prompt_runtime_pilot/runs/block-a-manipulation-prompt-runtime-pilot-pick-place-short-forward-tabletop-stage-a-p0-r1-s0/artifacts/planner_trace.json`
- `results/block_a_runtime_only_ablation/runs/block-a-runtime-only-ablation-runtime-nav-offset-probe-easy-empty-stage-f-p1-r1-s0/artifacts/planner_trace.json`

## Dominant invalid-action pattern

The clearest repeated `P0` invalid actions are unsupported tool names, not random
token noise:

- navigation failures emit `move_to_goal` even though the available dispatchable tool
  is `navigate_to`
- manipulation failures emit `move_object` even though the available dispatchable tool
  is `scripted_pick_place_step` with a `phase_name` argument

These failures appear immediately at step `1`, with `1` planner call, `0` tool
calls, and termination by `invalid_action_limit` under `R0`.

## Architecture reading

The under-specified minimal direct-action contract leaves the planner free to emit a
task-level verb that matches human intent but not the executor API. That is the key
architectural point: the planner knows the goal, but the interface does not force it
to bind the goal to a dispatchable tool and argument set. The typed contracts `P1`
and `P2` close that gap by making the executor-facing API explicit.

## Why runtime validation recovers

`R1` helps when the contract violation is easy to diagnose before execution. In the
traces, validation returns `unknown tool: move_to_goal` or `unknown tool:
move_object`, and the repair prompt then elicits executor-compatible calls such as
`navigate_to` with `target_pose` or `scripted_pick_place_step` with the next
`phase_name`. The runtime is therefore not inventing a new policy; it is exposing
the contract error early enough that one corrected planner call can continue the run.
