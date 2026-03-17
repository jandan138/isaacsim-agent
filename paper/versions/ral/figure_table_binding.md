# Figure and Table Binding

This file records the current reviewer-facing binding state for the RA-L
artifact stack after the artifact-overhaul pass.

## Main-text bindings

| Asset | Regenerated file(s) | Inserted from | Evidence binding | Notes |
| --- | --- | --- | --- | --- |
| Figure 1: system overview | `paper/versions/ral/figures/system_overview.{csv,tex}` | `sections/intro.tex` via `\input{figures/system_overview.tex}` | Frozen task layouts plus runtime-only run traces under `results/block_a_runtime_only_ablation/` | Reviewer-facing method figure. The environment insets and compact traces are schematic renderings grounded in frozen layouts and traces, not new experiments. |
| Main condition ordering | `paper/versions/ral/figures/main_condition_ordering.{csv,tex}` | `sections/results.tex` | `results/processed/block_a_master_summary/block_a_master_summary.json` and `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json` | Vector-first PGF/TikZ replacement for the old packaged success-rate figure. |
| Invalid actions and recovery | `paper/versions/ral/figures/invalid_actions_recovery.{csv,tex}` | `sections/results.tex` | `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.json` and `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.json` | Main mechanism figure for invalid-action elimination and runtime-assisted repair. |
| Planner/tool overhead | `paper/versions/ral/figures/planner_tool_overhead.{csv,tex}` | `sections/results.tex` | `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.json` and `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json` | Caption and prose keep the effect descriptive rather than overstating P2 efficiency. |
| Table I: experimental design | `paper/versions/ral/tables/experimental_design_summary.{csv,tex}` | `sections/setup.tex` | `results/processed/block_a_master_summary/block_a_master_summary.json` plus retained ablation and harder-manipulation summaries | Reformatted as a full-width reviewer-facing matrix summary. |
| Table II: outcomes | `paper/versions/ral/tables/main_outcome_summary.{csv,tex}` | `sections/results.tex` | Main retained cohorts from final closure, master summary, and harder manipulation | Splits success / invalid / retries away from workload metrics. |
| Table III: planner/tool overhead | `paper/versions/ral/tables/planner_tool_overhead_summary.{csv,tex}` | `sections/results.tex` | Main retained cohorts from final closure, master summary, and harder manipulation | Keeps workload cells separate from outcome cells. |

## Support-only bindings

- `paper/versions/ral/tables/final_closure_result_summary.{csv,tex}`
  - Evidence:
    retained cohorts from final closure, master summary, and harder
    manipulation
  - Status:
    generated but not inserted in the main manuscript
- `paper/versions/ral/tables/focused_ablation_summary.{csv,tex}`
  - Evidence:
    `results/processed/block_a_prompt_only_ablation/` and
    `results/processed/block_a_runtime_only_ablation/`
  - Status:
    generated but not inserted in the main manuscript
- `paper/versions/ral/tables/harder_task_summary.{csv,tex}`
  - Evidence:
    `results/processed/block_a_master_summary/` and
    `results/processed/block_a_manipulation_harder/`
  - Status:
    generated but not inserted in the main manuscript

## Variant hookup check

- Journal scaffold:
  `paper/versions/ral/main.tex`
  - uses the shared `sections/`, `figures/`, `tables/`, `refs/`, and
    `preamble_shared.tex`
- Reviewer-facing initial submission:
  `paper/versions/ral/reviewer_submission/main.tex`
  - points at the same shared assets through `\input@path{{../}}`

## Asset format note

- The manuscript-facing figures are now TeX/TikZ vector assets.
- The dormant PNG files from earlier packaging are no longer the
  manuscript-facing source of truth.
