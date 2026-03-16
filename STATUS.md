# STATUS.md

## Current status

- Date: 2026-03-16
- Plan source of truth: `plan.md`
- Active milestone: `M5 Logging / Eval Harness`
- Milestone state: completed for this repo run at the minimal offline-harness scope
- Completion level: a reusable M5 episode-level eval harness now scans canonical run directories, validates contract completeness vs run completeness, emits script-friendly summary tables plus aggregate reports, and reuses the existing M1.5/M2.5/M3/M4 artifact layout without changing baseline or runtime writers; M6 and later milestones remain intentionally untouched

## Milestone summary

- Completed in this run:
  - added `src/isaacsim_agent/eval/` with a minimal offline loader, validator, and summarizer over the existing `manifest.json`, `task_config.json`, `episode_result.json`, `events.jsonl`, and `artifacts/*` conventions
  - defined lightweight `RunRecord`, `RunValidation`, `ValidationIssue`, `EpisodeSummary`, and aggregate bundle structures for M5 consumption
  - implemented results-root scanning across multiple runs plus tolerant field extraction for navigation baseline, manipulation baseline, and M4 agent-runtime outputs
  - implemented explicit bad-run detection for missing required files, JSON parse failures, missing core schema fields, cross-file identity mismatches, interrupted runs without `episode_end`, and missing referenced artifacts
  - implemented summary export to both `jsonl` and `csv`, plus `aggregate.json` and `validation.json`
  - added `scripts/summarize_results.py` with `summarize` and `validate` subcommands and caller-selectable output directories under `results/processed/`
  - added M5 smoke coverage for a successful baseline run, a successful agent-runtime run, and a contract-complete but artifact-incomplete bad run
  - updated `results/schema.md` and `scripts/README.md` to document processed outputs and the new CLI
- Not completed in this run:
  - no `run_suite.py` batch launcher yet; this run stayed within the minimal offline harness requested for M5
  - no step-level analytics, dashboard/web UI, large sweep system, memory/context/runtime ablations, manipulation runtime expansion, or large experiment launch
  - no changes to the shared M1.5 writer contracts or existing M2.5/M3/M4 smoke paths beyond read-only reuse by the new eval harness

## M5 harness definition

- Scan target:
  - one results root containing `runs/<run_id>/...`
  - or a direct `runs/` directory
- Contract-complete run:
  - all required canonical files exist
  - required JSON/JSONL files parse successfully
  - core identity fields are present and consistent across manifest/task/result
- Run-complete run:
  - contract-complete
  - `events.jsonl` includes an `episode_end` record
  - referenced artifacts expected by the run metadata exist on disk
- Episode-level summary fields emitted:
  - `run_id`
  - `task_family`
  - `task_id`
  - `scene_id`
  - `success`
  - `termination_reason`
  - `failure_reason`
  - `step_count`
  - `planner_calls`
  - `tool_calls`
  - `invalid_actions`
  - `episode_time_s`
  - `backend_variant`
  - `model_variant`
  - `runtime_variant`
  - `planner_backend`
  - `tool_variant`
  - completeness flags plus explicit validation issue codes/messages
- Derived outputs:
  - `run_summary.jsonl`
  - `run_summary.csv`
  - `aggregate.json`
  - `validation.json`

## Contract notes

- The M1.5 canonical run artifacts were reused as-is; no shared schema writer or baseline/runtime artifact writer was changed for M5
- M5 derived outputs now live under `results/processed/` or a caller-specified directory, while canonical per-run artifacts remain under `results/runs/<run_id>/`
- The harness intentionally stays at episode level for now; it does not attempt step-level analytics or experiment orchestration

## Changed files

- `STATUS.md`
- `results/schema.md`
- `scripts/README.md`
- `scripts/summarize_results.py`
- `src/isaacsim_agent/eval/__init__.py`
- `src/isaacsim_agent/eval/loader.py`
- `src/isaacsim_agent/eval/summarize.py`
- `src/isaacsim_agent/eval/validate.py`
- `tests/test_eval_harness_smoke.py`

## Validation commands

- `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/eval/__init__.py src/isaacsim_agent/eval/loader.py src/isaacsim_agent/eval/validate.py src/isaacsim_agent/eval/summarize.py scripts/summarize_results.py tests/test_eval_harness_smoke.py`
- `PYTHONPATH=src uv run python -m unittest tests.test_eval_harness_smoke tests.test_agent_runtime_smoke tests.test_nav_smoke tests.test_pickplace_smoke`
- `mktemp -d /tmp/isaacsim-agent-m5-e2e-XXXXXX`
- `PYTHONPATH=src uv run python - <<'PY'
from pathlib import Path

from isaacsim_agent.runtime import build_agent_v0_navigation_task_config
from isaacsim_agent.runtime import run_and_write_agent_v0
from isaacsim_agent.tasks.manipulation import build_minimal_pickplace_task_config
from isaacsim_agent.tasks.manipulation import run_and_write_pickplace_baseline
from isaacsim_agent.tasks.navigation import build_minimal_navigation_task_config
from isaacsim_agent.tasks.navigation import run_and_write_navigation_baseline

results_root = Path('/tmp/isaacsim-agent-m5-e2e-D5ZvaQ/results')
run_and_write_navigation_baseline(
    config=build_minimal_navigation_task_config(backend='toy'),
    run_id='m5-nav-good',
    results_root=results_root,
)
run_and_write_agent_v0(
    config=build_agent_v0_navigation_task_config(backend='toy'),
    run_id='m5-agent-good',
    results_root=results_root,
)
_, bad_layout = run_and_write_pickplace_baseline(
    config=build_minimal_pickplace_task_config(backend='toy'),
    run_id='m5-pickplace-missing-artifact',
    results_root=results_root,
)
(bad_layout.artifacts_dir / 'trajectory.json').unlink()
print(results_root)
PY`
- `PYTHONPATH=src uv run python scripts/summarize_results.py summarize --results-root /tmp/isaacsim-agent-m5-e2e-D5ZvaQ/results --output-dir /tmp/isaacsim-agent-m5-e2e-D5ZvaQ/results/processed/manual-summary`
- `find /tmp/isaacsim-agent-m5-e2e-D5ZvaQ/results/processed/manual-summary -maxdepth 1 -type f | sort`
- `PYTHONPATH=src uv run python scripts/summarize_results.py validate --results-root /tmp/isaacsim-agent-m5-e2e-D5ZvaQ/results --output-dir /tmp/isaacsim-agent-m5-e2e-D5ZvaQ/results/processed/manual-validate`
- `git status --short`

## Validation results

- Python compilation check succeeded with no output
- Focused M5 eval harness plus existing M2.5/M3/M4 smoke suite passed with `Ran 9 tests in 21.203s` and `OK`
- Manual sample results root `/tmp/isaacsim-agent-m5-e2e-D5ZvaQ/results` was created with:
  - one successful navigation baseline run `m5-nav-good`
  - one successful agent-runtime run `m5-agent-good`
  - one intentionally incomplete run `m5-pickplace-missing-artifact` created by deleting `artifacts/trajectory.json` after a successful pick-and-place baseline run
- End-to-end summarize CLI run succeeded with:
  - `Runs scanned: 3`
  - `Contract-complete runs: 3`
  - `Run-complete runs: 2`
  - `Successful runs: 3`
  - `Bad runs: 1`
  - output files written under `/tmp/isaacsim-agent-m5-e2e-D5ZvaQ/results/processed/manual-summary`
- Summary output directory contained the expected files:
  - `/tmp/isaacsim-agent-m5-e2e-D5ZvaQ/results/processed/manual-summary/aggregate.json`
  - `/tmp/isaacsim-agent-m5-e2e-D5ZvaQ/results/processed/manual-summary/run_summary.csv`
  - `/tmp/isaacsim-agent-m5-e2e-D5ZvaQ/results/processed/manual-summary/run_summary.jsonl`
  - `/tmp/isaacsim-agent-m5-e2e-D5ZvaQ/results/processed/manual-summary/validation.json`
- End-to-end validate CLI run returned exit code `1` by design and explicitly flagged the bad run:
  - `Incomplete runs: m5-pickplace-missing-artifact`
- The emitted `run_summary.jsonl` preserved the requested episode-level fields and marked the bad run as:
  - `contract_complete: true`
  - `run_complete: false`
  - `validation_issue_codes: ["missing_artifact"]`

## Blockers

- None within the scoped minimal M5 offline eval harness
- `run_suite.py` remains intentionally deferred rather than being a blocker for the requested minimal M5 deliverable

## Recommended next step

- M5.1: add a thin suite runner that launches a small hand-picked batch of existing baseline/runtime scripts and immediately calls `scripts/summarize_results.py` to populate `results/processed/`, still without introducing sweeps, dashboards, or M6 ablations
