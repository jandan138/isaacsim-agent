# RA-L Version Policy

This directory is for the primary submission-target version.

## Why RA-L first

The current evidence is strongest as a compact controlled systems study with clean,
results-first takeaways. `docs/ral_writing_playbook.md` already defines the most
concrete writing constraints in the repo, so RA-L is the best first target for the
current Block A closure.

## What belongs in this version

- the tightest framing of the controlled-study story
- the highest-value figures and tables only
- the most compressed introduction and related work
- explicit limitations with no scope creep

Use these inputs first:

- `paper/shared/core_claim.md`
- `paper/shared/findings.md`
- `paper/shared/limitations.md`
- `paper/shared/figures_and_tables.md`
- `paper/outlines/ral_outline.md`

## Section triage under page pressure

Keep at full strength:

- results
- study design
- experimental setup
- limitations

Compress aggressively:

- introduction
- related work
- conclusion

Exclude unless a later task explicitly adds them:

- roadmap dimensions outside Block A
- long implementation detail
- expanded discussion that does not change interpretation

## Anonymity rules

- maintain double-anonymous wording in manuscript text
- avoid self-identifying repo history, names, affiliations, or prior ownership language
- do not state or imply that the paper is already submitted, accepted, or transferred

## Shared vs venue-specific text

Likely shared:

- results paragraphs
- variant definitions
- metric definitions
- most of the limitations wording

Must be RA-L-specific:

- title
- abstract
- introduction pacing
- related-work compression
- figure/table budget decisions
