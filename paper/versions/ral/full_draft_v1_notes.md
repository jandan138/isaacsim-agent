# Full Draft Assembly v1 Notes

## Base Selection

- Title base: candidate A1 from `title_candidates.md`, lightly tightened to
  `A Controlled Study of Planner-to-Executor Contracts and Runtime Validation
  for Embodied-Agent Execution in Isaac Sim` so the main axis stays explicit
  while the title reads slightly shorter.
- Abstract base: version A from `abstract_candidates.md`, with one selective
  import from version B so the abstract names the two independent ablations
  (`4/4` action-interface contrast and `2/4 -> 4/4` runtime-only contrast)
  without turning the opening into a stronger causal claim.

## Major Merge and Deletion Decisions

- Moved the full `P0/P1/P2` and `R0/R1` explanation into Section 3, so the
  introduction previews the matrix once and the results section does not
  redefine every variant.
- Folded cross-family consistency into the ending of the main-effect subsection
  instead of keeping a separate cross-family section.
- Kept the concrete `move_to_goal` / `move_object` failure example only in the
  ablation subsection; discussion and conclusion now keep the architectural
  lesson without repeating the log-level example.
- Added one explicit sentence that the runtime-only and action-interface
  ablations use different easy-task subsets, resolving the apparent tension
  between `P1` invalid actions in the runtime-only slice and zero invalid
  actions for `P1/R0` in the fixed-`R0` slice.
- Removed repeated scope-defense phrasing from setup/results/conclusion and kept
  the bounded-scope statement in the introduction plus the limitations
  subsection only.

## Page-Pressure Compression

- Kept the variant inventory table-driven through
  `[Table: experimental design summary]` rather than expanding each variant into
  a separate paragraph block.
- Collapsed setup and study design into one section, then kept results to three
  subsections: main contract x runtime effect, targeted ablations, and
  harder-task robustness.
- Compressed cross-family and harder-task detail to qualitative ordering plus a
  few headline numbers, rather than repeating per-family bookkeeping already
  destined for figures or tables.
- Left the merged final-closure success total out of headline prose so the
  manuscript does not read like package bookkeeping.
- Kept failure-case analysis to one compact paragraph rather than expanding it
  into a trace-by-trace report.
- Retained `[Table: focused ablation summary]` only as a placeholder; it is not
  duplicated with long prose and remains the first table to drop if a later
  page-budget pass needs room.

## Assembly-Stage Placeholder Retention

- The initial assembly pass kept placeholder citations `[RW1]` through `[RW17]`
  in Related Work only; the later citation-grounding pass removed them.
- Kept the figure/table planning markers `[Fig: main condition ordering]`,
  `[Fig: invalid actions and recovery]`, `[Fig: planner/tool overhead]`,
  `[Table: experimental design summary]`,
  `[Table: final closure result summary]`, and
  `[Table: focused ablation summary]`.
- Did not add final numbering, caption prose, or LaTeX cross-references in this
  assembly pass.

## Claim Tightening

- `P2` is described as associated with lower planner/tool overhead in the
  covered comparisons, not as a broad efficiency improvement.
- `R1` is described as recovering recoverable invalid-first-action runs, not as
  a general replacement for a well-specified interface.
- Harder-task language is limited to cost amplification without rank reversal in
  the current slices.
- The assembled paper-facing prose avoids `Block A`, package-closing rhetoric,
  and raw debug-style totals except where a compact ablation contrast is doing
  real argumentative work.

## Citation Grounding and Light Polish Pass

- Replaced all former `[RW1]` through `[RW17]` placeholders in the mother draft
  and the related-work source fragment with verified references from arXiv,
  `design.ros2.org`, `behaviortree.dev`, and official publication pages.
- Kept the embodied-planning cluster centered on Inner Monologue, PaLM-E,
  RT-2, VoxPoser, OK-Robot, SayCan, Code as Policies, and ProgPrompt so the
  literature coverage stays robotics-facing without sliding back into
  prompt-engineering framing.
- Chose ROS 2 architecture and actions references, PlanSys2, Behavior Trees in
  Robotics and AI, BehaviorTree.CPP, PDDLStream, and the integrated TAMP
  survey because they directly support the paper's contract / interface /
  runtime-validation story.
- Reframed the final related-work subsection around broader embodied
  evaluations, using EmbodiedBench, IS-Bench, and Mind and Motion Aligned to
  position the paper as a controlled study that complements, rather than tries
  to out-scale, benchmark-style work.

## Light Polish Decisions

- Abstract compression strategy:
  kept both ablation contrasts (`4/4` contract effect and `2/4 -> 4/4`
  runtime-only recovery effect), removed one redundant qualifier, and replaced
  `frozen study package` with `broader evaluation slices` so the abstract stays
  under the RA-L target without strengthening the claim.
- Section 4.1 cleanup:
  deleted the meta-commentary clause that labeled one pattern as `the paper's
  core empirical result` and left only the empirical pattern statement.
- Section 3.3 wording:
  renamed the subsection to `Metrics and Evaluation Protocol` and replaced
  `evidence freeze` / `frozen package` language with neutral evaluation wording.
- Discussion architectural mapping:
  added a short three-sentence bridge from the paper's contract/validation
  framing to ROS 2 goal-feedback-result semantics, behavior-tree precondition
  and execution guards, and TAMP operator signatures plus grounding interfaces.
- Bibliography preparation:
  added `bibliography_candidates.md` as a grouped reference list for the later
  LaTeX / BibTeX pass without attempting final bibliography formatting yet.

## Compiled-Draft Cleanup Pass

- Normalized the current LaTeX scaffold from the former references-note
  placeholder to a real BibTeX-backed bibliography flow.
- Kept the citation cleanup conservative: Related Work and Discussion now use
  `\cite{}` commands, while the manuscript structure and findings wording stay
  otherwise intact.
- Removed the focused ablation table from the current main-text float stack and
  left it as the first support/overflow asset to restore only if authors later
  decide the page budget allows it.

## Submission-Polish Pass

- Tightened the active LaTeX draft at the sentence level without changing the
  paper's findings, framing, or result ordering.
- Normalized the last local wording drift toward the shared terminology:
  `runtime validation policy` and `action-interface ablation` now replace the
  remaining older labels in the active `.tex` files.
- Upgraded the bibliography from a merely working BibTeX file to a more
  submission-facing one:
  - fuller author metadata for the cited embodied-planning references
  - verified venue / DOI / page fields where safely confirmed
  - title-case protection for terms that IEEEtran would otherwise downcase
  - an official Isaac Sim documentation citation
- Kept the current main-text asset set unchanged:
  `main_condition_ordering`, `invalid_actions_recovery`,
  `planner_tool_overhead`, `experimental_design_summary`, and
  `final_closure_result_summary`.
- Kept `focused_ablation_summary` and `harder_task_summary` support-only rather
  than reintroducing them into the letter.
- Audited the optional system diagram and recorded a `defer` recommendation:
  the present manuscript is self-contained, and adding another full-width
  figure would likely displace a more important result asset or worsen float
  delay.
