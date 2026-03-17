# LaTeX Assembly Notes

## Scope

- This pass maps `full_draft_v1.md` into a minimal IEEE/RA-L-style LaTeX
  scaffold under `paper/versions/ral/`.
- The current goal is a submission-polish draft state with stable figure/table
  hookups, bounded local prose cleanup, and honest handoff notes, not a fresh
  assembly or broad rewrite.

## Minimal prose adjustments

- Converted Markdown sectioning into LaTeX `\section{}` and `\subsection{}`
  structure while keeping the heading order unchanged.
- Replaced figure/table planning markers with `\input{}` calls that point to the
  regenerated assets under `figures/` and `tables/`.
- Removed Markdown backticks and converted only the executor tool names that
  require escaped underscores into `\texttt{...}`.
- Switched the compiled draft from the old references-note placeholder to a real
  BibTeX-backed bibliography path in `main.tex`.

## Compiled-Draft Cleanup Pass

- Populated `refs/references.bib` with conservative grounded entries using only
  source-verified titles, years, URLs, and minimal safe metadata.
- Normalized the Related Work and Discussion citations to `\cite{}` form
  without doing a broad prose rewrite.
- Bundled `IEEEtran.bst` locally because the host TeX distribution did not ship
  that bibliography style file.
- Removed `\input{tables/focused_ablation_summary.tex}` from the current main
  text to keep float pressure lower while leaving the table available as a
  support/overflow asset.
- Shortened the three figure captions slightly so the compiled draft stays
  tighter without changing the scientific claim.

## Submission-Polish Pass

- Performed a sentence-level compression pass in:
  - `sections/abstract.tex`
  - `sections/intro.tex`
  - `sections/setup.tex`
  - `sections/results.tex`
  - `sections/discussion.tex`
  - `sections/conclusion.tex`
- Normalized local terminology drift so the active LaTeX draft now prefers
  `runtime validation policy` and `action-interface ablation` wording over the
  older `runtime policy` and `action-interface-only` labels.
- Added one compact literature-positioning citation cluster in the introduction
  and one official Isaac Sim documentation citation at first technical mention
  in the setup section.
- Upgraded `refs/references.bib` from minimal safe placeholders to a more
  submission-facing state:
  - fuller author metadata for the cited embodied-planning references
  - verified venue / DOI / page metadata where it was safely confirmed
  - case protection for terms such as `3D`, `AI`, `VLM`, and `IsaacSim`
  - a cleaner ROS 2 actions entry and an official Isaac Sim documentation entry
- Regenerated the figure/table wrappers through
  `scripts/package_block_a_ral_assets.py` after updating the asset generator so
  caption style, support-only caption wording, and `[!t]` float specifiers stay
  reproducible.
- Kept the main-text asset boundary unchanged:
  `focused_ablation_summary` and `harder_task_summary` remain support-only.
- System-diagram decision:
  `defer`
  because the manuscript is currently self-contained and the existing full-width
  float queue already delays the ablation figure in the compiled PDF.

## Known follow-up work

- Do the final author-side line edit and anonymity pass on the compiled PDF.
- Review whether the late page-6 placement of the ablation figure is acceptable
  or whether authors want to swap one full-width float.
- Decide whether any remaining arXiv-only references should be replaced by
  later archival versions before submission.
