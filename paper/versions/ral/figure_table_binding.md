# Figure and Table Binding for `full_draft_v1.md`

The placeholders below are now bound to regenerated RA-L assets under
`paper/versions/ral/`. The figures and tables use the frozen final-closure
umbrella plus the retained slice summaries called out in the shared plan.

| Placeholder in `full_draft_v1.md` | Shared-plan entry | Evidence binding | Current asset status | Current binding action |
| --- | --- | --- | --- | --- |
| `[Fig: main condition ordering]` | Figure A in `paper/shared/figures_and_tables.md` | Canonical umbrella: `results/processed/block_a_final_closure/block_a_final_closure_summary.{json,md}`; cohort-level support: `results/processed/block_a_master_summary/block_a_master_summary.json` for navigation easy / navigation harder / manipulation easy, plus `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json` for manipulation harder | Refreshed as `paper/versions/ral/figures/main_condition_ordering.png` with LaTeX wrapper `paper/versions/ral/figures/main_condition_ordering.tex`; regenerated from frozen summaries rather than the legacy master-summary packaging | Bind in Results 4.1 as the primary success-rate figure. Caption direction: contract/runtime ordering across the four retained slices, with `P0/R0` weakest and `P0/R1` recovered |
| `[Fig: invalid actions and recovery]` | Figure B in `paper/shared/figures_and_tables.md` | Canonical: `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}` and `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.{json,md}`; supporting context: `results/processed/block_a_final_closure/block_a_final_closure_summary.md` | Refreshed as `paper/versions/ral/figures/invalid_actions_recovery.png` with LaTeX wrapper `paper/versions/ral/figures/invalid_actions_recovery.tex` | Bind in Results 4.2 for both the fixed-`R0` contract effect and the fixed-`P1` recovery effect. Caption direction: explicit contracts suppress invalid actions; validate-and-retry runtime adds bounded recovery work rather than a broader runtime claim |
| `[Fig: planner/tool overhead]` | Figure C in `paper/shared/figures_and_tables.md` | Canonical: `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}` and `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.{json,md}`; supporting context: `results/processed/block_a_final_closure/block_a_final_closure_summary.md`, `results/processed/block_a_master_summary/block_a_master_summary.md` | Refreshed as `paper/versions/ral/figures/planner_tool_overhead.png` with LaTeX wrapper `paper/versions/ral/figures/planner_tool_overhead.tex` | Bind in Results 4.1, 4.2, and 4.3. Caption direction: `P2` stays aligned with `P1` on success in the covered comparisons while using fewer planner/tool calls; keep the wording descriptive, not statistical |
| `[Table: experimental design summary]` | Table A in `paper/shared/figures_and_tables.md` | `results/processed/block_a_final_closure/block_a_final_closure_summary.json`, `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.json`, `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.json`, `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json`, with run-count context from `results/processed/block_a_master_summary/block_a_master_summary.json` | Authored as `paper/versions/ral/tables/experimental_design_summary.tex` with companion CSV `paper/versions/ral/tables/experimental_design_summary.csv` | Bind in Study Design 3.2 so the variant inventory stays table-driven under page pressure |
| `[Table: final closure result summary]` | Table B in `paper/shared/figures_and_tables.md` | Canonical umbrella: `results/processed/block_a_final_closure/block_a_final_closure_summary.json`; cohort-level support: `results/processed/block_a_master_summary/block_a_master_summary.json` and `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json` | Authored as `paper/versions/ral/tables/final_closure_result_summary.tex` with companion CSV `paper/versions/ral/tables/final_closure_result_summary.csv` | Bind at the end of 3.3 and in Results 4.1 / 4.3 as the compact per-cell reference table. The table carries success plus invalid-action / retry / planner-tool context without changing the paper's main claim to the merged total |
| `[Table: focused ablation summary]` | Table C in `paper/shared/figures_and_tables.md` | `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}` and `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.{json,md}` | Authored as `paper/versions/ral/tables/focused_ablation_summary.tex` with companion CSV `paper/versions/ral/tables/focused_ablation_summary.csv` | Bind in Results 4.2 if page budget allows. Priority remains optional / first to cut under page pressure |

## Supplemental Support Asset

- `paper/versions/ral/tables/harder_task_summary.tex`
  - Evidence binding:
    `results/processed/block_a_master_summary/block_a_master_summary.json` and
    `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json`
  - Status:
    generated as a support table with companion CSV
  - Binding:
    not mapped to a dedicated placeholder in `full_draft_v1.md`; keep it as an
    overflow asset for the harder-task paragraph or author-side appendix if the
    final RA-L page budget permits

## System Diagram Note

- `full_draft_v1.md` does not currently insert a system-art placeholder.
- If the manuscript adds a system schematic in a later pass, it should be an
  author-drawn execution-architecture diagram derived from Section 3 rather
  than from `results/processed/`.
- The shared plan already flags this as non-results artwork, so it remains the
  one diagram that still needs separate author drawing.
