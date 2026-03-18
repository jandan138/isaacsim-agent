# STATUS.md

## Current status

- Date: 2026-03-18
- Plan source of truth: `plan.md`
- Paper-writing source of truth: `docs/ral_writing_playbook.md`
- Active milestone: `M11. Paper drafting`
- Milestone state:
  - this run completed `expert-review blocking issues pass`
- Completion level:
  - the reviewer-facing submission variant compiles successfully at `8` pages:
    `paper/versions/ral/reviewer_submission/main.pdf`
  - the journal scaffold compiles successfully at `8` pages:
    `paper/versions/ral/main.pdf`
  - Figure 1 remains frozen at
    `paper/versions/ral/figures/fig1_system_overview_frozen.*`
  - the manuscript now includes a compact contract/interface display, explicit
    deterministic-planner framing, shared keywords, and clarified runtime /
    executor semantics

## Run context

- This run stayed within the requested boundaries:
  - no new experiments
  - no Figure 1 redesign, regeneration, relabeling, or replacement
  - no venue switch
  - no prompt-first reframing
  - no exaggerated efficiency claims
  - no fabricated examples, interface schemas, or citations
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
  - `paper/versions/ral/asset_manifest.md`
  - `results/processed/block_a_final_closure/`
  - `results/processed/block_a_master_summary/`
  - `results/processed/block_a_prompt_only_ablation/`
  - `results/processed/block_a_runtime_only_ablation/`
  - `results/processed/block_a_manipulation_harder/`
  - `results/processed/block_a_cross_family_summary/`
  - `scripts/package_block_a_ral_assets.py`
  - `src/isaacsim_agent/eval/block_a_ral_assets.py`
  - `src/isaacsim_agent/planner/`
  - `src/isaacsim_agent/runtime/`
- Agent teaming:
  - two explorer subagent worklogs were created for the current pass:
    - `.codex/worklogs/subagents/2026-03-18/impl-semantics-audit.md`
    - `.codex/worklogs/subagents/2026-03-18/manuscript-audit-current.md`
  - neither produced a usable result in the workspace; both worklogs record
    abandonment and the main session completed the audits locally

## Milestone summary

- Completed in this run:
  - added `paper/versions/ral/tables/contract_interface_examples.tex` as a
    compact manuscript-facing table with real `P0` / `P1` / `P2` outputs taken
    from saved prompt texts and archived `planner_trace.json` files
  - revised `sections/setup.tex`, `sections/results.tex`,
    `sections/discussion.tex`, and `sections/conclusion.tex` so the manuscript
    now states explicitly that:
    - the planner backend is deterministic by design
    - the empirical unit is the task instance, not repeated stochastic rollout
      replication
    - the main comparison covers 21 task instances across four cohorts
    - the two focused ablations add 8 task instances
    - the reported evaluation set contains 29 task instances and 146
      executions
    - the quantitative comparisons are descriptive rather than a
      confidence-interval / significance-test exercise
  - removed reviewer-facing internal wording from the active manuscript where
    avoidable and tightened repeated main-conclusion wording
  - added shared `IEEEkeywords` in `sections/abstract.tex`; both variants
    compile with the same keyword line
  - clarified the exact `R1` retry semantics:
    - same tool list on retry
    - literal `validation_error` string
    - appended repair instruction
    - one retry only
  - clarified executor-visible action semantics:
    - `navigate_to` dispatches one deterministic step toward the configured
      goal
    - `scripted_pick_place_step` advances one phase of a fixed scripted
      pick-and-place sequence
  - polished the related-work comparison to SayCan, Code as Policies, and
    ProgPrompt around affordance grounding, code/program generation, and
    declared action interfaces
  - added non-color labels inside Fig. 2's runtime panel cells so recovered
    outcomes remain distinguishable in grayscale / color-deficient viewing
  - rebuilt both manuscript variants, confirmed 8 pages for both, and checked
    that the new contract/interface display is present as Table I
- Not completed in this run:
  - no new experiments
  - no Figure 1 work beyond preserving the frozen asset
  - no bibliography expansion beyond the already-shared citation state

## Files changed in this run

- `STATUS.md`
- `paper/versions/ral/README.md`
- `paper/versions/ral/figure_table_binding.md`
- `paper/versions/ral/latex_assembly_notes.md`
- `paper/versions/ral/full_draft_v1_notes.md`
- `paper/versions/ral/sections/abstract.tex`
- `paper/versions/ral/sections/intro.tex`
- `paper/versions/ral/sections/related_work.tex`
- `paper/versions/ral/sections/setup.tex`
- `paper/versions/ral/sections/results.tex`
- `paper/versions/ral/sections/discussion.tex`
- `paper/versions/ral/sections/conclusion.tex`
- `paper/versions/ral/tables/contract_interface_examples.tex`
- `paper/versions/ral/main.pdf`
- `paper/versions/ral/reviewer_submission/main.pdf`
- `.codex/worklogs/main/2026-03-18/session-plan.md`
- `.codex/worklogs/main/2026-03-18/session-research.md`
- `.codex/worklogs/main/2026-03-18/session-handoff.md`
- `.codex/worklogs/subagents/2026-03-18/impl-semantics-audit.md`
- `.codex/worklogs/subagents/2026-03-18/manuscript-audit-current.md`

## Commands run

- Source-of-truth and repo-state reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,260p' AGENTS.md`
  - `sed -n '1,260p' STATUS.md`
  - `sed -n '1,260p' docs/ral_writing_playbook.md`
  - `git status --short --untracked-files=all`
- Manuscript and implementation audit:
  - `sed -n ...` over the requested paper-level `.md`, `.tex`, `.csv`, and
    `.bib` files
  - `rg -n ...` across `paper/versions/ral/`, `results/`, and
    `src/isaacsim_agent/`
  - `find results -name 'planner_trace.json' ...`
  - `python - <<'PY' ...` snippets to inspect saved task configs, planner
    traces, processed summaries, and final-closure counts
- Compile validation:
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex && bibtex main && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral`
  - `pdflatex -interaction=nonstopmode -halt-on-error main.tex && bibtex main && pdflatex -interaction=nonstopmode -halt-on-error main.tex && pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    with working directory `paper/versions/ral/reviewer_submission`
  - follow-up single-pass `pdflatex -interaction=nonstopmode -halt-on-error main.tex`
    in both `paper/versions/ral` and `paper/versions/ral/reviewer_submission`
    after inserting the manual contract table
  - `pdfinfo main.pdf | sed -n '1,20p'`
    with working directory `paper/versions/ral`
  - `pdfinfo main.pdf | sed -n '1,20p'`
    with working directory `paper/versions/ral/reviewer_submission`
  - `pdftotext paper/versions/ral/reviewer_submission/main.pdf - | rg -n ...`
    to confirm contract-table text appears in the reviewer-facing PDF

## Validation results

- Reviewer-facing submission:
  - `paper/versions/ral/reviewer_submission/main.pdf` compiles successfully
  - `pdfinfo` reports `Pages: 8`
  - `main.aux` records `\newlabel{tab:contract-interface-examples}{{I}{2}}`,
    so the new contract/interface display resolves as Table I on page 2
- Journal scaffold:
  - `paper/versions/ral/main.pdf` compiles successfully
  - `pdfinfo` reports `Pages: 8`
  - `main.aux` records `\newlabel{tab:contract-interface-examples}{{I}{2}}`
- Keywords:
  - the shared `IEEEkeywords` block compiles in both variants
- Figure 1 state:
  - still inserted via `figures/fig1_system_overview_frozen.tex`
  - still resolves to the frozen manual asset
  - intentionally not modified in this pass
- Remaining warnings / non-blockers:
  - underfull-box warnings remain in narrow-column prose
  - small overfull-box warnings remain in:
    - `tables/contract_interface_examples.tex`
    - `figures/main_condition_ordering.tex`
    - `figures/invalid_actions_recovery.tex`
  - the reviewer-facing conference build still emits the standard last-page
    column-balance reminder

## Remaining gaps

- do the final author-side line edit and anonymity pass
- decide whether any setup prose should be trimmed if another small page-margin
  reduction is needed
- optionally refine the new contract/interface table wording if the authors want
  the examples to be navigation-only or manipulation-only rather than mixed
- keep Figure 1 unchanged unless the authors explicitly choose a different
  frozen manual asset later

## Next recommended sub-milestone

- Move from `expert-review blocking issues pass` to `author final-edit /
  submission prep` by:
  - reviewing `paper/versions/ral/reviewer_submission/main.pdf` line by line
  - checking anonymity and wording one last time
  - deciding whether any final page-pressure trimming is still needed
  - preserving the frozen Figure 1 asset and the current contract/runtime
    framing unless the authors explicitly request another scope change
