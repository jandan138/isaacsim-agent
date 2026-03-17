# Figures and Tables Plan

This file maps paper-facing figures and tables back to immutable result assets. It
is a planning document only. No figures or tables are copied into `paper/assets/`
yet.

## Asset policy

- Treat `results/processed/` as immutable evidence.
- Treat `paper/assets/` as future derived outputs only.
- Use `results/processed/block_a_final_closure/` as the canonical freeze for final numbers.
- Use the packaged outputs under `results/processed/block_a_master_summary/paper_figures/`
  and `results/processed/block_a_master_summary/paper_tables/` only as layout/style templates because they predate final closure.

## Source hierarchy

1. Canonical umbrella evidence:
   `results/processed/block_a_final_closure/block_a_final_closure_summary.{json,csv,md}`
2. Slice-specific evidence:
   `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.{json,md}`
   `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}`
   `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.{json,md}`
   `results/processed/block_a_cross_family_summary/cross_family_summary.json`
   `results/processed/block_a_master_summary/block_a_master_summary.{json,md}`
3. Legacy packaging templates only:
   `results/processed/block_a_master_summary/paper_figures/`
   `results/processed/block_a_master_summary/paper_tables/`

## Core empirical figures

### Figure A: Main condition ordering

- Purpose:
  show the stable qualitative ordering across the six prompt/runtime conditions
- Main claim served:
  `P0/R0` is worst, `P0/R1` recovers, `P1/P2` are strong, and `P2` is not worse than `P1`
- Canonical data source:
  `results/processed/block_a_final_closure/block_a_final_closure_summary.md`
- Supporting sources:
  `results/processed/block_a_master_summary/block_a_master_summary.md`
  `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.md`
- Legacy template to inspect:
  `results/processed/block_a_master_summary/paper_figures/block_a_success_rate.png`
- RA-L priority:
  must include
- CoRL / Autonomous Robots:
  also core and reusable

### Figure B: Invalid actions and recovery

- Purpose:
  explain why structured prompts help and why runtime validation matters
- Main claim served:
  structured prompts reduce invalid actions; `R1` converts recoverable invalid-action runs into successful runs
- Canonical data sources:
  `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.md`
  `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.md`
- Supporting sources:
  `results/processed/block_a_final_closure/block_a_final_closure_summary.md`
- Legacy template to inspect:
  `results/processed/block_a_master_summary/paper_figures/block_a_invalid_actions.png`
- RA-L priority:
  must include
- CoRL / Autonomous Robots:
  core and expandable with more discussion

### Figure C: Planner/tool overhead

- Purpose:
  show that `P2` reduces planner/tool workload relative to `P1` in the tested setup
- Main claim served:
  brief self-check can improve efficiency without harming the success profile in current slices
- Canonical data sources:
  `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.md`
  `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.md`
- Supporting sources:
  `results/processed/block_a_master_summary/block_a_master_summary.md`
  `results/processed/block_a_final_closure/block_a_final_closure_summary.md`
- Legacy templates to inspect:
  `results/processed/block_a_master_summary/paper_figures/block_a_planner_calls.png`
  `results/processed/block_a_master_summary/paper_figures/block_a_tool_calls.png`
- RA-L priority:
  must include, likely as one compact figure or paired subplots
- CoRL / Autonomous Robots:
  core and reusable

## Core tables

### Table A: Experimental design summary

- Purpose:
  define task families, slices, variants, and run counts without over-explaining the roadmap
- Main claim served:
  the paper is a controlled study with a finite and explicit matrix
- Data sources:
  `results/processed/block_a_final_closure/block_a_final_closure_summary.json`
  `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.json`
  `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.json`
  `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json`
- Legacy template to inspect:
  none directly; this will likely be regenerated as a compact manuscript table
- RA-L priority:
  must include

### Table B: Final closure result summary

- Purpose:
  present the compact per-family/per-slice outcome summary with success, invalid actions, retries, planner calls, and tool calls
- Main claim served:
  the ordering remains stable across families and current harder slices
- Data sources:
  `results/processed/block_a_final_closure/block_a_final_closure_summary.json`
  `results/processed/block_a_master_summary/block_a_master_summary.json`
  `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json`
- Legacy templates to inspect:
  `results/processed/block_a_master_summary/paper_tables/block_a_success_table.csv`
  `results/processed/block_a_master_summary/paper_tables/block_a_invalid_actions_table.csv`
  `results/processed/block_a_master_summary/paper_tables/block_a_efficiency_table.csv`
- RA-L priority:
  must include
- CoRL / Autonomous Robots:
  core and reusable

### Table C: Focused ablation summary

- Purpose:
  summarize the independent prompt-only and runtime-only tests in one compact place
- Main claim served:
  prompt structure and runtime validation each have independent value
- Data sources:
  `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.json`
  `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.json`
- RA-L priority:
  optional if space remains
- CoRL priority:
  likely include
- Autonomous Robots priority:
  likely include

## Non-results figure note

`docs/ral_writing_playbook.md` recommends a system diagram for the eventual manuscript.
That schematic is not a current result asset and is intentionally out of scope for
this mapping pass. If it is added later, it should be authored from the method
description rather than inferred from `results/processed/`.

## Regeneration rule

Before any manuscript figure or table is committed under `paper/assets/`, record:

- the exact source files used
- whether the asset is regenerated from final closure or only a legacy layout reference
- any mismatch between a legacy packaged asset and the final-closure freeze
