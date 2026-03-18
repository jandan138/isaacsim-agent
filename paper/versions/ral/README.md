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

- Figure 1 remains the frozen manually selected asset and was not redesigned or
  regenerated in this pass.
- This pass addressed the expert-review blocking issues around:
  - a compact contract/interface example display built from saved prompt texts
    and archived planner traces
  - deterministic-planner framing and fixed-task-set evaluation language
  - reviewer-facing internal terminology cleanup
  - precise R1 feedback semantics and executor semantics
  - repeated conclusion wording, related-work polish, and keywords
  - low-risk Fig. 2 label support for grayscale / color-deficient reading
- The setup section now includes a compact implementation snapshot covering the
  deterministic local planner backend, the fixed evaluation set, contract and
  runtime realizations, and executor-visible action semantics.
- `sections/abstract.tex` now inserts shared `IEEEkeywords`, which compile in
  both the journal scaffold and the reviewer-facing build.
- Remaining non-blockers are documented in
  `paper/versions/ral/latex_assembly_notes.md` and `STATUS.md`.
