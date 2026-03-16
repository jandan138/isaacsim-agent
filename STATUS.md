# STATUS.md

## Current status

- Date: 2026-03-16
- Plan source of truth: `plan.md`
- Active milestone: `M6. Prompting and runtime ablations`
- Milestone state: completed for the scoped `M6 Block A result packaging` requested in this run
- Completion level:
  - the canonical Block A master summary remains available under `results/processed/block_a_master_summary/`
  - the new paper-facing Block A package is now available under:
    - `results/processed/block_a_master_summary/paper_tables/`
    - `results/processed/block_a_master_summary/paper_figures/`
    - `results/processed/block_a_master_summary/analysis/`
  - the previously generated Block A processed summaries remain available under:
    - `results/processed/block_a_navigation_prompt_runtime_pilot/`
    - `results/processed/block_a_navigation_prompt_runtime_expanded/`
    - `results/processed/block_a_manipulation_prompt_runtime_pilot/`
    - `results/processed/block_a_cross_family_summary/`
    - `results/processed/block_a_navigation_prompt_runtime_robustness/`

## Run context

- This run stayed within the requested boundaries:
  - Block A result packaging only
  - no new experiments
  - no `M7` memory/context work
  - no tool abstraction work
  - no randomization work
  - no heavy Isaac Sim / ROS workflow launch
- Existing artifacts reused in this run:
  - `results/processed/block_a_master_summary/block_a_master_summary.json`
  - `results/processed/block_a_master_summary/block_a_master_summary.csv`
  - `results/processed/block_a_master_summary/block_a_master_summary.md`
  - the existing processed Block A source slices referenced by the master summary
- Existing uncommitted worktree changes outside this packaging task remained in place and were not reverted:
  - `src/isaacsim_agent/experiments/pilot.py`
  - `configs/experiments/block_a/navigation_prompt_runtime_robustness.yaml`
  - `tests/test_block_a_robustness_smoke.py`
  - `scripts/summarize_block_a_master.py`
  - `src/isaacsim_agent/eval/block_a_master.py`
  - `tests/test_block_a_master_summary.py`
- Agent teaming:
  - spawned two explorer sub-agents to inspect the master-summary schema and reusable paper-output conventions
  - both sub-agents showed no output or status change across three wait windows (`30s`, `60s`, `120s`)
  - once the local implementation no longer depended on them, they were closed; the platform reported both as `Interrupted`
  - interruption reason recorded here per repo guidance: prolonged no-progress observation with the result no longer on the critical path

## Milestone summary

- Completed in this run:
  - added `src/isaacsim_agent/eval/block_a_paper.py`
  - added `scripts/package_block_a_paper.py`
  - exported the Block A paper-packaging entrypoints from `src/isaacsim_agent/eval/__init__.py`
  - documented the new packaging script in `scripts/README.md`
  - added focused coverage in `tests/test_block_a_paper_packaging.py`
  - generated the requested paper-facing outputs:
    - `results/processed/block_a_master_summary/paper_tables/block_a_success_table.csv`
    - `results/processed/block_a_master_summary/paper_tables/block_a_invalid_actions_table.csv`
    - `results/processed/block_a_master_summary/paper_tables/block_a_efficiency_table.csv`
    - `results/processed/block_a_master_summary/paper_figures/block_a_success_rate.png`
    - `results/processed/block_a_master_summary/paper_figures/block_a_invalid_actions.png`
    - `results/processed/block_a_master_summary/paper_figures/block_a_planner_calls.png`
    - `results/processed/block_a_master_summary/paper_figures/block_a_tool_calls.png`
    - `results/processed/block_a_master_summary/analysis/block_a_analysis.md`
- Not completed in this run:
  - no new Block A experiments
  - no manipulation harder slice
  - no new runtime axis
  - no `M7` implementation work
  - no tool-abstraction work
  - no randomization work

## Checkpoint results

- Paper package source of truth:
  - `results/processed/block_a_master_summary/block_a_master_summary.json`
- Overall merged Block A result retained from the canonical master summary:
  - `merged_runs = 108`
  - `successful_runs = 90`
  - `success_rate = 0.833333`
  - `total_planner_calls = 528`
  - `total_tool_calls = 492`
  - `total_invalid_actions = 36`
- Covered cohorts in the paper package:
  - `Navigation / Easy = 66` runs
  - `Navigation / Harder = 24` runs
  - `Manipulation / Easy = 18` runs
  - `Manipulation / Harder = missing`
- Stable paper-facing findings captured in `analysis/block_a_analysis.md`:
  - `P0/R0` fails in every covered cohort
  - `P0/R1` recovers to full success in navigation easy, navigation harder, and manipulation easy
  - `P1` and `P2` remain fully successful in every covered cohort
  - `P2` preserves success while using fewer planner/tool calls than `P1`
  - harder navigation increases planner/tool cost without changing the qualitative ranking

## Files changed

- `STATUS.md`
- `scripts/README.md`
- `scripts/package_block_a_paper.py`
- `src/isaacsim_agent/eval/__init__.py`
- `src/isaacsim_agent/eval/block_a_paper.py`
- `tests/test_block_a_paper_packaging.py`

## Generated outputs

- `results/processed/block_a_master_summary/paper_tables/block_a_success_table.csv`
- `results/processed/block_a_master_summary/paper_tables/block_a_invalid_actions_table.csv`
- `results/processed/block_a_master_summary/paper_tables/block_a_efficiency_table.csv`
- `results/processed/block_a_master_summary/paper_figures/block_a_success_rate.png`
- `results/processed/block_a_master_summary/paper_figures/block_a_invalid_actions.png`
- `results/processed/block_a_master_summary/paper_figures/block_a_planner_calls.png`
- `results/processed/block_a_master_summary/paper_figures/block_a_tool_calls.png`
- `results/processed/block_a_master_summary/analysis/block_a_analysis.md`

## Commands run

- Source-of-truth reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,240p' AGENTS.md`
  - `sed -n '1,260p' STATUS.md`
- Context inspection:
  - `git status --short`
  - `find results/processed/block_a_master_summary -maxdepth 2 \( -type f -o -type d \) | sort`
  - `sed -n '1,260p' results/processed/block_a_master_summary/block_a_master_summary.json`
  - `sed -n '1,260p' results/processed/block_a_master_summary/block_a_master_summary.csv`
  - `rg -n "paper_figures|paper_tables|matplotlib|plt\\.|savefig|analysis\\.md|summarize_block_a|cross_family_summary" -S scripts src tests results/processed`
  - `sed -n '1,260p' scripts/summarize_block_a_master.py`
  - `sed -n '1,360p' src/isaacsim_agent/eval/block_a_master.py`
  - `sed -n '1,280p' results/processed/block_a_master_summary/block_a_master_summary.md`
  - `find . -maxdepth 2 -type d | sort | sed -n '1,220p'`
  - `sed -n '1,220p' scripts/README.md`
  - `sed -n '1,260p' tests/test_block_a_master_summary.py`
  - `find paper -maxdepth 3 \( -type f -o -type d \) | sort | sed -n '1,220p'`
  - `python - <<'PY' ... inspect block_a_master_summary.json keys and coverage ... PY`
  - `python - <<'PY' ... inspect grouped prompt/runtime metric rows ... PY`
  - `rg -n "paper_block_a_cleanup|Block A|paper-facing|result freeze|M6" plan.md STATUS.md -S`
  - `python - <<'PY' ... import matplotlib probe ... PY`
  - `sed -n '1,220p' paper/README.md`
  - `sed -n '1,120p' src/isaacsim_agent/eval/__init__.py`
  - `python - <<'PY' ... inspect master summary table keys ... PY`
  - `sed -n '220,520p' tests/test_block_a_master_summary.py`
  - `which gnuplot || true`
  - `which convert || true`
  - `which ffmpeg || true`
  - `which Rscript || true`
  - `python - <<'PY' ... tkinter import probe ... PY`
  - `sed -n '1,260p' pyproject.toml`
  - `python - <<'PY' ... import PIL/cairosvg/reportlab probe ... PY`
- Implementation validation:
  - `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/eval/block_a_paper.py scripts/package_block_a_paper.py tests/test_block_a_paper_packaging.py`
  - `PYTHONPATH=src uv run python -m unittest tests.test_block_a_paper_packaging`
  - `PYTHONPATH=src uv run python -m unittest tests.test_block_a_master_summary`
  - `PYTHONPATH=src uv run python scripts/package_block_a_paper.py --master-summary-path results/processed/block_a_master_summary/block_a_master_summary.json --output-dir results/processed/block_a_master_summary`
  - `find results/processed/block_a_master_summary/paper_tables results/processed/block_a_master_summary/paper_figures results/processed/block_a_master_summary/analysis -maxdepth 2 -type f | sort`
  - `sed -n '1,220p' results/processed/block_a_master_summary/analysis/block_a_analysis.md`
  - `sed -n '1,120p' results/processed/block_a_master_summary/paper_tables/block_a_success_table.csv`
  - `python - <<'PY' ... read PNG sizes for paper figures ... PY`

## Validation results

- Python compilation succeeded:
  - command: `PYTHONPATH=src uv run python -m py_compile src/isaacsim_agent/eval/block_a_paper.py scripts/package_block_a_paper.py tests/test_block_a_paper_packaging.py`
  - result: success with no output
- Focused paper-packaging coverage succeeded:
  - command: `PYTHONPATH=src uv run python -m unittest tests.test_block_a_paper_packaging`
  - result:
    - `Ran 2 tests in 4.781s`
    - `OK`
- Block A master summary regression coverage also succeeded:
  - command: `PYTHONPATH=src uv run python -m unittest tests.test_block_a_master_summary`
  - result:
    - `Ran 2 tests in 0.161s`
    - `OK`
- Real-data paper packaging e2e succeeded:
  - command: `PYTHONPATH=src uv run python scripts/package_block_a_paper.py --master-summary-path results/processed/block_a_master_summary/block_a_master_summary.json --output-dir results/processed/block_a_master_summary`
  - result:
    - `Covered master cells: 18`
    - `Missing cohorts: manipulation/harder`
    - `Table consistency checks: 180`
    - `Figure consistency checks: 72`
    - `All consistency checks passed: True`
- Post-run artifact inspection succeeded:
  - all three paper tables exist under `results/processed/block_a_master_summary/paper_tables/`
  - all four paper figures exist under `results/processed/block_a_master_summary/paper_figures/`
  - `results/processed/block_a_master_summary/analysis/block_a_analysis.md` exists
  - figure sizes:
    - `block_a_success_rate.png = 1680 x 920`
    - `block_a_invalid_actions.png = 1680 x 920`
    - `block_a_planner_calls.png = 1680 x 920`
    - `block_a_tool_calls.png = 1680 x 920`

## Blockers

- None.

## Next recommended step

- Treat this Block A package as the paper-facing freeze point and move to manuscript integration using the packaged tables, figures, and analysis note.
- Only if a later paper pass explicitly requires harder-slice family symmetry, add the smallest possible manipulation-harder slice and stop there.
