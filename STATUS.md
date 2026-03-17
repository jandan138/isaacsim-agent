# STATUS.md

## Current status

- Date: 2026-03-17
- Plan source of truth: `plan.md`
- Paper-writing source of truth: `docs/ral_writing_playbook.md`
- Active milestone: `M11. Paper drafting`
- Milestone state:
  - this run completed `RA-L compiled-draft cleanup pass`
- Completion level:
  - the repository docs now match the current RA-L compiled draft and asset set
  - `paper/versions/ral/figure_table_binding.md` now records actual asset paths,
    actual `.tex` insertion points, and which assets are main-text versus
    support-only
  - the citation scaffold has been upgraded from a references-note placeholder
    to a real BibTeX-backed compile path using `refs/references.bib`
  - `paper/versions/ral/main.tex` now compiles with
    `pdflatex -> bibtex -> pdflatex -> pdflatex`
  - the current compiled draft remains within a 7-page RA-L-style layout with
    bibliography included
  - `focused_ablation_summary.tex` still exists but is no longer inserted in the
    current main-text float stack; it remains the first asset to restore or cut
    during final author page-budget decisions

## Run context

- This run stayed within the requested boundaries:
  - no new experiments
  - no experiment-code changes
  - no venue switch
  - no large prose rewrite
  - no change to the paper's contract / interface / runtime-validation framing
  - no change to the underlying results or result ordering
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
  - `paper/versions/ral/full_draft_v1_notes.md`
  - `paper/versions/ral/figure_table_binding.md`
  - `paper/versions/ral/page_pressure_plan.md`
  - `paper/versions/ral/asset_manifest.md`
  - `paper/versions/ral/latex_assembly_notes.md`
  - `paper/versions/ral/main.tex`
  - `paper/versions/ral/sections/`
  - `paper/versions/ral/figures/`
  - `paper/versions/ral/tables/`
  - `paper/versions/ral/refs/`
- Result assets and packaging code inspected in this run:
  - `results/processed/block_a_final_closure/`
  - `results/processed/block_a_master_summary/`
  - `scripts/package_block_a_ral_assets.py`
  - `src/isaacsim_agent/eval/block_a_ral_assets.py`
- Agent teaming:
  - no spawned sub-agent results were used in the final implementation path for
    this cleanup pass
  - the cleanup work stayed local because the binding, bibliography, float, and
    compile decisions were tightly coupled

## Milestone summary

- Completed in this run:
  - audited the existing RA-L compiled draft, generated assets, and repo-facing
    docs for consistency
  - updated `paper/versions/ral/figure_table_binding.md` from a mostly planning
    document into an actual binding-state document that records:
    - real asset paths
    - actual section-file insertion points
    - main-text versus support-only status
    - legacy packaging assets as layout templates only
  - upgraded the citation scaffold:
    - populated `paper/versions/ral/refs/references.bib` with conservative
      grounded entries
    - added local `paper/versions/ral/IEEEtran.bst` because the host TeX
      distribution did not ship that bibliography style
    - changed `paper/versions/ral/main.tex` to use
      `\bibliographystyle{IEEEtran}` and `\bibliography{refs/references}`
    - normalized the Related Work and Discussion citations to `\cite{}` form
  - reduced page / float pressure without changing results:
    - removed `\input{tables/focused_ablation_summary.tex}` from the current
      main-text results section
    - kept `focused_ablation_summary.{tex,csv}` as a support/overflow asset
    - kept `harder_task_summary.{tex,csv}` support-only
    - shortened the three figure captions slightly
  - updated repo-facing notes to match the new compiled-draft state:
    - `paper/versions/ral/README.md`
    - `paper/versions/ral/latex_assembly_notes.md`
    - `paper/versions/ral/full_draft_v1_notes.md`
  - rebuilt and verified the compiled draft with BibTeX and confirmed that the
    resulting `paper/versions/ral/main.pdf` is 7 pages
- Not completed in this run:
  - no final bibliography metadata polish beyond conservative safe fields
  - no system-diagram authoring
  - no final author-side sentence-level polish pass

## Files changed

- `STATUS.md`
- `paper/versions/ral/README.md`
- `paper/versions/ral/full_draft_v1_notes.md`
- `paper/versions/ral/figure_table_binding.md`
- `paper/versions/ral/latex_assembly_notes.md`
- `paper/versions/ral/main.tex`
- `paper/versions/ral/main.pdf`
- `paper/versions/ral/IEEEtran.bst`
- `paper/versions/ral/refs/references.bib`
- `paper/versions/ral/refs/references_note.tex`
- `paper/versions/ral/sections/related_work.tex`
- `paper/versions/ral/sections/discussion.tex`
- `paper/versions/ral/sections/results.tex`
- `paper/versions/ral/figures/main_condition_ordering.tex`
- `paper/versions/ral/figures/invalid_actions_recovery.tex`
- `paper/versions/ral/figures/planner_tool_overhead.tex`
- `paper/versions/ral/tables/focused_ablation_summary.tex`
- `paper/versions/ral/tables/harder_task_summary.tex`

## Commands run

- Source-of-truth reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,220p' AGENTS.md`
  - `sed -n '1,320p' STATUS.md`
  - `sed -n '1,260p' docs/ral_writing_playbook.md`
  - `sed -n '1,260p' paper/README.md`
  - `sed -n '1,260p' paper/shared/core_claim.md`
  - `sed -n '1,260p' paper/shared/contributions.md`
  - `sed -n '1,260p' paper/shared/findings.md`
  - `sed -n '1,260p' paper/shared/limitations.md`
  - `sed -n '1,260p' paper/shared/terminology.md`
  - `sed -n '1,320p' paper/shared/figures_and_tables.md`
  - `sed -n '1,260p' paper/versions/ral/README.md`
  - `sed -n '1,260p' paper/versions/ral/full_draft_v1.md`
  - `sed -n '1,260p' paper/versions/ral/full_draft_v1_notes.md`
  - `sed -n '1,260p' paper/versions/ral/figure_table_binding.md`
  - `sed -n '1,260p' paper/versions/ral/page_pressure_plan.md`
  - `sed -n '1,260p' paper/versions/ral/asset_manifest.md`
  - `sed -n '1,260p' paper/versions/ral/latex_assembly_notes.md`
  - `sed -n '1,220p' paper/versions/ral/main.tex`
  - `find paper/versions/ral/sections -maxdepth 1 -type f | sort`
  - `find paper/versions/ral/figures -maxdepth 1 -type f | sort`
  - `find paper/versions/ral/tables -maxdepth 1 -type f | sort`
  - `sed -n '1,220p' paper/versions/ral/refs/references.bib`
  - `sed -n '1,220p' paper/versions/ral/refs/references_note.tex`
- Result and packaging inspection:
  - `find results/processed/block_a_final_closure -maxdepth 2 -type f | sort`
  - `find results/processed/block_a_master_summary -maxdepth 2 -type f | sort`
  - `sed -n '1,260p' scripts/package_block_a_ral_assets.py`
  - `sed -n '1,360p' src/isaacsim_agent/eval/block_a_ral_assets.py`
  - `pdfinfo paper/versions/ral/main.pdf | sed -n '1,40p'`
- Compile and cleanup validation:
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral`
  - `python - <<'PY' ... download IEEEtran.bst from CTAN ... PY`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex && bibtex main && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdfinfo main.pdf | sed -n '1,20p'`
  - `rg -n '\\([A-Z][A-Za-z .-]+ et al\\.|[A-Z][A-Za-z .-]+ and [A-Z][A-Za-z .-]+, [0-9]{4}|[A-Z][A-Za-z .-]+ et al\\., [0-9]{4}' paper/versions/ral/sections/*.tex paper/versions/ral/main.tex`
  - `rg -n 'prompt engineering study|prompt ablation paper|state of the art|general embodied intelligence|real-world readiness|complete framework|universal best' paper/versions/ral/main.tex paper/versions/ral/sections paper/versions/ral/figures/*.tex paper/versions/ral/tables/*.tex`
  - `rg -n 'contract|runtime validation|action interface|planner-to-executor' paper/versions/ral/sections paper/versions/ral/figures/*.tex paper/versions/ral/tables/*.tex`
  - `rg -n '^\\section|^\\subsection' paper/versions/ral/sections`
  - `git status --short --untracked-files=all`

## Validation results

- STATUS / repo-state sync:
  - the status file now reflects the current compiled-draft cleanup state rather
    than the earlier first-compiled-draft state
- Figure/table binding sync:
  - `paper/versions/ral/figure_table_binding.md` now reflects actual LaTeX
    hookups
  - it explicitly records that `focused_ablation_summary.tex` and
    `harder_task_summary.tex` are generated but not currently inserted in the
    compiled draft
- Citation scaffold:
  - `paper/versions/ral/refs/references.bib` is no longer a placeholder-only
    note file
  - the scaffold now uses BibTeX successfully with local `IEEEtran.bst`
  - the current Related Work and Discussion citations are BibTeX-backed
- Page budget / float state:
  - removing the focused ablation table from the main-text float stack kept the
    compiled draft at 7 pages with bibliography included
  - harder-task support remains available as a support asset without adding
    float pressure to the main text
- Compile result:
  - final compile sequence completed successfully:
    - `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    - `bibtex main`
    - `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    - `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - `paper/versions/ral/main.pdf` was regenerated successfully
  - `pdfinfo` reports `Pages: 7`
- Remaining acceptable warnings:
  - underfull-box warnings remain from line breaking and narrow two-column text
  - no fatal compile blockers remain
- Framing discipline:
  - no banned prompt-first / benchmark / overclaim headline terms were found in
    the compiled-draft source files
  - the manuscript remains anchored to contract / interface / runtime-validation
    wording

## Remaining gaps

- do a final bibliography metadata polish before submission
- decide whether `focused_ablation_summary.tex` returns to the main letter or
  stays support-only
- perform author-side sentence compression and float polish against the final
  RA-L submission budget
- optionally author the system diagram if the methods section still wants it

## Next recommended sub-milestone

- Move from `author-ready cleanup draft` to `author polish / submission prep`
  by:
  - reviewing the 7-page compiled draft for final local sentence tightening
  - making the final keep/drop decision on `focused_ablation_summary.tex`
  - polishing bibliography metadata and citation style for submission
