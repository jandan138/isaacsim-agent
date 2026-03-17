# STATUS.md

## Current status

- Date: 2026-03-17
- Plan source of truth: `plan.md`
- Paper-writing source of truth: `docs/ral_writing_playbook.md`
- Active milestone: `M11. Paper drafting`
- Milestone state:
  - this run completed `RA-L submission-polish pass`
- Completion level:
  - the active RA-L LaTeX draft remains a 7-page compiled manuscript with
    bibliography included
  - `paper/versions/ral/refs/references.bib` has been upgraded from a merely
    working BibTeX file to a more submission-facing bibliography with fuller
    author metadata and verified venue / DOI / page fields where safely
    confirmed
  - the active `.tex` sources no longer contain inline author-year references
  - terminology, captions, and support-only asset wording have been normalized
    toward the contract / interface / runtime-validation framing
  - `paper/versions/ral/figure_table_binding.md`, `README.md`, and the RA-L
    notes now record the current main-text versus support-only boundary and the
    system-diagram decision

## Run context

- This run stayed within the requested boundaries:
  - no new experiments
  - no experiment-code changes
  - no venue switch
  - no figure/table overhaul
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
  - spawned two explorer sub-agents:
    - citation / bibliography audit
    - terminology / caption / float / system-diagram audit
  - waited for both explorers to complete and integrated their findings
  - no sub-agent stall, interruption, or reassignment occurred

## Milestone summary

- Completed in this run:
  - audited the current submission-facing gaps in the RA-L compiled draft
  - performed reference metadata polish:
    - expanded cited embodied-planning entries from placeholder-style author
      fields to fuller author metadata
    - upgraded safe publication metadata for:
      - `macenski2022ros2`
      - `martin2021plansys2`
      - `colledanchise2018behaviortrees`
      - `garrett2020pddlstream`
      - `garrett2021integratedtamp`
    - cleaned the ROS 2 actions entry and renamed its key to
      `biggs2019ros2actions`
    - added title-case protection for terms that IEEEtran would otherwise
      downcase
    - added an official Isaac Sim documentation reference and cite
  - performed sentence-level compression and local prose cleanup in:
    - `paper/versions/ral/sections/abstract.tex`
    - `paper/versions/ral/sections/intro.tex`
    - `paper/versions/ral/sections/setup.tex`
    - `paper/versions/ral/sections/results.tex`
    - `paper/versions/ral/sections/discussion.tex`
    - `paper/versions/ral/sections/conclusion.tex`
  - normalized terminology / caption consistency:
    - replaced the remaining `runtime policy` wording with
      `runtime validation policy`
    - replaced the remaining `action-interface-only` wording with
      `action-interface ablation`
    - kept the contract / interface / runtime-validation framing intact
  - performed low-risk float / width / spacing polish:
    - regenerated figure/table wrappers through
      `scripts/package_block_a_ral_assets.py`
    - updated wrapper captions for a more consistent submission-facing style
    - switched generated wrapper float specifiers to `[!t]`
    - rewrote dormant support-only captions so they no longer carry workflow
      language
    - tightened the setup tool-vocabulary sentence to reduce line-breaking
      pressure without changing meaning
  - kept the main-text vs support-only asset boundary unchanged and recorded it:
    - main-text:
      `main_condition_ordering`, `invalid_actions_recovery`,
      `planner_tool_overhead`, `experimental_design_summary`,
      `final_closure_result_summary`
    - support-only:
      `focused_ablation_summary`, `harder_task_summary`
  - completed the system-diagram audit and recorded:
    - recommendation: `defer`
    - rationale: current manuscript is self-contained, and the existing
      full-width float queue already delays the ablation figure
  - rebuilt and verified the manuscript
  - updated:
    - `paper/versions/ral/README.md`
    - `paper/versions/ral/figure_table_binding.md`
    - `paper/versions/ral/latex_assembly_notes.md`
    - `paper/versions/ral/full_draft_v1_notes.md`
    - `paper/versions/ral/refs/references_note.tex`
    - `STATUS.md`
- Not completed in this run:
  - no new experiments or result changes
  - no system diagram authoring
  - no aggressive float redesign; the ablation figure still floats late in the
    compiled PDF

## Files changed

- `STATUS.md`
- `paper/versions/ral/README.md`
- `paper/versions/ral/figure_table_binding.md`
- `paper/versions/ral/figures/invalid_actions_recovery.tex`
- `paper/versions/ral/figures/main_condition_ordering.tex`
- `paper/versions/ral/figures/planner_tool_overhead.tex`
- `paper/versions/ral/full_draft_v1_notes.md`
- `paper/versions/ral/latex_assembly_notes.md`
- `paper/versions/ral/main.pdf`
- `paper/versions/ral/refs/references.bib`
- `paper/versions/ral/refs/references_note.tex`
- `paper/versions/ral/sections/abstract.tex`
- `paper/versions/ral/sections/conclusion.tex`
- `paper/versions/ral/sections/discussion.tex`
- `paper/versions/ral/sections/intro.tex`
- `paper/versions/ral/sections/related_work.tex`
- `paper/versions/ral/sections/results.tex`
- `paper/versions/ral/sections/setup.tex`
- `paper/versions/ral/tables/experimental_design_summary.tex`
- `paper/versions/ral/tables/final_closure_result_summary.tex`
- `paper/versions/ral/tables/focused_ablation_summary.tex`
- `paper/versions/ral/tables/harder_task_summary.tex`
- `src/isaacsim_agent/eval/block_a_ral_assets.py`

## Commands run

- Source-of-truth and repo-state reads:
  - `sed -n '1,260p' plan.md`
  - `sed -n '1,260p' AGENTS.md`
  - `sed -n '1,360p' STATUS.md`
  - `sed -n '1,260p' docs/ral_writing_playbook.md`
  - `sed -n '1,260p' paper/README.md`
  - `sed -n '1,320p' paper/shared/*.md`
  - `sed -n '1,260p' paper/versions/ral/*.md`
  - `sed -n '1,260p' paper/versions/ral/main.tex`
  - `sed -n '1,240p' paper/versions/ral/sections/*.tex`
  - `sed -n '1,260p' paper/versions/ral/figures/*.tex`
  - `sed -n '1,260p' paper/versions/ral/tables/*.tex`
  - `sed -n '1,260p' paper/versions/ral/refs/references.bib`
  - `sed -n '1,200p' paper/versions/ral/refs/references_note.tex`
  - `find results/processed/block_a_final_closure -maxdepth 2 -type f | sort`
  - `find results/processed/block_a_master_summary -maxdepth 2 -type f | sort`
  - `git status --short --untracked-files=all`
- Search / audit commands:
  - `rg -n '\\cite{...}' paper/versions/ral/sections paper/versions/ral/main.tex`
  - `rg -n 'prompt engineering study|prompt-first|state of the art|...' ...`
  - `rg -n 'runtime policy|action-interface-only|...' ...`
  - `rg -n '[A-Z][A-Za-z ...] et al\\.|...' paper/versions/ral/sections paper/versions/ral/main.tex`
- External metadata checks used for safe bibliography upgrades:
  - `python - <<'PY' ... arXiv API metadata lookups for cited papers ... PY`
  - `python - <<'PY' ... DOI / Crossref lookups for Macenski, PlanSys2, Behavior Trees, PDDLStream, Integrated TAMP ... PY`
  - `python - <<'PY' ... inspect ROS 2 actions design article metadata ... PY`
  - `python - <<'PY' ... inspect Isaac Sim documentation title ... PY`
- Asset regeneration and compile validation:
  - `python scripts/package_block_a_ral_assets.py`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex && bibtex main && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral`
  - `pdfinfo main.pdf | sed -n '1,20p'`
  - `pdftoppm -png main.pdf /tmp/ral_polish_page`
  - `find paper/versions/ral -maxdepth 1 \( -name 'main.aux' -o -name 'main.bbl' -o -name 'main.blg' \) -delete`

## Validation results

- Bibliography / citation state:
  - `paper/versions/ral/refs/references.bib` is materially more complete and
    consistent than the prior cleanup pass
  - no inline author-year citations remain in the active RA-L `.tex` sources
  - `paper/versions/ral/main.log` no longer has final-pass undefined citation
    blockers
- Terminology and framing:
  - the LaTeX draft remains anchored to planner-to-executor contract design,
    action-interface specification, runtime validation, invalid actions,
    recovery, and planner/tool overhead
  - no prompt-first headline wording or overclaim language was reintroduced
- Main-text vs support-only asset state:
  - main-text asset set remains the same five assets listed above
  - `focused_ablation_summary` and `harder_task_summary` remain support-only
- Compile result:
  - `paper/versions/ral/main.pdf` regenerated successfully
  - `pdfinfo` reports `Pages: 7`
- Visual / float check:
  - the manuscript remains visually stable after the polish pass
  - the ablation figure still floats late to page 6; this is acceptable but
    remains the main non-blocker layout issue
- Remaining warnings:
  - only underfull-box warnings remain, mainly from narrow two-column line
    breaking and float-page composition
  - no fatal compile blockers remain

## Remaining gaps

- do the final author-side line edit and anonymity pass
- decide whether the late page-6 placement of the ablation figure is acceptable
  or whether authors want a float swap
- decide whether `focused_ablation_summary` should stay support-only or replace
  another main-text float
- optionally replace any arXiv-only bibliography entries with later archival
  versions if authors prefer them

## Next recommended sub-milestone

- Move from `submission-polish draft` to `author final-edit / submission prep`
  by:
  - reviewing the current 7-page PDF line by line
  - keeping the present contract/runtime framing intact
  - preserving the current asset boundary unless authors explicitly choose a
    float swap
