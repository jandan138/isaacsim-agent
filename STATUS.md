# STATUS.md

## Current status

- Date: 2026-03-16
- Plan source of truth: `plan.md`
- Active milestone: `M2.5 Minimal Isaac-backed Navigation Baseline`
- Milestone state: completed for this repo run
- Completion level: one minimal Isaac-backed navigation baseline is implemented, validated, and writing contract-compliant run artifacts; manipulation and later milestones remain untouched

## Milestone summary

- Completed in this run:
  - upgraded the earlier toy navigation runner into a dual-backend baseline with an Isaac-backed path as the primary M2.5 entrypoint
  - created a minimal procedural Isaac stage with `/World`, `/World/PhysicsScene`, one agent prim, and one goal prim
  - preserved the M1.5 task/result/event contracts and reused the M2 runner/result layout
  - kept the controller deterministic and scripted with no LLM planner, memory, Nav2, recovery policy, or complex assets
  - added stage export under `artifacts/stage.usda` for Isaac-backed runs
  - updated smoke tests and repo docs for the Isaac wrapper workflow
- Not completed in this run:
  - full navigation stack integration, Nav2, scene complexity, sensors, or obstacle-rich navigation
  - manipulation, instruction following, LLM planner logic, memory, runtime policy, experiments, or paper-writing work

## M2.5 baseline definition

- Task: move one minimal agent marker from a fixed start pose to one fixed goal pose inside a headless procedural Isaac stage
- Isaac world setup:
  - `/World` root prim
  - `/World/PhysicsScene`
  - `/World/Robot` sphere prim as the controllable agent representation
  - `/World/Goal` cube prim as the target marker
- Reset: restore the agent prim to `metadata.navigation_baseline.start_pose` and clear step/time/stuck counters
- Start: stored in `TaskConfig.metadata["navigation_baseline"]["start_pose"]`
- Target: stored in `TaskConfig.navigation.goal_pose` with `goal_ref="goal_marker_A"` and mirrored to the goal prim in the stage
- Step logic: compute the next deterministic straight-line step with the existing scripted controller, apply the pose to the Isaac agent prim, and advance the stage a fixed number of updates
- Success condition: `distance_to_goal_m <= navigation.success_radius_m`
- Termination conditions:
  - `success`
  - `max_steps`
  - `max_time_sec`
  - `robot_stuck`

## Contract notes

- The M1.5 contracts were reused as-is; no schema changes were required
- Navigation-specific task details remain under `TaskConfig.metadata["navigation_baseline"]`
- Backend and minimal Isaac world settings are recorded under `metadata.navigation_baseline.backend` and `metadata.navigation_baseline.isaac`
- Task-specific metrics remain namespaced under `navigation.*`
- Extra trace data stays under `artifacts/`, with:
  - `artifacts/trajectory.json` for the deterministic pose trace
  - `artifacts/stage.usda` for the exported minimal Isaac stage

## Changed files

- `README.md`
- `STATUS.md`
- `docs/setup.md`
- `scripts/README.md`
- `scripts/run_nav_baseline.py`
- `src/isaacsim_agent/tasks/navigation/baseline.py`
- `src/isaacsim_agent/tasks/navigation/isaac_world.py`
- `tests/test_nav_smoke.py`

## Validation commands

- `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/tasks/navigation/baseline.py src/isaacsim_agent/tasks/navigation/isaac_world.py scripts/run_nav_baseline.py`
- `PYTHONPATH=src uv run python scripts/run_nav_baseline.py --backend toy --run-id nav-toy-smoke-2 --results-root /tmp/isaacsim-agent-nav-toy-2`
- `bash -lc './scripts/isaac_python.sh scripts/run_nav_baseline.py --backend isaac --run-id nav-isaac-smoke-3 --results-root /tmp/isaacsim-agent-nav-isaac-3 > /tmp/nav_isaac_smoke_3.log 2>&1; printf "RC=%s\n" "$?"'`
- `PYTHONPATH=src uv run python -m unittest tests.test_nav_smoke`
- `PYTHONPATH=src uv run python -m unittest discover -s tests -p 'test_*.py'`
- `git status --short`

## Validation results

- Python compilation check succeeded with no output
- Toy backend smoke run succeeded with:
  - run directory `/tmp/isaacsim-agent-nav-toy-2/runs/nav-toy-smoke-2/`
  - `Termination: success`
  - `Steps: 4`
  - `Final goal distance (m): 0.0`
  - `NAV_BASELINE_OK`
- Isaac-backed wrapper run succeeded with:
  - shell return code `RC=0`
  - log markers `Run directory: /tmp/isaacsim-agent-nav-isaac-3/runs/nav-isaac-smoke-3`
  - `Termination: success`
  - `NAV_BASELINE_OK`
  - canonical artifacts present:
    - `/tmp/isaacsim-agent-nav-isaac-3/runs/nav-isaac-smoke-3/manifest.json`
    - `/tmp/isaacsim-agent-nav-isaac-3/runs/nav-isaac-smoke-3/task_config.json`
    - `/tmp/isaacsim-agent-nav-isaac-3/runs/nav-isaac-smoke-3/episode_result.json`
    - `/tmp/isaacsim-agent-nav-isaac-3/runs/nav-isaac-smoke-3/events.jsonl`
    - `/tmp/isaacsim-agent-nav-isaac-3/runs/nav-isaac-smoke-3/artifacts/trajectory.json`
    - `/tmp/isaacsim-agent-nav-isaac-3/runs/nav-isaac-smoke-3/artifacts/stage.usda`
  - `episode_result.json` recorded `success=true`, `termination_reason="success"`, `step_count=4`, `navigation.backend="isaac"`, and `navigation.stage_artifact_written=true`
- `tests.test_nav_smoke` passed with `Ran 2 tests in 14.787s` and `OK`
- Full test suite passed with `Ran 7 tests in 25.959s` and `OK`

## Blockers

- None within the scoped M2.5 baseline
- Isaac Sim still emits expected headless startup warnings in this environment (for example GLFW/audio/display warnings), but the minimal baseline run succeeds and writes the expected artifacts

## Isaac runtime handoff notes

- Run Isaac-backed scripts through `./scripts/isaac_python.sh`; plain `uv` Python cannot import `isaacsim`, `omni.*`, or `pxr`
- Keep repo imports working under Isaac Python by ensuring `src/` is added to `sys.path` in script entrypoints that run through the wrapper
- Headless Isaac runs on this machine print many GLFW/audio/display warnings during startup; treat them as expected unless the run fails to produce artifacts or exits non-zero
- Isaac startup is much heavier than toy-path Python execution, so keep tests minimal and avoid spawning extra `SimulationApp` instances when a toy-path check is enough
- Prefer the current minimal `SimulationApp + omni.usd + pxr.UsdGeom` path for controlled baselines; avoid pulling in deprecated `omni.isaac.*` APIs or heavier world/controller stacks unless a later milestone explicitly needs them
- `run_and_write_navigation_baseline()` writes `manifest.json` and `task_config.json` before execution; if an Isaac run is interrupted or crashes early, a partially populated run directory can exist and should not be mistaken for a successful contract-complete run

## Recommended next step

- Start `M3 Manipulation baseline` with the same contract discipline: one minimal deterministic pick-and-place task, one scripted baseline runner, contract-compliant artifacts, and lightweight validation first
