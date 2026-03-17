# Figure and Table Binding for `full_draft_v1.md`

This document records the **actual** binding state of the current RA-L compiled
draft. The manuscript-facing assets now live under `paper/versions/ral/`, while
the immutable evidence remains under `results/processed/`.

## Binding summary

| Draft placeholder | Regenerated asset | LaTeX insertion point | Main-text status | Evidence binding | Notes |
| --- | --- | --- | --- | --- | --- |
| `[Fig: main condition ordering]` | `paper/versions/ral/figures/main_condition_ordering.{png,csv,tex}` | `paper/versions/ral/sections/results.tex` in Section 4.1 via `\input{figures/main_condition_ordering.tex}` | main-text asset | Final-closure umbrella, with cohort-level support from `results/processed/block_a_master_summary/block_a_master_summary.json` and `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json` | Primary success-rate figure. Legacy `results/processed/block_a_master_summary/paper_figures/block_a_success_rate.png` remains a template only. |
| `[Fig: invalid actions and recovery]` | `paper/versions/ral/figures/invalid_actions_recovery.{png,csv,tex}` | `paper/versions/ral/sections/results.tex` in Section 4.2 via `\input{figures/invalid_actions_recovery.tex}` | main-text asset | `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}` and `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.{json,md}` | Main mechanism figure for fixed-`R0` contract effect and fixed-`P1` runtime recovery. Legacy `block_a_invalid_actions.png` is not evidence. |
| `[Fig: planner/tool overhead]` | `paper/versions/ral/figures/planner_tool_overhead.{png,csv,tex}` | `paper/versions/ral/sections/results.tex` in Section 4.1, with the same figure serving the narrower `P2` references in Sections 4.2 and 4.3 | main-text asset | `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}` and `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.{json,md}` | Caption and prose keep the effect descriptive: lower planner/tool overhead in the covered slices, not a broader statistical efficiency claim. |
| `[Table: experimental design summary]` | `paper/versions/ral/tables/experimental_design_summary.{tex,csv}` | `paper/versions/ral/sections/setup.tex` in Section 3.2 via `\input{tables/experimental_design_summary.tex}` | main-text asset | Final-closure umbrella plus the retained ablation and harder-manipulation summaries, with run-count context from `results/processed/block_a_master_summary/block_a_master_summary.json` | Keeps the variant inventory table-driven for page control. No legacy table template is reused as evidence. |
| `[Table: final closure result summary]` | `paper/versions/ral/tables/final_closure_result_summary.{tex,csv}` | `paper/versions/ral/sections/setup.tex` at the end of Section 3.3 via `\input{tables/final_closure_result_summary.tex}` | main-text asset | Final-closure umbrella, with retained cohort-level support from `results/processed/block_a_master_summary/block_a_master_summary.json` and `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json` | The table is generated and hooked once in the compiled draft, then referenced by the Results prose. |
| `[Table: focused ablation summary]` | `paper/versions/ral/tables/focused_ablation_summary.{tex,csv}` | not currently inserted in `main.tex` | support / overflow asset | `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}` and `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.{json,md}` | Deliberately removed from the current main-text float stack in this cleanup pass to keep page pressure lower. It remains the first asset to restore or cut depending on final author-page decisions. |

## Support-only asset

- `paper/versions/ral/tables/harder_task_summary.{tex,csv}`
  - Current status:
    generated but not inserted in `main.tex`
  - Evidence binding:
    `results/processed/block_a_master_summary/block_a_master_summary.json` and
    `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json`
  - Intended role:
    overflow/support table for the harder-task paragraph or an appendix-style
    author handoff, not a current main-text float

## Legacy packaging status

- `results/processed/block_a_master_summary/paper_figures/`
  and `results/processed/block_a_master_summary/paper_tables/`
  were inspected only as layout/style precedents.
- Those legacy packaged assets are **not** the final evidence base because they
  predate the final-closure additions.

## Current manuscript hookup check

- `paper/versions/ral/sections/setup.tex` currently inserts:
  - `tables/experimental_design_summary.tex`
  - `tables/final_closure_result_summary.tex`
- `paper/versions/ral/sections/results.tex` currently inserts:
  - `figures/main_condition_ordering.tex`
  - `figures/planner_tool_overhead.tex`
  - `figures/invalid_actions_recovery.tex`
- `focused_ablation_summary.tex` and `harder_task_summary.tex` both exist but
  are not currently inserted in the compiled draft.

## System diagram status

- `full_draft_v1.md` still has no dedicated system-diagram placeholder.
- If a schematic is added later, it should remain author-drawn method artwork,
  not a derived result asset.
