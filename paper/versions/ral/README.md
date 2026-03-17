# RA-L Working Draft Stack

This directory holds the active RA-L branch for the current Block A paper. The
evidence base remains fixed to the controlled-study scope defined in
`paper/shared/` and `docs/ral_writing_playbook.md`.

Current branch state:

- first-pass core prose is complete for introduction, setup/study design, and results
- second-pass prose is now complete for related work, discussion/limitations, and
  conclusion
- the branch now covers all main body sections in draft prose, but it has not yet
  been assembled into a final page-budgeted manuscript

## Branch policy

RA-L remains the best first target because the current evidence fits a compact,
results-first controlled systems study. This branch should continue to optimize for:

- the tightest framing of the controlled-study story
- the highest-value figures and tables only
- compressed introduction and related work
- explicit limitations with no scope creep

Use these inputs first:

- `paper/shared/core_claim.md`
- `paper/shared/findings.md`
- `paper/shared/limitations.md`
- `paper/shared/figures_and_tables.md`
- `paper/outlines/ral_outline.md`

## Current draft files

| File | Stage | Role |
| --- | --- | --- |
| `title_candidates.md` | prose | Candidate RA-L titles grouped by framing strength and reviewer risk. |
| `abstract_candidates.md` | prose | Three abstract variants that share the same Block A claim boundary. |
| `intro_draft.md` | prose | First-pass introduction that states the problem, gap, scope, findings preview, and contributions. |
| `setup_and_study_design_draft.md` | prose | Combined setup and study-design text defining task families, slices, contracts, variants, and metrics. |
| `results_draft.md` | prose | Results-first manuscript core anchored to the frozen Block A summaries. |
| `related_work_draft.md` | prose | Short RA-L related-work draft using explicit placeholder citations that still require literature verification. |
| `discussion_and_limitations_draft.md` | prose | Discussion of robotics relevance, design implications, and explicit study boundaries. |
| `conclusion_draft.md` | prose | Short conclusion that closes on bounded system-design findings. |
| `page_pressure_plan.md` | planning | Concrete trimming plan for assembling the draft within the RA-L 6-8 page budget. |
| `README.md` | prose | Branch policy, file relationships, and remaining work status for this RA-L version. |

## How these drafts relate

The documents are meant to be read in the same claim order as the eventual letter:

1. `title_candidates.md` and `abstract_candidates.md` define the outer framing.
2. `intro_draft.md` turns that framing into the paper's problem statement, scope, and
   contribution set.
3. `setup_and_study_design_draft.md` defines the controlled matrix that makes the
   claims interpretable.
4. `results_draft.md` is the anchor document for all scientific claims and should be
   treated as the main guardrail against drift in later prose passes.
5. `related_work_draft.md` positions the paper without widening the scope beyond the
   controlled-study framing.
6. `discussion_and_limitations_draft.md` and `conclusion_draft.md` close the argument
   while keeping the claims aligned to the frozen evidence.
7. `page_pressure_plan.md` defines what should be cut, compressed, or moved when the
   branch is assembled into a letter.

Practical rule:

- if a title, abstract, or introduction sentence cannot be supported by
  `results_draft.md` plus the frozen summaries, it should be revised or removed

## Placeholder policy for figures and tables

This prose pass intentionally uses placeholder markers instead of final numbering. The
allowed placeholders in this branch are:

- `[Fig: main condition ordering]`
- `[Fig: invalid actions and recovery]`
- `[Fig: planner/tool overhead]`
- `[Table: experimental design summary]`
- `[Table: final closure result summary]`
- `[Table: focused ablation summary]`

These labels are aligned with `paper/shared/figures_and_tables.md`. They are planning
markers only and do not imply that final manuscript assets already exist.

## Current prose coverage

The RA-L branch now has prose drafts for all major manuscript sections:

- title
- abstract
- introduction
- related work
- experimental setup / study design
- results
- discussion / limitations
- conclusion

## What remains before full draft assembly

The branch is not yet at full draft assembly. The main remaining steps are:

- replace the `[RW*]` placeholder citations in `related_work_draft.md` with verified
  literature
- assemble the section drafts into one manuscript-order body with consistent
  transitions and no duplicated wording
- execute the trimming actions in `page_pressure_plan.md`, especially for
  `intro_draft.md`, `setup_and_study_design_draft.md`, and `results_draft.md`
- regenerate final figures and tables from the `block_a_final_closure` freeze and
  decide whether the focused ablation table fits the RA-L page budget
- draft appendix / supplementary notes, anonymous artifact wording, and submission
  metadata as separate assembly-stage assets

## Anonymity and scope reminders

- maintain double-anonymous wording throughout
- keep the paper on Block A only
- do not widen the branch to memory, context management, tool abstraction, or randomization
- do not present the paper as a new-model paper or as a broad deployment claim
