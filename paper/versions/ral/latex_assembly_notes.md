# LaTeX Assembly Notes

## Scope of this pass

- Preserve the journal-style scaffold under `paper/versions/ral/`.
- Keep the existing anonymous reviewer-facing submission entry under
  `paper/versions/ral/reviewer_submission/`.
- Keep the contract / runtime-validation framing intact.
- Keep Figure 1 frozen and out of scope.
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
    `7`
- Shared content for both:
  - `sections/`
  - `figures/`
  - `tables/`
  - `refs/`
  - `preamble_shared.tex`

## Figure assembly changes

- Figure 1 is now frozen to the manually selected asset:
  - `figures/fig1_system_overview_frozen.png`
  - `figures/fig1_system_overview_frozen.pdf` when present
- The shared manuscript now reaches that frozen asset through
  `figures/fig1_system_overview_frozen.tex`.
- This pass does not redesign, regenerate, or iterate on Figure 1.
- Replaced the old shared grouped-bar template with figure-specific
  manuscript-facing assets:
  - `main_condition_ordering`
    - now a full-width outcome matrix with explicit `fail`, `recovered`, and
      `clean` states
  - `planner_tool_overhead`
    - now a consolidated retained `P1` / `P2` workload comparison with
      `planner/tool` labels instead of duplicated planner/tool panels
  - `invalid_actions_recovery`
    - now a two-part mechanism figure showing invalid-action elimination and
      runtime recovery rather than retry-only micro-panels

## Table assembly changes

- Kept the three main-text tables but refreshed their captions/labels so their
  roles are clearer beside the redesigned figures:
  - `tables/experimental_design_summary.tex`
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

- Tightened the introduction, setup, discussion, and conclusion wording without
  rewriting the manuscript around a new thesis.
- Updated `refs/references.bib` conservatively:
  - aligned `RT-2` to official PMLR proceedings metadata
  - added version/access notes to the BehaviorTree.CPP documentation entries
  - left `OK-Robot` and the two 2025 benchmark citations conservative where no
    same-title archival replacement was safely introduced in this pass

## Build verification

- Shared asset regeneration:
  `python scripts/package_block_a_ral_assets.py`
- Journal scaffold:
  `cd paper/versions/ral && pdflatex ... && bibtex main && pdflatex ...`
  - compile status:
    success
  - page count:
    `7`
- Reviewer-facing submission:
  `cd paper/versions/ral/reviewer_submission && pdflatex ... && bibtex main && pdflatex ...`
  - compile status:
    success
  - page count:
    `7`

## Remaining non-blockers

- Underfull-box warnings remain from narrow-column line breaking and float-page
  composition.
- Small overfull-box warnings remain in the compact Fig. 2 / Fig. 4
  table-figure hybrids, but the rendered reviewer PDF is legible.
- The reviewer-facing system-overview insets are schematic renderings grounded
  in frozen layouts and traces; authors may still swap in literal simulator
  screenshots later if desired.
- Figure 1 itself is no longer an active generator-owned asset.
- The `IEEEtran` conference build emits the standard last-page column-balance
  reminder for camera-ready handling.
