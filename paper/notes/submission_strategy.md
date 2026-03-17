# Submission Strategy

This workspace assumes sequential submission planning, not simultaneous multi-venue
submission.

## Why the first target is RA-L

RA-L is the best first fit for the current Block A package because:

- the repo already contains explicit RA-L writing guidance in `docs/ral_writing_playbook.md`
- the current evidence is strongest as a compact controlled systems study with clear, reviewer-friendly findings
- the Block A closure package is already organized around a small number of clean design questions rather than a broad benchmark story

In short:

- RA-L is the primary framing target
- the neutral branch is the mother draft policy
- CoRL-style and Autonomous Robots-style branches are fallback adaptations, not parallel active submissions

## If RA-L is not used or is rejected

The fast branch path should be:

1. keep `paper/shared/` unchanged unless the evidence changes
2. reuse the neutral outline and any future neutral prose as the mother source
3. port the RA-L-compressed results and figure priorities into the target venue branch
4. rewrite venue-specific framing sections first:
   title, abstract, introduction, related work, and discussion
5. expand system/setup detail only where the target venue style benefits from it

## Venue-invariant content

These parts should stay as stable as possible across versions:

- core claim boundary
- prompt/runtime variant definitions
- task-family and metric definitions
- supported findings
- limitations and non-claims
- empirical figure/table content, once regenerated from the correct freeze

## Venue-specific content

These parts should be expected to change per branch:

- title
- abstract
- introduction opening and problem framing
- related-work emphasis
- discussion tone and breadth
- figure/table budget and placement
- section compression versus expansion

## Dual-submission rule for this workspace

Do not treat this workspace as a dual-submission preparation area.

Operational rule:

- only one venue branch should be the active submission target at a time
- other venue folders exist to reduce rewrite cost after a decision, not to support simultaneous active submission

This is especially important because `docs/ral_writing_playbook.md` already states
RA-L-specific submission constraints. Unless an owner explicitly requests otherwise,
keep the workflow sequential and conservative.
