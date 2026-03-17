# Neutral Version Policy

This directory is the mother-draft policy for prose that should survive venue
changes with minimal rewriting.

## Role of the neutral version

- hold the least venue-specific wording
- preserve evidence-backed results and limitations in their clearest form
- act as the branch point for RA-L, CoRL-style, and Autonomous Robots-style rewrites

The neutral version should not try to satisfy page pressure or venue rhetoric too
early.

## What should live here first

- reusable setup prose
- reusable study-design prose
- reusable results prose
- reusable limitations prose

## What should not be locked here too early

- title
- abstract
- introduction hook
- related-work emphasis
- venue-specific discussion style

## Relationship to shared docs

Use `paper/shared/` as the evidence lock and vocabulary lock.
The neutral version is where those shared constraints can later expand into prose.

## Branching rule

When a venue branch is created:

- copy or adapt neutral prose only after checking it against `paper/shared/findings.md`
- keep venue-specific edits local to the venue branch when possible
- update `paper/notes/version_deltas.md` if a paragraph becomes intentionally branch-specific
