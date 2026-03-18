# Figure and Table Binding

This file records the current reviewer-facing binding state for the RA-L
artifact stack after the artifact-overhaul pass.

## Main-text bindings

| Asset | Regenerated file(s) | Inserted from | Evidence binding | Notes |
| --- | --- | --- | --- | --- |
| Figure 1: system overview | `paper/versions/ral/figures/fig1_system_overview_frozen.png` and optional `paper/versions/ral/figures/fig1_system_overview_frozen.pdf`, wrapped by `paper/versions/ral/figures/fig1_system_overview_frozen.tex` | `sections/intro.tex` via `\input{figures/fig1_system_overview_frozen.tex}` | Manually selected frozen asset | Frozen by author choice. This figure is now out of scope for further generator-driven iteration or redesign. |
| Main condition ordering | `paper/versions/ral/figures/main_condition_ordering.{csv,tex}` | `sections/results.tex` | `results/processed/block_a_master_summary/block_a_master_summary.json` and `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json` | Full-width table-figure hybrid. In-cell counts and `fail` / `recovered` / `clean` labels replace the old repeated success-rate bar panels. |
| Invalid actions and recovery | `paper/versions/ral/figures/invalid_actions_recovery.{csv,tex}` | `sections/results.tex` | `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.json` and `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.json` | Two-part mechanism figure: fixed-`R0` invalid-action elimination on top, fixed-`P1` runtime recovery on bottom, with retries kept as annotation rather than the only runtime signal. |
| Planner/tool overhead | `paper/versions/ral/figures/planner_tool_overhead.{csv,tex}` | `sections/results.tex` | retained `P1` / `P2` rows from `results/processed/block_a_master_summary/block_a_master_summary.json` plus `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json` | Consolidated retained-workload comparison. Equal planner/tool pairs are collapsed into single bars labeled `planner/tool` so the `P1` versus `P2` contrast stays legible. |
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

- Figure 1 is now a frozen manual asset; the remaining manuscript-facing result
  figures are TeX/TikZ vector assets.
- The current result figures deliberately preserve the frozen data and claims,
  not the older bar-panel layouts.
- The dormant PNG files from earlier packaging are no longer the
  manuscript-facing source of truth.
