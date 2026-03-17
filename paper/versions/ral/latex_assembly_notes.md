# LaTeX Assembly Notes

## Scope of this pass

- Preserve the journal-style scaffold under `paper/versions/ral/`.
- Keep the existing anonymous reviewer-facing submission entry under
  `paper/versions/ral/reviewer_submission/`.
- Keep the contract / runtime-validation framing intact.
- Do not add experiments, invent numbers, or widen the evidence base.

## Variant split

- Initial RA-L submission artifact:
  `paper/versions/ral/reviewer_submission/main.tex`
  - class mode:
    `IEEEtran` conference style
  - current compiled PDF:
    `paper/versions/ral/reviewer_submission/main.pdf`
  - current page count:
    `7`
- Accepted-version journal assembly scaffold:
  `paper/versions/ral/main.tex`
  - class mode:
    `IEEEtran` journal style
  - current compiled PDF:
    `paper/versions/ral/main.pdf`
  - current page count:
    `6`
- Shared content for both:
  - `sections/`
  - `figures/`
  - `tables/`
  - `refs/`
  - `preamble_shared.tex`

## Figure assembly changes

- Added `figures/system_overview.tex` as the new Figure 1.
- Folded the compact failure trace into Figure 1 rather than allocating a
  separate main-text float.
- Replaced the manuscript-facing raster wrappers with vector-first TikZ/PGF
  assets for:
  - `main_condition_ordering`
  - `invalid_actions_recovery`
  - `planner_tool_overhead`
- Removed the old debug-style visual treatment from the active manuscript
  figures: no packaging annotations, no beige debug canvas, and no raster-first
  dependence in the active reviewer-facing build.

## Table assembly changes

- Reformatted `experimental_design_summary.tex` into a full-width reviewer-
  facing matrix table.
- Replaced the former dense combined result table in the main text with:
  - `tables/main_outcome_summary.tex`
  - `tables/planner_tool_overhead_summary.tex`
- Kept `tables/final_closure_result_summary.tex`,
  `tables/focused_ablation_summary.tex`, and `tables/harder_task_summary.tex`
  as support-only assets.

## Reproducibility wording

- Added a compact implementation snapshot in `sections/setup.tex` covering:
  - planner identity and local access path
  - deterministic JSON decoding / no temperature or top-$p$
  - P0/P1/P2 realizations
  - R0/R1 realizations
  - executor tool namespaces

## Citation and prose cleanup

- Tightened the introduction wording without rewriting the manuscript around a
  new thesis.
- Kept the safer formal-venue replacements already present in
  `refs/references.bib`; remaining arXiv-only items stay only where no safer
  archival replacement was applied in this pass.

## Build verification

- Shared asset regeneration:
  `python scripts/package_block_a_ral_assets.py`
- Journal scaffold:
  `cd paper/versions/ral && pdflatex ... && bibtex main && pdflatex ...`
  - compile status:
    success
  - page count:
    `6`
- Reviewer-facing submission:
  `cd paper/versions/ral/reviewer_submission && pdflatex ... && bibtex main && pdflatex ...`
  - compile status:
    success
  - page count:
    `7`

## Remaining non-blockers

- Underfull-box warnings remain from narrow-column line breaking and float-page
  composition.
- The reviewer-facing system-overview insets are schematic renderings grounded
  in frozen layouts and traces; authors may still swap in literal simulator
  screenshots later if desired.
- The `IEEEtran` conference build emits the standard last-page column-balance
  reminder for camera-ready handling.
