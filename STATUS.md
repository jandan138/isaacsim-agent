# STATUS.md

## Current status

- Date: 2026-03-16
- Plan source of truth: `plan.md`
- Active milestone: `M5.1 Easy Pilot Runs`
- Milestone state: completed for this repo run at the minimal post-M5, pre-M6 navigation-only pilot scope
- Completion level: the repo now has a config-driven easy pilot workflow that reuses the existing M1.5 contracts, M4 navigation-only runtime v0, and M5 eval harness to launch a very small local sequential run matrix, preserve canonical per-run artifacts, and emit pilot-level aggregate summaries for manual go/no-go review before any M6 ablations

## Milestone summary

- Completed in this run:
  - added a minimal pilot experiment config layer under `configs/experiments/pilot/` with one small easy navigation suite definition
  - added `src/isaacsim_agent/experiments/pilot.py` to load JSON-compatible YAML configs, validate the very small matrix size, expand task x prompt x runtime variants, and inject experiment metadata into `task_config.runtime_options.extra_options` and `task_config.metadata`
  - added `scripts/run_suite.py` to run the pilot suite sequentially through the existing M4 runtime entrypoint, preserve canonical run artifacts under `results/.../runs/<run_id>/`, reuse the M5 summarize/write path, and write `pilot_summary.json`, `pilot_summary.md`, and `run_plan.json`
  - extended the M4 runtime prompt construction so pilot runs can record and actually use config-supplied prompt text without changing the shared contracts
  - extended the M5 summary layer to preserve `prompt_variant` and explicit `runtime_variant` metadata in `run_summary.{jsonl,csv}` while keeping older fallback behavior intact
  - added `tests/test_run_suite_smoke.py` to cover config parsing, sequential pilot execution, canonical artifact writing, M5 summarize reuse, and pilot summary artifact generation
  - updated `configs/README.md`, `scripts/README.md`, and `results/schema.md` to document the pilot config location, suite runner, and derived pilot outputs
- Not completed in this run:
  - no full M6 block A implementation
  - no large sweep orchestration, parallel execution, dashboard, or scheduler integration
  - no memory, context, tool abstraction, randomization, or paper asset work
  - no manipulation runtime expansion
  - no retry/recovery/fallback stack beyond the pre-existing minimal invalid-action handling already present in M4
  - no second runtime variant beyond `R0`; the delivered pilot matrix is `3 tasks x 2 prompt variants x 1 runtime variant = 6 runs`

## Pilot workflow definition

- Supported scope:
  - navigation-only pilots
  - easy tasks only
  - very small local sequential execution only
  - current backend support limited to the lightweight `toy` path for this milestone
- Config schema highlights:
  - `experiment_name`
  - `description`
  - `task_family`
  - `execution_mode`
  - `backend`
  - `planner_backend`
  - `defaults`
  - `prompt_variants[]`
  - `runtime_variants[]`
  - `tasks[]`
- Canonical per-run reuse:
  - `manifest.json`
  - `task_config.json`
  - `episode_result.json`
  - `events.jsonl`
  - `artifacts/trajectory.json`
  - `artifacts/planner_trace.json`
  - `artifacts/tool_trace.json`
- Derived pilot outputs:
  - `run_summary.jsonl`
  - `run_summary.csv`
  - `aggregate.json`
  - `validation.json`
  - `pilot_summary.json`
  - `pilot_summary.md`
  - `run_plan.json`
- Per-run pilot metadata recorded in `task_config.json`:
  - `prompt_variant`
  - `runtime_variant`
  - `runtime_policy`
  - `planner_prompt_text`
  - `suite_experiment`
  - `metadata.prompting.instruction_text`

## Changed files

- `STATUS.md`
- `configs/README.md`
- `configs/experiments/pilot/easy_navigation_minimal.yaml`
- `results/schema.md`
- `scripts/README.md`
- `scripts/run_suite.py`
- `src/isaacsim_agent/eval/summarize.py`
- `src/isaacsim_agent/experiments/__init__.py`
- `src/isaacsim_agent/experiments/pilot.py`
- `src/isaacsim_agent/runtime/session.py`
- `tests/test_run_suite_smoke.py`

## Validation commands

- `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/experiments/pilot.py src/isaacsim_agent/experiments/__init__.py src/isaacsim_agent/runtime/session.py src/isaacsim_agent/eval/summarize.py scripts/run_suite.py tests/test_run_suite_smoke.py`
- `PYTHONPATH=src uv run python -m unittest tests.test_run_suite_smoke tests.test_eval_harness_smoke tests.test_agent_runtime_smoke tests.test_nav_smoke tests.test_pickplace_smoke`
- `mktemp -d /tmp/isaacsim-agent-pilot-e2e-XXXXXX`
- `PYTHONPATH=src uv run python scripts/run_suite.py --config configs/experiments/pilot/easy_navigation_minimal.yaml --results-root /tmp/isaacsim-agent-pilot-e2e-shjWmq/results --output-dir /tmp/isaacsim-agent-pilot-e2e-shjWmq/results/processed/easy_navigation_pilot_v0`
- `sed -n '1,220p' /tmp/isaacsim-agent-pilot-e2e-shjWmq/results/processed/easy_navigation_pilot_v0/pilot_summary.md`
- `sed -n '1,120p' /tmp/isaacsim-agent-pilot-e2e-shjWmq/results/processed/easy_navigation_pilot_v0/run_summary.jsonl`
- `git status --short`

## Validation results

- Python compilation check succeeded with no output
- Focused smoke coverage across the new pilot suite plus the existing M2.5/M3/M4/M5 paths passed with `Ran 10 tests in 19.738s` and `OK`
- Manual pilot suite e2e run succeeded at `/tmp/isaacsim-agent-pilot-e2e-shjWmq/results` with:
  - `Planned runs: 6`
  - `Runs scanned: 6`
  - `Contract-complete runs: 6`
  - `Run-complete runs: 6`
  - `Successful runs: 6`
- The manual e2e suite produced the expected derived files under `/tmp/isaacsim-agent-pilot-e2e-shjWmq/results/processed/easy_navigation_pilot_v0`:
  - `aggregate.json`
  - `pilot_summary.json`
  - `pilot_summary.md`
  - `run_plan.json`
  - `run_summary.csv`
  - `run_summary.jsonl`
  - `validation.json`
- The emitted `pilot_summary.md` shows:
  - 3 easy tasks exercised
  - 2 prompt variants exercised
  - 1 runtime variant exercised
  - per-variant rows for `P0/R0` and `P1/R0`
  - all 6 runs successful, contract-complete, and run-complete
- The emitted `run_summary.jsonl` preserves the requested pilot-facing identifiers and outcome fields for each run, including:
  - `task_id`
  - `scene_id`
  - `prompt_variant`
  - `runtime_variant`
  - `success`
  - `termination_reason`
  - `step_count`
  - `planner_calls`
  - `tool_calls`
  - `invalid_actions`
  - `run_complete`
  - `contract_complete`

## Blockers

- None within the scoped M5.1 easy pilot workflow
- A second runtime variant remains intentionally deferred until there is a concrete reason to extend beyond the current `R0` path

## Recommended next step

- Review the pilot prompt texts and the emitted `pilot_summary.md`, then decide whether to enter M6 with prompt-only ablations on the existing `R0` runtime first, or introduce one carefully scoped `R1` runtime variant only if a truly minimal validation-handling difference is needed
