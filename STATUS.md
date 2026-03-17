# STATUS.md

## Current status

- Date: 2026-03-17
- Plan source of truth: `plan.md`
- Paper-writing source of truth: `docs/ral_writing_playbook.md`
- Active milestone: `M11. Paper drafting`
- Milestone state:
  - this run completed `RA-L final figure/table refresh + LaTeX scaffold preparation`
- Completion level:
  - formal RA-L figure assets now exist under `paper/versions/ral/figures/`
  - formal RA-L table assets now exist under `paper/versions/ral/tables/`
  - `paper/versions/ral/main.tex` plus `sections/` and `refs/` now provide a
    first compiled draft scaffold
  - the scaffold now compiles locally to `paper/versions/ral/main.pdf`
  - `paper/versions/ral/IEEEtran.cls` is now bundled locally so the scaffold
    compiles against an IEEE-style journal class even though the host TeX
    distribution did not ship `IEEEtran.cls`

## Run context

- This run stayed within the requested boundaries:
  - no new experiments
  - no experiment-code changes
  - no heavy Isaac Sim / ROS workflow launch
  - no venue switch
  - no large prose rewrite
  - no change to the paper's contract / interface / runtime-validation framing
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
  - `paper/versions/ral/bibliography_candidates.md`
- Frozen result assets inspected in this run:
  - `results/processed/block_a_final_closure/`
  - `results/processed/block_a_master_summary/`
  - `results/processed/block_a_prompt_only_ablation/`
  - `results/processed/block_a_runtime_only_ablation/`
  - `results/processed/block_a_manipulation_harder/`
  - `results/processed/block_a_cross_family_summary/`
  - legacy paper packaging under
    `results/processed/block_a_master_summary/paper_figures/` and
    `results/processed/block_a_master_summary/paper_tables/`
- Agent teaming:
  - spawned two explorer sub-agents for parallel paper/result inspection
  - spawned one worker sub-agent for the RA-L LaTeX scaffold
  - waited `120000 ms`, then `180000 ms`, and sent one focused progress /
    blocker check when the worker still had not returned a usable scaffold
  - because the scaffold was now on the critical path, local takeover proceeded
    to finish `main.tex`, the section files, the bundled `IEEEtran.cls`, and
    compile validation
  - the worker was then closed and reported terminal status `Interrupted`; this
    was accepted because the blocking scaffold work had already been completed
    locally

## Milestone summary

- Completed in this run:
  - added a reproducible RA-L asset packaging path via
    `src/isaacsim_agent/eval/block_a_ral_assets.py` and
    `scripts/package_block_a_ral_assets.py`
  - regenerated the retained figure set under `paper/versions/ral/figures/`:
    - `main_condition_ordering.{png,csv,tex}`
    - `invalid_actions_recovery.{png,csv,tex}`
    - `planner_tool_overhead.{png,csv,tex}`
  - regenerated the retained table set under `paper/versions/ral/tables/`:
    - `experimental_design_summary.{csv,tex}`
    - `final_closure_result_summary.{csv,tex}`
    - `focused_ablation_summary.{csv,tex}`
    - `harder_task_summary.{csv,tex}` as an optional support asset
  - wrote `paper/versions/ral/asset_manifest.md` to bind the regenerated assets
    back to the frozen processed summaries
  - updated `paper/versions/ral/figure_table_binding.md` so the draft
    placeholders now point to concrete regenerated assets and LaTeX placement
  - created the RA-L LaTeX scaffold:
    - `paper/versions/ral/main.tex`
    - `paper/versions/ral/sections/{abstract,intro,related_work,setup,results,discussion,conclusion}.tex`
    - `paper/versions/ral/refs/references.bib`
    - `paper/versions/ral/refs/references_note.tex`
    - `paper/versions/ral/latex_assembly_notes.md`
  - updated `paper/versions/ral/README.md` to reflect the refreshed assets,
    scaffold state, and current compile path
- Not completed in this run:
  - no BibTeX keying pass that converts the author-year prose citations to
    `\cite{}` commands
  - no page-budget tightening pass yet
  - no optional system-diagram authoring

## Files changed

- `STATUS.md`
- `paper/versions/ral/README.md`
- `paper/versions/ral/figure_table_binding.md`
- `paper/versions/ral/asset_manifest.md`
- `paper/versions/ral/IEEEtran.cls`
- `paper/versions/ral/main.tex`
- `paper/versions/ral/main.pdf`
- `paper/versions/ral/latex_assembly_notes.md`
- `paper/versions/ral/sections/abstract.tex`
- `paper/versions/ral/sections/intro.tex`
- `paper/versions/ral/sections/related_work.tex`
- `paper/versions/ral/sections/setup.tex`
- `paper/versions/ral/sections/results.tex`
- `paper/versions/ral/sections/discussion.tex`
- `paper/versions/ral/sections/conclusion.tex`
- `paper/versions/ral/refs/references.bib`
- `paper/versions/ral/refs/references_note.tex`
- `paper/versions/ral/figures/main_condition_ordering.csv`
- `paper/versions/ral/figures/main_condition_ordering.png`
- `paper/versions/ral/figures/main_condition_ordering.tex`
- `paper/versions/ral/figures/invalid_actions_recovery.csv`
- `paper/versions/ral/figures/invalid_actions_recovery.png`
- `paper/versions/ral/figures/invalid_actions_recovery.tex`
- `paper/versions/ral/figures/planner_tool_overhead.csv`
- `paper/versions/ral/figures/planner_tool_overhead.png`
- `paper/versions/ral/figures/planner_tool_overhead.tex`
- `paper/versions/ral/tables/experimental_design_summary.csv`
- `paper/versions/ral/tables/experimental_design_summary.tex`
- `paper/versions/ral/tables/final_closure_result_summary.csv`
- `paper/versions/ral/tables/final_closure_result_summary.tex`
- `paper/versions/ral/tables/focused_ablation_summary.csv`
- `paper/versions/ral/tables/focused_ablation_summary.tex`
- `paper/versions/ral/tables/harder_task_summary.csv`
- `paper/versions/ral/tables/harder_task_summary.tex`
- `scripts/package_block_a_ral_assets.py`
- `src/isaacsim_agent/eval/block_a_ral_assets.py`
- `src/isaacsim_agent/eval/__init__.py`

## Commands run

- Source-of-truth reads:
  - `sed -n '1,240p' plan.md`
  - `sed -n '1,240p' AGENTS.md`
  - `sed -n '1,260p' STATUS.md`
  - `sed -n '1,240p' docs/ral_writing_playbook.md`
  - `sed -n '1,220p' paper/README.md`
  - `sed -n '1,220p' paper/shared/core_claim.md`
  - `sed -n '1,220p' paper/shared/contributions.md`
  - `sed -n '1,220p' paper/shared/findings.md`
  - `sed -n '1,220p' paper/shared/limitations.md`
  - `sed -n '1,260p' paper/shared/terminology.md`
  - `sed -n '1,320p' paper/shared/figures_and_tables.md`
  - `sed -n '1,220p' paper/versions/ral/README.md`
  - `sed -n '1,360p' paper/versions/ral/full_draft_v1.md`
  - `sed -n '1,320p' paper/versions/ral/full_draft_v1_notes.md`
  - `sed -n '1,260p' paper/versions/ral/figure_table_binding.md`
  - `sed -n '1,260p' paper/versions/ral/page_pressure_plan.md`
  - `sed -n '1,260p' paper/versions/ral/bibliography_candidates.md`
- Asset and code inspection:
  - `rg --files results/processed/block_a_final_closure results/processed/block_a_master_summary paper/versions/ral`
  - `rg --files results/processed/block_a_prompt_only_ablation results/processed/block_a_runtime_only_ablation results/processed/block_a_manipulation_harder results/processed/block_a_cross_family_summary`
  - `rg -n "block_a_(final_closure|prompt_only|runtime_only|manipulation_harder|cross_family|master_summary)|paper_figures|paper_tables|matplotlib|seaborn|plotly|DataFrame" scripts src paper`
  - `sed -n '1,220p' scripts/package_block_a_paper.py`
  - `sed -n '1,260p' src/isaacsim_agent/eval/block_a_final_closure.py`
  - `sed -n '1,1360p' src/isaacsim_agent/eval/block_a_paper.py`
  - multiple `python - <<'PY' ...` structure-inspection snippets over the
    summary JSON files
- Asset refresh and scaffold validation:
  - `python scripts/package_block_a_ral_assets.py`
  - `find paper/versions/ral/figures -maxdepth 1 -type f | sort`
  - `find paper/versions/ral/tables -maxdepth 1 -type f | sort`
  - `python - <<'PY' ... PNG signature check ...`
  - `rg -n "prompt engineering study|prompt ablation paper|state of the art|general embodied intelligence|real-world readiness|complete framework|universal best" paper/versions/ral/main.tex paper/versions/ral/sections paper/versions/ral/figures/*.tex paper/versions/ral/tables/*.tex`
  - `rg -n "contract|runtime validation|action interface|planner-to-executor" paper/versions/ral/sections paper/versions/ral/figures/*.tex paper/versions/ral/tables/*.tex`
  - `rg -n '^\\section|^\\subsection' paper/versions/ral/sections`
  - `ls -l paper/versions/ral/main.pdf paper/versions/ral/IEEEtran.cls`
  - `sed -n '1,40p' paper/versions/ral/IEEEtran.cls`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral`
  - repeated `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    passes after fixing `main.tex` to prefer the local `IEEEtran.cls` and use
    `refs/references_note.tex`
  - `find paper/versions/ral -maxdepth 1 -type f \( -name 'main.aux' -o -name 'main.log' \) -delete`
  - `git status --short`

## Validation results

- Formal figure and table existence:
  - command:
    `find paper/versions/ral/figures -maxdepth 1 -type f | sort`
  - result:
    - all expected figure files exist:
      `main_condition_ordering.{png,csv,tex}`,
      `invalid_actions_recovery.{png,csv,tex}`,
      and `planner_tool_overhead.{png,csv,tex}`
  - command:
    `find paper/versions/ral/tables -maxdepth 1 -type f | sort`
  - result:
    - all expected table files exist:
      `experimental_design_summary.{csv,tex}`,
      `final_closure_result_summary.{csv,tex}`,
      `focused_ablation_summary.{csv,tex}`,
      and `harder_task_summary.{csv,tex}`
- PNG integrity:
  - command:
    `python - <<'PY' ... PNG signature check ...`
  - result:
    - all three regenerated figure binaries start with the PNG signature and
      have non-zero file sizes
- Framing / wording scan:
  - command:
    `rg -n "prompt engineering study|prompt ablation paper|state of the art|general embodied intelligence|real-world readiness|complete framework|universal best" paper/versions/ral/main.tex paper/versions/ral/sections paper/versions/ral/figures/*.tex paper/versions/ral/tables/*.tex`
  - result:
    - no banned headline-framing terms were found in the scaffolded manuscript
      files
  - command:
    `rg -n "contract|runtime validation|action interface|planner-to-executor" paper/versions/ral/sections paper/versions/ral/figures/*.tex paper/versions/ral/tables/*.tex`
  - result:
    - the scaffold and captions remain anchored to contract / interface /
      runtime-validation wording
- Section structure:
  - command:
    `rg -n '^\\section|^\\subsection' paper/versions/ral/sections`
  - result:
    - the split section files preserve the heading sequence from
      `full_draft_v1.md`
- IEEE class availability:
  - command:
    `ls -l paper/versions/ral/main.pdf paper/versions/ral/IEEEtran.cls`
  - result:
    - a local `paper/versions/ral/IEEEtran.cls` is present and is the class
      file used by the current compile path
- LaTeX compile:
  - command:
    `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    run twice from `paper/versions/ral/`
  - result:
    - both final passes completed with exit code `0`
    - the scaffold compiled to `paper/versions/ral/main.pdf`
    - remaining messages are underfull-box warnings, not hard compile blockers
- Build-artifact cleanup:
  - command:
    `find paper/versions/ral -maxdepth 1 -type f \( -name 'main.aux' -o -name 'main.log' \) -delete`
  - result:
    - temporary auxiliary outputs were removed after validation
    - the compiled `main.pdf` was kept as the first compiled draft artifact

## Next recommended sub-milestone

- Move from `first compiled draft` to `author polish / page-budget tightening`
  by:
  - trimming the scaffold against the actual RA-L page target while keeping the
    regenerated assets and contract/runtime framing intact
  - deciding whether `focused_ablation_summary.tex` stays in the main letter
  - converting the author-year prose citations to BibTeX-backed `\cite{}`
    commands
