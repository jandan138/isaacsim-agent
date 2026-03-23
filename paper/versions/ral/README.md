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
- This pass focused on non-Figure-1 manuscript improvement, specifically Table I.
- This pass refined the previous Table I matrix draft into a more restrained
  manuscript-style comparison table.
- Table I was intentionally retained as a table-numbered asset rather than
  converted into a formal figure so the manuscript could keep the existing
  figure numbering, table numbering, and intro/setup cross-references stable.
- The manual `tables/contract_interface_examples.tex` asset was substantially
  tightened into a quieter manuscript-style comparison table with:
  - one low-key shared-tool note
  - a four-column comparison matrix
  - short micro-subtitles under the `P0` / `P1` / `P2` headers
  - only two body rows: example emission and dispatchability
- The design goal was reduction and manuscript fit, not decorative styling.
- The redesign touched only the Table I asset and the two short intro/setup
  sentences that frame it; the other main-text figures, tables, and core
  result claims were left unchanged.
- The prior reviewer-facing cleanup items from the previous pass remain in
  place; this pass did not reopen Figure 1, add experiments, or change the core
  claim/contribution/finding/limitation layer.
- One extra compile pair was needed after the dispatchability-row wrapping fix
  before the final one-pass sync compile.
- After the Table I reduction pass, both manuscript variants were rebuilt
  successfully and remain at `8` pages.
- A follow-up final polish pass kept Figure 1 frozen and preserved the same
  Table I structure, label, insertion point, and reviewer-facing anonymity.
- That follow-up was not a redesign pass: it kept the existing matrix layout
  and limited the live Table I refinements to the shorter caption, the
  lower-weight `Declared tools:` note, and lighter P2 wording.
- The follow-up stayed inside `tables/contract_interface_examples.tex`; the
  earlier intro/setup framing sentences remained unchanged in this round.
- A fresh single-pass rebuild of both manuscript variants after the final
  polish follow-up kept both PDFs at `8` pages with stable references.
- Remaining non-blockers are documented in
  `paper/versions/ral/latex_assembly_notes.md` and `STATUS.md`.
