# STATUS.md

## Current status

- Date: 2026-03-18
- Plan source of truth: `plan.md`
- Paper-writing source of truth: `docs/ral_writing_playbook.md`
- Active milestone: `M11. Paper drafting`
- Milestone state:
  - this run completed `Fig. 2 / 3 / 4 readability, table/setup clarity, and bibliography polish`
- Completion level:
  - the reviewer-facing submission variant compiles successfully at `7` pages:
    `paper/versions/ral/reviewer_submission/main.pdf`
  - the journal scaffold compiles successfully at `7` pages:
    `paper/versions/ral/main.pdf`
  - Figure 1 remains frozen at
    `paper/versions/ral/figures/fig1_system_overview_frozen.*`
  - the active manuscript-facing result figures are now regenerated from the
    frozen processed summaries with figure-specific layouts rather than the old
    generic grouped-bar template

## Run context

- This run stayed within the requested boundaries:
  - no new experiments
  - no Figure 1 redesign, regeneration, relabeling, or replacement
  - no venue switch
  - no change to the paper's contract / runtime-validation framing
  - no reversion to prompt-first wording
  - no strong P2 efficiency overclaim
  - no large-scale prose rewrite
  - no invented numbers or citations
- Source-of-truth docs consumed in this run:
  - `plan.md`
  - `AGENTS.md`
  - `STATUS.md`
  - `docs/ral_writing_playbook.md`
  - `paper/README.md`
  - `paper/shared/core_claim.md`
  - `paper/shared/contributions.md`
  - `paper/shared/findings.md`
  - `paper/shared/limitations.md`
  - `paper/shared/terminology.md`
  - `paper/shared/figures_and_tables.md`
  - `paper/versions/ral/README.md`
  - `paper/versions/ral/figure_table_binding.md`
  - `paper/versions/ral/page_pressure_plan.md`
  - `paper/versions/ral/latex_assembly_notes.md`
  - `paper/versions/ral/full_draft_v1.md`
  - `paper/versions/ral/full_draft_v1_notes.md`
  - `paper/versions/ral/reviewer_submission/main.tex`
  - `paper/versions/ral/main.tex`
  - `paper/versions/ral/sections/`
  - `paper/versions/ral/figures/`
  - `paper/versions/ral/tables/`
  - `paper/versions/ral/refs/`
  - `paper/versions/ral/asset_manifest.md`
  - `results/processed/block_a_final_closure/`
  - `results/processed/block_a_master_summary/`
  - `results/processed/block_a_prompt_only_ablation/`
  - `results/processed/block_a_runtime_only_ablation/`
  - `results/processed/block_a_manipulation_harder/`
  - `results/processed/block_a_cross_family_summary/`
  - `scripts/package_block_a_ral_assets.py`
  - `src/isaacsim_agent/eval/block_a_ral_assets.py`
- Agent teaming:
  - used three sub-agents with completed worklogs:
    - figure-audit explorer:
      `.codex/worklogs/subagents/2026-03-18/figure-audit.md`
    - text/table worker:
      `.codex/worklogs/subagents/2026-03-18/text-table-worker.md`
    - citation-audit explorer:
      `.codex/worklogs/subagents/2026-03-18/citation-audit.md`
  - all three sub-agents completed normally; no interruptions or stall
    interventions were needed

## Milestone summary

- Completed in this run:
  - audited the current reviewer-facing PDF, manuscript figure wrappers,
    generator code, and frozen result summaries to separate data-equality
    effects from layout problems
  - replaced the old generic grouped-bar result-figure pipeline with
    figure-specific manuscript designs:
    - Fig. 2:
      full-width outcome matrix with in-cell counts and explicit
      `fail` / `recovered` / `clean` states
    - Fig. 3:
      consolidated retained `P1` versus `P2` workload comparison with
      `planner/tool` pair labels instead of duplicated planner/tool panels
    - Fig. 4:
      two-part mechanism figure showing fixed-`R0` invalid-action elimination
      plus fixed-`P1` runtime recovery, with retries demoted to annotation
  - tightened `sections/results.tex` to match the redesigned figures
  - tightened `sections/setup.tex`, `sections/intro.tex`,
    `sections/discussion.tex`, and `sections/conclusion.tex` for local
    readability and reproducibility clarity without changing findings
  - improved the table captions/labels in the generator-owned RA-L tables
  - polished the bibliography conservatively:
    - aligned `RT-2` to official PMLR proceedings metadata
    - added checked version/access notes to the BehaviorTree.CPP
      documentation entries
    - left `OK-Robot` as a manual author decision rather than auto-swapping to
      a different-title RSS demo citation
  - rebuilt both manuscript variants and checked figure rendering from the
    reviewer-facing PDF rasterization
- Not completed in this run:
  - no new experiments
  - no Figure 1 work beyond preserving the frozen asset
  - no bulk cite-key rename pass

## Files changed

- `STATUS.md`
- `paper/versions/ral/README.md`
- `paper/versions/ral/asset_manifest.md`
- `paper/versions/ral/figure_table_binding.md`
- `paper/versions/ral/latex_assembly_notes.md`
- `paper/versions/ral/full_draft_v1_notes.md`
- `paper/versions/ral/figures/main_condition_ordering.csv`
- `paper/versions/ral/figures/main_condition_ordering.tex`
- `paper/versions/ral/figures/invalid_actions_recovery.csv`
- `paper/versions/ral/figures/invalid_actions_recovery.tex`
- `paper/versions/ral/figures/planner_tool_overhead.csv`
- `paper/versions/ral/figures/planner_tool_overhead.tex`
- `paper/versions/ral/refs/references.bib`
- `paper/versions/ral/refs/references_note.tex`
- `paper/versions/ral/sections/conclusion.tex`
- `paper/versions/ral/sections/discussion.tex`
- `paper/versions/ral/sections/intro.tex`
- `paper/versions/ral/sections/results.tex`
- `paper/versions/ral/sections/setup.tex`
- `paper/versions/ral/tables/experimental_design_summary.csv`
- `paper/versions/ral/tables/experimental_design_summary.tex`
- `paper/versions/ral/tables/main_outcome_summary.tex`
- `paper/versions/ral/tables/planner_tool_overhead_summary.tex`
- `paper/versions/ral/main.pdf`
- `paper/versions/ral/reviewer_submission/main.pdf`
- `src/isaacsim_agent/eval/block_a_ral_assets.py`

## Commands run

- Source-of-truth and repo-state reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,240p' AGENTS.md`
  - `sed -n '1,260p' STATUS.md`
  - `sed -n '1,260p' docs/ral_writing_playbook.md`
  - `git status --short --untracked-files=all`
- Manuscript and asset audit:
  - `sed -n ...` over the requested paper-level `.md`, `.tex`, `.csv`, and
    `.bib` files
  - `pdftoppm -png paper/versions/ral/reviewer_submission/main.pdf /tmp/ral_review_current`
  - `pdftoppm -f 4 -l 6 -png paper/versions/ral/reviewer_submission/main.pdf /tmp/ral_review_new`
- Packaging and code validation:
  - `python -m py_compile src/isaacsim_agent/eval/block_a_ral_assets.py`
  - `python scripts/package_block_a_ral_assets.py`
- Compile validation:
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex && bibtex main && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex && bibtex main && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral/reviewer_submission`
  - `pdfinfo main.pdf | sed -n '1,20p'`
    with working directory `paper/versions/ral`
  - `pdfinfo main.pdf | sed -n '1,20p'`
    with working directory `paper/versions/ral/reviewer_submission`

## Validation results

- Reviewer-facing submission:
  - `paper/versions/ral/reviewer_submission/main.pdf` compiles successfully
  - `pdfinfo` reports `Pages: 7`
  - reviewer-scale rasterization confirms that:
    - Fig. 2 is now a readable full-width matrix
    - Fig. 3 is now a readable retained-workload comparison
    - Fig. 4 is now a readable invalid/recovery mechanism figure
- Journal scaffold:
  - `paper/versions/ral/main.pdf` compiles successfully
  - `pdfinfo` reports `Pages: 7`
- Figure 1 state:
  - still inserted via `figures/fig1_system_overview_frozen.tex`
  - still resolves to the frozen manual asset
  - intentionally not modified in this pass
- Bibliography state:
  - `references.bib` compiles successfully after the conservative metadata
    cleanup
- Remaining warnings / non-blockers:
  - underfull-box warnings remain in narrow-column prose
  - small overfull-box warnings remain in the compact Fig. 2 / Fig. 4
    table-figure hybrids, but the rendered reviewer PDF is legible
  - the reviewer-facing `conference` build still emits the standard
    column-balance reminder

## Remaining gaps

- do the final author-side line edit and anonymity pass
- optionally decide whether `OK-Robot` should stay arXiv-only or move to the
  RSS demo-format citation
- optionally trim the setup implementation snapshot if another small page/flow
  reduction is needed
- keep Figure 1 unchanged unless the authors explicitly choose a different
  frozen manual asset later

## Next recommended sub-milestone

- Move from `Fig. 2 / 3 / 4 readability pass` to `author final-edit /
  submission prep` by:
  - reviewing `paper/versions/ral/reviewer_submission/main.pdf` line by line
  - checking anonymity and wording one last time
  - making the final manual decision on any optional bibliography swaps
  - preserving the frozen Figure 1 asset and the current contract/runtime
    framing unless authors explicitly request another scope change
