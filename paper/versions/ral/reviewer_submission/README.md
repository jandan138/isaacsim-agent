# Reviewer-Facing Submission Variant

This directory holds the anonymous reviewer-facing RA-L submission entry point.

- Source entry: `paper/versions/ral/reviewer_submission/main.tex`
- Compiled PDF: `paper/versions/ral/reviewer_submission/main.pdf`
- Current page count: `7`
- Shared content:
  - `paper/versions/ral/sections/`
  - `paper/versions/ral/figures/`
  - `paper/versions/ral/tables/`
  - `paper/versions/ral/refs/`
- Intended artifact:
  the anonymous conference-style PDF used for the initial RA-L submission

Compile from this directory:

- `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
- `bibtex main`
- `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
- `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
