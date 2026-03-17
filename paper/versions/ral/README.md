# RA-L Working Draft Stack

This directory holds the active RA-L branch for the current controlled-study
paper in Isaac Sim. The evidence base remains fixed to the scope defined in
`paper/shared/` and `docs/ral_writing_playbook.md`.

Current branch state:

- `full_draft_v1.md` has now reached a citation-grounded and lightly polished
  state
- the draft keeps the contract/runtime framing, replaces the former
  placeholder citations with verified literature, and preserves the existing
  figure/table planning markers
- branch support files now record citation grounding, editing decisions,
  bibliography candidates, and figure/table binding
- no figure/table regeneration or LaTeX manuscript conversion has been done yet

## Branch policy

RA-L remains the best first target because the current evidence fits a compact,
results-first controlled systems study. This branch should continue to optimize
for:

- contract/runtime framing rather than prompt-engineering framing
- the highest-value figures and tables only
- one or two bounded scope statements in the manuscript, not repeated exclusion
  lists in every section
- verified citations that remain aligned with the current robotics-systems
  framing

Use these inputs first:

- `paper/shared/core_claim.md`
- `paper/shared/findings.md`
- `paper/shared/limitations.md`
- `paper/shared/figures_and_tables.md`
- `paper/outlines/ral_outline.md`

## Current draft files

| File | Stage | Role |
| --- | --- | --- |
| `full_draft_v1.md` | assembled prose | Manuscript-order RA-L mother draft with unified framing, grounded citations, and light expert-review polish. |
| `full_draft_v1_notes.md` | process note | Records title/abstract base selection, merge decisions, compression actions, citation-grounding decisions, and tightened claims. |
| `citation_todo.md` | process note | Logs how the former `[RW*]` placeholders were replaced with verified literature. |
| `bibliography_candidates.md` | process note | Groups the grounded references and source URLs for later LaTeX / bibliography assembly. |
| `figure_table_binding.md` | process note | Binds each figure/table placeholder in `full_draft_v1.md` to shared planning docs and processed assets. |
| `title_candidates.md` | source prose | Candidate RA-L titles aligned to the contract/runtime framing. |
| `abstract_candidates.md` | source prose | Candidate abstracts centered on action interfaces, runtime validation, recovery, and planner/tool overhead. |
| `intro_draft.md` | source prose | Introduction source fragment for the assembled draft. |
| `setup_and_study_design_draft.md` | source prose | Setup/study-design source fragment defining the controlled matrix and execution boundary. |
| `results_draft.md` | source prose | Results source fragment with the main ordering, ablations, harder-task analysis, and failure-case grounding. |
| `related_work_draft.md` | source prose | Grounded related-work source fragment for the robotics-systems framing. |
| `discussion_and_limitations_draft.md` | source prose | Discussion and limitations source fragment emphasizing planner/executor separation and runtime safeguards. |
| `conclusion_draft.md` | source prose | Short conclusion source fragment. |
| `page_pressure_plan.md` | planning | Compression guide for the later author-polish pass. |
| `failure_case_notes.md` | planning/evidence | Compact prose workbench anchored to existing failure traces and summaries. |

## How the branch fits together

The current flow is:

1. `paper/shared/` sets the claim boundary and reusable wording.
2. The section drafts remain the source fragments for local rewrites.
3. `full_draft_v1.md` assembles those fragments into one readable manuscript
   body with unified terminology and reduced duplication.
4. `full_draft_v1_notes.md`, `citation_todo.md`,
   `bibliography_candidates.md`, and `figure_table_binding.md` capture the
   grounded-reference state and the remaining asset work without widening the
   scientific scope.

Practical rule:

- if a title, abstract, or discussion sentence cannot be supported by the
  frozen summaries and `full_draft_v1.md`, revise or remove it

## Placeholder policy for figures and tables

The allowed placeholders in this branch remain:

- `[Fig: main condition ordering]`
- `[Fig: invalid actions and recovery]`
- `[Fig: planner/tool overhead]`
- `[Table: experimental design summary]`
- `[Table: final closure result summary]`
- `[Table: focused ablation summary]`

These are planning markers only. They do not imply that final manuscript assets
already exist.

## What remains after citation grounding and light polish

- regenerate figures and tables from the final-closure and ablation freezes
- decide whether `[Table: focused ablation summary]` survives the final page
  budget
- author the optional system diagram if the methods section keeps it
- convert the polished manuscript to anonymous RA-L LaTeX later, after prose and
  asset freeze

## Next recommended action

- refresh figure/table assets and caption text from the frozen summaries, then
  prepare the anonymous RA-L LaTeX assembly pass

## Anonymity and scope reminders

- maintain double-anonymous wording throughout
- keep the paper on the current controlled-study scope only
- do not widen the branch to memory, context management, tool abstraction, or
  randomization
- do not turn the paper back into a prompt-engineering study or a benchmark
  package
