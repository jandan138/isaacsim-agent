# STATUS.md

## Current status

- Date: 2026-03-16
- Plan source of truth: `plan.md`
- Active milestone: `M3 Minimal Isaac-backed Pick-and-Place Baseline`
- Milestone state: completed for this repo run
- Completion level: one minimal Isaac-backed pick-and-place baseline is implemented, validated, and writing contract-compliant run artifacts; M0, M1, M1.5, M2, and M2.5 remain completed, while M4 and later milestones remain intentionally untouched

## Milestone summary

- Completed in this run:
  - implemented a minimal deterministic manipulation baseline that mirrors the M2.5 navigation runner/result/artifact pattern
  - added a manipulation tool module with `Pose3D`, scripted pick-place actions, and 3D path-length helpers
  - created a shared scripted pick-place state machine with fixed reset state, fixed phase order, explicit success criteria, and explicit failure termination reasons
  - added an Isaac-backed manipulation world that uses a procedural USD stage with `/World`, `/World/PhysicsScene`, one gripper marker prim, one object prim, and fixed source/target zone prims
  - added a contract-compliant runner script and smoke tests, including a clean blocker path when Isaac is unavailable
  - extended contract tests with a `pick_place` round-trip to verify the M1.5 schema is still used as-is
- Not completed in this run:
  - no complex articulated arm stack, grasp planner, IK, motion planning, perception, learned policy, LLM planner, memory, runtime policy, experiments, or M4+ runtime work
  - no extra manipulation scenes, distractors, domain randomization, or long-horizon sequencing beyond the single scripted baseline

## M3 baseline definition

- Task: move one object from a fixed source pose to one fixed target pose inside a minimal headless Isaac stage using a fixed scripted pick, lift, transfer, place, and retreat sequence
- Isaac world setup:
  - `/World` root prim
  - `/World/PhysicsScene`
  - `/World/Gripper` sphere prim as the controllable end-effector marker
  - `/World/Object` cube prim as the manipulated object
  - `/World/SourceZone` cube prim as the source marker
  - `/World/TargetZone` cube prim as the place target marker
- Reset: restore the gripper and object poses from `metadata.manipulation_baseline.start_state`, open the gripper, clear the phase counter, and detach the object
- Start: stored in `TaskConfig.metadata["manipulation_baseline"]["start_state"]`
- Target: stored in `TaskConfig.pick_place.target_pose` with `object_id="block_A"`, `source_id="source_zone_A"`, and `target_id="target_zone_B"`
- Step logic: execute the next deterministic scripted phase from `metadata.manipulation_baseline.scripted_sequence`, update the gripper pose, attach the object during the grasp phase when within tolerance, carry it during transfer, release it during the place phase, and advance the stage a fixed number of updates
- Success condition: scripted sequence completes and the object is released within `place_tolerance_m` of `pick_place.target_pose`
- Termination conditions:
  - `success`
  - `max_steps`
  - `max_time_sec`
  - `tool_failure`

## Contract notes

- The M1.5 contracts were reused as-is; no schema changes were required
- Manipulation-specific task details live under `TaskConfig.metadata["manipulation_baseline"]`
- The fixed object target remains under `TaskConfig.pick_place.target_pose`
- Backend and minimal Isaac world settings are recorded under `metadata.manipulation_baseline.backend` and `metadata.manipulation_baseline.isaac`
- Task-specific metrics remain namespaced under `manipulation.*`
- Extra trace data stays under `artifacts/`, with:
  - `artifacts/trajectory.json` for the scripted gripper/object state trace
  - `artifacts/stage.usda` for the exported minimal Isaac stage

## Changed files

- `STATUS.md`
- `scripts/README.md`
- `scripts/run_pickplace_baseline.py`
- `src/isaacsim_agent/tasks/__init__.py`
- `src/isaacsim_agent/tasks/manipulation/__init__.py`
- `src/isaacsim_agent/tasks/manipulation/baseline.py`
- `src/isaacsim_agent/tasks/manipulation/isaac_world.py`
- `src/isaacsim_agent/tools/__init__.py`
- `src/isaacsim_agent/tools/manipulation.py`
- `tests/test_contracts.py`
- `tests/test_pickplace_smoke.py`

## Validation commands

- `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/tools/manipulation.py src/isaacsim_agent/tasks/manipulation/baseline.py src/isaacsim_agent/tasks/manipulation/isaac_world.py scripts/run_pickplace_baseline.py tests/test_pickplace_smoke.py`
- `PYTHONPATH=src uv run python -m unittest tests.test_contracts tests.test_pickplace_smoke`
- `PYTHONPATH=src uv run python - <<'PY'
from isaacsim_agent.tasks.manipulation import build_minimal_pickplace_task_config
from isaacsim_agent.tasks.manipulation import execute_pickplace_baseline
for index in range(3):
    run_data = execute_pickplace_baseline(
        config=build_minimal_pickplace_task_config(backend='toy'),
        run_id=f'toy-pickplace-episode-{index}',
    )
    print(
        f'episode={index} success={run_data.result.success} '
        f'termination={run_data.result.termination_reason.value} '
        f'steps={run_data.result.step_count} '
        f'distance={run_data.result.metrics["manipulation.final_object_to_target_distance_m"]}'
    )
PY`
- `PYTHONPATH=src uv run python -m unittest discover -s tests -p 'test_*.py'`
- `bash -lc './scripts/isaac_python.sh scripts/run_pickplace_baseline.py --backend isaac --run-id pickplace-isaac-smoke-1 --results-root /tmp/isaacsim-agent-pickplace-isaac-1 > /tmp/pickplace_isaac_smoke_1.log 2>&1; printf "RC=%s\n" "$?"'`
- `git status --short`

## Validation results

- Python compilation check succeeded with no output
- Focused contract + pick-place smoke tests passed with `Ran 4 tests in 11.869s` and `OK`
- Three lightweight scripted toy episodes all succeeded with:
  - `episode=0 success=True termination=success steps=8 distance=0.0`
  - `episode=1 success=True termination=success steps=8 distance=0.0`
  - `episode=2 success=True termination=success steps=8 distance=0.0`
- Full test suite passed with `Ran 9 tests in 33.270s` and `OK`
- Isaac-backed wrapper run succeeded with:
  - shell return code `RC=0`
  - run directory `/tmp/isaacsim-agent-pickplace-isaac-1/runs/pickplace-isaac-smoke-1/`
  - `Termination: success`
  - `Steps: 8`
  - `Final object-to-target distance (m): 0.0`
  - `PICKPLACE_BASELINE_OK`
  - canonical artifacts present:
    - `/tmp/isaacsim-agent-pickplace-isaac-1/runs/pickplace-isaac-smoke-1/manifest.json`
    - `/tmp/isaacsim-agent-pickplace-isaac-1/runs/pickplace-isaac-smoke-1/task_config.json`
    - `/tmp/isaacsim-agent-pickplace-isaac-1/runs/pickplace-isaac-smoke-1/episode_result.json`
    - `/tmp/isaacsim-agent-pickplace-isaac-1/runs/pickplace-isaac-smoke-1/events.jsonl`
    - `/tmp/isaacsim-agent-pickplace-isaac-1/runs/pickplace-isaac-smoke-1/artifacts/trajectory.json`
    - `/tmp/isaacsim-agent-pickplace-isaac-1/runs/pickplace-isaac-smoke-1/artifacts/stage.usda`
  - `episode_result.json` recorded `success=true`, `termination_reason="success"`, `step_count=8`, `manipulation.backend="isaac"`, `manipulation.grasp_completed=true`, `manipulation.object_placed=true`, and `manipulation.stage_artifact_written=true`

## Blockers

- None within the scoped M3 baseline
- Isaac Sim still emits expected headless startup and shutdown warnings in this environment (for example RTX, graph-category, and audio-context warnings), but the minimal baseline run succeeds and writes the expected artifacts

## Isaac runtime handoff notes

- Run Isaac-backed scripts through `./scripts/isaac_python.sh`; plain `uv` Python cannot import `isaacsim`, `omni.*`, or `pxr`
- Keep repo imports working under Isaac Python by ensuring `src/` is added to `sys.path` in script entrypoints that run through the wrapper
- Headless Isaac runs on this machine print many warnings during startup and shutdown; treat them as expected unless the run fails to produce artifacts or exits non-zero
- Prefer the current minimal `SimulationApp + omni.usd + pxr.UsdGeom` path for controlled baselines; avoid pulling in deprecated `omni.isaac.*` APIs or heavier controller stacks unless a later milestone explicitly needs them
- `run_and_write_pickplace_baseline()` writes `manifest.json` and `task_config.json` before execution; if an Isaac run is interrupted or crashes early, a partially populated run directory can exist and should not be mistaken for a successful contract-complete run

## Recommended next step

- Stay within M3 scope and add one deterministic failure-path smoke case for grasp or place miss before unfreezing any later milestone
