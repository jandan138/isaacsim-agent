# STATUS.md

## Current status

- Date: 2026-03-16
- Plan source of truth: `plan.md`
- Active milestone: `M6. Prompting and runtime ablations`
- Milestone state: completed for the scoped `M6 block A cross-family analysis` requested in this run
- Completion level:
  - the prior `M6 block A navigation expansion` remains completed and available under `results/processed/block_a_navigation_prompt_runtime_expanded/`
  - the prior `M6 block A manipulation pilot` remains completed and available under `results/processed/block_a_manipulation_prompt_runtime_pilot/`
  - the new combined block A cross-family summary is completed and available under `results/processed/block_a_cross_family_summary/`

## Run context

- This run stayed within the requested boundaries:
  - block A only
  - no new experiments
  - reused the existing processed navigation and manipulation summaries
  - no `R2`
  - no `M7` memory/context work
  - no tool abstraction work
  - no randomization
- Input sources merged in this run:
  - `results/processed/block_a_navigation_prompt_runtime_expanded/`
  - `results/processed/block_a_manipulation_prompt_runtime_pilot/`
- Agent teaming:
  - used explorer sub-agents to inspect the cross-family statistics design and the minimal pipeline/test extension points
  - no sub-agent interruptions were needed

## Milestone summary

- Completed in this run:
  - added `src/isaacsim_agent/eval/cross_family.py` to merge existing processed block A summaries, rewrite merged canonical `run_summary.{jsonl,csv}` plus `aggregate.json` and `validation.json`, and emit the requested cross-family JSON/CSV/Markdown outputs
  - exported the new cross-family helper through `src/isaacsim_agent/eval/__init__.py`
  - added the new entrypoint `scripts/summarize_block_a_cross_family.py`
  - added focused coverage in `tests/test_block_a_cross_family_summary.py`
  - documented the new entrypoint in `scripts/README.md`
  - generated the requested processed outputs under `results/processed/block_a_cross_family_summary/`
- Not completed in this run:
  - no new navigation runs
  - no new manipulation runs
  - no `R2`
  - no `M7` work
  - no tool abstraction work
  - no randomization
  - no `M7+` work

## Cross-family summary results

- Merged overall result:
  - `total_runs = 66`
  - `contract_complete_runs = 66`
  - `run_complete_runs = 66`
  - `successful_runs = 55`
  - `success_rate = 0.833333`
  - `total_planner_calls = 317`
  - `total_tool_calls = 295`
  - `total_invalid_actions = 22`
  - `total_retries = 11`
- Per-family overview from the merged `aggregate.json` / `cross_family_summary.json`:
  - `navigation`: `48` runs, `success_rate = 0.833333`, `total_invalid_actions = 16`, `total_retries = 8`
  - `pick_place` (`Manipulation` in the cross-family tables): `18` runs, `success_rate = 0.833333`, `total_invalid_actions = 6`, `total_retries = 3`
- Cross-task takeaways surfaced by the new tables:
  - `P0/R0` is the only failing cell in both families:
    - navigation: `success_rate = 0.0`, `average_invalid_actions = 1.0`, `average_planner_calls = 1.0`, `average_tool_calls = 0.0`
    - manipulation: `success_rate = 0.0`, `average_invalid_actions = 1.0`, `average_planner_calls = 1.0`, `average_tool_calls = 0.0`
  - `P0/R1` recovers in both families:
    - navigation: `success_rate = 1.0`, `average_retries = 1.0`, `average_planner_calls = 3.875`, `average_tool_calls = 2.875`
    - manipulation: `success_rate = 1.0`, `average_retries = 1.0`, `average_planner_calls = 9.0`, `average_tool_calls = 8.0`
  - `P1` and `P2` succeed across both families with zero invalid actions and zero retries
  - manipulation remains more planner/tool intensive than navigation:
    - `P1`: navigation average planner/tool calls `4.875` vs manipulation `10.0`
    - `P2`: navigation average planner/tool calls `3.875` vs manipulation `8.0`

## Files changed

- `STATUS.md`
- `scripts/README.md`
- `scripts/summarize_block_a_cross_family.py`
- `src/isaacsim_agent/eval/__init__.py`
- `src/isaacsim_agent/eval/cross_family.py`
- `tests/test_block_a_cross_family_summary.py`

## Generated outputs

- `results/processed/block_a_cross_family_summary/run_summary.jsonl`
- `results/processed/block_a_cross_family_summary/run_summary.csv`
- `results/processed/block_a_cross_family_summary/aggregate.json`
- `results/processed/block_a_cross_family_summary/validation.json`
- `results/processed/block_a_cross_family_summary/cross_family_summary.json`
- `results/processed/block_a_cross_family_summary/cross_family_summary.csv`
- `results/processed/block_a_cross_family_summary/block_a_cross_family_summary.md`

## Commands run

- Source-of-truth reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,260p' AGENTS.md`
  - `sed -n '1,260p' STATUS.md`
- Repo and pipeline inspection:
  - `git status --short`
  - `rg -n "cross_family|cross-family|block_a_summary|run_summary|aggregate" src scripts tests configs results/processed -g '!results/**/runs/**'`
  - `find results/processed -maxdepth 2 -type f \( -path 'results/processed/block_a_navigation_prompt_runtime_expanded/*' -o -path 'results/processed/block_a_manipulation_prompt_runtime_pilot/*' \) | sort`
  - `sed -n '1,360p' src/isaacsim_agent/eval/summarize.py`
  - `sed -n '420,920p' src/isaacsim_agent/experiments/pilot.py`
  - `sed -n '1,260p' tests/test_block_a_expanded_smoke.py`
  - `sed -n '1,260p' tests/test_block_a_manipulation_pilot_smoke.py`
  - `sed -n '1,220p' src/isaacsim_agent/eval/__init__.py`
  - `sed -n '1,240p' tests/test_eval_harness_smoke.py`
  - `sed -n '1,220p' scripts/README.md`
  - `sed -n '1,220p' scripts/run_suite.py`
  - `find src/isaacsim_agent -maxdepth 2 -type f | sort`
  - `python - <<'PY' ... inspect block_a_summary.json and run_summary.jsonl schemas ... PY`
- Validation and output generation:
  - `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/eval/cross_family.py src/isaacsim_agent/eval/__init__.py scripts/summarize_block_a_cross_family.py tests/test_block_a_cross_family_summary.py`
  - `PYTHONPATH=src uv run python -m unittest tests.test_block_a_cross_family_summary tests.test_eval_harness_smoke tests.test_run_suite_smoke`
  - `find results/processed -maxdepth 1 -type d -name 'block_a_cross_family_summary' | sort`
  - `PYTHONPATH=src uv run python scripts/summarize_block_a_cross_family.py`
  - `find results/processed/block_a_cross_family_summary -maxdepth 1 -type f | sort`
  - `python - <<'PY' ... inspect cross_family_summary.json table payloads ... PY`
  - `sed -n '1,240p' results/processed/block_a_cross_family_summary/block_a_cross_family_summary.md`
  - `PYTHONPATH=src uv run python -m unittest tests.test_block_a_cross_family_summary tests.test_block_a_expanded_smoke tests.test_block_a_manipulation_pilot_smoke tests.test_eval_harness_smoke tests.test_run_suite_smoke`

## Validation results

- Python compilation succeeded:
  - command: `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/eval/cross_family.py src/isaacsim_agent/eval/__init__.py scripts/summarize_block_a_cross_family.py tests/test_block_a_cross_family_summary.py`
  - result: success with no output
- Focused unit/smoke coverage for the new cross-family path succeeded:
  - command: `PYTHONPATH=src uv run python -m unittest tests.test_block_a_cross_family_summary tests.test_eval_harness_smoke tests.test_run_suite_smoke`
  - result:
    - `Ran 5 tests in 0.505s`
    - `OK`
- Broader block-A regression coverage succeeded:
  - command: `PYTHONPATH=src uv run python -m unittest tests.test_block_a_cross_family_summary tests.test_block_a_expanded_smoke tests.test_block_a_manipulation_pilot_smoke tests.test_eval_harness_smoke tests.test_run_suite_smoke`
  - result:
    - `Ran 9 tests in 0.840s`
    - `OK`
- Cross-family summary generation succeeded against the real processed inputs:
  - command: `PYTHONPATH=src uv run python scripts/summarize_block_a_cross_family.py`
  - result:
    - `Input 1 runs: 48`
    - `Input 2 runs: 18`
    - `Merged runs: 66`
    - `Run-complete runs: 66`
    - `Successful runs: 55`
    - outputs written under `results/processed/block_a_cross_family_summary/`
- The generated markdown tables match the expected block-A trends:
  - Table 1 shows `P0/R0` fails in both families and `P0/R1` recovers to `1.0` success rate in both
  - Table 2 shows invalid-action frequency is `1.0` only for `P0` rows and `0.0` for `P1`/`P2`
  - Table 3 shows manipulation is consistently more planner/tool intensive than navigation for `P0/R1`, `P1`, and `P2`

## Blockers

- None.

## Next recommended step

- Use the new `results/processed/block_a_cross_family_summary/` artifacts for the planned M6 analysis checkpoint or paper-facing results drafting, while keeping the experiment scope frozen unless a later run explicitly authorizes work beyond block A.
