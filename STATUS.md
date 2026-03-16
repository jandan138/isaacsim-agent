# STATUS.md

## Current status

- Date: 2026-03-16
- Plan source of truth: `plan.md`
- Active milestone: `M6. Prompting and runtime ablations`
- Milestone state: completed for the scoped `M6 block A manipulation pilot` requested in this run
- Completion level:
  - the repo now has a completed and validated manipulation-only block A pilot built on the existing M1.5 contracts, M3 manipulation baseline, M4 runtime v0, M5 eval harness, `scripts/run_suite.py`, and the existing summary pipeline
  - the prior `M6 block A navigation expansion` remains completed and available under `results/processed/block_a_navigation_prompt_runtime_expanded/`
  - the new manipulation pilot outputs are available under `results/processed/block_a_manipulation_prompt_runtime_pilot/`

## Run context

- This run stayed within the requested boundaries:
  - block A only
  - manipulation slice only
  - prompt variants: `P0`, `P1`, `P2`
  - runtime variants: `R0`, `R1`
  - no `R2`
  - no M7 memory/context work
  - no tool abstraction work
  - no randomization
  - no expansion beyond pilot scale
- Reused components:
  - M1.5 contracts
  - M3 manipulation baseline
  - M4 runtime v0
  - M5 eval harness
  - `scripts/run_suite.py`
  - existing summary pipeline
- Agent teaming:
  - used explorer sub-agents to inspect manipulation baseline scope and block-A config/test patterns
  - no sub-agent interruptions were needed
- Preexisting target artifact directories were present before the final refresh and were backed up:
  - `results/block_a_manipulation_prompt_runtime_pilot_pre_refresh_20260316T112919Z`
  - `results/processed/block_a_manipulation_prompt_runtime_pilot_pre_refresh_20260316T112919Z`

## Milestone summary

- Completed in this run:
  - extended `src/isaacsim_agent/runtime/session.py` so M4 runtime v0 now supports both `navigation` and `pick_place`
  - added the minimal manipulation tool surface needed by runtime v0 in `src/isaacsim_agent/tools/registry.py`:
    - `get_gripper_state`
    - `get_object_state`
    - `get_target_state`
    - `scripted_pick_place_step`
  - extended `src/isaacsim_agent/planner/mock.py` so both `mock_rule_based` and `mock_block_a` support `pick_place`
  - exposed manipulation task builders through `src/isaacsim_agent/runtime/__init__.py`
  - generalized `src/isaacsim_agent/experiments/pilot.py` so block-A pilot configs can target:
    - `task_family: navigation`
    - `task_family: manipulation`
  - added the requested manipulation pilot config:
    - `configs/experiments/block_a/manipulation_prompt_runtime_pilot.yaml`
  - added focused manipulation pilot smoke coverage:
    - `tests/test_block_a_manipulation_pilot_smoke.py`
  - expanded runtime smoke coverage to include successful `pick_place` execution:
    - `tests/test_agent_runtime_smoke.py`
  - executed one full manipulation pilot end-to-end and refreshed the requested processed outputs at:
    - `results/processed/block_a_manipulation_prompt_runtime_pilot/`
- Not completed in this run:
  - no `R2`
  - no mixed-backend manipulation expansion
  - no memory/context work
  - no tool abstraction work
  - no randomization
  - no paper assets
  - no M7+ work

## Manipulation pilot definition

- Scope:
  - manipulation-only
  - prompt variants: `P0`, `P1`, `P2`
  - runtime variants: `R0`, `R1`
  - backend: `toy`
  - tasks: `3`
  - planned runs: `18`
- Config entrypoint:
  - `configs/experiments/block_a/manipulation_prompt_runtime_pilot.yaml`
- Reused execution path:
  - `scripts/run_suite.py`
  - `src/isaacsim_agent/experiments/pilot.py`
  - `src/isaacsim_agent/runtime/session.py`
  - `src/isaacsim_agent/eval/summarize.py`
- Task slice:
  - `pick_place_short_forward`
  - `pick_place_lateral_left`
  - `pick_place_diagonal_long`

## Files changed in this run

- `STATUS.md`
- `configs/experiments/block_a/manipulation_prompt_runtime_pilot.yaml`
- `src/isaacsim_agent/experiments/pilot.py`
- `src/isaacsim_agent/planner/mock.py`
- `src/isaacsim_agent/runtime/__init__.py`
- `src/isaacsim_agent/runtime/session.py`
- `src/isaacsim_agent/tools/__init__.py`
- `src/isaacsim_agent/tools/registry.py`
- `tests/test_agent_runtime_smoke.py`
- `tests/test_block_a_manipulation_pilot_smoke.py`

## Generated outputs

- `results/block_a_manipulation_prompt_runtime_pilot/`
- `results/processed/block_a_manipulation_prompt_runtime_pilot/run_summary.jsonl`
- `results/processed/block_a_manipulation_prompt_runtime_pilot/run_summary.csv`
- `results/processed/block_a_manipulation_prompt_runtime_pilot/aggregate.json`
- `results/processed/block_a_manipulation_prompt_runtime_pilot/validation.json`
- `results/processed/block_a_manipulation_prompt_runtime_pilot/block_a_summary.json`
- `results/processed/block_a_manipulation_prompt_runtime_pilot/block_a_summary.md`
- `results/processed/block_a_manipulation_prompt_runtime_pilot/run_plan.json`

## Commands run

- Source-of-truth reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,240p' AGENTS.md`
  - `sed -n '1,260p' STATUS.md`
- Repo and milestone inspection:
  - `git status --short`
  - `rg -n "manipulation|block A|pilot|M6" plan.md src tests configs scripts results -g '!results/block_a_navigation_prompt_runtime_expanded*' -g '!results/processed/block_a_navigation_prompt_runtime_expanded*'`
  - `find configs/experiments -maxdepth 3 -type f | sort`
  - `find src/isaacsim_agent/tasks -maxdepth 3 -type f | sort`
  - `find tests -maxdepth 2 -type f | sort`
  - `sed -n '540,620p' plan.md`
  - `sed -n '1,240p' configs/experiments/block_a/navigation_prompt_runtime_pilot.yaml`
  - `sed -n '1,320p' scripts/run_suite.py`
  - `sed -n '1,360p' src/isaacsim_agent/experiments/pilot.py`
  - `sed -n '360,940p' src/isaacsim_agent/experiments/pilot.py`
  - `sed -n '940,1125p' src/isaacsim_agent/experiments/pilot.py`
  - `sed -n '1,320p' src/isaacsim_agent/runtime/session.py`
  - `sed -n '260,760p' src/isaacsim_agent/runtime/session.py`
  - `sed -n '760,1200p' src/isaacsim_agent/runtime/session.py`
  - `sed -n '1200,1760p' src/isaacsim_agent/runtime/session.py`
  - `sed -n '1817,1998p' src/isaacsim_agent/runtime/session.py`
  - `sed -n '1,320p' src/isaacsim_agent/planner/mock.py`
  - `sed -n '1,260p' src/isaacsim_agent/tools/registry.py`
  - `sed -n '1,240p' src/isaacsim_agent/tools/__init__.py`
  - `sed -n '1,360p' src/isaacsim_agent/tasks/manipulation/baseline.py`
  - `sed -n '360,1080p' src/isaacsim_agent/tasks/manipulation/baseline.py`
  - `sed -n '1,260p' src/isaacsim_agent/tasks/manipulation/isaac_world.py`
  - `sed -n '1,320p' src/isaacsim_agent/eval/summarize.py`
  - `sed -n '320,520p' src/isaacsim_agent/eval/summarize.py`
  - `sed -n '1,260p' src/isaacsim_agent/eval/loader.py`
  - `sed -n '1,260p' tests/test_block_a_pilot_smoke.py`
  - `sed -n '1,260p' tests/test_block_a_expanded_smoke.py`
  - `sed -n '1,260p' tests/test_pickplace_smoke.py`
  - `sed -n '1,260p' tests/test_agent_runtime_smoke.py`
  - `sed -n '1,220p' scripts/run_agent_v0_task_config.py`
  - `PYTHONPATH=src uv run python - <<'PY' ... scratch manipulation run_pilot_suite config sanity check ... PY`
- Validation and output inspection:
  - `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/experiments/pilot.py src/isaacsim_agent/runtime/session.py src/isaacsim_agent/planner/mock.py scripts/run_suite.py tests/test_block_a_manipulation_pilot_smoke.py`
  - `find results -maxdepth 2 -type d \( -path 'results/block_a_manipulation_prompt_runtime_pilot' -o -path 'results/processed/block_a_manipulation_prompt_runtime_pilot' \) | sort`
  - `find results/block_a_manipulation_prompt_runtime_pilot -maxdepth 2 -type f | sort`
  - `find results/processed/block_a_manipulation_prompt_runtime_pilot -maxdepth 1 -type f | sort`
  - `PYTHONPATH=src uv run python -m unittest tests.test_block_a_manipulation_pilot_smoke tests.test_block_a_pilot_smoke tests.test_block_a_expanded_smoke tests.test_agent_runtime_smoke tests.test_pickplace_smoke tests.test_eval_harness_smoke`
  - `mktemp -d /tmp/isaacsim-agent-block-a-manip-smoke-XXXXXX`
  - `PYTHONPATH=src uv run python scripts/run_suite.py --config configs/experiments/block_a/manipulation_prompt_runtime_pilot.yaml --results-root /tmp/isaacsim-agent-block-a-manip-smoke-GoVs7S/results --output-dir /tmp/isaacsim-agent-block-a-manip-smoke-GoVs7S/results/processed/block_a_manipulation_prompt_runtime_pilot`
  - `date -u +%Y%m%dT%H%M%SZ`
  - `python - <<'PY' ... rename existing manipulation pilot result directories to *_pre_refresh_20260316T112919Z ... PY`
  - `PYTHONPATH=src uv run python scripts/run_suite.py --config configs/experiments/block_a/manipulation_prompt_runtime_pilot.yaml --results-root results/block_a_manipulation_prompt_runtime_pilot --output-dir results/processed/block_a_manipulation_prompt_runtime_pilot > /tmp/block_a_manipulation_prompt_runtime_pilot_e2e.log 2>&1`
  - `tail -n 40 /tmp/block_a_manipulation_prompt_runtime_pilot_e2e.log`
  - `find results/processed/block_a_manipulation_prompt_runtime_pilot -maxdepth 1 -type f | sort`
  - `sed -n '1,260p' results/processed/block_a_manipulation_prompt_runtime_pilot/aggregate.json`
  - `sed -n '1,220p' results/processed/block_a_manipulation_prompt_runtime_pilot/validation.json`
  - `sed -n '1,220p' results/processed/block_a_manipulation_prompt_runtime_pilot/block_a_summary.md`
  - `sed -n '1,6p' results/processed/block_a_manipulation_prompt_runtime_pilot/run_summary.jsonl`
  - `python - <<'PY' ... required run_summary field check plus P0/P1/P2 trend check ... PY`
  - `sed -n '1,220p' results/block_a_manipulation_prompt_runtime_pilot/runs/block-a-manipulation-prompt-runtime-pilot-pick-place-short-forward-tabletop-stage-a-p2-r0-s0/manifest.json`
  - `git diff --stat`
  - `git diff -- src/isaacsim_agent/experiments/pilot.py src/isaacsim_agent/planner/mock.py src/isaacsim_agent/runtime/__init__.py src/isaacsim_agent/runtime/session.py src/isaacsim_agent/tools/__init__.py src/isaacsim_agent/tools/registry.py tests/test_agent_runtime_smoke.py STATUS.md`
  - `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/tools/registry.py src/isaacsim_agent/tools/__init__.py src/isaacsim_agent/planner/mock.py src/isaacsim_agent/runtime/session.py src/isaacsim_agent/runtime/__init__.py src/isaacsim_agent/experiments/pilot.py tests/test_agent_runtime_smoke.py tests/test_block_a_manipulation_pilot_smoke.py scripts/run_suite.py scripts/run_agent_v0_task_config.py`
  - `PYTHONPATH=src uv run python -m unittest tests.test_agent_runtime_smoke tests.test_block_a_manipulation_pilot_smoke tests.test_block_a_pilot_smoke tests.test_block_a_expanded_smoke tests.test_run_suite_smoke tests.test_pickplace_smoke tests.test_eval_harness_smoke`

## Validation results

- Python compilation succeeded:
  - command: `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/tools/registry.py src/isaacsim_agent/tools/__init__.py src/isaacsim_agent/planner/mock.py src/isaacsim_agent/runtime/session.py src/isaacsim_agent/runtime/__init__.py src/isaacsim_agent/experiments/pilot.py tests/test_agent_runtime_smoke.py tests/test_block_a_manipulation_pilot_smoke.py scripts/run_suite.py scripts/run_agent_v0_task_config.py`
  - result: success with no output
- Focused unit tests succeeded:
  - command: `PYTHONPATH=src uv run python -m unittest tests.test_agent_runtime_smoke tests.test_block_a_manipulation_pilot_smoke tests.test_block_a_pilot_smoke tests.test_block_a_expanded_smoke tests.test_run_suite_smoke tests.test_pickplace_smoke tests.test_eval_harness_smoke`
  - result:
    - `Ran 15 tests in 10.532s`
    - `OK`
- `run_suite.py` smoke for the manipulation pilot succeeded:
  - command: `PYTHONPATH=src uv run python scripts/run_suite.py --config configs/experiments/block_a/manipulation_prompt_runtime_pilot.yaml --results-root /tmp/isaacsim-agent-block-a-manip-smoke-GoVs7S/results --output-dir /tmp/isaacsim-agent-block-a-manip-smoke-GoVs7S/results/processed/block_a_manipulation_prompt_runtime_pilot`
  - result:
    - `Planned runs: 18`
    - `Runs scanned: 18`
    - `Contract-complete runs: 18`
    - `Run-complete runs: 18`
    - `Successful runs: 15`
- Full manipulation block A end-to-end run succeeded:
  - command: `PYTHONPATH=src uv run python scripts/run_suite.py --config configs/experiments/block_a/manipulation_prompt_runtime_pilot.yaml --results-root results/block_a_manipulation_prompt_runtime_pilot --output-dir results/processed/block_a_manipulation_prompt_runtime_pilot > /tmp/block_a_manipulation_prompt_runtime_pilot_e2e.log 2>&1`
  - suite outputs:
    - results root: `results/block_a_manipulation_prompt_runtime_pilot/`
    - processed outputs: `results/processed/block_a_manipulation_prompt_runtime_pilot/`
  - aggregate result:
    - `total_runs = 18`
    - `contract_complete_runs = 18`
    - `run_complete_runs = 18`
    - `successful_runs = 15`
    - `success_rate = 0.833333`
    - `total_invalid_actions = 6`
    - `total_retries = 3`
- `validation.json` confirms every manipulation pilot run is contract-complete and run-complete:
  - `18` entries
  - no missing artifacts
  - no validation issues
- `run_summary.jsonl` field check confirms all requested fields are present:
  - `rows 18`
  - `missing []`
  - `task_families ['pick_place']`
- The manipulation trend matches the requested block-A expectation:
  - `P0/R0` failed on all `3` tasks with `termination_reason=invalid_action_limit`
  - `P0/R1` recovered and succeeded on all `3` tasks with `invalid_actions=1` and `retries=1` per run
  - `P1` succeeded on all `3` tasks under both `R0` and `R1`
  - `P2` succeeded on all `3` tasks under both `R0` and `R1`
  - `P2` planner/tool calls remained below `P1`:
    - `P1 average_planner_calls = 10.0`
    - `P2 average_planner_calls = 8.0`
    - `P1 average_tool_calls = 10.0`
    - `P2 average_tool_calls = 8.0`
- Sample manifest metadata confirms the requested run-level metadata is recorded:
  - `planner_backend`
  - `prompt_variant`
  - `runtime_policy`
  - `runtime_variant`
  - `scene_id`
  - `suite_experiment`
  - `task_id`

## Blockers

- None.

## Next recommended step

- Analyze the combined navigation + manipulation block A outcomes, then decide whether to:
  - keep manipulation at pilot scale and move to the planned pilot-analysis checkpoint
  - or run one strictly scoped manipulation expansion next only if an Isaac-backed slice is explicitly required
