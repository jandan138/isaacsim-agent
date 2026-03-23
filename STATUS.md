# STATUS.md

## Current status

- Date: 2026-03-23
- Plan source of truth: `plan.md`
- Paper-writing source of truth: `docs/ral_writing_playbook.md`
- Active milestone: `Paper final-edit / submission prep`
- Milestone state:
  - this run rejected the latest card-style Table I variant and restored the
    restrained manuscript-style comparison matrix
  - Figure 1 was intentionally frozen and left untouched
  - no new experiments were added
  - Table I remained a table-numbered asset with the same label, insertion
    point, and reviewer-facing anonymity
  - this run restored the exact user-provided matrix text in the live Table I
    asset and removed the three-card / panel-style layout from the manuscript
  - the goal of this pass was non-Figure-1 manuscript stabilization, not a new
    redesign or any change in claims, examples, or terminology
- Completion level:
  - the restored restrained-matrix Table I state is compile-verified
  - reviewer-facing and journal scaffold PDFs both compile successfully
  - both compiled PDFs remain at `8` pages
  - manuscript notes, bindings, and status docs are updated for this restore

## 2026-03-23 restore pass

- This restore pass stayed within the requested boundaries:
  - read the repository-level and paper-level source-of-truth files before
    editing
  - keep Figure 1 frozen
  - do not add experiments
  - do not change Table I scientific meaning, label, insertion point, or
    reviewer-facing anonymity
  - reject the latest card-style / panel-style Table I variant
- Restore implementation:
  - replaced the entire contents of
    `paper/versions/ral/tables/contract_interface_examples.tex` with the exact
    user-provided restrained matrix LaTeX
  - removed the live three-card / panel-style variant completely
  - left `sections/intro.tex` and `sections/setup.tex` unchanged because the
    rebuilt manuscript compiled and read coherently without further wording
    changes
- Commands run in this restore pass:
  - source-of-truth and manuscript reads:
    - `sed -n '1,220p' plan.md`
    - `sed -n '1,220p' AGENTS.md`
    - `sed -n '1,240p' STATUS.md`
    - `sed -n '1,220p' docs/ral_writing_playbook.md`
    - `sed -n ...` and `rg -n ...` over the listed `paper/shared/*.md`,
      `paper/versions/ral/*.md`, `paper/versions/ral/sections/*.tex`,
      `paper/versions/ral/tables/*.tex`, `paper/versions/ral/figures/*`, and
      `paper/versions/ral/refs/*`
  - compile verification:
    - `cd paper/versions/ral/reviewer_submission && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    - `cd paper/versions/ral && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    - reran the same pair once more to clear a transient label-stability rerun
      warning in the journal scaffold build
  - page/log/visual checks:
    - `pdfinfo paper/versions/ral/reviewer_submission/main.pdf | rg '^Pages:'`
    - `pdfinfo paper/versions/ral/main.pdf | rg '^Pages:'`
    - `rg -n "Undefined|undefined|Overfull|Underfull|Rerun|Warning: Citation|Warning: Reference|Label\\(s\\) may have changed|Conference Paper" paper/versions/ral/reviewer_submission/main.log paper/versions/ral/main.log`
    - `cp paper/versions/ral/reviewer_submission/main.pdf /tmp/ral_reviewer_main_table_i_restore.pdf`
    - `pdftoppm -png -f 2 -singlefile /tmp/ral_reviewer_main_table_i_restore.pdf /tmp/ral_reviewer_page2_table_i_restore`
    - `view_image /tmp/ral_reviewer_page2_table_i_restore.png`
- Validation results in this restore pass:
  - reviewer-facing build:
    - success
    - `Pages: 8`
  - journal scaffold:
    - success
    - `Pages: 8`
  - reviewer page 2 visual check:
    - latest card-style variant is gone
    - Table I is restored to the restrained manuscript-style comparison matrix
      below the frozen Figure 1
  - warning status:
    - no undefined references, citation warnings, or rerun warnings remain
    - remaining overfull warnings are still limited to
      `paper/versions/ral/figures/main_condition_ordering.tex` and
      `paper/versions/ral/figures/invalid_actions_recovery.tex`
    - underfull box warnings remain in narrow-column prose
    - the reviewer-facing conference build still emits the standard last-page
      column-balance reminder
- Files updated in this restore pass:
  - `paper/versions/ral/tables/contract_interface_examples.tex`
  - `STATUS.md`
  - `paper/versions/ral/README.md`
  - `paper/versions/ral/figure_table_binding.md`
  - `paper/versions/ral/latex_assembly_notes.md`
  - `paper/versions/ral/full_draft_v1_notes.md`
  - `paper/versions/ral/main.pdf`
  - `paper/versions/ral/reviewer_submission/main.pdf`
- Agent teaming in this restore pass:
  - explorer audit completed and confirmed that the three-card variant should
    be rejected, Figure 1 should remain frozen, and intro/setup could stay
    unchanged by default
  - worker completed the exact full-file replacement for
    `paper/versions/ral/tables/contract_interface_examples.tex`
  - reviewer acceptance remains desirable but was not required to proceed with
    the exact user-directed restoration once builds and screenshot checks
    passed
- Next recommended sub-milestone:
  - author review of the restored reviewer-page screenshot only; avoid further
    Table I redesign work unless the user explicitly reopens it

## 2026-03-23 redesign pass

- This redesign pass stayed within the requested boundaries:
  - read the repository-level and RA-L source-of-truth files before editing
  - keep Figure 1 frozen
  - keep Table I as the same manual asset with the same label and insertion
    path
  - preserve P0 / P1 / P2 identity, declared-tools meaning, and example
    semantics
  - keep the reviewer-facing manuscript anonymous, compilable, and page-stable
- Redesign implementation:
  - replaced the internal 4-column grid in
    `paper/versions/ral/tables/contract_interface_examples.tex` with a
    reviewer-safe three-card horizontal panel for `P0`, `P1`, and `P2`
  - added a subtle full-width declared-tools strip above the cards
  - gave each card:
    - a short subtitle cue
    - a light-gray monospace example-emission box
    - a short dispatchability block
  - used low-saturation accent treatment only; no new experiments, claims, or
    terminology were introduced
  - kept the caption and label intact and made only the minimal surrounding
    wording edits needed for the more figure-like presentation:
    - `records` -> `juxtaposes` in
      `paper/versions/ral/sections/intro.tex`
    - `records` -> `juxtaposes` in
      `paper/versions/ral/sections/setup.tex`
- Commands run in this redesign pass:
  - source-of-truth and manuscript reads:
    - `sed -n '1,220p' AGENTS.md`
    - `sed -n '1,220p' plan.md`
    - `sed -n '1,220p' STATUS.md`
    - `sed -n '1,220p' docs/ral_writing_playbook.md`
    - `sed -n ...` over `paper/versions/ral/README.md`,
      `paper/versions/ral/figure_table_binding.md`,
      `paper/versions/ral/preamble_shared.tex`,
      `paper/versions/ral/tables/contract_interface_examples.tex`,
      `paper/versions/ral/sections/intro.tex`, and
      `paper/versions/ral/sections/setup.tex`
  - compile verification:
    - `cd paper/versions/ral/reviewer_submission && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    - `cd paper/versions/ral && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    - reran the same pair once after a transient label-stability rerun warning
    - reran the same pair once more after the `records` -> `juxtaposes`
      wording sync
  - page/log/visual checks:
    - `pdfinfo paper/versions/ral/reviewer_submission/main.pdf | rg '^Pages:'`
    - `pdfinfo paper/versions/ral/main.pdf | rg '^Pages:'`
    - `rg -n "Undefined|undefined|Overfull|Underfull|Rerun|Warning: Citation|Warning: Reference|Label\\(s\\) may have changed|Conference Paper" paper/versions/ral/reviewer_submission/main.log paper/versions/ral/main.log`
    - `cp paper/versions/ral/reviewer_submission/main.pdf /tmp/ral_reviewer_main_table_i_redesign_final.pdf`
    - `pdftoppm -png -f 2 -singlefile /tmp/ral_reviewer_main_table_i_redesign_final.pdf /tmp/ral_reviewer_page2_table_i_redesign_final`
    - `view_image /tmp/ral_reviewer_page2_table_i_redesign_final.png`
- Validation results in this redesign pass:
  - reviewer-facing build:
    - success
    - `Pages: 8`
  - journal scaffold:
    - success
    - `Pages: 8`
  - reviewer page 2 visual check:
    - Table I now reads as a restrained figure-like comparison panel rather
      than a plain appendix-style table
    - the three-card layout, declared-tools strip, and light code boxes fit
      below the frozen Figure 1 without changing page count
  - warning status:
    - no undefined references, citation warnings, or rerun warnings remain
    - remaining overfull warnings are still limited to
      `paper/versions/ral/figures/main_condition_ordering.tex` and
      `paper/versions/ral/figures/invalid_actions_recovery.tex`
    - underfull box warnings remain in narrow-column prose
    - the reviewer-facing conference build still emits the standard last-page
      column-balance reminder
    - one non-blocking tradeoff remains: the monospace code inside the cards is
      smaller at reviewer scale so the redesigned panel can fit below Figure 1
- Files updated in this redesign pass:
  - `paper/versions/ral/tables/contract_interface_examples.tex`
  - `paper/versions/ral/sections/intro.tex`
  - `paper/versions/ral/sections/setup.tex`
  - `STATUS.md`
  - `paper/versions/ral/README.md`
  - `paper/versions/ral/figure_table_binding.md`
  - `paper/versions/ral/latex_assembly_notes.md`
  - `paper/versions/ral/full_draft_v1_notes.md`
  - `paper/versions/ral/main.pdf`
  - `paper/versions/ral/reviewer_submission/main.pdf`
- Agent teaming in this redesign pass:
  - explorer audit completed and confirmed the redesign-safe boundary while
    keeping Figure 1 frozen and the table identity stable
  - worker implementation completed the single-file Table I redesign
  - reviewer acceptance completed and found no blocking issues
- Next recommended sub-milestone:
  - author-facing submission sign-off / packaging only; avoid further Table I
    redesign unless a new reviewer-facing readability issue appears

## 2026-03-23 final polish follow-up

- This follow-up stayed within the requested boundaries:
  - read the listed repository-level and paper-level source-of-truth files
  - do not modify Figure 1
  - do not add experiments
  - do not change Table I's scientific meaning, table identity, label, or
    4-column matrix structure
  - keep the reviewer-facing manuscript anonymous, compilable, and page-stable
- Current-target verification in this follow-up:
  - confirmed `paper/versions/ral/tables/contract_interface_examples.tex`
    remains the existing `table*` + `minipage` note + `tabularx` 4-column
    matrix
  - confirmed label `tab:contract-interface-examples` remains unchanged
  - confirmed insertion from `paper/versions/ral/sections/intro.tex` and prose
    references in `paper/versions/ral/sections/intro.tex` and
    `paper/versions/ral/sections/setup.tex`
  - confirmed Figure 1 remained frozen and untouched in this pass
  - confirmed the live Table I wording now carries only the requested
    final-polish refinements:
    - shorter caption with `P1 yields a dispatchable typed call`
    - lower-weight shared note using `Declared tools:`
    - compressed P2 example wording ending in `goal pose`
    - compressed P2 dispatchability wording ending in
      `+ planner-side check`
- Commands run in this follow-up:
  - source-of-truth and manuscript reads:
    - `sed -n '1,220p' plan.md`
    - `sed -n '1,240p' STATUS.md`
    - `sed -n '1,220p' docs/ral_writing_playbook.md`
    - `sed -n ...` / `rg -n ...` over the listed `paper/shared/*.md`,
      `paper/versions/ral/*.md`, `paper/versions/ral/sections/*.tex`,
      `paper/versions/ral/reviewer_submission/main.tex`, and
      `paper/versions/ral/main.tex`
  - compile verification:
    - `cd paper/versions/ral/reviewer_submission && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    - `cd paper/versions/ral && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - page/log/visual checks:
    - `pdfinfo paper/versions/ral/reviewer_submission/main.pdf | rg '^Pages:'`
    - `pdfinfo paper/versions/ral/main.pdf | rg '^Pages:'`
    - `rg -n "Undefined|undefined|Overfull|Underfull|Rerun|Warning: Citation|Warning: Reference|Label\\(s\\) may have changed|Conference Paper" paper/versions/ral/reviewer_submission/main.log paper/versions/ral/main.log`
    - `pdftoppm -png -f 2 -singlefile paper/versions/ral/reviewer_submission/main.pdf /tmp/ral_reviewer_page2_table_i_polish`
    - `view_image /tmp/ral_reviewer_page2_table_i_polish.png`
- Validation results in this follow-up:
  - reviewer-facing build:
    - success
    - `Pages: 8`
  - journal scaffold:
    - success
    - `Pages: 8`
  - reviewer page 2 visual check:
    - shared-tool note reads as a low-key annotation rather than a secondary
      heading
    - the shorter caption and lighter P2 wording make the rightmost column feel
      less dense while preserving the same science
  - warning status:
    - no undefined references or citation failures were introduced
    - remaining overfull warnings are still limited to
      `paper/versions/ral/figures/main_condition_ordering.tex` and
      `paper/versions/ral/figures/invalid_actions_recovery.tex`
    - underfull box warnings remain in narrow-column prose
    - the reviewer-facing conference build still emits the standard last-page
      column-balance reminder
- Files updated in this follow-up:
  - `paper/versions/ral/tables/contract_interface_examples.tex`
  - `STATUS.md`
  - `paper/versions/ral/README.md`
  - `paper/versions/ral/figure_table_binding.md`
  - `paper/versions/ral/latex_assembly_notes.md`
  - `paper/versions/ral/full_draft_v1_notes.md`
  - `paper/versions/ral/main.pdf`
  - `paper/versions/ral/reviewer_submission/main.pdf`
- Agent teaming in this follow-up:
  - attempted delegated source-of-truth / binding-surface audit slots, but no
    usable independent subagent output was collected before the main session
    completed the same audit locally
  - attempted delegated build verification, but the spawned worker remained at
    an assigned stub for two wait windows totaling about `55s`
  - after the second no-progress wait, the main session took over compile
    verification by exception and completed the reviewer-page visual check
- Next recommended sub-milestone:
  - author-facing submission sign-off / packaging only; do not reopen Figure 1
    or redesign Table I unless a new blocking reviewer-facing issue appears

## Run context

- This run stayed within the requested boundaries:
  - read the listed repository-level and paper-level source-of-truth files
  - do not modify Figure 1
  - do not add experiments
  - do not widen the core claim / contributions / findings / limitations
  - keep the reviewer-facing manuscript anonymous and compilable
- Source-of-truth docs and inputs consumed in this run:
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
  - `paper/versions/ral/figure_table_binding.md`
  - `paper/versions/ral/page_pressure_plan.md`
  - `paper/versions/ral/latex_assembly_notes.md`
  - `paper/versions/ral/full_draft_v1.md`
  - `paper/versions/ral/full_draft_v1_notes.md`
  - `paper/versions/ral/reviewer_submission/main.tex`
  - `paper/versions/ral/main.tex`
  - `paper/versions/ral/sections/`
  - `paper/versions/ral/figures/`
  - `paper/versions/ral/tables/`
  - `paper/versions/ral/refs/`
  - archived planner traces under
    `results/block_a_navigation_prompt_runtime_expanded_e2e_20260316_py/runs/`
- Relevant current-target inspection completed in this run:
  - located Table I source at
    `paper/versions/ral/tables/contract_interface_examples.tex`
  - confirmed label `tab:contract-interface-examples`
  - confirmed insertion from `paper/versions/ral/sections/intro.tex`
  - confirmed in-text references in
    `paper/versions/ral/sections/intro.tex` and
    `paper/versions/ral/sections/setup.tex`
  - confirmed the asset is manual and not regenerated by the RA-L packaging
    script
  - cross-checked the `P0` / `P1` / `P2` example semantics against archived
    short-forward navigation `planner_trace.json` files
- Agent teaming:
  - attempted a new explorer slot for a Table I binding audit
    - result:
      no usable subagent output before shutdown; main session completed the
      audit locally
    - worklog:
      `.codex/worklogs/subagents/2026-03-20/table-i-reduction-binding-audit.md`
  - attempted two worker slots for the single-file Table I rebuild
    - result:
      both slots were closed after suspected stall and no collected output
    - worklogs:
      `.codex/worklogs/subagents/2026-03-20/table-i-reduction-worker.md`
      `.codex/worklogs/subagents/2026-03-20/table-i-reduction-worker-v2.md`
  - a narrower follow-up worker completed a file-only Table I reduction draft
    - worklog:
      `.codex/worklogs/subagents/2026-03-20/table-i-reduction-worker-v3.md`
  - main session took over implementation, compilation, and doc updates by
    exception so the manuscript task could complete within this run
  - final acceptance was performed in the main session through build-log review
    and reviewer-page visual inspection

## Milestone summary

- Completed in this run:
  - retained Table I as a table-numbered asset instead of converting it into a
    formal figure
  - refined the previous matrix draft into a quieter 4-column comparison
    matrix:
    - column 1:
      row labels
    - column 2:
      `P0 --- Free JSON`
    - column 3:
      `P1 --- Typed call`
    - column 4:
      `P2 --- Typed call + self-check`
  - removed the shaded shared-tool strip, the separate `Cue` row, and the
    standalone binding-strength cue
  - reduced the shared declared tool list to one low-key note above the body
  - limited the body to the two requested rows:
    - `Example emission`
    - `Dispatchability`
  - shortened the caption and tightened the intro/setup framing sentences so
    the table reads as a restrained manuscript comparison table rather than an
    explanatory panel
  - updated manuscript/docs bookkeeping in:
    - `paper/versions/ral/README.md`
    - `paper/versions/ral/figure_table_binding.md`
    - `paper/versions/ral/latex_assembly_notes.md`
    - `paper/versions/ral/full_draft_v1_notes.md`
    - `STATUS.md`
  - recompiled both manuscript variants successfully
  - visually checked reviewer page 2 after rebuild
- Preserved in this run:
  - same scientific content for `P0`, `P1`, and `P2`
  - same shared declared tool list
  - same table label and intro insertion point
  - frozen Figure 1 and the existing non-Table-I result assets
  - reviewer-facing anonymity
- Not completed in this run:
  - no human author final pass
  - no cleanup of the pre-existing Figure 2 / Figure 4 overfull warnings
  - no cleanup of the remaining narrow-column underfull warnings outside Table I

## Files changed in this run

- `STATUS.md`
- `paper/versions/ral/README.md`
- `paper/versions/ral/figure_table_binding.md`
- `paper/versions/ral/full_draft_v1_notes.md`
- `paper/versions/ral/latex_assembly_notes.md`
- `paper/versions/ral/sections/intro.tex`
- `paper/versions/ral/sections/setup.tex`
- `paper/versions/ral/tables/contract_interface_examples.tex`
- `paper/versions/ral/main.pdf`
- `paper/versions/ral/reviewer_submission/main.pdf`
- `.codex/worklogs/main/2026-03-20/session-plan.md`
- `.codex/worklogs/main/2026-03-20/session-research.md`
- `.codex/worklogs/main/2026-03-20/session-handoff.md`
- `.codex/worklogs/subagents/2026-03-20/table-i-reduction-binding-audit.md`
- `.codex/worklogs/subagents/2026-03-20/table-i-reduction-review.md`
- `.codex/worklogs/subagents/2026-03-20/table-i-reduction-worker.md`
- `.codex/worklogs/subagents/2026-03-20/table-i-reduction-worker-v2.md`
- `.codex/worklogs/subagents/2026-03-20/table-i-reduction-worker-v3.md`

## Commands run

- Source-of-truth and manuscript reads:
  - `sed -n '1,240p' plan.md`
  - `sed -n '1,260p' STATUS.md`
  - `sed -n '1,220p' docs/ral_writing_playbook.md`
  - `sed -n ...` / `nl -ba ...` over the listed `paper/shared/*.md`,
    `paper/versions/ral/*.md`, `paper/versions/ral/sections/*.tex`,
    `paper/versions/ral/reviewer_submission/main.tex`, and
    `paper/versions/ral/main.tex`
  - `wc -l ...` over the main paper-note/manuscript files
- Binding/evidence inspection:
  - `rg -n "contract_interface_examples|tab:contract-interface-examples|Table I|short-forward|P0|P1|P2" paper/versions/ral -S`
  - `sed -n ...` over the archived `planner_trace.json` files for `P0`, `P1`,
    and `P2`
  - `sed -n '1,260p' paper/versions/ral/preamble_shared.tex`
- Repo-state inspection:
  - `git status --short --untracked-files=all`
  - `git diff -- paper/versions/ral/tables/contract_interface_examples.tex paper/versions/ral/sections/intro.tex paper/versions/ral/sections/setup.tex`
- Compile verification:
  - initial quick check:
    - `cd paper/versions/ral/reviewer_submission && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    - `cd paper/versions/ral && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - reran the same pair after fixing the dispatchability-row cell wrapping:
    - `cd paper/versions/ral/reviewer_submission && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    - `cd paper/versions/ral && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
  - final sync after the last Table I note/intro wording tweak:
    - `cd paper/versions/ral/reviewer_submission && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    - `cd paper/versions/ral && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
- Log/page/visual inspection:
  - `pdfinfo paper/versions/ral/reviewer_submission/main.pdf | rg '^Pages:'`
  - `pdfinfo paper/versions/ral/main.pdf | rg '^Pages:'`
  - `rg -n "Undefined|undefined|Overfull|Underfull|Rerun|Warning: Citation|Warning: Reference|Label\\(s\\) may have changed|Conference Paper" paper/versions/ral/reviewer_submission/main.log`
  - `rg -n "Undefined|undefined|Overfull|Underfull|Rerun|Warning: Citation|Warning: Reference|Label\\(s\\) may have changed|Conference Paper" paper/versions/ral/main.log`
  - `pdftoppm -png -f 2 -singlefile paper/versions/ral/reviewer_submission/main.pdf /tmp/ral_reviewer_page2_reduction`
  - `view_image /tmp/ral_reviewer_page2_reduction.png`

## Validation results

- Binding/path validation:
  - Table I still lives at
    `paper/versions/ral/tables/contract_interface_examples.tex`
  - label remains `tab:contract-interface-examples`
  - insertion point remains `paper/versions/ral/sections/intro.tex`
  - intro/setup references remain coherent
- Compile status:
  - reviewer-facing build:
    - success
    - `Pages: 8`
  - journal scaffold:
    - success
    - `Pages: 8`
- Log status:
  - no undefined references or citation rerun failures remain after the final
    rebuild
  - Table I no longer emits a table-local overfull warning
  - remaining overfull warnings are limited to:
    - `paper/versions/ral/figures/main_condition_ordering.tex`
    - `paper/versions/ral/figures/invalid_actions_recovery.tex`
  - underfull box warnings remain in narrow-column prose and column balancing
  - the reviewer-facing conference build still emits the standard last-page
    column-balance reminder
- Visual inspection:
  - reviewer page 2 shows Table I as a restrained 4-column comparison matrix
    below the frozen Figure 1
  - the table now reads more quietly through reduced wording, lighter note
    treatment, and the removal of the previous gray strip / cue row
  - the table remains grayscale-safe through rules, alignment, and type
    hierarchy rather than decorative styling

## Supplemental run update

- Date:
  `2026-03-20`
- Request:
  download several RA-L papers into a new folder under `tmp/`
- Scope:
  no manuscript source or experiment changes; this was a literature asset
  download only
- Target folder:
  `tmp/ral_papers_2026-03-20`
- Files added:
  - `tmp/ral_papers_2026-03-20/README.md`
  - `tmp/ral_papers_2026-03-20/what_matters_language_conditioned_robotic_imitation_unstructured_data.pdf`
  - `tmp/ral_papers_2026-03-20/lemma_learning_language_conditioned_multi_robot_manipulation.pdf`
  - `tmp/ral_papers_2026-03-20/bench_mr_motion_planning_benchmark_wheeled_mobile_robots.pdf`
  - `tmp/ral_papers_2026-03-20/ramp_benchmark_robotic_assembly_manipulation_planning.pdf`
  - `tmp/ral_papers_2026-03-20/deep_episodic_memory_verbalization_robot_experience.pdf`
  - `.codex/worklogs/main/2026-03-20/ral-paper-download-session-plan.md`
  - `.codex/worklogs/main/2026-03-20/ral-paper-download-session-research.md`
  - `.codex/worklogs/main/2026-03-20/ral-paper-download-session-handoff.md`
- Selection note:
  the user did not name exact titles, so the set was chosen as a best-effort
  project-relevant slice spanning language-conditioned manipulation, navigation
  benchmarks, assembly planning, and robot memory
- Commands run:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,260p' STATUS.md`
  - `sed -n '150,230p' paper/versions/ral/refs/references.bib`
  - `sed -n '1,220p' paper/versions/ral/bibliography_candidates.md`
  - `sed -n '1,220p' paper/versions/ral/citation_todo.md`
  - `curl -L --fail --retry 2 --connect-timeout 20 --max-time 180 -o ...`
    over the five selected PDF URLs into `tmp/ral_papers_2026-03-20/`
  - `pdfinfo tmp/ral_papers_2026-03-20/*.pdf | rg '^Pages:'`
  - `head -c 5 tmp/ral_papers_2026-03-20/*.pdf`
  - `ls -lh tmp/ral_papers_2026-03-20`
  - `du -sh tmp/ral_papers_2026-03-20`
- Validation results:
  - all five PDFs downloaded successfully
  - each file begins with `%PDF-`
  - `pdfinfo` reported a page count for every file
  - total folder size is `17M`
- No blockers:
  - the shell utility `file` was unavailable, so validation used PDF header
    inspection plus `pdfinfo` instead

## Supplemental run update

- Date:
  `2026-03-20`
- Request:
  download the specific paper `Adaptive Neural Computed Torque Control for
  Robot Joints With Asymmetric Friction Model`
- Scope:
  literature asset fetch only; no manuscript or experiment changes
- Requested target folder:
  `tmp/ral_papers_2026-03-20`
- Paper metadata:
  - DOI:
    `10.1109/LRA.2024.3512372`
  - IEEE Xplore document id:
    `10778318`
- Commands run:
  - `sed -n '1,120p' plan.md`
  - `sed -n '1,260p' STATUS.md`
  - `ls -lh tmp/ral_papers_2026-03-20`
  - `curl -L --head https://sri-lab.com/publication/luo2024adaptive/`
  - `curl -L https://sri-lab.com/publication/luo2024adaptive/ | rg -n 'pdf|download|doi|10778318|3512372' -i`
  - `curl -L https://sri-lab.com/publication/luo2024adaptive/cite.bib`
  - OpenAlex lookup for `10.1109/LRA.2024.3512372`
  - Unpaywall lookup for `10.1109/LRA.2024.3512372`
  - `curl --http1.1 -I -L ... 'https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=10778318&ref='`
  - `curl --http1.1 -L ... -o tmp/ral_papers_2026-03-20/adaptive_neural_computed_torque_control_robot_joints_asymmetric_friction_model.pdf 'https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=10778318&ref='`
  - `head -c 5 tmp/ral_papers_2026-03-20/adaptive_neural_computed_torque_control_robot_joints_asymmetric_friction_model.pdf`
  - `pdfinfo tmp/ral_papers_2026-03-20/adaptive_neural_computed_torque_control_robot_joints_asymmetric_friction_model.pdf`
  - Python unlink to remove the invalid HTML payload saved with a `.pdf` name
- Validation and outcome:
  - the author page exposes DOI and IEEE Xplore links only; no public PDF link
  - OpenAlex and Unpaywall both report the work as closed access with no
    repository full text
  - the official IEEE PDF endpoint returns a `302` redirect to the login route
    with `authDecision=-203`
  - the downloaded payload from the official PDF endpoint was HTML, not PDF
  - the invalid temp file was removed immediately
  - no valid PDF for this paper was added to `tmp/ral_papers_2026-03-20`
- Blocker:
  - access control on the official source and no public mirror found from the
    checked sources

## Supplemental run update

- Date:
  `2026-03-23`
- Request:
  commit and push the completed Table I reduction manuscript pass
- Scope:
  repo-state handoff only; no new experiments or new manuscript claims
- Intended commit scope:
  - `STATUS.md`
  - `paper/versions/ral/README.md`
  - `paper/versions/ral/figure_table_binding.md`
  - `paper/versions/ral/full_draft_v1_notes.md`
  - `paper/versions/ral/latex_assembly_notes.md`
  - `paper/versions/ral/sections/intro.tex`
  - `paper/versions/ral/sections/setup.tex`
  - `paper/versions/ral/tables/contract_interface_examples.tex`
  - `paper/versions/ral/main.pdf`
  - `paper/versions/ral/reviewer_submission/main.pdf`
- Repo-state note:
  - leave the unrelated local `.claude/` settings files out of the commit
  - keep the temporary-download `.gitignore` change separate unless explicitly
    requested
- Validation before commit:
  - current branch and remote checked
  - working-tree diff reviewed against the intended manuscript scope

## Remaining gaps

- Underfull-box warnings remain in narrow-column prose.
- Small overfull-box warnings remain in:
  - `paper/versions/ral/figures/main_condition_ordering.tex`
  - `paper/versions/ral/figures/invalid_actions_recovery.tex`
- The reviewer-facing conference build still emits the standard last-page
  column-balance reminder.
- A final human author pass for wording, anonymization, metadata, and
  submission packaging is still outstanding.

## Next recommended sub-milestone

- `Paper author final edit / submission packaging`:
  - final human sentence-level review
  - final anonymization / metadata / cover-letter checks
  - optional cleanup of the remaining non-Table-I LaTeX warnings
- `Literature asset follow-up (optional)`:
  - if needed, replace the best-effort RA-L paper set with an exact user-named
    download list
  - if the user can provide an accessible PDF URL, uploaded file, or library
    proxy route for `10.1109/LRA.2024.3512372`, retry the download directly
