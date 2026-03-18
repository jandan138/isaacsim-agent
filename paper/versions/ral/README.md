# RA-L Artifact Stack

This directory is now the shared manuscript source tree and the journal-style
assembly scaffold for the current Block A RA-L package.

## Variant split

- Initial anonymous reviewer-facing RA-L submission:
  `paper/versions/ral/reviewer_submission/main.tex`
  - compiled PDF:
    `paper/versions/ral/reviewer_submission/main.pdf`
  - current page count:
    `7`
- Accepted-version journal scaffold:
  `paper/versions/ral/main.tex`
  - compiled PDF:
    `paper/versions/ral/main.pdf`
  - current page count:
    `7`

## Shared source layout

- `sections/`
  shared prose for both variants
- `figures/`
  frozen Figure 1 asset plus the three vector-first main result figures
- `tables/`
  reviewer-facing study matrix, split outcome/workload tables, and support-only
  tables
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
  - `tables/experimental_design_summary.{csv,tex}`
  - `tables/main_outcome_summary.{csv,tex}`
  - `tables/planner_tool_overhead_summary.{csv,tex}`
- Support-only tables:
  - `tables/final_closure_result_summary.{csv,tex}`
  - `tables/focused_ablation_summary.{csv,tex}`
  - `tables/harder_task_summary.{csv,tex}`

## Compile workflow

Regenerate shared assets from the repo root:

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

- The manuscript keeps the contract / runtime-validation framing and does not
  revert to prompt-first wording.
- Figure 1 is now a frozen manually selected asset and is out of scope for any
  further redesign in this branch.
- The setup section now includes a compact implementation snapshot covering the
  local planner backend, deterministic JSON decoding, contract realizations,
  runtime realizations, and executor namespaces.
- Remaining non-blockers are documented in
  `paper/versions/ral/latex_assembly_notes.md` and `STATUS.md`.
