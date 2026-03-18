# STATUS.md

## Current status

- Date: 2026-03-18
- Plan source of truth: `plan.md`
- Paper-writing source of truth: `docs/ral_writing_playbook.md`
- Active milestone: `M11. Paper drafting`
- Milestone state:
  - this run completed `freeze Figure 1 asset and retarget manuscript references`
- Completion level:
  - the RA-L stack is now split into:
    - initial anonymous reviewer-facing submission:
      `paper/versions/ral/reviewer_submission/main.pdf`
    - accepted-version journal scaffold:
      `paper/versions/ral/main.pdf`
  - the reviewer-facing submission variant compiles successfully at `7` pages
  - the journal scaffold compiles successfully at `7` pages
  - both manuscript variants now point Figure 1 to the frozen manually selected
    asset under `paper/versions/ral/figures/fig1_system_overview_frozen.*`
  - the old generated `system_overview` figure is no longer referenced by the
    manuscript

## Run context

- This run stayed within the requested boundaries:
  - no new experiments
  - no Figure 1 redesign or regeneration
  - no venue switch
  - no change to the paper's contract / runtime-validation framing
  - no reversion to prompt-first framing
  - no overstated P2 efficiency claims
  - no invented numbers or citations
- Source-of-truth docs consumed in this run:
  - `plan.md`
  - `AGENTS.md`
  - `STATUS.md`
  - `docs/ral_writing_playbook.md`
  - `paper/versions/ral/figures/fig1_system_overview_frozen.png`
  - `paper/versions/ral/main.tex`
  - `paper/versions/ral/reviewer_submission/main.tex`
  - `paper/versions/ral/sections/intro.tex`
  - `paper/versions/ral/figure_table_binding.md`
  - `paper/versions/ral/latex_assembly_notes.md`
  - `src/isaacsim_agent/eval/block_a_ral_assets.py`
- Agent teaming:
  - no sub-agents used in this run

## Milestone summary

- Completed in this run:
  - redirected the shared Figure 1 insertion point to the frozen manual asset
    wrapper `fig1_system_overview_frozen.tex`
  - stopped the asset generator from regenerating the old `system_overview`
    manuscript figure
  - updated manuscript-facing notes to record that Figure 1 is frozen and out
    of scope for further iteration
  - rebuilt both manuscript variants and confirmed the frozen Figure 1 renders
    without missing-file or include errors
- Not completed in this run:
  - no further Figure 1 iteration

## Files changed

- `README.md`
- `STATUS.md`
- `paper/versions/ral/asset_manifest.md`
- `paper/versions/ral/figure_table_binding.md`
- `paper/versions/ral/figures/fig1_system_overview_frozen.tex`
- `paper/versions/ral/latex_assembly_notes.md`
- `paper/versions/ral/README.md`
- `paper/versions/ral/reviewer_submission/main.pdf`
- `paper/versions/ral/sections/intro.tex`
- `src/isaacsim_agent/eval/block_a_ral_assets.py`

## Commands run

- Source-of-truth and repo-state reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,260p' STATUS.md`
  - `git status --short --untracked-files=all`
- Figure-freeze inspection:
  - `find paper/versions/ral/figures -maxdepth 1 -type f | sort`
  - `rg -n "system_overview|fig1_system_overview_frozen|fig:system-overview" paper/versions/ral paper/versions/ral/reviewer_submission -g '*.tex' -g '*.md'`
- Asset regeneration and compile validation:
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex && bibtex main && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex && bibtex main && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral/reviewer_submission`
  - `pdfinfo main.pdf | sed -n '1,20p'`
    with working directory `paper/versions/ral`
  - `pdfinfo main.pdf | sed -n '1,20p'`
    with working directory `paper/versions/ral/reviewer_submission`
  - `pdftoppm -f 1 -l 2 -png main.pdf /tmp/ral_review_fig1_check`
    with working directory `paper/versions/ral/reviewer_submission`

## Validation results

- Reviewer-facing submission:
  - `paper/versions/ral/reviewer_submission/main.pdf` compiles successfully
  - `pdfinfo` reports `Pages: 7`
- Figure 1 state:
  - the shared manuscript now includes
    `figures/fig1_system_overview_frozen.tex`
  - the wrapper resolves to the frozen PNG asset
  - `pdftoppm` successfully rasterized the compiled reviewer PDF pages after the
    rebuild, with no missing-figure error in the LaTeX log
- Journal scaffold:
  - `paper/versions/ral/main.pdf` compiles successfully
  - `pdfinfo` reports `Pages: 7`
- Framing check:
  - no prompt-first headline wording was reintroduced
  - no new experiments or invented numbers were added
  - Figure 1 is now frozen and no longer part of the generator-owned iteration
- Remaining warnings:
  - underfull-box warnings remain from narrow-column line breaking
  - the reviewer-facing `conference` build emits the standard final camera-
    ready column-balance reminder

## Remaining gaps

- do the final author-side line edit and anonymity pass
- keep the frozen Figure 1 asset unchanged unless the authors explicitly choose
  a different manual frozen file later
- optionally rebuild the journal scaffold if authors want a fresh post-freeze
  journal PDF before submission handoff

## Next recommended sub-milestone

- Move from `Figure 1 freeze retargeting` to `author final-edit / submission
  prep` by:
  - reviewing `paper/versions/ral/reviewer_submission/main.pdf` line by line
  - keeping the frozen Figure 1 asset out of scope for further redesign
  - preserving the current contract/runtime framing unless authors explicitly
    request another scope change
