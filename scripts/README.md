# scripts

Runnable utilities such as setup checks, simulator smoke tests, baseline launchers, and evaluation entrypoints live here.

- `isaac_python.sh`: locate Isaac Sim and run the local `python.sh` wrapper
- `smoke_test_env.py`: verify the repo-facing Python and `uv` workflow
- `smoke_test_isaac.py`: verify Isaac Sim imports and minimal headless stage creation
- `validate_contracts.py`: emit a dummy run that exercises the shared task/result/event contracts
- `run_nav_baseline.py`: run the M2 minimal deterministic navigation baseline and write contract-compliant artifacts under `results/runs/<run_id>/`
