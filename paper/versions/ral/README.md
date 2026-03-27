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

- The active milestone for this branch remains paper final-edit / submission
  prep.
- The latest pass focused on Fig. 4 layout cleanup only.
- Figure 1 was intentionally frozen and left untouched in this pass.
- Table I was intentionally left unchanged in this pass.
- The live `figures/invalid_actions_recovery.tex` asset keeps the same data,
  caption claim, panel meaning, and legend semantics, but now uses stricter
  table-driven geometry:
  - Panel A is a compact `Family | P0 | P1 | P2` matrix with a shared
    fixed-`R0` subtitle
  - Panel B is a fixed `Family | Runtime | Outcomes | Outcomes | Retry` grid
  - retry values now sit in a real column and the legend is one aligned bottom
    row
- The design goal in this pass was geometric alignment and manuscript fit, not
  palette redesign or new scientific content.
- After the latest Fig. 4 verification pass, both manuscript variants still
  compile successfully and remain at `8` pages.
- The current remaining non-blockers are now:
  - the long-standing overfull warning in `figures/main_condition_ordering.tex`
  - narrow-column underfull warnings in prose
  - the reviewer-facing conference column-balance reminder
- Earlier Table I-focused pass history remains documented in
  `paper/versions/ral/latex_assembly_notes.md` and `STATUS.md`.
