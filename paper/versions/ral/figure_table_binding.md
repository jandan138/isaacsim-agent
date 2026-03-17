# Figure and Table Binding for `full_draft_v1.md`

No final manuscript-ready assets exist yet under `paper/assets/`. The bindings
below map each placeholder in `full_draft_v1.md` to the shared figures/tables
plan and to the current processed evidence on disk.

| Placeholder in `full_draft_v1.md` | Shared-plan entry | Evidence binding | Existing asset status | Current action |
| --- | --- | --- | --- | --- |
| `[Fig: main condition ordering]` | Figure A in `paper/shared/figures_and_tables.md` | Canonical: `results/processed/block_a_final_closure/block_a_final_closure_summary.{json,md}`; supporting: `results/processed/block_a_master_summary/block_a_master_summary.md`, `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.md` | Legacy template exists at `results/processed/block_a_master_summary/paper_figures/block_a_success_rate.png`, but it predates final closure | Regenerate from the final-closure freeze before paper asset export |
| `[Fig: invalid actions and recovery]` | Figure B in `paper/shared/figures_and_tables.md` | Canonical: `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}` and `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.{json,md}`; supporting: `results/processed/block_a_final_closure/block_a_final_closure_summary.md` | Legacy template exists at `results/processed/block_a_master_summary/paper_figures/block_a_invalid_actions.png`, but it is only a pre-final-closure template | Refresh from the frozen prompt-only and runtime-only ablation summaries |
| `[Fig: planner/tool overhead]` | Figure C in `paper/shared/figures_and_tables.md` | Canonical: `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}` and `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.{json,md}`; supporting: `results/processed/block_a_final_closure/block_a_final_closure_summary.md`, `results/processed/block_a_master_summary/block_a_master_summary.md` | Legacy component templates exist at `results/processed/block_a_master_summary/paper_figures/block_a_planner_calls.png` and `results/processed/block_a_master_summary/paper_figures/block_a_tool_calls.png` | Refresh as one compact figure or paired subplots from the frozen summaries |
| `[Table: experimental design summary]` | Table A in `paper/shared/figures_and_tables.md` | `results/processed/block_a_final_closure/block_a_final_closure_summary.json`, `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.json`, `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.json`, `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json` | No packaged table asset currently exists | Author a fresh compact manuscript table from the frozen summaries |
| `[Table: final closure result summary]` | Table B in `paper/shared/figures_and_tables.md` | Canonical: `results/processed/block_a_final_closure/block_a_final_closure_summary.json`; supporting: `results/processed/block_a_master_summary/block_a_master_summary.json`, `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json` | Legacy metric-split CSV templates exist at `results/processed/block_a_master_summary/paper_tables/block_a_success_table.csv`, `results/processed/block_a_master_summary/paper_tables/block_a_invalid_actions_table.csv`, and `results/processed/block_a_master_summary/paper_tables/block_a_efficiency_table.csv` | Build one refreshed compact table from final closure instead of reusing the split legacy tables |
| `[Table: focused ablation summary]` | Table C in `paper/shared/figures_and_tables.md` | `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}` and `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.{json,md}` | No dedicated packaged table exists | Regenerate from the frozen ablation summaries if the final page budget keeps this table |

## System Diagram Note

- `full_draft_v1.md` does not currently insert a system-art placeholder.
- If the manuscript adds a system schematic in a later pass, it should be an
  author-drawn execution-architecture diagram derived from Section 3 rather
  than from `results/processed/`.
- The shared plan already flags this as non-results artwork, so it remains the
  one diagram that still needs separate author drawing.
