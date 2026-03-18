# LaTeX Assembly Notes

## Scope of this pass

- Preserve the shared RA-L scaffold under `paper/versions/ral/`.
- Keep the anonymous reviewer-facing entry under
  `paper/versions/ral/reviewer_submission/`.
- Keep Figure 1 frozen and out of scope.
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
- Kept the regenerated main-text tables:
  - `tables/experimental_design_summary.tex`
  - `tables/main_outcome_summary.tex`
  - `tables/planner_tool_overhead_summary.tex`
- Kept the support-only tables:
  - `tables/final_closure_result_summary.tex`
  - `tables/focused_ablation_summary.tex`
  - `tables/harder_task_summary.tex`

## Reproducibility and wording changes

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
- The related-work comparison to SayCan, Code as Policies, and ProgPrompt was
  tightened around affordance grounding, code/program generation, and declared
  action interfaces.
- Shared `IEEEkeywords` were added in `sections/abstract.tex`; both variants
  compile with the same keyword line.

## Build verification

- Full rebuild, journal scaffold:
  `cd paper/versions/ral && pdflatex -interaction=nonstopmode -halt-on-error main.tex && bibtex main && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - compile status:
    success
  - page count:
    `8`
- Full rebuild, reviewer-facing submission:
  `cd paper/versions/ral/reviewer_submission && pdflatex -interaction=nonstopmode -halt-on-error main.tex && bibtex main && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - compile status:
    success
  - page count:
    `8`
- Follow-up compile after the manual contract table insertion:
  - `cd paper/versions/ral && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - `cd paper/versions/ral/reviewer_submission && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - both completed successfully

## Remaining non-blockers

- Underfull-box warnings remain in narrow-column prose.
- Small overfull-box warnings remain in:
  - one row of `tables/contract_interface_examples.tex`
  - `figures/main_condition_ordering.tex`
  - `figures/invalid_actions_recovery.tex`
- The reviewer-facing conference build still emits the standard last-page
  column-balance reminder.
- Figure 1 itself remains out of scope for this branch.
