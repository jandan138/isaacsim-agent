# RA-L Working Draft Stack

This directory holds the active RA-L branch for the current controlled-study
paper in Isaac Sim. The evidence base remains fixed to the scope defined in
`paper/shared/` and `docs/ral_writing_playbook.md`.

Current branch state:

- `full_draft_v1.md` remains the citation-grounded mother draft, while
  `main.tex` and the split section files now carry the submission-polish draft
- the draft keeps the contract/runtime framing, stays within the existing
  compiled-draft asset set, and applies sentence-level compression plus local
  terminology cleanup rather than a broad prose rewrite
- branch support files now record citation grounding, editing decisions,
  bibliography candidates, and figure/table binding
- formal RA-L figure PNGs, figure wrappers, table CSVs, and table wrappers now
  live under `paper/versions/ral/figures/` and `paper/versions/ral/tables/`
- the LaTeX scaffold now lives under `paper/versions/ral/main.tex`,
  `sections/`, and `refs/`
- the submission-polish pass keeps the main-text float set unchanged, retains
  the focused ablation and harder-task tables as support-only assets, and
  leaves the current compiled PDF at 7 pages with bibliography included

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

## Main-text asset boundary

- Main-text figures:
  - `figures/main_condition_ordering.{png,csv,tex}`
  - `figures/invalid_actions_recovery.{png,csv,tex}`
  - `figures/planner_tool_overhead.{png,csv,tex}`
- Main-text tables:
  - `tables/experimental_design_summary.{csv,tex}`
  - `tables/final_closure_result_summary.{csv,tex}`
- Support-only / overflow assets:
  - `tables/focused_ablation_summary.{csv,tex}`
  - `tables/harder_task_summary.{csv,tex}`
- Current recommendation:
  keep the support-only tables out of the main letter unless authors explicitly
  trade away another float to make room.

## What remains after the submission-polish pass

- do the author-side sentence-by-sentence line edit and anonymity check
- review the current float locality in the compiled PDF, especially the late
  placement of the ablation figure on page 6
- decide whether to keep the present asset boundary or swap in one support-only
  table by removing another float
- do a final human spot-check of whether any arXiv items should be replaced by
  later archival versions before submission

## Next recommended action

- do an author-side hand edit pass on the current 7-page PDF, keeping the
  contract/runtime framing and the present asset boundary intact

## Anonymity and scope reminders

- maintain double-anonymous wording throughout
- keep the paper on the current controlled-study scope only
- do not widen the branch to memory, context management, tool abstraction, or
  randomization
- do not turn the paper back into a prompt-engineering study or a benchmark
  package

## Compile note

- `main.tex` is now in submission-polish-draft state.
- `paper/versions/ral/IEEEtran.cls` is bundled locally so the current scaffold
  compiles against an IEEE-style journal class even when the host TeX
  distribution does not ship `IEEEtran.cls`.
- `paper/versions/ral/IEEEtran.bst` is bundled locally for the same reason.
- Current regenerate-and-compile sequence:
  - `python scripts/package_block_a_ral_assets.py`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - `bibtex main`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
- The current polished draft compiles to `paper/versions/ral/main.pdf` and is
  7 pages with bibliography included.

## Asset provenance

- Figures and tables are regenerated by
  `scripts/package_block_a_ral_assets.py`.
- The generation logic lives in
  `src/isaacsim_agent/eval/block_a_ral_assets.py`.
- Provenance for the current asset set is recorded in
  `paper/versions/ral/asset_manifest.md`.

## Citation status

- `refs/references.bib` now contains fuller author metadata and verified
  venue/DOI/page fields where those were safely confirmed.
- The compiled scaffold now uses `\cite{}`-based bibliography handling instead
  of the former references note placeholder.
- No inline author-year references remain in the active RA-L `.tex` sources.
- Remaining citation work is now optional author spot-checking: decide whether
  any arXiv-only entries should be swapped to later archival versions and do a
  final bibliography-style glance before submission.

## System diagram decision

- Recommendation: `defer`.
- Rationale:
  the manuscript is currently self-contained without a system diagram, and the
  present full-width float queue already pushes the ablation figure late in the
  PDF. Add a system diagram only as a swap against an existing full-width
  figure, not as a fourth main-text figure.
