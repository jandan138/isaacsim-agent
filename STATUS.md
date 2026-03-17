# STATUS.md

## Current status

- Date: 2026-03-17
- Plan source of truth: `plan.md`
- Paper-writing source of truth: `docs/ral_writing_playbook.md`
- Active milestone: `M11. Paper drafting`
- Milestone state:
  - this run completed `RA-L citation grounding + light polish pass`
- Completion level:
  - `paper/versions/ral/full_draft_v1.md` now carries grounded related-work
    citations, keeps the contract/runtime framing, has a `176`-word abstract,
    removes the Section 4.1 meta-commentary, uses neutral Section 3.3 wording,
    and adds the requested architectural mapping in discussion
  - `paper/versions/ral/related_work_draft.md` now uses verified literature
    rather than `[RW*]` placeholders and stays anchored to the robotics-systems
    framing
  - `paper/versions/ral/citation_todo.md`,
    `paper/versions/ral/full_draft_v1_notes.md`,
    `paper/versions/ral/README.md`, and
    `paper/versions/ral/bibliography_candidates.md` now record the grounded
    citation set, abstract-compression strategy, discussion-mapping rationale,
    and current draft state

## Run context

- This run stayed within the requested boundaries:
  - no new experiments
  - no experiment-code changes
  - no heavy Isaac Sim / ROS workflow launch
  - no figure/table regeneration
  - no LaTeX manuscript assembly
  - no venue switch
  - no full-structure rewrite
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
  - `paper/versions/ral/README.md`
  - `paper/versions/ral/full_draft_v1.md`
  - `paper/versions/ral/related_work_draft.md`
  - `paper/versions/ral/citation_todo.md`
  - `paper/versions/ral/full_draft_v1_notes.md`
  - `paper/versions/ral/figure_table_binding.md`
  - `paper/notes/review_risks.md`
  - `paper/notes/version_deltas.md`
- Literature verification sources consulted:
  - arXiv abstract pages for the embodied-planning, TAMP, and benchmark-style
    references used in the grounded drafts
  - `design.ros2.org/articles/actions.html`
  - `https://doi.org/10.1126/scirobotics.abm6074`
  - `https://www.behaviortree.dev/docs/intro/`
  - `https://www.behaviortree.dev/docs/4.0.2/tutorial-advanced/pre_post_conditions/`
- Agent teaming:
  - spawned two explorer sub-agents for parallel citation mapping
  - soft-timeout waits of `120000 ms` and `180000 ms` produced no completion
    notification while local drafting continued
  - sent one focused progress/blocker check to each agent without interrupting
    or reassigning work
  - both sub-agents later completed normally and reported no blockers; their
    outputs were used as cross-checks against the final local grounding pass

## Milestone summary

- Completed in this run:
  - replaced the former `[RW1]` through `[RW17]` placeholders in
    `paper/versions/ral/full_draft_v1.md` and
    `paper/versions/ral/related_work_draft.md` with verified literature
  - kept the priority citation anchors requested in the task:
    SayCan, Code as Policies, ProgPrompt, ROS 2 actions, BehaviorTree.CPP,
    PDDLStream, and the integrated TAMP review
  - tightened the execution-architecture related-work paragraph around ROS 2,
    PlanSys2, behavior trees, BehaviorTree.CPP, and TAMP interfaces
  - rewrote the broader-positioning paragraph around EmbodiedBench, IS-Bench,
    and Mind and Motion Aligned so the paper is framed as a narrower controlled
    systems study rather than a benchmark paper
  - compressed and checked the abstract to stay under the requested
    `<= 200`-word limit
  - removed the Section 4.1 meta-commentary sentence and left only the
    empirical pattern statement
  - renamed Section 3.3 to `Metrics and Evaluation Protocol` and removed
    `frozen study package` / `evidence freeze` phrasing from paper-facing text
  - added the requested discussion bridge to ROS 2 action semantics,
    behavior-tree guards, and TAMP operator/execution interfaces
  - updated the supporting docs that track citation status, rationale, and next
    steps
- Not completed in this run:
  - no figure/table asset refresh under `paper/assets/`
  - no caption-writing pass beyond keeping the approved figure/table markers
  - no anonymous RA-L LaTeX conversion

## Files changed

- `STATUS.md`
- `paper/versions/ral/README.md`
- `paper/versions/ral/full_draft_v1.md`
- `paper/versions/ral/related_work_draft.md`
- `paper/versions/ral/citation_todo.md`
- `paper/versions/ral/full_draft_v1_notes.md`
- `paper/versions/ral/bibliography_candidates.md`

Pre-existing modified shared files and source section drafts already present in
the working tree were left intact and not reverted.

## Commands run

- Source-of-truth reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,220p' AGENTS.md`
  - `sed -n '1,260p' STATUS.md`
  - `sed -n '1,260p' docs/ral_writing_playbook.md`
  - `sed -n '1,240p' paper/README.md`
  - `sed -n '1,220p' paper/shared/core_claim.md`
  - `sed -n '1,220p' paper/shared/contributions.md`
  - `sed -n '1,220p' paper/shared/findings.md`
  - `sed -n '1,220p' paper/shared/limitations.md`
  - `sed -n '1,260p' paper/shared/terminology.md`
  - `sed -n '1,260p' paper/shared/figures_and_tables.md`
  - `sed -n '1,260p' paper/versions/ral/README.md`
  - `sed -n '1,340p' paper/versions/ral/full_draft_v1.md`
  - `sed -n '1,260p' paper/versions/ral/related_work_draft.md`
  - `sed -n '1,260p' paper/versions/ral/citation_todo.md`
  - `sed -n '1,260p' paper/versions/ral/full_draft_v1_notes.md`
  - `sed -n '1,260p' paper/versions/ral/figure_table_binding.md`
  - `sed -n '1,260p' paper/notes/review_risks.md`
  - `sed -n '1,260p' paper/notes/version_deltas.md`
- Working-tree and inspection commands:
  - `git status --short`
  - `rg -n '\[RW[0-9]+\]' paper/versions/ral/full_draft_v1.md paper/versions/ral/related_work_draft.md`
  - `rg -n 'frozen study package|evidence freeze|prompt engineering study|prompt structure|package bookkeeping|core empirical result because' paper/versions/ral/full_draft_v1.md paper/versions/ral/related_work_draft.md`
  - `awk 'BEGIN{inabs=0} /^## Abstract/{inabs=1;next} /^## 1\./{inabs=0} inabs{print}' paper/versions/ral/full_draft_v1.md | wc -w`
  - `rg -n 'EmbodiedBench|IS-Bench|Mind and Motion Aligned|BehaviorTree.CPP documentation|Macenski et al\., 2022|Biggs et al\., 2019/2020|Garrett et al\., 2020' paper/versions/ral/full_draft_v1.md paper/versions/ral/related_work_draft.md`
  - `git diff -- paper/versions/ral/full_draft_v1.md paper/versions/ral/related_work_draft.md paper/versions/ral/citation_todo.md paper/versions/ral/full_draft_v1_notes.md paper/versions/ral/README.md paper/versions/ral/bibliography_candidates.md`

## Validation results

- Abstract length:
  - command:
    `awk 'BEGIN{inabs=0} /^## Abstract/{inabs=1;next} /^## 1\./{inabs=0} inabs{print}' paper/versions/ral/full_draft_v1.md | wc -w`
  - result:
    - abstract word count is `176`
- Placeholder scan:
  - command:
    `rg -n '\[RW[0-9]+\]' paper/versions/ral/full_draft_v1.md paper/versions/ral/related_work_draft.md`
  - result:
    - no `[RW*]` placeholders remain in either paper-facing draft
- Internal-term / expert-fix scan:
  - command:
    `rg -n 'frozen study package|evidence freeze|prompt engineering study|prompt structure|package bookkeeping|core empirical result because' paper/versions/ral/full_draft_v1.md paper/versions/ral/related_work_draft.md`
  - result:
    - no matches remain in the paper-facing drafts
- Priority-citation presence scan:
  - command:
    `rg -n 'EmbodiedBench|IS-Bench|Mind and Motion Aligned|BehaviorTree.CPP documentation|Macenski et al\., 2022|Biggs et al\., 2019/2020|Garrett et al\., 2020' paper/versions/ral/full_draft_v1.md paper/versions/ral/related_work_draft.md`
  - result:
    - the grounded drafts contain the intended execution-architecture and
      broader-positioning references
- Working-tree check:
  - command:
    `git status --short`
  - result:
    - the RA-L draft files listed above are modified or newly added as expected
    - pre-existing modified shared files and source drafts remain in the tree
      and were not reverted

## Next recommended sub-milestone

- Move from `citation-grounded + light polish` to `asset grounding` by:
  - regenerating the retained figures and tables from the final-closure and
    ablation freezes
  - drafting concise caption text aligned with the now-grounded related-work
    framing
  - deciding whether `[Table: focused ablation summary]` survives the RA-L page
    budget before the later anonymous LaTeX pass
