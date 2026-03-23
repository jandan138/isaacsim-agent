# LaTeX Assembly Notes

## Scope of this pass

- Preserve the shared RA-L scaffold under `paper/versions/ral/`.
- Keep the anonymous reviewer-facing entry under
  `paper/versions/ral/reviewer_submission/`.
- Keep Figure 1 frozen and out of scope.
- Focus this pass on improving Table I / non-Figure-1 manuscript fit.
- Treat the latest Table I follow-up as a final polish pass, not a redesign
  pass.
- Do not add experiments, invent numbers, or widen the evidence base.
- Address the expert-review blocking issues around:
  - a concrete contract/interface display
  - deterministic-planner framing and fixed-task-set coverage
  - reviewer-facing internal terminology cleanup
  - precise R1 feedback semantics and executor semantics
  - repeated main-conclusion wording and related-work polish
  - keywords and a low-risk Fig. 2 accessibility follow-through

## Variant split

- Initial RA-L submission artifact:
  `paper/versions/ral/reviewer_submission/main.tex`
  - class mode:
    `IEEEtran` conference style
  - current compiled PDF:
    `paper/versions/ral/reviewer_submission/main.pdf`
  - current page count:
    `8`
- Accepted-version journal assembly scaffold:
  `paper/versions/ral/main.tex`
  - class mode:
    `IEEEtran` journal style
  - current compiled PDF:
    `paper/versions/ral/main.pdf`
  - current page count:
    `8`
- Shared content for both:
  - `sections/`
  - `figures/`
  - `tables/`
  - `refs/`
  - `preamble_shared.tex`

## Figure assembly changes

- Figure 1 remains frozen to the manually selected asset:
  - `figures/fig1_system_overview_frozen.png`
  - `figures/fig1_system_overview_frozen.pdf` when present
  - `figures/fig1_system_overview_frozen.tex`
- This pass did not redesign, regenerate, or iterate on Figure 1.
- The active result figures remain:
  - `main_condition_ordering`
    - full-width outcome matrix with explicit `fail`, `recovered`, and `clean`
      labels in the cells
  - `planner_tool_overhead`
    - consolidated workload comparison with `planner/tool` labels
  - `invalid_actions_recovery`
    - two-part mechanism figure; the runtime panel now carries explicit text
      labels inside the colored cells so the distinction does not rely on color
      alone

## Table assembly changes

- Added one manual manuscript-facing table:
  - `tables/contract_interface_examples.tex`
  - built from saved prompt texts and archived planner traces
  - retained as `Table I` instead of being converted to a formal figure
    because keeping the existing table identity avoids figure/table renumbering,
    caption churn, and new float-order risk in the 8-page RA-L layout
  - this pass refined the previous matrix draft into a quieter
    manuscript-style comparison table:
    - one low-key shared declared-tool note
    - a 4-column comparison matrix
    - two body rows only: example emission and dispatchability
  - the design goal was reduction and manuscript fit, not decorative styling
  - the final polish follow-up kept the same layout and limited the remaining
    Table I refinements to:
    - the shorter requested caption
    - the lower-weight `Declared tools:` note
    - lighter P2 example / dispatchability wording
- Kept the regenerated main-text tables:
  - `tables/experimental_design_summary.tex`
  - `tables/main_outcome_summary.tex`
  - `tables/planner_tool_overhead_summary.tex`
- Kept the support-only tables:
  - `tables/final_closure_result_summary.tex`
  - `tables/focused_ablation_summary.tex`
  - `tables/harder_task_summary.tex`

## Reproducibility and wording changes

- The earlier Table I reduction pass changed the Table I asset and the short
  intro/setup sentences that describe it; the final polish follow-up changed
  only the live Table I asset and left those intro/setup framing sentences
  unchanged.
- The deterministic-planner framing, executor semantics, and other wording
  clarifications listed below remained in place from the earlier
  reviewer-facing cleanup work.
- `sections/setup.tex` now states explicitly that:
  - the planner backend is deterministic by design
  - the empirical unit is the task instance, not i.i.d. stochastic rollout
    replication
  - the main comparison covers 21 task instances across four cohorts
  - the two focused ablations add 8 task instances
  - the reported evaluation set contains 29 task instances and 146 executions
  - the quantitative comparisons are descriptive rather than a
    confidence-interval / significance-test exercise
- The setup/results text now explains the exact `R1` repair path:
  - same tool list on retry
  - literal `validation_error` string
  - appended repair instruction
  - one retry only
- The setup text now clarifies the executor-visible action semantics:
  - `navigate_to` dispatches one deterministic step toward the configured goal
  - `scripted_pick_place_step` advances one phase of a fixed scripted
    pick-and-place sequence
- Reviewer-facing internal wording was removed where avoidable in the active
  manuscript.
- Earlier reviewer-facing cleanup work also normalized the last small labels:
  - `covered` -> `evaluated`
  - `Main factorial` -> `Main matrix`
  - `Recoverable probes` -> `Recovery probes`
  - the ROS 2 analogy now emphasizes typed interface definition more directly
- The related-work comparison to SayCan, Code as Policies, and ProgPrompt was
  tightened around affordance grounding, code/program generation, and declared
  action interfaces.
- Shared `IEEEkeywords` were added in `sections/abstract.tex`; both variants
  compile with the same keyword line.

## Build verification

- Current verification, journal scaffold:
  `cd paper/versions/ral && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - compile status:
    success
  - page count:
    `8`
- Current verification, reviewer-facing submission:
  `cd paper/versions/ral/reviewer_submission && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - compile status:
    success
  - page count:
    `8`
- Follow-up compile after the Table I reduction pass:
  - `cd paper/versions/ral/reviewer_submission && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - `cd paper/versions/ral && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - reran the same single-pass pair after fixing the dispatchability-row cell
    wrapping
  - reran the same single-pass pair once more so the final shared-note and
    intro/setup wording tweaks were synchronized into both PDFs
  - both variants completed successfully and remained at `8` pages
- Final polish follow-up compile pair:
  - `cd paper/versions/ral/reviewer_submission && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - `cd paper/versions/ral && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - both variants completed successfully and remained at `8` pages

## Remaining non-blockers

- Underfull-box warnings remain in narrow-column prose.
- Small overfull-box warnings remain in:
  - `figures/main_condition_ordering.tex`
  - `figures/invalid_actions_recovery.tex`
- The refined Table I now compiles without its previous table-local overfull-box
  warning; reviewer page 2 was checked after rebuild and the table now reads as
  a quieter manuscript comparison table rather than an explanatory panel.
- The final polish follow-up did not introduce new Table I-local warnings and
  further reduced the top-note and P2-column visual weight on reviewer page 2.
- The reviewer-facing conference build still emits the standard last-page
  column-balance reminder.
- Figure 1 itself remains out of scope for this branch.
