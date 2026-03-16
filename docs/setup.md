# Setup

This project uses `uv` as the default Python workflow and treats the local Isaac Sim runtime as a separate execution context for simulator imports.

## Target Python version

- Target interpreter for this repo: Python `3.10`
- Tracked in `.python-version`
- Declared in `pyproject.toml` as `>=3.10,<3.11`

This matches the local Isaac Sim installation on this machine, where `/isaac-sim/python.sh` currently provides an Isaac Sim 4.5.0 Python 3.10 runtime.

## Recommended workflow with `uv`

From the repo root:

```bash
uv sync --python 3.10
uv run python scripts/smoke_test_env.py
uv run python -m unittest discover -s tests -p 'test_*.py'
```

### Why `uv` is primary here

- `uv` manages the project environment, lockfile, and normal Python execution.
- Isaac Sim module imports are **not** installed from PyPI in this repo.
- Scripts that need Isaac Sim should run through `scripts/isaac_python.sh`, which delegates to the local Isaac Sim `python.sh`.

## Isaac Sim installation assumptions on this machine

The smoke-test and wrapper scripts use this search order:

1. `ISAAC_SIM_ROOT` if it points to a directory containing `python.sh`
2. `/isaac-sim`
3. the newest `isaac_sim-*` directory under `$HOME/.local/share/ov/pkg`
4. `/opt/nvidia/isaac-sim`
5. `/opt/NVIDIA/isaac-sim`
6. `/opt/omniverse/isaac-sim`

### Discovered local installation

During this run, Isaac Sim was found at:

- `/isaac-sim`
- runner: `/isaac-sim/python.sh`
- version file: `/isaac-sim/VERSION`
- detected version string: `4.5.0-rc.36+release.19112.f59b3005.gl`

## Recommended environment variables

- `ISAAC_SIM_ROOT` — optional override when Isaac Sim is installed somewhere other than the default search paths
- `OMNI_KIT_ACCEPT_EULA=YES` — recommended for non-interactive smoke-test runs

Example:

```bash
export ISAAC_SIM_ROOT=/isaac-sim
export OMNI_KIT_ACCEPT_EULA=YES
```

## Smoke-test usage

### 1. Repo environment smoke test

Runs inside the `uv` environment and checks the repo-facing Python setup:

```bash
uv run python scripts/smoke_test_env.py
```

### 2. Isaac Sim smoke test

Runs inside Isaac Sim's Python runtime:

```bash
./scripts/isaac_python.sh scripts/smoke_test_isaac.py
```

Expected behavior:

- If Isaac Sim is available and the script is launched through `scripts/isaac_python.sh`, it imports the required modules, starts a headless `SimulationApp`, creates a minimal stage with `/World`, prints diagnostics, and exits `0`.
- If Isaac Sim is unavailable, or if the script is launched with a Python interpreter that cannot import Isaac Sim modules, it exits in an explicit `EXPECTED_MISSING_DEPENDENCY` mode with exit code `3`.

### 3. Minimal Isaac-backed navigation baseline

Milestone `M2.5` is the first task baseline that should be launched through the Isaac runtime itself.

```bash
./scripts/isaac_python.sh scripts/run_nav_baseline.py --backend isaac --run-id demo-nav-isaac
```

Expected behavior:

- the script creates a minimal Isaac stage with one agent prim and one goal prim
- the agent resets to the configured start pose and moves deterministically toward the goal
- canonical run artifacts are written under `results/runs/<run_id>/`
- Isaac-backed runs also export `artifacts/stage.usda`

## Minimal reproducible validation sequence

```bash
mkdir -p results/setup
uv sync --python 3.10
uv run python scripts/smoke_test_env.py --json-out results/setup/smoke_test_env.json 2>&1 | tee results/setup/smoke_test_env.log
./scripts/isaac_python.sh scripts/smoke_test_isaac.py --json-out results/setup/smoke_test_isaac.json 2>&1 | tee results/setup/smoke_test_isaac.log
./scripts/isaac_python.sh scripts/run_nav_baseline.py --backend isaac --run-id setup-nav-isaac 2>&1 | tee results/setup/run_nav_baseline.log
uv run python -m unittest discover -s tests -p 'test_*.py' 2>&1 | tee results/setup/unittest.log
```

## Isaac runtime gotchas

- Use `scripts/isaac_python.sh` for any script that imports `isaacsim`, `omni.*`, or `pxr`; `uv` remains the default for everything else
- Isaac Python does not automatically know about this repo package, so Isaac-backed script entrypoints should add `src/` to `sys.path`
- Headless runs in this environment emit many GLFW/audio/display warnings even when the run is healthy
- A partial run directory containing only `manifest.json` and `task_config.json` usually means execution started but did not finish; only treat the run as complete when `episode_result.json`, `events.jsonl`, and the expected artifacts are present
