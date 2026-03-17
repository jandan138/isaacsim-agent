# STATUS.md

## Current status

- Date: 2026-03-17
- Plan source of truth: `plan.md`
- Active milestone: `M6. Prompting and runtime ablations`
- Milestone state:
  - Block A experimental closure remains completed from the previous run
  - this run created the paper-writing scaffold for the frozen Block A package
- Completion level:
  - the frozen Block A evidence base remains under:
    - `results/processed/block_a_final_closure/`
    - `results/processed/block_a_master_summary/`
    - `results/processed/block_a_runtime_only_ablation/`
    - `results/processed/block_a_prompt_only_ablation/`
    - `results/processed/block_a_manipulation_harder/`
    - `results/processed/block_a_cross_family_summary/`
  - the new paper workspace now exists under:
    - `paper/shared/`
    - `paper/outlines/`
    - `paper/versions/`
    - `paper/assets/`
    - `paper/notes/`

## Run context

- This run stayed within the requested boundaries:
  - no new experiments
  - no code main-function changes
  - no `M7+` implementation work
  - no tool-abstraction work
  - no randomization work
  - no venue switch in repo metadata
  - no heavy Isaac Sim / ROS workflow launch
- Existing artifacts consumed in this run:
  - `results/processed/block_a_final_closure/block_a_final_closure_summary.{json,csv,md}`
  - `results/processed/block_a_master_summary/block_a_master_summary.{json,md}`
  - `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.{json,md}`
  - `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.{json,md}`
  - `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.{json,md}`
  - `results/processed/block_a_cross_family_summary/cross_family_summary.json`
  - legacy packaging templates under:
    - `results/processed/block_a_master_summary/paper_figures/`
    - `results/processed/block_a_master_summary/paper_tables/`
    - `results/processed/block_a_master_summary/analysis/block_a_analysis.md`
- Agent teaming:
  - spawned two explorer sub-agents in parallel
  - one explored claim boundaries and evidence-safe findings for the Block A paper scaffold
  - one explored current paper-facing assets and stale-packaging risks
  - one wait window timed out with no completed result, but no interruption was sent
  - both explorers later returned successfully
  - no sub-agent stall intervention or reassignment was needed

## Milestone summary

- Completed in this run:
  - replaced the placeholder `paper/README.md` with a multi-version workspace guide
  - created the reusable claim and evidence layer:
    - `paper/shared/core_claim.md`
    - `paper/shared/contributions.md`
    - `paper/shared/findings.md`
    - `paper/shared/limitations.md`
    - `paper/shared/terminology.md`
    - `paper/shared/figures_and_tables.md`
  - created the outline layer:
    - `paper/outlines/ral_outline.md`
    - `paper/outlines/neutral_outline.md`
    - `paper/outlines/corl_outline.md`
    - `paper/outlines/autonomous_robots_outline.md`
  - created venue-specific branch notes:
    - `paper/versions/ral/README.md`
    - `paper/versions/neutral/README.md`
    - `paper/versions/corl/README.md`
    - `paper/versions/autonomous_robots/README.md`
  - created asset-mapping notes without copying result binaries:
    - `paper/assets/README.md`
    - `paper/assets/figures/README.md`
    - `paper/assets/tables/README.md`
  - created writing-strategy and handoff notes:
    - `paper/notes/submission_strategy.md`
    - `paper/notes/review_risks.md`
    - `paper/notes/version_deltas.md`
    - `paper/notes/open_questions.md`
  - validated markdown links, referenced paths, and wording against the frozen Block A scope
- Not completed in this run:
  - no manuscript section prose yet
  - no final paper figures/tables regenerated from final closure
  - no system diagram drafting
  - no related-work refresh
  - no new experiments or analysis reruns

## Frozen evidence snapshot

- Unified final closure:
  - output dir: `results/processed/block_a_final_closure/`
  - merged runs: `146`
  - successful runs: `119`
  - success rate: `0.815068`
  - all six closure questions remain `yes`
  - verdict remains: `freeze_block_a_and_write_paper`
- Runtime-only ablation:
  - output dir: `results/processed/block_a_runtime_only_ablation/`
  - fixed condition: `P1`
  - success: `2/4 -> 4/4` from `R0` to `R1`
  - invalid-action runs remain `2` vs `2`; successful recoveries rise `0 -> 2`
- Prompt-only ablation:
  - output dir: `results/processed/block_a_prompt_only_ablation/`
  - fixed condition: `R0`
  - `P0/R0` success rate: `0.0`
  - `P1/R0` success rate: `1.0`
  - `P2/R0` success rate: `1.0`
  - `P2/R0` average planner/tool calls: `6.0 / 6.0`
  - `P1/R0` average planner/tool calls: `7.5 / 7.5`
- Manipulation harder slice:
  - output dir: `results/processed/block_a_manipulation_harder/`
  - `P0/R0` fails on all `3` harder tasks
  - `P0/R1` recovers on all `3` harder tasks
  - `P1/P2` remain fully successful
  - `P2` planner/tool calls remain below `P1`

## Files changed

- `STATUS.md`
- `paper/README.md`
- `paper/assets/README.md`
- `paper/assets/figures/README.md`
- `paper/assets/tables/README.md`
- `paper/notes/open_questions.md`
- `paper/notes/review_risks.md`
- `paper/notes/submission_strategy.md`
- `paper/notes/version_deltas.md`
- `paper/outlines/autonomous_robots_outline.md`
- `paper/outlines/corl_outline.md`
- `paper/outlines/neutral_outline.md`
- `paper/outlines/ral_outline.md`
- `paper/shared/contributions.md`
- `paper/shared/core_claim.md`
- `paper/shared/figures_and_tables.md`
- `paper/shared/findings.md`
- `paper/shared/limitations.md`
- `paper/shared/terminology.md`
- `paper/versions/autonomous_robots/README.md`
- `paper/versions/corl/README.md`
- `paper/versions/neutral/README.md`
- `paper/versions/ral/README.md`

## Commands run

- Source-of-truth reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,260p' AGENTS.md`
  - `sed -n '1,260p' STATUS.md`
  - `sed -n '1,260p' docs/ral_writing_playbook.md`
  - `sed -n '260,520p' docs/ral_writing_playbook.md`
  - `rg -n '^##|^###' docs/ral_writing_playbook.md`
- Context inspection:
  - `find paper -maxdepth 3 -print 2>/dev/null | sort`
  - `find results/processed -maxdepth 2 -type d | sort | rg 'block_a|packag|figure|table|analysis'`
  - `sed -n '1,220p' paper/README.md`
  - `sed -n '1,260p' results/processed/block_a_final_closure/block_a_final_closure_summary.md`
  - `sed -n '1,260p' results/processed/block_a_final_closure/block_a_final_closure_summary.json`
  - `sed -n '1,220p' results/processed/block_a_final_closure/block_a_final_closure_summary.csv`
  - `sed -n '1,240p' results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.json`
  - `sed -n '1,220p' results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.json`
  - `sed -n '1,260p' results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json`
  - `sed -n '1,260p' results/processed/block_a_master_summary/block_a_master_summary.json`
  - `sed -n '1,260p' results/processed/block_a_cross_family_summary/cross_family_summary.json`
  - `find results/processed/block_a_master_summary -maxdepth 2 -type f | sort`
  - `find results/processed/block_a_master_summary/paper_tables -maxdepth 2 -type f | sort`
  - `find results/processed/block_a_master_summary/paper_figures -maxdepth 2 -type f | sort`
  - `find results/processed/block_a_master_summary/analysis -maxdepth 2 -type f | sort`
  - `sed -n '1,200p' results/processed/block_a_master_summary/analysis/block_a_analysis.md`
- Workspace setup:
  - `mkdir -p paper/shared paper/versions/ral paper/versions/corl paper/versions/autonomous_robots paper/versions/neutral paper/assets/figures paper/assets/tables paper/notes paper/outlines`
- Validation:
  - `python - <<'PY' ... verify markdown links and referenced result paths under paper/ ... PY`
  - `rg -n "state of the art|strongest embodied agent|general embodied intelligence|sim-to-real|real-world safety|accepted|submitted|dual submission|first Isaac Sim embodied-agent benchmark|memory/context/tool abstraction are solved|new model" paper -S`
  - `find paper -maxdepth 4 -print | sort`

## Validation results

- Markdown links and referenced paths under `paper/` all resolved successfully.
  - command: `python - <<'PY' ... verify markdown links and referenced result paths under paper/ ... PY`
  - result: `OK`
- Keyword scan only found explicit negative guardrails and caution text; no conflicting positive claim about SOTA, submission state, or general embodied intelligence was introduced.
  - command: `rg -n "state of the art|strongest embodied agent|general embodied intelligence|sim-to-real|real-world safety|accepted|submitted|dual submission|first Isaac Sim embodied-agent benchmark|memory/context/tool abstraction are solved|new model" paper -S`
  - result: matches were all negative guardrails or branch-policy cautions
- The expected paper workspace structure now exists.
  - command: `find paper -maxdepth 4 -print | sort`
  - result: all requested top-level subdirectories and required markdown files are present

## Next recommended sub-milestone

- Draft the RA-L main-text core from this scaffold in results-first order:
  - `Results`
  - `Study Design`
  - `Experimental Setup`
  - `Discussion and Limitations`
- When that work starts, use `paper/shared/findings.md`, `paper/shared/figures_and_tables.md`, and `paper/outlines/ral_outline.md` as the immediate source documents.
