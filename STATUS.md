# STATUS.md

## Current status

- Date: 2026-03-16
- Plan source of truth: `plan.md`
- Active milestone: `M6. Prompting and runtime ablations`
- Milestone state: completed for the scoped `M6 block A navigation expansion` requested in this run
- Completion level: the repo now has a completed and validated navigation-only expanded block A suite on top of the existing M1.5 contracts, M4 runtime v0, M5 eval harness, existing suite runner, and existing summary pipeline, with final processed outputs under `results/processed/block_a_navigation_prompt_runtime_expanded/`

## Run context

- At the start of this run, the repo source-of-truth files were inconsistent:
  - `STATUS.md` still reported only the earlier 18-run pilot completion
  - the worktree already contained unrecorded expanded-block-A scaffolding, including:
    - `configs/experiments/block_a/navigation_prompt_runtime_expanded.yaml`
    - `scripts/run_agent_v0_task_config.py`
    - README/schema mentions for expanded outputs
    - mixed-backend support already present in `src/isaacsim_agent/experiments/pilot.py` and metadata propagation already present in `src/isaacsim_agent/runtime/session.py`
    - partial old artifacts at the requested target paths:
      - `results/block_a_navigation_prompt_runtime_expanded/`
      - `results/processed/block_a_navigation_prompt_runtime_expanded/`
- This run treated that preexisting scaffold as context, fixed the remaining bugs, added missing focused coverage, backed up the incomplete old artifacts, reran the full suite, and refreshed `STATUS.md`

## Milestone summary

- Completed in this run:
  - updated `src/isaacsim_agent/experiments/pilot.py` to support `summary_title`, so config-selected summaries can render the correct markdown heading (`Block A Summary`) without changing the existing suite entrypoint or artifact layout
  - kept the existing mixed-backend expanded suite design intact:
    - prompt variants: `P0`, `P1`, `P2`
    - runtime variants: `R0`, `R1`
    - backends: `toy` plus a small `isaac` slice
    - total matrix size: `48` runs
  - updated `configs/experiments/block_a/navigation_prompt_runtime_expanded.yaml` to set `summary_title: Block A Summary`
  - fixed a real backend error in `src/isaacsim_agent/tasks/navigation/isaac_world.py`:
    - missing Isaac imports were raising the undefined name `IsaacBackendUnavailableError`
    - the failure path now correctly raises `NavigationBackendUnavailableError`
    - this restores clean `task_precondition_failed` behavior when the helper is executed outside Isaac Python
  - added `tests/test_block_a_expanded_smoke.py` with focused coverage for:
    - loading the expanded config
    - planning the full `48`-run mixed-backend matrix
    - running a minimal mixed-backend suite and checking backend-aware summary outputs
  - preserved the required metadata across artifacts:
    - `prompt_variant`
    - `runtime_variant`
    - `runtime_policy`
    - `task_id`
    - `scene_id`
  - preserved the required summary fields in `run_summary.{jsonl,csv}`:
    - `success`
    - `termination_reason`
    - `step_count`
    - `planner_calls`
    - `tool_calls`
    - `invalid_actions`
    - `retries`
    - `planner_latency_s`
    - `episode_time_s`
  - backed up the preexisting incomplete target outputs before rerunning:
    - `results/block_a_navigation_prompt_runtime_expanded_pre_refresh_20260316T105915Z`
    - `results/processed/block_a_navigation_prompt_runtime_expanded_pre_refresh_20260316T105915Z`
  - executed one full expanded block A end-to-end run and refreshed the requested processed outputs at:
    - `results/processed/block_a_navigation_prompt_runtime_expanded/`
- Not completed in this run:
  - no `R2`
  - no manipulation block A
  - no memory or context work
  - no tool abstraction work
  - no randomization
  - no paper assets
  - no M7+ work

## Expanded block A definition

- Scope:
  - navigation-only
  - prompt variants: `P0`, `P1`, `P2`
  - runtime variants: `R0`, `R1`
  - no `R2`
  - no manipulation
  - no M7+ dimensions
- Config entrypoint:
  - `configs/experiments/block_a/navigation_prompt_runtime_expanded.yaml`
- Reused execution path:
  - `scripts/run_suite.py`
  - `src/isaacsim_agent/experiments/pilot.py`
  - `src/isaacsim_agent/runtime/session.py`
  - `src/isaacsim_agent/eval/summarize.py`
- Backend mix:
  - `toy`: 6 tasks, 36 runs
  - `isaac`: 2 tasks, 12 runs
  - total: 8 tasks, 48 runs

## Files changed in this run

- `STATUS.md`
- `configs/experiments/block_a/navigation_prompt_runtime_expanded.yaml`
- `src/isaacsim_agent/experiments/pilot.py`
- `src/isaacsim_agent/tasks/navigation/isaac_world.py`
- `tests/test_block_a_expanded_smoke.py`

## Pre-existing relevant worktree state

- The following relevant paths were already present or dirty when this run started and were not edited in this run:
  - `configs/README.md`
  - `results/schema.md`
  - `scripts/README.md`
  - `scripts/run_agent_v0_task_config.py`
  - `src/isaacsim_agent/runtime/session.py`
  - `tests/test_block_a_pilot_smoke.py`
- The following target artifact directories already existed with incomplete old outputs and were backed up before the final rerun:
  - `results/block_a_navigation_prompt_runtime_expanded/`
  - `results/processed/block_a_navigation_prompt_runtime_expanded/`

## Generated outputs

- `results/processed/block_a_navigation_prompt_runtime_expanded/run_summary.jsonl`
- `results/processed/block_a_navigation_prompt_runtime_expanded/run_summary.csv`
- `results/processed/block_a_navigation_prompt_runtime_expanded/aggregate.json`
- `results/processed/block_a_navigation_prompt_runtime_expanded/validation.json`
- `results/processed/block_a_navigation_prompt_runtime_expanded/block_a_summary.json`
- `results/processed/block_a_navigation_prompt_runtime_expanded/block_a_summary.md`
- `results/processed/block_a_navigation_prompt_runtime_expanded/run_plan.json`

## Commands run

- Source-of-truth reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,220p' AGENTS.md`
  - `sed -n '1,260p' STATUS.md`
- Repo and milestone inspection:
  - `rg -n "M6|block A|navigation" plan.md`
  - `rg --files`
  - `git status --short`
  - `sed -n '540,620p' plan.md`
  - `sed -n '1,240p' configs/experiments/block_a/navigation_prompt_runtime_pilot.yaml`
  - `sed -n '1,260p' scripts/run_suite.py`
  - `sed -n '1,320p' src/isaacsim_agent/experiments/pilot.py`
  - `sed -n '320,640p' src/isaacsim_agent/experiments/pilot.py`
  - `sed -n '640,940p' src/isaacsim_agent/experiments/pilot.py`
  - `sed -n '1,320p' src/isaacsim_agent/eval/summarize.py`
  - `sed -n '1,320p' src/isaacsim_agent/runtime/session.py`
  - `sed -n '1,320p' src/isaacsim_agent/tasks/navigation/isaac_world.py`
  - `sed -n '1,320p' src/isaacsim_agent/tasks/navigation/baseline.py`
  - `sed -n '320,640p' src/isaacsim_agent/tasks/navigation/baseline.py`
  - `sed -n '640,960p' src/isaacsim_agent/tasks/navigation/baseline.py`
  - `sed -n '1,360p' src/isaacsim_agent/planner/mock.py`
  - `sed -n '1,260p' tests/test_block_a_pilot_smoke.py`
  - `sed -n '1,240p' tests/test_run_suite_smoke.py`
  - `sed -n '1,240p' configs/README.md`
  - `rg -n "def run_and_write_agent_v0|backend == \\\"isaac\\\"|isaac_python|NavigationBackendUnavailableError|run_agent_v0" src/isaacsim_agent/runtime/session.py scripts/run_agent_v0.py tests`
  - `sed -n '320,760p' src/isaacsim_agent/runtime/session.py`
  - `sed -n '1,260p' scripts/run_agent_v0.py`
  - `sed -n '1,260p' tests/test_agent_runtime_smoke.py`
  - `sed -n '1,240p' scripts/isaac_python.sh`
  - `sed -n '1,240p' tests/test_nav_smoke.py`
  - `sed -n '1,240p' tests/test_smoke_test_isaac.py`
  - `sed -n '1,240p' docs/setup.md`
  - `sed -n '1,220p' results/README.md`
  - `sed -n '1,260p' results/schema.md`
  - `sed -n '1,260p' scripts/README.md`
  - `find results -maxdepth 3 -type d | sort`
  - `find configs/experiments -maxdepth 3 -type f | sort`
  - `sed -n '1,260p' configs/experiments/block_a/navigation_prompt_runtime_expanded.yaml`
  - `find results/processed/block_a_navigation_prompt_runtime_expanded -maxdepth 1 -type f | sort`
  - `sed -n '1,220p' results/processed/block_a_navigation_prompt_runtime_expanded/block_a_summary.md`
  - `python - <<'PY'\nfrom pathlib import Path\nruns = sorted((Path('results/block_a_navigation_prompt_runtime_expanded/runs')).iterdir())\nprint(len(runs))\nprint(runs[:3])\nPY`
  - `rg -n "def read_task_config|load_task_config|TaskConfig.from_dict|write_task_config|read_json" src/isaacsim_agent/contracts src/isaacsim_agent/runtime scripts`
  - `sed -n '1,260p' src/isaacsim_agent/contracts/io.py`
  - `sed -n '1,260p' src/isaacsim_agent/contracts/models.py`
  - `sed -n '1,240p' scripts/run_agent_v0_task_config.py`
  - `sed -n '12,32p' src/isaacsim_agent/experiments/pilot.py`
  - `rg -n "SRC_ROOT|ISAAC_WRAPPER" src/isaacsim_agent/experiments/pilot.py`
- Validation and debugging:
  - `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/experiments/pilot.py scripts/run_agent_v0_task_config.py tests/test_block_a_expanded_smoke.py tests/test_block_a_pilot_smoke.py tests/test_run_suite_smoke.py tests/test_agent_runtime_smoke.py scripts/run_suite.py`
  - `PYTHONPATH=src uv run python -m unittest tests.test_block_a_expanded_smoke tests.test_block_a_pilot_smoke tests.test_run_suite_smoke tests.test_agent_runtime_smoke tests.test_eval_harness_smoke`
  - `rg -n "IsaacBackendUnavailableError" -n src/isaacsim_agent/tasks/navigation/isaac_world.py src/isaacsim_agent/tasks/navigation/baseline.py src/isaacsim_agent/runtime/session.py`
  - `sed -n '1,90p' src/isaacsim_agent/tasks/navigation/isaac_world.py`
  - `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/tasks/navigation/isaac_world.py`
  - `PYTHONPATH=src uv run python -m unittest tests.test_block_a_expanded_smoke tests.test_block_a_pilot_smoke tests.test_run_suite_smoke tests.test_agent_runtime_smoke tests.test_eval_harness_smoke`
  - `sed -n '1,260p' src/isaacsim_agent/eval/validate.py`
  - `sed -n '930,1095p' src/isaacsim_agent/runtime/session.py`
  - `sed -n '1,260p' src/isaacsim_agent/eval/loader.py`
  - `PYTHONPATH=src uv run python -m unittest tests.test_block_a_expanded_smoke tests.test_block_a_pilot_smoke tests.test_run_suite_smoke tests.test_agent_runtime_smoke tests.test_eval_harness_smoke`
  - `mktemp -d /tmp/isaacsim-agent-block-a-smoke-XXXXXX`
  - `PYTHONPATH=src uv run python scripts/run_suite.py --config configs/experiments/block_a/navigation_prompt_runtime_pilot.yaml --results-root /tmp/isaacsim-agent-block-a-smoke-M9Jvfk/results --output-dir /tmp/isaacsim-agent-block-a-smoke-M9Jvfk/results/processed/block_a_navigation_prompt_runtime_pilot`
  - `date -u +%Y%m%dT%H%M%SZ`
  - `mv results/block_a_navigation_prompt_runtime_expanded results/block_a_navigation_prompt_runtime_expanded_pre_refresh_20260316T105915Z`
  - `mv results/processed/block_a_navigation_prompt_runtime_expanded results/processed/block_a_navigation_prompt_runtime_expanded_pre_refresh_20260316T105915Z`
  - `python - <<'PY'\nfrom pathlib import Path\npairs = [\n    (\n        Path('results/block_a_navigation_prompt_runtime_expanded'),\n        Path('results/block_a_navigation_prompt_runtime_expanded_pre_refresh_20260316T105915Z'),\n    ),\n    (\n        Path('results/processed/block_a_navigation_prompt_runtime_expanded'),\n        Path('results/processed/block_a_navigation_prompt_runtime_expanded_pre_refresh_20260316T105915Z'),\n    ),\n]\nfor source, target in pairs:\n    if source.exists():\n        source.rename(target)\n        print(f\"RENAMED {source} -> {target}\")\n    else:\n        print(f\"SKIPPED {source}\")\nPY`
  - `PYTHONPATH=src uv run python scripts/run_suite.py --config configs/experiments/block_a/navigation_prompt_runtime_expanded.yaml > /tmp/block_a_navigation_prompt_runtime_expanded_e2e.log 2>&1`
- Output inspection:
  - `tail -n 40 /tmp/block_a_navigation_prompt_runtime_expanded_e2e.log`
  - `tail -n 60 /tmp/block_a_navigation_prompt_runtime_expanded_e2e.log`
  - `find results/processed/block_a_navigation_prompt_runtime_expanded -maxdepth 1 -type f | sort`
  - `sed -n '1,260p' results/processed/block_a_navigation_prompt_runtime_expanded/aggregate.json`
  - `sed -n '1,260p' results/processed/block_a_navigation_prompt_runtime_expanded/validation.json`
  - `sed -n '1,260p' results/processed/block_a_navigation_prompt_runtime_expanded/block_a_summary.md`
  - `sed -n '1,6p' results/processed/block_a_navigation_prompt_runtime_expanded/run_summary.jsonl`
  - `sed -n '1,3p' results/processed/block_a_navigation_prompt_runtime_expanded/run_summary.csv`
  - `python - <<'PY'\nimport json\nfrom pathlib import Path\nrows = [json.loads(line) for line in Path('results/processed/block_a_navigation_prompt_runtime_expanded/run_summary.jsonl').read_text().splitlines() if line.strip()]\nrequired = ['success','termination_reason','step_count','planner_calls','tool_calls','invalid_actions','retries','planner_latency_s','episode_time_s','prompt_variant','runtime_variant','runtime_policy','task_id','scene_id']\nmissing = sorted({field for field in required if any(field not in row for row in rows)})\nprint('rows', len(rows))\nprint('missing', missing)\nprint('backends', sorted({row['backend_variant'] for row in rows}))\nprint('p0_r0_failures', sum(1 for row in rows if row['prompt_variant']=='P0' and row['runtime_variant']=='R0' and row['success'] is False))\nprint('isaac_runs', sum(1 for row in rows if row['backend_variant']=='isaac'))\nprint('toy_runs', sum(1 for row in rows if row['backend_variant']=='toy'))\nPY`
  - `sed -n '1,220p' results/block_a_navigation_prompt_runtime_expanded/runs/block-a-navigation-prompt-runtime-expanded-isaac-nav-short-forward-minimal-isaac-stage-a-p2-r1-s0/manifest.json`
  - `rg -n "expanded|block_a_summary|run_agent_v0_task_config|mixed backend|Block A Summary" configs/README.md scripts/README.md results/schema.md STATUS.md tests src/isaacsim_agent/experiments/pilot.py`
  - `sed -n '1,260p' STATUS.md`
  - `git status --short`
  - `ls -l STATUS.md`
  - `pwd && find . -maxdepth 1 -type f | sort`

## Validation results

- Python compilation succeeded:
  - command: `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/experiments/pilot.py scripts/run_agent_v0_task_config.py tests/test_block_a_expanded_smoke.py tests/test_block_a_pilot_smoke.py tests/test_run_suite_smoke.py tests/test_agent_runtime_smoke.py scripts/run_suite.py`
  - result: success with no output
- Focused unit tests succeeded after fixing the Isaac missing-dependency exception path:
  - command: `PYTHONPATH=src uv run python -m unittest tests.test_block_a_expanded_smoke tests.test_block_a_pilot_smoke tests.test_run_suite_smoke tests.test_agent_runtime_smoke tests.test_eval_harness_smoke`
  - result:
    - `Ran 10 tests in 0.750s`
    - `OK`
- Existing `run_suite.py` smoke still succeeded on the earlier 18-run pilot config:
  - command: `PYTHONPATH=src uv run python scripts/run_suite.py --config configs/experiments/block_a/navigation_prompt_runtime_pilot.yaml --results-root /tmp/isaacsim-agent-block-a-smoke-M9Jvfk/results --output-dir /tmp/isaacsim-agent-block-a-smoke-M9Jvfk/results/processed/block_a_navigation_prompt_runtime_pilot`
  - result:
    - `Planned runs: 18`
    - `Runs scanned: 18`
    - `Contract-complete runs: 18`
    - `Run-complete runs: 18`
    - `Successful runs: 15`
- Full expanded block A end-to-end run succeeded:
  - command: `PYTHONPATH=src uv run python scripts/run_suite.py --config configs/experiments/block_a/navigation_prompt_runtime_expanded.yaml > /tmp/block_a_navigation_prompt_runtime_expanded_e2e.log 2>&1`
  - suite outputs:
    - results root: `results/block_a_navigation_prompt_runtime_expanded/`
    - processed outputs: `results/processed/block_a_navigation_prompt_runtime_expanded/`
  - aggregate result:
    - `total_runs = 48`
    - `contract_complete_runs = 48`
    - `run_complete_runs = 48`
    - `successful_runs = 40`
    - `success_rate = 0.833333`
    - `total_invalid_actions = 16`
    - `total_retries = 8`
- `validation.json` confirms every expanded run is contract-complete and run-complete:
  - `48` entries
  - no missing artifacts
  - no validation issues
- `run_summary.jsonl` field check confirms all requested fields are present:
  - `rows 48`
  - `missing []`
  - `backends ['isaac', 'toy']`
  - `p0_r0_failures 8`
  - `isaac_runs 12`
  - `toy_runs 36`
- Sample manifest metadata confirms the requested run-level metadata is recorded:
  - `manifest.json.metadata.runtime_policy`
  - `manifest.json.metadata.task_id`
  - `manifest.json.metadata.scene_id`
  - `manifest.json.metadata.prompt_variant`
  - `manifest.json.metadata.runtime_variant`
- `block_a_summary.md` confirms the trend is stable across both toy and Isaac slices:
  - `P0/R0` failed on all 8 tasks with `termination_reason=invalid_action_limit`
  - `P0/R1` recovered and succeeded on all 8 tasks with `invalid_actions=1` and `retries=1` per run
  - `P1` succeeded on all 8 tasks under both `R0` and `R1`
  - `P2` succeeded on all 8 tasks under both `R0` and `R1`
  - in both toy and Isaac slices, `P2` uses fewer planner/tool calls than `P1`

## Blockers

- No outstanding blocker remains for the scoped `M6 block A navigation expansion`
- Resolved in this run:
  - preexisting incomplete old artifacts already occupied the requested output paths
  - action taken: backed them up to `_pre_refresh_20260316T105915Z` before rerunning the final suite
- Resolved in this run:
  - `src/isaacsim_agent/tasks/navigation/isaac_world.py` raised the undefined name `IsaacBackendUnavailableError` when Isaac imports were unavailable under normal Python
  - action taken: switched the failure path to `NavigationBackendUnavailableError`
  - impact: mixed-backend unit coverage now reports clean `task_precondition_failed` instead of `runtime_error`
- Agent-team note:
  - explorer agent `019cf63d-db1b-7950-8a00-7faf5c2cf032` eventually completed and returned a consistent summary
  - explorer agent `019cf63d-db33-79c3-82b6-a0376dec81bf` produced no output after waits of `60000 ms`, `120000 ms`, and `10000 ms`, plus one focused progress check
  - because its result was no longer on the critical path, it was closed and later reported `Interrupted`
  - no repository decision or code change depended on that unfinished agent output

## Recommended next step

- Review `results/processed/block_a_navigation_prompt_runtime_expanded/block_a_summary.md` and decide whether this 48-run navigation-only toy-plus-Isaac block A definition is stable enough to freeze as the navigation block A experiment
- If the design is accepted, the next recommended sub-milestone is still within M6 scope:
  - repeat the same navigation-only block A matrix with additional seeds or a slightly larger Isaac task slice
  - do not introduce `R2`, manipulation block A, memory/context, tool abstraction, randomization, or paper assets yet
