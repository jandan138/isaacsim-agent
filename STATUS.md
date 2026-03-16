# STATUS.md

## Current status

- Date: 2026-03-16
- Plan source of truth: `plan.md`
- Active milestone: `M6. Prompting and runtime ablations`
- Milestone state: completed for the scoped `M6 block A pilot subset` requested in this run
- Completion level: the repo now has a minimal, config-driven navigation-only block A pilot on top of the existing M1.5 contracts, M4 runtime v0, M5 eval harness, and completed easy pilot workflow, with `P0/P1/P2 x R0/R1` variants, manifest/summary metadata propagation, retry accounting, and first pilot summary artifacts ready for human review before any larger sweep

## Milestone summary

- Completed in this run:
  - added `src/isaacsim_agent/agent/` with a minimal prompting helper module for prompt-variant normalization, prompt rendering, and short retry-repair instruction text
  - preserved the existing `mock_rule_based` planner path used by the completed easy pilot, and added a separate `mock_block_a` planner backend for prompt-sensitive block A behavior so the old pilot contract and tests remain intact
  - extended `PlannerRequest` so runtime-injected prompt/runtime metadata and retry feedback can reach the planner without hand-editing code between conditions
  - extended the M4 navigation runtime so `R0` and `R1` are config-driven:
    - `R0`: no validation, no retry; invalid dispatches fail cleanly
    - `R1`: validation plus one retry on invalid action
  - reused the existing `recovery_count` contract field as retry count and propagated retry metadata through episode metrics, planner traces, manifests, and run summaries
  - extended the M5 summary layer to preserve `runtime_policy` and `retries` alongside the existing block-facing identifiers and outcome metrics
  - kept the existing `scripts/run_suite.py` / pilot config workflow and added a new block A config under `configs/experiments/block_a/`
  - added `tests/test_block_a_pilot_smoke.py` to cover the small `P0/P1/P2 x R0/R1` matrix, expected unsuccessful `P0/R0` runs, successful `P0/R1` retries, manifest metadata, and `block_a_pilot_summary.{json,md}` output generation
  - updated the config/script/results docs for the new block A pilot path and summary naming
- Not completed in this run:
  - no `R2` implementation
  - no full sweep or scheduler-style orchestration
  - no manipulation-runtime expansion
  - no memory, context, summarization, retrieval, tool abstraction, randomization, or paper asset work
  - no M7+ work

## Block A pilot definition

- Supported scope:
  - navigation-only
  - toy backend only for lightweight local pilot execution
  - 3 easy navigation tasks
  - prompt variants: `P0`, `P1`, `P2`
  - runtime variants: `R0`, `R1`
  - total matrix size: `18` runs
- Config entrypoint:
  - `configs/experiments/block_a/navigation_prompt_runtime_pilot.yaml`
- Reused execution path:
  - `scripts/run_suite.py`
  - `src/isaacsim_agent/experiments/pilot.py`
  - `src/isaacsim_agent/runtime/session.py`
  - `src/isaacsim_agent/eval/summarize.py`
- Derived outputs produced by the block A pilot:
  - `run_summary.jsonl`
  - `run_summary.csv`
  - `aggregate.json`
  - `validation.json`
  - `block_a_pilot_summary.json`
  - `block_a_pilot_summary.md`
  - `run_plan.json`
- Variant metadata now recorded across artifacts:
  - `manifest.json.metadata.prompt_variant`
  - `manifest.json.metadata.runtime_variant`
  - `manifest.json.metadata.runtime_policy`
  - `task_config.json.runtime_options.extra_options.prompt_variant`
  - `task_config.json.runtime_options.extra_options.runtime_variant`
  - `task_config.json.runtime_options.extra_options.runtime_policy`
  - `run_summary.{jsonl,csv}` fields for `prompt_variant`, `runtime_variant`, `runtime_policy`, `success`, `termination_reason`, `step_count`, `planner_calls`, `tool_calls`, `invalid_actions`, `retries`, `planner_latency_s`, and `episode_time_s`

## Changed files

- `STATUS.md`
- `configs/README.md`
- `configs/experiments/block_a/navigation_prompt_runtime_pilot.yaml`
- `results/schema.md`
- `scripts/README.md`
- `src/isaacsim_agent/agent/__init__.py`
- `src/isaacsim_agent/agent/prompting.py`
- `src/isaacsim_agent/contracts/models.py`
- `src/isaacsim_agent/eval/summarize.py`
- `src/isaacsim_agent/experiments/pilot.py`
- `src/isaacsim_agent/planner/__init__.py`
- `src/isaacsim_agent/planner/base.py`
- `src/isaacsim_agent/planner/mock.py`
- `src/isaacsim_agent/runtime/session.py`
- `tests/test_block_a_pilot_smoke.py`

## Validation commands

- `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/agent/__init__.py src/isaacsim_agent/agent/prompting.py src/isaacsim_agent/contracts/models.py src/isaacsim_agent/eval/summarize.py src/isaacsim_agent/experiments/pilot.py src/isaacsim_agent/planner/__init__.py src/isaacsim_agent/planner/base.py src/isaacsim_agent/planner/mock.py src/isaacsim_agent/runtime/session.py tests/test_block_a_pilot_smoke.py tests/test_run_suite_smoke.py tests/test_agent_runtime_smoke.py scripts/run_suite.py`
- `PYTHONPATH=src uv run python -m unittest tests.test_block_a_pilot_smoke tests.test_run_suite_smoke tests.test_agent_runtime_smoke tests.test_eval_harness_smoke`
- `mktemp -d /tmp/isaacsim-agent-block-a-e2e-XXXXXX`
- `PYTHONPATH=src uv run python scripts/run_suite.py --config configs/experiments/block_a/navigation_prompt_runtime_pilot.yaml --results-root /tmp/isaacsim-agent-block-a-e2e-6sSyLM/results --output-dir /tmp/isaacsim-agent-block-a-e2e-6sSyLM/results/processed/block_a_navigation_prompt_runtime_pilot_v0`
- `sed -n '1,240p' /tmp/isaacsim-agent-block-a-e2e-6sSyLM/results/processed/block_a_navigation_prompt_runtime_pilot_v0/block_a_pilot_summary.md`
- `sed -n '1,220p' /tmp/isaacsim-agent-block-a-e2e-6sSyLM/results/processed/block_a_navigation_prompt_runtime_pilot_v0/run_summary.jsonl`
- `git status --short`

## Validation results

- Python compilation check succeeded with no output
- Focused smoke coverage across the new block A pilot plus the existing easy-pilot/runtime/eval paths passed with `Ran 7 tests in 0.659s` and `OK`
- Manual block A pilot e2e run succeeded at `/tmp/isaacsim-agent-block-a-e2e-6sSyLM/results` with:
  - `Planned runs: 18`
  - `Runs scanned: 18`
  - `Contract-complete runs: 18`
  - `Run-complete runs: 18`
  - `Successful runs: 15`
- The manual e2e block A run produced the expected derived files under `/tmp/isaacsim-agent-block-a-e2e-6sSyLM/results/processed/block_a_navigation_prompt_runtime_pilot_v0`:
  - `aggregate.json`
  - `block_a_pilot_summary.json`
  - `block_a_pilot_summary.md`
  - `run_plan.json`
  - `run_summary.csv`
  - `run_summary.jsonl`
  - `validation.json`
- The emitted `block_a_pilot_summary.md` shows:
  - `P0/R0` failed on all 3 tasks with `termination_reason=invalid_action_limit`
  - `P0/R1` recovered and succeeded on all 3 tasks with `invalid_actions=1` and `retries=1` per run
  - `P1` and `P2` both succeeded on all 3 tasks under both `R0` and `R1`
  - `P2` used fewer planner/tool calls than `P1` on the same easy tasks in this minimal pilot
- The emitted `run_summary.jsonl` preserves the requested block-facing identifiers and outcome fields, including:
  - `prompt_variant`
  - `runtime_variant`
  - `runtime_policy`
  - `success`
  - `termination_reason`
  - `step_count`
  - `planner_calls`
  - `tool_calls`
  - `invalid_actions`
  - `retries`
  - `planner_latency_s`
  - `episode_time_s`

## Blockers

- No code blocker remained within the scoped `M6 block A pilot subset`
- Agent-team note:
  - explorer agent `019cf610-3af3-7a80-a66e-db16e696682d` produced no status update or output after two `wait` windows of `60000 ms` each
  - because its result was no longer on the critical path, it was closed after the second wait and later reported `Interrupted`
  - no repository decision or code change depended on that unfinished sub-agent output

## Recommended next step

- Review `/tmp/isaacsim-agent-block-a-e2e-6sSyLM/results/processed/block_a_navigation_prompt_runtime_pilot_v0/block_a_pilot_summary.md` and decide whether the current `P0/P1/P2` and `R0/R1` definitions are good enough to scale into a larger block A run, or whether the prompt/runtime semantics should be adjusted first
- Do not start a full sweep, `R2`, manipulation block A, or any M7+ work until that human review is complete
