# STATUS.md

## Current status

- Date: 2026-03-17
- Plan source of truth: `plan.md`
- Paper-writing source of truth: `docs/ral_writing_playbook.md`
- Active milestone: `M11. Paper drafting`
- Milestone state:
  - this run completed `RA-L reviewer-facing artifact overhaul`
- Completion level:
  - the RA-L stack is now split into:
    - initial anonymous reviewer-facing submission:
      `paper/versions/ral/reviewer_submission/main.pdf`
    - accepted-version journal scaffold:
      `paper/versions/ral/main.pdf`
  - the reviewer-facing submission variant compiles successfully at `7` pages
  - the journal scaffold compiles successfully at `6` pages
  - the active manuscript now includes a reviewer-facing Figure 1 system
    overview, vector-first main figures, split reviewer-facing main tables, and
    a setup-level implementation snapshot

## Run context

- This run stayed within the requested boundaries:
  - no new experiments
  - no experiment-code changes beyond manuscript asset generation
  - no venue switch
  - no change to the paper's contract / runtime-validation framing
  - no reversion to prompt-first framing
  - no overstated P2 efficiency claims
  - no invented numbers or citations
- Source-of-truth docs consumed in this run:
  - `plan.md`
  - `AGENTS.md`
  - prior `STATUS.md` from `HEAD`
  - `docs/ral_writing_playbook.md`
  - `paper/versions/ral/main.tex`
  - `paper/versions/ral/sections/`
  - `paper/versions/ral/figures/`
  - `paper/versions/ral/tables/`
  - `paper/versions/ral/refs/`
  - `paper/versions/ral/latex_assembly_notes.md`
  - `results/processed/block_a_final_closure/`
  - `scripts/package_block_a_ral_assets.py`
  - `src/isaacsim_agent/eval/block_a_ral_assets.py`
- Agent teaming:
  - spawned two explorer sub-agents for:
    - variant split / LaTeX-structure audit
    - citation / intro-cleanup audit
  - waited on both agents with cumulative wait windows of roughly:
    - `1s`
    - `10s`
    - `30s`
    - `10s` after a focused status check
  - observed no returned output or blocker summary from either agent
  - sent one focused progress check to each agent, then closed both as stalled
    because the main task no longer depended on their result
  - action taken:
    abandoned sub-agent integration and completed the overhaul locally

## Milestone summary

- Completed in this run:
  - split the manuscript packaging into:
    - reviewer-facing anonymous RA-L submission variant:
      `paper/versions/ral/reviewer_submission/`
    - journal-style accepted-version scaffold:
      `paper/versions/ral/`
  - added the new Figure 1 system overview:
    - task -> planner -> contract variant -> runtime policy -> Isaac Sim
      executor -> metrics/outcomes
    - navigation and tabletop environment insets grounded in frozen layouts
    - compact failure-repair trace inset covering:
      `move_to_goal` / `move_object` -> non-dispatchable -> validation/retry ->
      corrected tool
  - professionalized the main manuscript figures:
    - reviewer-facing figures now compile from vector-first TikZ/PGF assets
    - active figure captions use systems wording rather than prompt-engineering
      wording
    - retained main result figures:
      `main_condition_ordering`, `invalid_actions_recovery`,
      `planner_tool_overhead`
  - reworked the tables for readability:
    - `experimental_design_summary` is now the readable reviewer-facing matrix
      table
    - main dense result reporting is split into:
      - `main_outcome_summary`
      - `planner_tool_overhead_summary`
    - `final_closure_result_summary` is retained as support-only
  - added a setup-level implementation snapshot covering:
    - local planner identity / access path
    - deterministic JSON decoding and lack of temperature / top-$p$
    - P0/P1/P2 realizations
    - R0/R1 realizations
    - executor tool namespaces
  - kept the contract / runtime-validation framing intact while tightening the
    introduction wording
  - kept safe publication-backed citations in `refs/references.bib` and left
    unresolved arXiv-only items untouched where no safer archival replacement
    was applied in this pass
  - regenerated manuscript assets and rebuilt both PDFs
  - updated:
    - `README.md`
    - `paper/versions/ral/README.md`
    - `paper/versions/ral/figure_table_binding.md`
    - `paper/versions/ral/latex_assembly_notes.md`
    - `paper/versions/ral/reviewer_submission/README.md`
    - `STATUS.md`
- Not completed in this run:
  - no new experiments or result changes
  - no literal simulator screenshot capture workflow
  - no final author-side line edit or anonymity pass

## Files changed

- `README.md`
- `STATUS.md`
- `paper/versions/ral/README.md`
- `paper/versions/ral/asset_manifest.md`
- `paper/versions/ral/figure_table_binding.md`
- `paper/versions/ral/figures/invalid_actions_recovery.csv`
- `paper/versions/ral/figures/invalid_actions_recovery.tex`
- `paper/versions/ral/figures/main_condition_ordering.csv`
- `paper/versions/ral/figures/main_condition_ordering.tex`
- `paper/versions/ral/figures/planner_tool_overhead.csv`
- `paper/versions/ral/figures/planner_tool_overhead.tex`
- `paper/versions/ral/figures/system_overview.csv`
- `paper/versions/ral/figures/system_overview.tex`
- `paper/versions/ral/latex_assembly_notes.md`
- `paper/versions/ral/main.pdf`
- `paper/versions/ral/main.tex`
- `paper/versions/ral/preamble_shared.tex`
- `paper/versions/ral/refs/references.bib`
- `paper/versions/ral/reviewer_submission/README.md`
- `paper/versions/ral/reviewer_submission/main.pdf`
- `paper/versions/ral/reviewer_submission/main.tex`
- `paper/versions/ral/sections/intro.tex`
- `paper/versions/ral/sections/results.tex`
- `paper/versions/ral/sections/setup.tex`
- `paper/versions/ral/tables/experimental_design_summary.csv`
- `paper/versions/ral/tables/experimental_design_summary.tex`
- `paper/versions/ral/tables/final_closure_result_summary.csv`
- `paper/versions/ral/tables/final_closure_result_summary.tex`
- `paper/versions/ral/tables/focused_ablation_summary.csv`
- `paper/versions/ral/tables/focused_ablation_summary.tex`
- `paper/versions/ral/tables/harder_task_summary.csv`
- `paper/versions/ral/tables/harder_task_summary.tex`
- `paper/versions/ral/tables/main_outcome_summary.csv`
- `paper/versions/ral/tables/main_outcome_summary.tex`
- `paper/versions/ral/tables/planner_tool_overhead_summary.csv`
- `paper/versions/ral/tables/planner_tool_overhead_summary.tex`
- `src/isaacsim_agent/eval/block_a_ral_assets.py`

## Commands run

- Source-of-truth and repo-state reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,220p' AGENTS.md`
  - `git show HEAD:STATUS.md`
  - `sed -n '1,260p' docs/ral_writing_playbook.md`
  - `sed -n '1,260p' paper/versions/ral/main.tex`
  - `sed -n '1,220p' paper/versions/ral/sections/*.tex`
  - `sed -n '1,220p' paper/versions/ral/figures/*.tex`
  - `sed -n '1,220p' paper/versions/ral/tables/*.tex`
  - `sed -n '1,260p' paper/versions/ral/refs/references.bib`
  - `find results/processed/block_a_final_closure -maxdepth 2 -type f | sort`
  - `git status --short --untracked-files=all`
- Result and artifact inspection:
  - `sed -n '1,260p' results/processed/block_a_final_closure/block_a_final_closure_summary.{md,json}`
  - `sed -n '1,260p' results/processed/block_a_final_closure/run_summary.jsonl`
  - `sed -n '1,260p' results/block_a_runtime_only_ablation/.../events.jsonl`
  - `sed -n '1,260p' results/block_a_prompt_only_ablation/.../events.jsonl`
  - `sed -n '1,260p' results/.../artifacts/planner_trace.json`
  - `sed -n '1,260p' results/.../artifacts/trajectory.json`
- Asset regeneration and compile validation:
  - `python scripts/package_block_a_ral_assets.py`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex && bibtex main && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex && bibtex main && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral/reviewer_submission`
  - `pdfinfo main.pdf | sed -n '1,20p'`
    with working directories:
    - `paper/versions/ral`
    - `paper/versions/ral/reviewer_submission`

## Validation results

- Reviewer-facing submission:
  - `paper/versions/ral/reviewer_submission/main.pdf` compiles successfully
  - `pdfinfo` reports `Pages: 7`
- Journal scaffold:
  - `paper/versions/ral/main.pdf` compiles successfully
  - `pdfinfo` reports `Pages: 6`
- Figure / table state:
  - Figure 1 is present in the shared manuscript source and compiles in both
    variants
  - the three main result figures remain active manuscript figures
  - the main dense result reporting is split across `main_outcome_summary` and
    `planner_tool_overhead_summary`
- Framing check:
  - no prompt-first headline wording was reintroduced
  - no new experiments or invented numbers were added
  - P2 workload wording remains descriptive rather than overstated
- Remaining warnings:
  - underfull-box warnings remain from narrow-column line breaking
  - the reviewer-facing `conference` build emits the standard final camera-
    ready column-balance reminder

## Remaining gaps

- do the final author-side line edit and anonymity pass
- decide whether the schematic Figure 1 environment insets should remain as
  reviewer-facing surrogates or be replaced by literal simulator screenshots
- decide whether the support-only dense result summary should remain support-
  only in the final submission package
- optionally replace any remaining arXiv-only references if authors later
  confirm archival versions they prefer

## Next recommended sub-milestone

- Move from `reviewer-facing artifact overhaul` to `author final-edit /
  submission prep` by:
  - reviewing `paper/versions/ral/reviewer_submission/main.pdf` line by line
  - checking the 7-page reviewer-facing PDF for anonymity and final float
    locality
  - preserving the current contract/runtime framing unless authors explicitly
    request another scope change
