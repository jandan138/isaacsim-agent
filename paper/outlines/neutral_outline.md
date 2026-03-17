# Neutral Outline

This is the venue-neutral mother outline. It is the safest place to draft shareable
scientific prose before compressing for RA-L or expanding for another venue.

## Neutral drafting rules

- Keep wording descriptive and evidence-locked.
- Avoid venue-specific rhetoric.
- Prefer reusable prose for setup, study design, results, and limitations.
- Treat title, abstract, introduction tone, related-work emphasis, and discussion framing as later branches.

## 1. Working title and abstract placeholders

- Use neutral wording such as `controlled study`, `embodied-agent execution`, and `Isaac Sim`.
- Do not bake in venue-specific page pressure or stylistic hooks yet.

## 2. Introduction

### 2.1 Motivation

- focus on execution reliability in embodied agents
- motivate invalid actions, recovery, and execution overhead

### 2.2 Gap

- explain why controlled design-axis studies are useful even when larger benchmarks exist

### 2.3 Scope

- navigation and manipulation
- prompt/interface structure and runtime validation
- current harder slices

### 2.4 Findings preview

- stable ordering
- runtime recovery effect
- `P2` efficiency effect

Shareable later:

- most of the problem statement and findings preview

Likely venue-specific rewrite:

- opening hook, novelty language, and related-work bridge

## 3. Study Scope and Setup

### 3.1 Simulator setting

- controlled Isaac Sim setup

### 3.2 Task families and slices

- easy/shared slices
- harder navigation
- harder manipulation

### 3.3 Metrics

- success
- invalid actions
- retries
- planner calls
- tool calls

Shareable later:

- almost all of this section

## 4. Design Axes

### 4.1 Prompt/interface variants

- define `P0`, `P1`, `P2`

### 4.2 Runtime variants

- define `R0`, `R1`

### 4.3 Analysis structure

- main effect
- runtime-only
- prompt-only
- cross-family
- harder tasks

Shareable later:

- almost all of this section

## 5. Results

### 5.1 Main prompt x runtime ordering

- stable ranking and headline pattern

### 5.2 Runtime-only ablation

- independent value of validation plus retry

### 5.3 Prompt-only ablation

- independent value of structured interfaces

### 5.4 Cross-family consistency

- same qualitative direction in the covered navigation/manipulation slices

### 5.5 Harder-task effect

- workload increase without ordering change in current harder slices

Shareable later:

- this should be the most reusable prose across all versions

## 6. Discussion

### 6.1 Interpretation

- design principles supported by the data

### 6.2 Boundaries

- controlled study limitations

### 6.3 What remains outside scope

- memory
- context compression
- tool abstraction
- randomization

Likely venue-specific rewrite:

- the balance between empirical insight and system detail

## 7. Conclusion

- one short paragraph restating the strongest evidence-backed takeaways

## 8. Optional appendices or artifact notes

- source manifest for figures/tables
- extended design table
- venue-specific reproducibility notes if later required
