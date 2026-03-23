# Figure and Table Binding

This file records the current reviewer-facing binding state for the RA-L
artifact stack after the Table I reduction pass.

## Main-text bindings

| Asset | File(s) | Inserted from | Evidence binding | Notes |
| --- | --- | --- | --- | --- |
| Figure 1: system overview | `paper/versions/ral/figures/fig1_system_overview_frozen.png` and optional `paper/versions/ral/figures/fig1_system_overview_frozen.pdf`, wrapped by `paper/versions/ral/figures/fig1_system_overview_frozen.tex` | `sections/intro.tex` via `\input{figures/fig1_system_overview_frozen.tex}` | Manually selected frozen asset | Figure 1 stayed frozen by author request and was not redesigned or regenerated in this pass. |
| Table I: contract/interface examples | `paper/versions/ral/tables/contract_interface_examples.tex` | `sections/intro.tex` | Saved prompt texts from the task configs plus archived planner responses from `results/block_a_navigation_prompt_runtime_expanded_e2e_20260316_py/runs/block-a-navigation-prompt-runtime-expanded-toy-nav-short-forward-easy-empty-stage-a-p0-r0-s0/artifacts/planner_trace.json`, `...-p1-r0-s0/artifacts/planner_trace.json`, and `...-p2-r0-s0/artifacts/planner_trace.json` | Manual manuscript-facing table, retained as a table-numbered asset to avoid renumbering the figure stack. This pass refined the previous matrix draft into a quieter 4-column comparison table with one low-key declared-tool note and only two body rows. |
| Table II: experimental design | `paper/versions/ral/tables/experimental_design_summary.{csv,tex}` | `sections/setup.tex` | `results/processed/block_a_master_summary/block_a_master_summary.json` plus the focused ablation and harder-manipulation summaries | Full-width reviewer-facing matrix summary. |
| Figure 2: main condition ordering | `paper/versions/ral/figures/main_condition_ordering.{csv,tex}` | `sections/results.tex` | `results/processed/block_a_master_summary/block_a_master_summary.json` and `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json` | Full-width table-figure hybrid. In-cell counts and `fail` / `recovered` / `clean` labels replace the old repeated success-rate bar panels. |
| Table III: outcomes | `paper/versions/ral/tables/main_outcome_summary.{csv,tex}` | `sections/results.tex` | Main reported cohorts from final closure, master summary, and harder manipulation | Splits success / invalid / retries away from workload metrics. |
| Figure 3: planner/tool overhead | `paper/versions/ral/figures/planner_tool_overhead.{csv,tex}` | `sections/results.tex` | `P1` / `P2` rows from `results/processed/block_a_master_summary/block_a_master_summary.json` plus `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json` | Consolidated workload comparison with `planner/tool` labels. |
| Table IV: planner/tool overhead | `paper/versions/ral/tables/planner_tool_overhead_summary.{csv,tex}` | `sections/results.tex` | Main reported cohorts from final closure, master summary, and harder manipulation | Keeps workload cells separate from outcome cells. |
| Figure 4: invalid actions and recovery | `paper/versions/ral/figures/invalid_actions_recovery.{csv,tex}` | `sections/results.tex` | `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.json` and `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.json` | Two-part mechanism figure: fixed-`R0` invalid-action elimination on top, fixed-`P1` runtime recovery on bottom, with explicit non-color labels inside the runtime panel cells. |

## Pass note

- Figure 1 stayed frozen and out of scope.
- This pass focused on non-Figure-1 manuscript improvement and changed only Table
  I's presentation, not its evidence source.
- Table I kept its table identity and insertion point in `sections/intro.tex`
  because converting it into a formal figure would have disturbed the active
  figure numbering, table numbering, and existing reviewer-facing references.
- The redesign preserved the existing trace bindings while refining the prior
  matrix draft into a more restrained manuscript-style comparison table.
- The redesign goal was reduction and manuscript fit, not decorative styling.

## Support-only bindings

- `paper/versions/ral/tables/final_closure_result_summary.{csv,tex}`
  - Evidence:
    reported cohorts from final closure, master summary, and harder
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

- Figure 1 remains a frozen manual asset.
- The three result figures remain TeX/TikZ vector assets.
- `tables/contract_interface_examples.tex` remains the only manual
  manuscript-facing table; it is not regenerated by the packaging script.
