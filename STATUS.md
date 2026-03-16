# STATUS.md

## Current status

- Date: 2026-03-16
- Plan source of truth: `plan.md`
- Active milestone: `M2 Minimal Deterministic Navigation Baseline`
- Milestone state: completed for this repo run
- Completion level: one minimal deterministic navigation baseline is implemented, validated, and writing contract-compliant run artifacts; later milestones remain untouched

## Milestone summary

- Completed in this run:
  - defined one minimal navigation task: `minimal_deterministic_navigation` in scene `minimal_empty_stage`
  - encoded reset/start/target/success/termination semantics without changing the M1.5 schema
  - implemented a deterministic scripted straight-line controller with no planner, memory, recovery policy, or manipulation logic
  - added a repo-facing runner that writes `manifest.json`, `task_config.json`, `episode_result.json`, `events.jsonl`, and `artifacts/trajectory.json`
  - added navigation smoke tests and documented the baseline run command
- Not completed in this run:
  - Isaac-scene-backed robot navigation or Nav2 integration
  - manipulation, instruction following, LLM planner logic, memory, runtime policy, experiments, or paper-writing work

## M2 baseline definition

- Task: move a point robot from a fixed start pose to one fixed goal pose on an empty 2D plane
- Reset: restore the robot pose to `metadata.navigation_baseline.start_pose` and clear step/time/stuck counters
- Start: stored in `TaskConfig.metadata["navigation_baseline"]["start_pose"]`
- Target: stored in `TaskConfig.navigation.goal_pose` with `goal_ref="goal_marker_A"`
- Success condition: `distance_to_goal_m <= navigation.success_radius_m`
- Termination conditions:
  - `success`
  - `max_steps`
  - `max_time_sec`
  - `robot_stuck`

## Contract notes

- The M1.5 contracts were reused as-is; no schema changes were required
- Navigation-specific task details beyond the base contract are stored under `TaskConfig.metadata["navigation_baseline"]`
- The deterministic controller writes task-specific metrics using the required `navigation.*` namespace
- Extra trace data is written only under `artifacts/trajectory.json`, preserving the canonical top-level result layout

## Changed files

- `README.md`
- `STATUS.md`
- `scripts/README.md`
- `scripts/run_nav_baseline.py`
- `src/isaacsim_agent/tasks/__init__.py`
- `src/isaacsim_agent/tasks/navigation/__init__.py`
- `src/isaacsim_agent/tasks/navigation/baseline.py`
- `src/isaacsim_agent/tools/__init__.py`
- `src/isaacsim_agent/tools/navigation.py`
- `tests/test_nav_smoke.py`

## Validation commands

- `PYTHONPATH=src uv run python -m unittest tests.test_nav_smoke`
- `PYTHONPATH=src uv run python scripts/run_nav_baseline.py --run-id nav-baseline-smoke --results-root /tmp/isaacsim-agent-nav-smoke`
- `PYTHONPATH=src uv run python scripts/run_nav_baseline.py --run-id nav-baseline-ep1 --results-root /tmp/isaacsim-agent-nav-validation`
- `PYTHONPATH=src uv run python scripts/run_nav_baseline.py --run-id nav-baseline-ep2 --results-root /tmp/isaacsim-agent-nav-validation`
- `PYTHONPATH=src uv run python scripts/run_nav_baseline.py --run-id nav-baseline-ep3 --results-root /tmp/isaacsim-agent-nav-validation`
- `PYTHONPATH=src uv run python -m unittest discover -s tests -p 'test_*.py'`
- `git status --short`

## Validation results

- `tests.test_nav_smoke` passed with `Ran 2 tests in 0.170s` and `OK`
- `scripts/run_nav_baseline.py` succeeded for `nav-baseline-smoke` with `Termination: success`, `Steps: 4`, `Final goal distance (m): 0.0`, and `NAV_BASELINE_OK`
- Three additional scripted episodes (`nav-baseline-ep1`, `nav-baseline-ep2`, `nav-baseline-ep3`) all succeeded in 4 steps with `NAV_BASELINE_OK`
- Full test suite passed with `Ran 7 tests in 10.360s` and `OK`
- Run outputs were written in the canonical layout under:
  - `/tmp/isaacsim-agent-nav-smoke/runs/nav-baseline-smoke/`
  - `/tmp/isaacsim-agent-nav-validation/runs/nav-baseline-ep1/`
  - `/tmp/isaacsim-agent-nav-validation/runs/nav-baseline-ep2/`
  - `/tmp/isaacsim-agent-nav-validation/runs/nav-baseline-ep3/`
- Output files conformed to the M1.5 contract layout and included the navigation trajectory artifact under `artifacts/trajectory.json`

## Blockers

- None within the scoped M2 baseline
- The implemented baseline is intentionally pure Python and does not yet drive a real Isaac Sim robot asset; that limitation is a scope choice for this milestone, not a blocker for the current validation path

## Recommended next step

- Start `M3 Manipulation baseline` with the same contract discipline: one minimal deterministic pick-and-place task, one scripted baseline runner, contract-compliant artifacts, and lightweight validation first
