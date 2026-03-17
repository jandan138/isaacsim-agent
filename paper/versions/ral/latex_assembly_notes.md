# LaTeX Assembly Notes

## Scope

- This pass maps `full_draft_v1.md` into a minimal IEEE/RA-L-style LaTeX
  scaffold under `paper/versions/ral/`.
- The current goal is structural correctness, real figure/table hookups, and an
  author-ready cleanup draft state, not final copyediting.

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

## Known follow-up work

- Polish BibTeX entry metadata where authors want fuller venue fields or final
  submission-facing cleanup.
- Run a later page-pressure pass after authors review float placement in the
  compiled PDF.
- Decide whether `tables/focused_ablation_summary.tex` returns to the final main
  letter or remains support-only.
