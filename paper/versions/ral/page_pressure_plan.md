# RA-L Page Pressure Plan

## Current pressure snapshot

The current prose stack is already close to RA-L page pressure before final assembly.
Measured with `wc -w`, the first-batch drafts are approximately:

- `intro_draft.md`: `622` words
- `setup_and_study_design_draft.md`: `922` words
- `results_draft.md`: `1065` words

That is roughly `2609` words before adding Related Work, Discussion and
Limitations, Conclusion, captions, and final figures/tables. Because the RA-L
playbook targets a tight `6-8` page letter with results as the dominant section, the
main risk is not lack of result coverage. The main risk is duplicated explanation
across Introduction, Setup/Study Design, and Results, combined with too many exact
numbers in prose once captions and floats are added.

## What must stay in the main body

The body should keep only the material needed to make the controlled-study claim
interpretable:

- Introduction:
  - the execution-boundary motivation
  - the narrow gap statement
  - one compact scope sentence naming navigation, manipulation, `P0/P1/P2`, and
    `R0/R1`
  - one short preview of the stable ordering
  - concise contribution bullets
- Setup / Study Design:
  - the controlled Isaac Sim setting
  - the definitions of `invalid action`, `recovery`, and `runtime validation with a
    single retry`
  - one short explanation of why prompt/interface structure and runtime validation
    are the only two studied axes
- Results:
  - the stable prompt x runtime ordering
  - the runtime-only headline result `2/4 -> 4/4`
  - the prompt-only headline contrast from `P0/R0` failure to `P1/R0` and `P2/R0`
    success
  - one compact statement that `P2` reduces planner/tool overhead in the tested
    slices
  - one compact statement that harder tasks increase workload without rank reversal
- Discussion / Limitations:
  - why the findings matter for embodied execution design
  - why runtime validation is a high-leverage design point
  - the explicit controlled-study boundaries
- Conclusion:
  - two or three short paragraphs only

## What should be compressed into tables, figures, or captions

Several modules are scientifically useful but should not remain as full prose
paragraphs in the assembled RA-L body:

- `Table: experimental design summary` should absorb most of the variant inventory:
  `P0`, `P1`, `P2`, `R0`, `R1`, the slice list, and the metric list
- `Table: final closure result summary` should carry the per-family and per-slice
  ordering so the body can avoid restating each cell in full
- `Table: focused ablation summary` can carry the exact prompt-only and runtime-only
  side-by-side numbers if space allows; if the letter is tight, this is the first
  table to drop
- figure captions should carry exact planner/tool call pairs, retry counts, and
  family-level breakdowns that are too detailed for body prose

In practical terms, the current Setup / Study Design draft is the largest compression
opportunity. Most of the long-form definitions of variants, slices, and metrics
should become table content, leaving only the contract definitions needed to
interpret `invalid action`, `recovery`, and the `R1` retry path.

## What can move to appendix or supplementary material

The following content is useful for transparency but not essential to the RA-L body:

- expanded evidence provenance describing the umbrella `block_a_final_closure` source
  and the slice-specific supporting summaries
- the mixed backend-coverage note explaining which slices are Isaac-backed versus
  toy-backed
- full slice-by-slice numeric matrices for planner calls, tool calls, retries, and
  invalid actions
- any longer failure examples or artifact-generation notes
- any extra table that simply reproduces exact per-cell bookkeeping already visible
  in figures

This material should be prepared as appendix or supplementary content rather than
kept inline in the letter body.

## Current draft modules most likely to overrun the page budget

The highest-risk overlength areas in the existing prose drafts are:

1. `setup_and_study_design_draft.md`
   - the Experimental Setup paragraphs on task families, harder-slice taxonomy,
     metrics, and evidence provenance
   - the Study Design paragraphs that define all prompt/runtime variants and then
     restate the analysis-block structure already visible in Results
2. `intro_draft.md`
   - the scope paragraph that names the axes and also lists what the paper does not
     cover
   - the results-preview paragraph, which currently carries more detail than RA-L
     needs before the reader reaches Results
   - the four contribution bullets, which likely need to compress to three shorter
     bullets at assembly time
3. `results_draft.md`
   - the `Cross-family Consistency` subsection, which mostly repeats patterns already
     established in the main effect and ablations
   - the `Harder-task Robustness` subsection, where precise workload deltas are
     likely better placed in a figure/table or caption than in main prose

The second-pass drafts created in this run should stay tight to avoid adding new page
pressure. `related_work_draft.md` should remain a short positioning section,
`discussion_and_limitations_draft.md` should stay below a page in assembled form, and
`conclusion_draft.md` should stay minimal.

## Which numbers should stay in prose versus figures/tables

Keep only the highest-signal numbers in prose:

- runtime-only success `2/4 -> 4/4`
- runtime-only successful recoveries `0 -> 2`
- prompt-only `P0/R0` failure on `0/4` success versus `P1/R0` and `P2/R0` success on
  `4/4`
- at most one explicit efficiency comparison if needed, preferably `7.5/7.5 ->
  6.0/6.0` for the prompt-only `P1` to `P2` change

Prefer figures, tables, or captions for:

- family-specific planner/tool call pairs such as `4.875/4.875 -> 3.875/3.875`,
  `5.0/5.0 -> 4.0/4.0`, and `10.0/10.0 -> 8.0/8.0`
- the harder-navigation exact workload delta `2.931818`
- the harder-manipulation exact `P1` versus `P2` overhead values
- retry totals per slice
- any full per-cell summary already recoverable from `Table: final closure result
  summary`

The merged package totals such as `146` runs and `0.815068` overall success should
stay out of the main prose entirely. If they appear at all, they should be relegated
to bookkeeping or supplementary context rather than used as headline results.

## Recommended trimming order for full draft assembly

1. Compress `setup_and_study_design_draft.md` around a table-driven presentation.
2. Collapse `results_draft.md` cross-family discussion to one short paragraph or fold
   it into the main-effect section.
3. Shorten the Introduction scope paragraph, results preview, and contribution list.
4. Move exact planner/tool call pairs and harder-slice workload deltas into
   figures/tables or captions.
5. Drop `Table: focused ablation summary` first if the letter is still over budget.
6. Keep Related Work, Discussion and Limitations, and Conclusion on strict short-form
   budgets rather than trying to recover pages from Results alone.
