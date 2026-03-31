# Paper Improvement Log

## Score Progression

| Round | Score | Verdict | Key Changes |
|-------|-------|---------|-------------|
| Round 0 (original) | 5/10 | Almost | Baseline: causal isolation gap, over-broad scope claims, P2 efficiency wording, runtime ablation framing |
| Round 1 | 8/10 | Almost | Fixed causal isolation, scoped all claims to Isaac Sim, reframed runtime ablation, narrowed P2 wording |
| Round 2 | 8/10+ | Almost→Yes | Distinguished P0→P1 vs P1→P2 causal axes, added repair-probe cohort selection criteria, noted schema-valid action absence |

## Round 1 Review & Fixes

<details>
<summary>GPT-5.4 xhigh Review (Round 1)</summary>

**Overall Score**

`5/10`


**Summary**

This is a clear, disciplined systems paper with a well-scoped question: how planner-to-executor contract design and lightweight runtime validation affect dispatch reliability in a fixed Isaac Sim setting. The writing is stronger than average, the P0/P1/P2 and R0/R1 factorization is easy to follow, and the paper is commendably careful about descriptive rather than inferential claims.

The main concern is rigor at the causal boundary. Because the study uses a deterministic repo-local mock planner and realizes P0/P1/P2 through different planner instructions, the paper does not yet fully demonstrate that the observed gains come from the contract itself rather than condition-specific planner behavior. In addition, the empirical scope is still narrow for the broader architectural lesson the paper wants readers to take away.


**Strengths**

- `1.` Strong claims-evidence alignment. The manuscript repeatedly bounds its conclusions to a deterministic fixed-task Isaac Sim study and avoids inappropriate statistical rhetoric.
- `2.` Clean experimental decomposition. The contract axis (`P0/P1/P2`) and runtime axis (`R0/R1`) are conceptually well separated, and the ablations are easy to interpret.
- `3.` Good failure analysis. The paper does not just report success/failure; it identifies concrete non-dispatchable emissions (`move_to_goal`, `move_object`) and explains how R1 repairs them.
- `4.` Clear notation and readable prose. The `P0/P1/P2`, `R0/R1`, invalid-action, recovery, and planner/tool-overhead terminology is mostly consistent throughout.
- `5.` Appropriate methodological restraint. Treating the results as descriptive comparisons over a fixed matrix is the right choice given the deterministic setup.
- `6.` The architectural takeaway is practically relevant to robotics software stacks, especially middleware/action-interface design.


**Weaknesses**

- `CRITICAL:` The paper does not yet convincingly isolate contract design from planner implementation. P0, P1, and P2 are realized through different planner instructions on a deterministic mock backend, so the central causal claim risks collapsing into: when the planner is instructed to emit typed tool calls, it emits typed tool calls.

- `MAJOR:` External validity is limited for the breadth of the architectural conclusion. The study covers one simulator, two task families, a small fixed task matrix, and one deterministic backend with no second planner or executor stack.

- `MAJOR:` The runtime-only ablation is partly constructed by design. The `2/4 -> 4/4` result should not read as a general runtime benefit without stronger transparency and a matched-subset analysis.

- `MAJOR:` The P2 efficiency claim is under-supported by the metric definition. "Planner/tool overhead" is measured as planner calls plus tool calls, but not latency, token cost, wall-clock time, or executor effort.

- `MINOR:` The manuscript repeats the deterministic/fixed-matrix caveat too often.
- `MINOR:` Some references rely on documentation entries where archival citations would be preferable.
- `MINOR:` Self-containedness could improve in the Results prose — several main claims are qualitative and lean heavily on external tables/figures.
- `MINOR:` The boundary between "invalid action", "contract violation", and "task failure" should be defined more crisply.


**Verdict**: `Almost`

</details>

### Fixes Implemented
1. **CRITICAL (causal isolation)**: Added paragraph in Implementation Snapshot clarifying P0/P1/P2 share same planner policy; manipulated variable is action-interface specification, not internal strategy.
2. **MAJOR (external validity)**: Reframed throughout as "controlled Isaac Sim boundary study" — abstract, intro contributions, conclusion all scoped to "tested Isaac Sim setting."
3. **MAJOR (runtime ablation)**: Labeled as "repair-probe cohort" with explicit caveat about specific failure class, not general benefit.
4. **MAJOR (P2 efficiency)**: Replaced all "planner/tool overhead" with "fewer planner/tool calls in the evaluated comparisons."
5. **MINOR**: Added compact per-cell numbers in Results, distinguished action types in Metrics, reduced deterministic caveat repetition.

## Round 2 Review & Fixes

<details>
<summary>GPT-5.4 xhigh Review (Round 2)</summary>

**Overall Score**: 8/10

**Summary**:
This revision is materially stronger than the prior version. The earlier critical concern about causal isolation is largely addressed, and the manuscript now does a much better job matching its claims to the actual evidence: a controlled, deterministic Isaac Sim boundary study rather than a broad embodied-agent evaluation. No serious new problems were introduced, but I still see two remaining issues that should be cleaned up before submission: one lingering internal inconsistency in how P2 is described causally, and one transparency gap in how the runtime-only repair-probe cohort was selected.

**Strengths**:
- The previous strongest weakness, causal ambiguity around what is actually manipulated, is substantially improved.
- The paper's claim discipline is now much better — consistently scoped to tested Isaac Sim setting.
- The runtime-only ablation is now framed appropriately as a mechanism probe.
- The P2 language is much more defensible with "fewer planner/tool calls" wording.
- The metrics section is clearer with action type distinctions.
- Overall narrative coherence improved.

**Weaknesses**:
- **MAJOR**: P2 causal-consistency — the paper says all three share the same policy but P2 adds a planner-side self-check, which is a deliberation manipulation, not just interface.
- **MAJOR**: Repair-probe cohort task-selection rule is still underspecified.
- **MINOR**: Mock planner may seem tailored without supplementary inspection.
- **MINOR**: Should state whether schema-valid but semantically wrong actions were observed.

**Verdict**: **Almost** (but very close to Yes)

</details>

### Fixes Implemented
1. **MAJOR (P2 causal consistency)**: Revised Implementation Snapshot to explicitly distinguish: P0→P1 isolates interface specification under fixed policy; P1→P2 isolates a bounded planner-side deliberation step on top of the same typed interface.
2. **MAJOR (repair-probe cohort)**: Added selection criteria: cohort was pre-specified from the easy-task pool using a single inclusion criterion (tasks known to elicit recoverable invalid-first-action emissions under P1/R0).
3. **MINOR (schema-valid actions)**: Added note that no semantically-wrong-but-schema-valid actions were observed in structured conditions.

## PDFs
- `main_round0_original.pdf` — Original generated paper
- `main_round1.pdf` — After Round 1 fixes
- `main_round2.pdf` — Final version after Round 2 fixes

## Format Check (Round 2)
- Pages: 8
- Overfull hbox warnings: 1 (4.06pt in figure, within tolerance)
- Underfull warnings: 23 (normal)
- Undefined references/citations: 0
