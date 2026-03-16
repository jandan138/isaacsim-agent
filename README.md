# isaacsim-agent

This repository hosts a milestone-driven scaffold for an embodied-agent study in NVIDIA Isaac Sim, following `plan.md` as the project source of truth.

## Scaffold status

This repo now has the first minimal Isaac-backed task baseline in addition to the earlier scaffold and contract work. It still does **not** claim that LLM planning, memory, Nav2, manipulation, experiments, or paper artifacts are implemented.

## Current repository layout

```text
.
├── AGENTS.md
├── STATUS.md
├── README.md
├── plan.md
├── configs/
├── docs/
├── paper/
├── results/
├── scripts/
├── skills/
├── src/isaacsim_agent/
│   ├── planner/
│   ├── memory/
│   ├── runtime/
│   ├── tools/
│   ├── experiments/
│   └── paper/
└── tests/
```

## Milestone 1 bootstrap notes

- `src/isaacsim_agent/` contains importable placeholder packages for planner, memory, runtime, tools, experiments, and paper-facing utilities.
- `tests/test_scaffold_smoke.py` verifies the scaffold imports and required top-level directories.
- `STATUS.md` records the current milestone boundary, validations, known issues, and the next recommended sub-milestone.

## Minimal validation

Run the built-in smoke test from the repo root:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Environment setup

Milestone `M1` uses `uv` as the primary workflow for Python setup and uses the local Isaac Sim `python.sh` runtime only for scripts that must import `isaacsim`, `omni.*`, or `pxr`.

- Setup guide: `docs/setup.md`
- Isaac wrapper: `scripts/isaac_python.sh`
- Environment smoke test: `scripts/smoke_test_env.py`
- Isaac smoke test: `scripts/smoke_test_isaac.py`

## Shared contracts

Before task baselines begin, the repo now defines a project-wide contracts layer for task configs, episode results, event logs, metrics, and run artifact layout.

- Contract docs: `docs/contracts.md`
- Output schema guide: `results/schema.md`
- Validation script: `scripts/validate_contracts.py`

## M2.5 navigation baseline

Milestone `M2.5` upgrades the earlier toy navigation task into a minimal Isaac-backed baseline. The task stays tightly scoped on purpose: a procedural Isaac stage is created headlessly, a simple agent prim is reset to a fixed start pose, a fixed goal prim marks the target state, and a deterministic scripted controller moves the agent in straight-line steps until it reaches the success radius or terminates on `max_steps`, `max_time_sec`, or `robot_stuck`.

Run it from the repo root:

```bash
./scripts/isaac_python.sh scripts/run_nav_baseline.py --backend isaac --run-id demo-nav-baseline
```

For a fast non-Isaac contract smoke path, the legacy toy backend is still available:

```bash
uv run python scripts/run_nav_baseline.py --backend toy --run-id demo-nav-toy
```

The run writes canonical artifacts under `results/runs/<run_id>/`, including `manifest.json`, `task_config.json`, `episode_result.json`, `events.jsonl`, and `artifacts/trajectory.json`. Isaac-backed runs also export the minimal stage as `artifacts/stage.usda`.
