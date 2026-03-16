# isaacsim-agent

This repository hosts a milestone-driven scaffold for an embodied-agent study in NVIDIA Isaac Sim, following `plan.md` as the project source of truth.

## Scaffold status

This run only establishes the repository bootstrap needed before the plan-defined environment and simulator setup work. It does **not** claim that the Isaac Sim runtime, experiments, or paper artifacts are implemented yet.

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
