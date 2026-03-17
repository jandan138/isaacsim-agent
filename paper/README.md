# Paper Workspace

This directory is the manuscript workspace for the current Block A paper effort.
Its job is to keep one evidence base and multiple venue evolutions aligned without
copying unstable claims across drafts.

## Source of truth and scope

Use these repo files in this order before writing or revising paper text:

1. `docs/ral_writing_playbook.md`
2. `STATUS.md`
3. `plan.md`
4. `AGENTS.md`

Current manuscript scope:

- Block A only
- no new experiments
- no M7+ memory/context/tool-abstraction/randomization claims
- no "new model" or "strongest agent" framing

Primary evidence base:

- `results/processed/block_a_final_closure/`

Supporting slice-specific evidence:

- `results/processed/block_a_master_summary/`
- `results/processed/block_a_runtime_only_ablation/`
- `results/processed/block_a_prompt_only_ablation/`
- `results/processed/block_a_manipulation_harder/`
- `results/processed/block_a_cross_family_summary/`

Legacy paper-facing assets under `results/processed/block_a_master_summary/paper_figures/`
and `results/processed/block_a_master_summary/paper_tables/` are templates only. They
must not be treated as the final frozen numbers because they predate the final-closure
additions.

## Workspace layout

- [shared/core_claim.md](shared/core_claim.md): one-sentence paper identity and claim boundary
- [shared/contributions.md](shared/contributions.md): reusable contribution bullets
- [shared/findings.md](shared/findings.md): supported findings, careful claims, and non-claims
- [shared/limitations.md](shared/limitations.md): explicit study boundaries
- [shared/terminology.md](shared/terminology.md): stable wording and label mapping
- [shared/figures_and_tables.md](shared/figures_and_tables.md): result-asset consumption plan
- [outlines/ral_outline.md](outlines/ral_outline.md): RA-L-first detailed outline
- [outlines/neutral_outline.md](outlines/neutral_outline.md): venue-neutral mother outline
- [outlines/corl_outline.md](outlines/corl_outline.md): CoRL-style adaptation outline
- [outlines/autonomous_robots_outline.md](outlines/autonomous_robots_outline.md): Autonomous Robots-style adaptation outline
- [versions/ral/README.md](versions/ral/README.md): RA-L version policy
- [versions/neutral/README.md](versions/neutral/README.md): neutral mother-draft policy
- [versions/corl/README.md](versions/corl/README.md): CoRL migration notes
- [versions/autonomous_robots/README.md](versions/autonomous_robots/README.md): Autonomous Robots migration notes
- [assets/README.md](assets/README.md): how paper assets map back to immutable results
- [notes/submission_strategy.md](notes/submission_strategy.md): sequential submission plan
- [notes/review_risks.md](notes/review_risks.md): likely reviewer attacks and how to avoid self-inflicted issues
- [notes/version_deltas.md](notes/version_deltas.md): shared vs venue-specific rewrite map
- [notes/open_questions.md](notes/open_questions.md): writing gaps that remain without requiring new experiments

## Multi-version strategy

The versioning model is:

- `shared/` holds evidence-locked claims and reusable scientific content
- `outlines/` holds structure before prose is expanded
- `versions/neutral/` is the mother draft policy for venue-neutral prose
- `versions/ral/` is the first active target because the current evidence best fits a tight controlled-study letter
- `versions/corl/` and `versions/autonomous_robots/` define how to reframe the same evidence without re-scoping the science

Practical rule:

- share results wording, metric definitions, task descriptions, and limitations where possible
- rewrite title, abstract, introduction, related-work emphasis, and discussion per venue
- regenerate empirical figures/tables from the frozen evidence base instead of copying old packaged outputs

## Recommended writing flow

When actual manuscript drafting starts, follow this order:

1. results
2. study design
3. experimental setup
4. discussion and limitations
5. introduction
6. related work
7. abstract
8. title

That order matches `docs/ral_writing_playbook.md` and reduces claim drift.

## Maintenance rules

- Update `shared/` first when a claim boundary changes.
- Update `outlines/` before writing venue-specific prose.
- Keep `versions/*/README.md` focused on framing and section tradeoffs, not experimental facts.
- Keep `assets/` as mapping and future derived outputs only. Do not copy immutable results into this workspace unless a later task explicitly regenerates them from the correct frozen source.
