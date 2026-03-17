# RA-L Outline

This is the primary target outline. It follows the RA-L playbook in
`docs/ral_writing_playbook.md`: tight, results-first, double-anonymous, and limited
to Block A.

## Global constraints

- Target a compact 6-8 page letter.
- Keep results as the dominant section.
- Use Block A only.
- Use double-anonymous wording throughout.
- Do not widen the paper to memory, context, tool abstraction, randomization, or broader framework claims.

## 1. Introduction

### 1.1 Problem motivation

Write:

- embodied agents often fail at execution boundaries, not only at high-level planning
- invalid actions, brittle interfaces, and weak runtime handling motivate a controlled study

Do not write:

- a broad "general embodied intelligence" motivation
- a claim that the paper solves embodied planning

### 1.2 Gap and paper type

Write:

- the literature is crowded with agents and benchmarks
- there is still value in a controlled systems study that isolates design choices in Isaac Sim
- the paper studies prompt/interface structure and runtime validation

Do not write:

- a novelty claim built on size, first-ness, or benchmark breadth

### 1.3 Scope and main findings preview

Write:

- navigation and manipulation task families
- prompt variants `P0`, `P1`, `P2`
- runtime variants `R0`, `R1`
- preview the stable ordering and the efficiency role of `P2`

Do not write:

- roadmap items outside Block A

### 1.4 Contribution bullets

Write:

- a compact version of `paper/shared/contributions.md`

Do not write:

- contribution bullets that imply a new model or a full-framework paper

## 2. Related Work

### 2.1 Embodied-agent and benchmark context

Write:

- only enough related work to motivate why a controlled study matters

Do not write:

- a long survey detached from the paper's actual scope

### 2.2 Runtime reliability and execution validation

Write:

- prior interest in reliability, execution, and safety-adjacent runtime checks

Do not write:

- claims that the present runtime layer is a full safety guarantee

### 2.3 Controlled empirical design studies

Write:

- why isolated design-axis studies complement larger benchmarks

Do not write:

- unrelated coverage of memory, tool abstraction, or sim-to-real unless directly needed for positioning

## 3. Experimental Setup

### 3.1 Isaac Sim setting and task families

Write:

- navigation and tabletop manipulation
- controlled simulator setting
- the current easy/shared and harder slices

Do not write:

- the full future project architecture from `plan.md`

### 3.2 Planner/runtime contract

Write:

- typed action or tool-call outputs
- runtime validation path
- retry behavior in `R1`

Do not write:

- unnecessary implementation detail that does not help interpret the results

### 3.3 Metrics and artifacts

Write:

- success
- invalid actions
- retries
- planner calls
- tool calls

Do not write:

- unmeasured metrics or significance language

## 4. Study Design

### 4.1 Prompt/interface variants

Write:

- `P0` minimal direct-action prompt
- `P1` structured tool-call prompt
- `P2` structured tool-call prompt with a brief self-check

Do not write:

- claims that `P2` is universally best

### 4.2 Runtime variants

Write:

- `R0` bare runtime
- `R1` validation plus single retry

Do not write:

- a bigger runtime-policy taxonomy than the evidence supports

### 4.3 Analysis blocks

Write:

- main factorial result
- runtime-only ablation
- prompt-only ablation
- cross-family consistency
- harder-task robustness

Do not write:

- new experiments or unrun ablations

### 4.4 Evidence freeze

Write:

- the primary use of `results/processed/block_a_final_closure/`
- the slice-specific supporting summaries

Do not write:

- stale reliance on the earlier packaged figures/tables as final evidence

## 5. Results

This section should dominate the manuscript.

### 5.1 Main effect: prompt x runtime ordering

Write:

- the stable qualitative ordering
- the fact that `P0/R0` is weakest
- the fact that `P0/R1` recovers
- the fact that `P1/P2` stay strong and `P2` is more efficient than `P1`

Use:

- Figure A
- Table B
- `results/processed/block_a_final_closure/block_a_final_closure_summary.md`

Do not write:

- the merged `0.815068` success rate as the headline scientific message

### 5.2 Runtime-only ablation

Write:

- fixed-`P1` comparison
- `2/4 -> 4/4` success improvement
- recovery rather than invalid-attempt suppression
- family-level replication in navigation and manipulation

Use:

- Figure B
- Table C if space allows
- `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.md`

Do not write:

- a claim that runtime is always more important than prompting

### 5.3 Prompt-only ablation

Write:

- fixed-`R0` comparison
- invalid actions drop from `P0` to `P1/P2`
- `P2` planner/tool efficiency advantage over `P1`

Use:

- Figure B
- Figure C
- Table C if space allows
- `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.md`

Do not write:

- a claim that prompting alone solves all failures

### 5.4 Cross-family consistency

Write:

- the same direction of effects in navigation and manipulation within the covered easy slices and focused ablations

Use:

- Table B or a compact family comparison
- `results/processed/block_a_cross_family_summary/cross_family_summary.json`
- `results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.md`
- `results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.md`

Do not write:

- universal cross-domain generalization claims

### 5.5 Harder-task robustness

Write:

- harder tasks increase planner/tool workload
- the current harder navigation and harder manipulation slices preserve the qualitative ordering

Use:

- Table B
- Figure C
- `results/processed/block_a_master_summary/block_a_master_summary.md`
- `results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.md`

Do not write:

- claims about a broad difficulty benchmark or open-ended long-horizon robustness

## 6. Discussion and Limitations

### 6.1 Design implications

Write:

- structure helps by reducing invalid actions
- lightweight validation helps by recovering fragile runs
- a brief self-check can lower planner/tool overhead in the tested setup

Do not write:

- universal design laws

### 6.2 Explicit boundaries

Write:

- simulator-based controlled setting
- Block A only
- no M7+ axes
- no SOTA claim
- limited backend and task coverage

Do not write:

- softened or hidden caveats

### 6.3 Reviewer-facing honesty

Write:

- the paper aims to establish controlled design lessons, not broad benchmark supremacy

Do not write:

- apologetic language that weakens supported findings

## 7. Conclusion

### 7.1 Short takeaways

Write:

- structure reduces invalid actions
- lightweight validation recovers fragile runs
- a brief self-check lowers planner/tool overhead in the tested setup

Do not write:

- new scope beyond Block A
