# RA-L Artifact Stack

This directory is the shared manuscript source tree plus the journal-style
assembly scaffold for the current RA-L package.

## Variant split

- Initial anonymous reviewer-facing submission:
  `paper/versions/ral/reviewer_submission/main.tex`
  - compiled PDF:
    `paper/versions/ral/reviewer_submission/main.pdf`
  - current page count:
    `8`
- Accepted-version journal scaffold:
  `paper/versions/ral/main.tex`
  - compiled PDF:
    `paper/versions/ral/main.pdf`
  - current page count:
    `8`

## Shared source layout

- `sections/`
  shared prose for both variants
- `figures/`
  frozen Figure 1 asset plus the three vector-first main result figures
- `tables/`
  the manual contract/interface display, the study matrix, and the main outcome
  / workload tables
- `refs/`
  shared bibliography and citation assets
- `preamble_shared.tex`
  shared packages, colors, and table helpers

## Main-text asset boundary

- Main-text figures:
  - `figures/fig1_system_overview_frozen.png`
  - `figures/fig1_system_overview_frozen.pdf` when present
  - `figures/fig1_system_overview_frozen.tex`
  - `figures/main_condition_ordering.{csv,tex}`
  - `figures/invalid_actions_recovery.{csv,tex}`
  - `figures/planner_tool_overhead.{csv,tex}`
- Main-text tables:
  - `tables/contract_interface_examples.tex`
  - `tables/experimental_design_summary.{csv,tex}`
  - `tables/main_outcome_summary.{csv,tex}`
  - `tables/planner_tool_overhead_summary.{csv,tex}`
- Support-only tables:
  - `tables/final_closure_result_summary.{csv,tex}`
  - `tables/focused_ablation_summary.{csv,tex}`
  - `tables/harder_task_summary.{csv,tex}`

## Compile workflow

Regenerate the summary-derived shared assets from the repo root when needed:

```bash
python scripts/package_block_a_ral_assets.py
```

Journal scaffold:

```bash
cd paper/versions/ral
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Reviewer-facing submission:

```bash
cd paper/versions/ral/reviewer_submission
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

## Current notes

- The active milestone for this branch is back on paper final-edit /
  submission prep; render-side work is parked for this pass.
- Figure 1 remains the frozen manually selected asset and was not redesigned or
  regenerated in this pass.
- This pass focused on non-Figure-1 manuscript visuals, specifically Table I.
- This pass replaced the previous card-style Table I redesign with a cleaner
  matrix-style manuscript table.
- Table I was intentionally retained as a table-numbered asset rather than
  converted into a formal figure so the manuscript could keep the existing
  figure numbering, table numbering, and intro/setup cross-references stable.
- The manual `tables/contract_interface_examples.tex` asset was substantially
  redesigned into a cleaner matrix-style manuscript table with:
  - one thin shared declared-tool strip
  - a four-column comparison matrix
  - row labels for cue, example emission, and runtime effect
- The design goal was readability and main-paper fit, not decorative figure
  styling.
- The redesign touched only the Table I asset and the two short intro/setup
  sentences that frame it; the other main-text figures, tables, and core
  result claims were left unchanged.
- The prior reviewer-facing cleanup items from the previous pass remain in
  place; this pass did not reopen Figure 1, add experiments, or change the core
  claim/contribution/finding/limitation layer.
- After the Table I redesign, both manuscript variants were rebuilt
  successfully and remain at `8` pages.
- Remaining non-blockers are documented in
  `paper/versions/ral/latex_assembly_notes.md` and `STATUS.md`.
