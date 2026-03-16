# scripts

Runnable utilities such as setup checks, simulator smoke tests, baseline launchers, and evaluation entrypoints live here.

- `isaac_python.sh`: locate Isaac Sim and run the local `python.sh` wrapper
- `smoke_test_env.py`: verify the repo-facing Python and `uv` workflow
- `smoke_test_isaac.py`: verify Isaac Sim imports and minimal headless stage creation
- `validate_contracts.py`: emit a dummy run that exercises the shared task/result/event contracts
- `run_nav_baseline.py`: run the M2.5 minimal navigation baseline with either the Isaac-backed stage path (`--backend isaac`, recommended via `scripts/isaac_python.sh`) or the lightweight toy path (`--backend toy`) and write contract-compliant artifacts under `results/runs/<run_id>/`
- `run_pickplace_baseline.py`: run the M3 minimal pick-and-place baseline with the Isaac-backed stage path (`--backend isaac`, recommended via `scripts/isaac_python.sh`) or the lightweight reference path (`--backend toy`) and write contract-compliant artifacts under `results/runs/<run_id>/`
- `run_agent_v0.py`: run the M4 minimal planner/runtime path on top of the existing navigation baseline, write canonical run artifacts, and save `planner_trace.json` plus `tool_trace.json` under `artifacts/`
- `run_suite.py`: expand a very small config-driven easy navigation pilot matrix, launch sequential M4 runtime runs, then reuse the M5 summary path to emit canonical run summaries plus `pilot_summary.{json,md}` and `run_plan.json`
- `summarize_results.py`: scan a results root, validate run completeness, and export episode-level summary tables plus aggregate/validation JSON under `results/processed/` or a caller-specified output directory
