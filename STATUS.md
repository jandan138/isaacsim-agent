# STATUS.md

## Current status

- Date: 2026-03-17
- Plan source of truth: `plan.md`
- Paper-writing source of truth: `docs/ral_writing_playbook.md`
- Active milestone: `M11. Paper drafting`
- Milestone state:
  - the frozen Block A evidence base remains unchanged
  - this run advanced the RA-L branch from first-pass core prose to full main-body
    prose coverage plus an explicit RA-L trimming plan
- Completion level:
  - immutable evidence remains under:
    - `results/processed/block_a_final_closure/`
    - `results/processed/block_a_master_summary/`
    - `results/processed/block_a_runtime_only_ablation/`
    - `results/processed/block_a_prompt_only_ablation/`
    - `results/processed/block_a_manipulation_harder/`
    - `results/processed/block_a_cross_family_summary/`
  - the RA-L prose workspace now includes:
    - `paper/versions/ral/title_candidates.md`
    - `paper/versions/ral/abstract_candidates.md`
    - `paper/versions/ral/intro_draft.md`
    - `paper/versions/ral/setup_and_study_design_draft.md`
    - `paper/versions/ral/results_draft.md`
    - `paper/versions/ral/related_work_draft.md`
    - `paper/versions/ral/discussion_and_limitations_draft.md`
    - `paper/versions/ral/conclusion_draft.md`
    - `paper/versions/ral/page_pressure_plan.md`
    - `paper/versions/ral/README.md`

## Run context

- This run stayed within the requested boundaries:
  - no new experiments
  - no experiment-code changes
  - no `M7+` implementation work
  - no CoRL / Autonomous Robots branch migration
  - no final manuscript figure/table regeneration
  - no LaTeX manuscript assembly
  - no heavy Isaac Sim / ROS workflow launch
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
  - `paper/outlines/ral_outline.md`
  - `paper/versions/ral/README.md`
  - `paper/notes/submission_strategy.md`
  - `paper/notes/review_risks.md`
  - `paper/notes/version_deltas.md`
  - `paper/notes/open_questions.md`
  - `paper/versions/ral/title_candidates.md`
  - `paper/versions/ral/abstract_candidates.md`
  - `paper/versions/ral/intro_draft.md`
  - `paper/versions/ral/setup_and_study_design_draft.md`
  - `paper/versions/ral/results_draft.md`
- Frozen evidence consumed in this run:
  - none directly reopened
  - second-pass prose stayed anchored to the frozen evidence via
    `paper/shared/core_claim.md`, `paper/shared/findings.md`,
    `paper/shared/limitations.md`, and the first-pass RA-L drafts
- Agent teaming:
  - spawned two explorer sub-agents in parallel
  - one explorer returned a compact claim / terminology / scope-boundary memo for the
    first-pass drafts
  - one explorer returned a page-pressure memo tied to concrete RA-L draft modules
  - both sub-agents completed normally; no stall intervention or reassignment was
    needed

## Milestone summary

- Completed in this run:
  - created `paper/versions/ral/related_work_draft.md`
  - created `paper/versions/ral/discussion_and_limitations_draft.md`
  - created `paper/versions/ral/conclusion_draft.md`
  - created `paper/versions/ral/page_pressure_plan.md`
  - updated `paper/versions/ral/README.md` to reflect full main-body prose coverage
    and remaining assembly-stage work
  - kept Related Work citations as explicit `[RW*]` placeholders rather than
    pretending the literature pass was already complete
  - kept Discussion and Conclusion aligned to the Block A controlled-study framing
    and explicit non-claims
  - produced a page-pressure plan that identifies concrete overlength hotspots in the
    existing Introduction, Setup/Study Design, and Results drafts
- Not completed in this run:
  - no verified literature replacement for `[RW*]` placeholder citations
  - no single-file full manuscript assembly yet
  - no final figure/table regeneration from the final-closure freeze
  - no appendix / supplementary / anonymous artifact statement yet
  - no trimming edits yet to the first-pass introduction, setup/study design, or
    results prose

## Files changed

- `STATUS.md`
- `paper/versions/ral/README.md`
- `paper/versions/ral/related_work_draft.md`
- `paper/versions/ral/discussion_and_limitations_draft.md`
- `paper/versions/ral/conclusion_draft.md`
- `paper/versions/ral/page_pressure_plan.md`

## Commands run

- Source-of-truth reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,260p' AGENTS.md`
  - `sed -n '1,260p' STATUS.md`
  - `sed -n '1,260p' docs/ral_writing_playbook.md`
  - `sed -n '1,220p' paper/README.md`
  - `sed -n '1,220p' paper/shared/core_claim.md`
  - `sed -n '1,220p' paper/shared/contributions.md`
  - `sed -n '1,260p' paper/shared/findings.md`
  - `sed -n '1,260p' paper/shared/limitations.md`
  - `sed -n '1,260p' paper/shared/terminology.md`
  - `sed -n '1,260p' paper/shared/figures_and_tables.md`
  - `sed -n '1,320p' paper/outlines/ral_outline.md`
  - `sed -n '321,420p' paper/outlines/ral_outline.md`
  - `sed -n '1,260p' paper/versions/ral/README.md`
  - `sed -n '1,240p' paper/notes/submission_strategy.md`
  - `sed -n '1,240p' paper/notes/review_risks.md`
  - `sed -n '1,240p' paper/notes/version_deltas.md`
  - `sed -n '1,260p' paper/notes/open_questions.md`
  - `sed -n '1,260p' paper/versions/ral/title_candidates.md`
  - `sed -n '1,260p' paper/versions/ral/abstract_candidates.md`
  - `sed -n '1,320p' paper/versions/ral/intro_draft.md`
  - `sed -n '1,320p' paper/versions/ral/setup_and_study_design_draft.md`
  - `sed -n '1,360p' paper/versions/ral/results_draft.md`
- Local status and sizing:
  - `wc -w paper/versions/ral/*.md`
  - `git status --short`
- Post-edit reads:
  - `sed -n '1,240p' paper/versions/ral/related_work_draft.md`
  - `sed -n '1,260p' paper/versions/ral/discussion_and_limitations_draft.md`
  - `sed -n '1,220p' paper/versions/ral/conclusion_draft.md`
  - `sed -n '1,320p' paper/versions/ral/page_pressure_plan.md`
  - `sed -n '1,260p' paper/versions/ral/README.md`
- Validation:
  - `rg -n "state of the art|general embodied intelligence|sim-to-real|real-world safety|real-world readiness|deployment-ready|deployment ready|SOTA|universal best|complete framework|benchmark supremacy|generally best embodied|generally strongest|safety guarantee" paper/versions/ral -S`
  - `rg -n "\[RW[0-9]+\]" paper/versions/ral -S`
  - `rg -n "prompt/interface structure|runtime validation|invalid action|recovery|planner/tool overhead|controlled systems study|controlled study" paper/versions/ral/related_work_draft.md paper/versions/ral/discussion_and_limitations_draft.md paper/versions/ral/conclusion_draft.md -S`
  - `wc -w paper/versions/ral/related_work_draft.md paper/versions/ral/discussion_and_limitations_draft.md paper/versions/ral/conclusion_draft.md paper/versions/ral/page_pressure_plan.md paper/versions/ral/README.md`
  - `git diff -- paper/versions/ral/README.md paper/versions/ral/related_work_draft.md paper/versions/ral/discussion_and_limitations_draft.md paper/versions/ral/conclusion_draft.md paper/versions/ral/page_pressure_plan.md`
  - `git status --short paper/versions/ral STATUS.md`

## Validation results

- Overclaim scan found only negative guardrail phrasing, not unsupported positive
  claims.
  - command:
    `rg -n "state of the art|general embodied intelligence|sim-to-real|real-world safety|real-world readiness|deployment-ready|deployment ready|SOTA|universal best|complete framework|benchmark supremacy|generally best embodied|generally strongest|safety guarantee" paper/versions/ral -S`
  - result:
    - `paper/versions/ral/intro_draft.md` contains a negative guardrail phrase about
      not claiming benchmark supremacy
    - `paper/versions/ral/related_work_draft.md` contains a negative guardrail phrase
      about not claiming a deployment-ready runtime stack
- Placeholder citation scan confirmed that `[RW*]` markers appear only in
  `paper/versions/ral/related_work_draft.md`.
  - command: `rg -n "\[RW[0-9]+\]" paper/versions/ral -S`
  - result: all placeholder-citation matches were confined to the related-work draft
- Terminology scan confirmed that the new second-pass prose uses the intended core
  terms.
  - command:
    `rg -n "prompt/interface structure|runtime validation|invalid action|recovery|planner/tool overhead|controlled systems study|controlled study" paper/versions/ral/related_work_draft.md paper/versions/ral/discussion_and_limitations_draft.md paper/versions/ral/conclusion_draft.md -S`
  - result: all new files contain the expected terminology without introducing a new
    framing
- New-file word counts are within a plausible RA-L drafting range, while
  `page_pressure_plan.md` intentionally remains longer because it is a planning note.
  - command:
    `wc -w paper/versions/ral/related_work_draft.md paper/versions/ral/discussion_and_limitations_draft.md paper/versions/ral/conclusion_draft.md paper/versions/ral/page_pressure_plan.md paper/versions/ral/README.md`
  - result:
    - `related_work_draft.md`: `420`
    - `discussion_and_limitations_draft.md`: `791`
    - `conclusion_draft.md`: `175`
    - `page_pressure_plan.md`: `1014`
    - `README.md`: `755`
- Diff inspection matched the requested file scope for this run.
  - command:
    `git diff -- paper/versions/ral/README.md paper/versions/ral/related_work_draft.md paper/versions/ral/discussion_and_limitations_draft.md paper/versions/ral/conclusion_draft.md paper/versions/ral/page_pressure_plan.md`
  - result: only the requested RA-L prose/planning files changed inside the active
    scope, plus `STATUS.md`

## Next recommended sub-milestone

- Move from section-level prose coverage to `full draft assembly` by:
  - verifying and replacing the `[RW*]` citations in `related_work_draft.md`
  - merging the section drafts into one RA-L-order manuscript body
  - trimming the existing Introduction, Setup/Study Design, and Results drafts
    according to `paper/versions/ral/page_pressure_plan.md`
  - deciding the final RA-L figure/table budget before appendix and submission
    metadata are drafted
