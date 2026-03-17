# LaTeX Assembly Notes

## Scope

- This pass maps `full_draft_v1.md` into a minimal IEEE/RA-L-style LaTeX
  scaffold under `paper/versions/ral/`.
- The goal is structural correctness, real figure/table hookups, and a first
  compilable draft state, not final copyediting.

## Minimal prose adjustments

- Converted Markdown sectioning into LaTeX `\section{}` and `\subsection{}`
  structure while keeping the heading order unchanged.
- Replaced figure/table planning markers with `\input{}` calls that point to the
  regenerated assets under `figures/` and `tables/`.
- Removed Markdown backticks and converted only the executor tool names that
  require escaped underscores into `\texttt{...}`.
- Kept author-year reference strings inline in the prose for this scaffold pass,
  then added `refs/references_note.tex` plus a conservative `refs/references.bib`
  placeholder so the grounded reference set remains staged without forcing a
  risky citation-style rewrite in the same pass.

## Known follow-up work

- Convert the inline author-year references to `\cite{}` form and move the
  staged bibliography into a finalized BibTeX workflow.
- Run a later page-pressure pass after authors review float placement in the
  compiled PDF.
- Decide whether `tables/focused_ablation_summary.tex` survives the final RA-L
  page budget.
