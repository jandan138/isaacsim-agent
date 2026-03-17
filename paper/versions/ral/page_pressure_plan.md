# RA-L Page Pressure Plan

## Current pressure snapshot

After the targeted reframing and tightening pass, the main prose hotspots are
smaller but still real. Current word counts are approximately:

- `intro_draft.md`: `545`
- `setup_and_study_design_draft.md`: `691`
- `results_draft.md`: `931`

The remaining risk is now less about uncontrolled bulk and more about repeated
explanation across Introduction, Setup/Study Design, and Results, plus exact
numeric detail that belongs in tables or captions rather than in body prose.

## Highest-leverage compression moves

1. Move the full `P0/P1/P2` and `R0/R1` inventory into
   `[Table: experimental design summary]`.
2. Keep cross-family consistency inside the main-effect ending or the ablation
   ending as one or two sentences; do not restore it as a standalone results
   subsection unless a later assembly pass finds a strong need.
3. Keep the Introduction scope boundary to one short sentence and avoid
   repeated `this paper does not...` lists elsewhere.
4. Let Setup/Study Design define the planner-to-executor contract once, then do
   not restate the same contract in each results subsection.
5. Push exact planner/tool pairs, retry totals, and family-specific breakdowns
   into figures, tables, or captions unless a number is carrying a headline
   result.

## What should stay in the main body

- Introduction:
  - planner/executor boundary as the problem
  - one short gap statement
  - one compact scope sentence naming navigation, manipulation, `P0/P1/P2`, and
    `R0/R1`
  - one short findings preview
  - three concise contribution bullets
- Setup / Study Design:
  - controlled Isaac Sim setting
  - execution architecture at the planner/executor boundary
  - definitions of `invalid action`, `recovery`, and `runtime validation with a
    single retry`
  - one compact explanation of how `P0/P1/P2` and `R0/R1` differ
- Results:
  - stable main ordering
  - runtime-only headline `2/4 -> 4/4`
  - interface-only headline `0/4 -> 4/4`
  - one compact `P2` lower-overhead statement
  - one short failure-case analysis paragraph or subsection
  - one short harder-task paragraph
- Discussion / Limitations:
  - planner-to-executor contract design as a systems lever
  - runtime validation as an execution-time safeguard
  - bounded study limits only
- Conclusion:
  - two short paragraphs plus one bounding sentence if needed

## Sentence types to cut or merge

The easiest sentences to delete during assembly are:

- repeated lists of what the paper is not about
- family-by-family restatements after the main effect has already established the
  ordering
- bookkeeping about the frozen evidence package after the first methods mention
- repeated metric definitions outside Setup/Study Design
- long decimal workload values that can live in captions instead
- repeated claims that the study is controlled or narrow once that has already
  been established in the Introduction

## What should move to tables, figures, or captions

- the full design inventory for `P0/P1/P2`, `R0/R1`, slices, and metrics
- per-family planner/tool call pairs
- retry totals and per-slice invalid-action counts beyond the headline ablation
  numbers
- harder-slice workload deltas
- exact family-level overhead comparisons used only to support the `P2` pattern

If space becomes tight, `[Table: focused ablation summary]` is still the first
table to drop because the key runtime-only and interface-only contrasts can stay
in the prose and figures.

## Recommended trimming order for full draft assembly

1. Keep the variant inventory table-driven in Setup/Study Design.
2. Fold cross-family consistency into the main effect or ablations.
3. Shorten the Introduction scope sentence and remove repeated exclusion prose.
4. Move exact planner/tool counts and harder-slice deltas into captions.
5. Trim any repeated discussion of the same failure mode after the dedicated
   failure-analysis paragraph.
6. Drop `[Table: focused ablation summary]` if the assembled letter is still
   over budget.
