# RA-L Asset Manifest

- Evidence base: fixed evaluation summary plus supporting slice summaries.
- Final closure merged runs: `146`
- Final closure successful runs: `119`
- Cross-family prompt/runtime rows: `12`
- Figure style: manuscript figures are emitted as PGF/TikZ-backed `.tex` assets for vector-first compilation.
- Figure 1 is a frozen manually selected asset and is intentionally out of scope for this generator.
- This final reviewer-facing cleanup pass did not change the asset inventory or
  evidence bindings; it only normalized wording in shared figure/table text.
- Main reviewer-facing figures:
  - `figures/fig1_system_overview_frozen.png`
  - `figures/fig1_system_overview_frozen.pdf` (optional when present)
  - `figures/main_condition_ordering.tex`
  - `figures/invalid_actions_recovery.tex`
  - `figures/planner_tool_overhead.tex`
- Main reviewer-facing tables:
  - `tables/contract_interface_examples.tex`
  - `tables/experimental_design_summary.tex`
  - `tables/main_outcome_summary.tex`
  - `tables/planner_tool_overhead_summary.tex`
- Support-only tables:
  - `tables/focused_ablation_summary.tex`
  - `tables/harder_task_summary.tex`

## Written outputs

- `experimental_design_summary_csv`: `paper/versions/ral/tables/experimental_design_summary.csv`
- `experimental_design_summary_tex`: `paper/versions/ral/tables/experimental_design_summary.tex`
- `final_closure_result_summary_csv`: `paper/versions/ral/tables/final_closure_result_summary.csv`
- `final_closure_result_summary_tex`: `paper/versions/ral/tables/final_closure_result_summary.tex`
- `focused_ablation_summary_csv`: `paper/versions/ral/tables/focused_ablation_summary.csv`
- `focused_ablation_summary_tex`: `paper/versions/ral/tables/focused_ablation_summary.tex`
- `harder_task_summary_csv`: `paper/versions/ral/tables/harder_task_summary.csv`
- `harder_task_summary_tex`: `paper/versions/ral/tables/harder_task_summary.tex`
- `invalid_actions_recovery_csv`: `paper/versions/ral/figures/invalid_actions_recovery.csv`
- `invalid_actions_recovery_tex`: `paper/versions/ral/figures/invalid_actions_recovery.tex`
- `main_condition_ordering_csv`: `paper/versions/ral/figures/main_condition_ordering.csv`
- `main_condition_ordering_tex`: `paper/versions/ral/figures/main_condition_ordering.tex`
- `main_outcome_summary_csv`: `paper/versions/ral/tables/main_outcome_summary.csv`
- `main_outcome_summary_tex`: `paper/versions/ral/tables/main_outcome_summary.tex`
- `planner_tool_overhead_csv`: `paper/versions/ral/figures/planner_tool_overhead.csv`
- `planner_tool_overhead_summary_csv`: `paper/versions/ral/tables/planner_tool_overhead_summary.csv`
- `planner_tool_overhead_summary_tex`: `paper/versions/ral/tables/planner_tool_overhead_summary.tex`
- `planner_tool_overhead_tex`: `paper/versions/ral/figures/planner_tool_overhead.tex`
