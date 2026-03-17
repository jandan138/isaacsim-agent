# CoRL Migration Notes

This directory is for a CoRL-style branch if the RA-L version is not used or is
not accepted. It is a style plan only; it does not assert current CoRL policy or
format rules.

## Migration goal

Retain the same Block A evidence while allowing:

- a somewhat broader empirical framing around embodied decision-making
- more explicit discussion of design axes
- more room for analysis and interpretation than the RA-L version can afford

## Best source to branch from

Branch from:

- the neutral mother draft for reusable prose
- the RA-L branch for compact claims and figure priorities

Use `paper/outlines/corl_outline.md` as the structure guide.

## What can stay shared

- task and metric definitions
- prompt/runtime variant descriptions
- core results paragraphs
- limitations about scope and non-claims
- the core empirical figures and tables

## What should be rewritten

- title
- abstract
- introduction
- related-work framing
- discussion emphasis

## Guardrails

- do not invent new experiments or new claims just to sound more conference-like
- do not convert the paper into a new-model paper
- do not claim official CoRL constraints here unless a later task verifies them
