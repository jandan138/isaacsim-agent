# RA-L Writing Playbook for This Repo

**Recommended repo path:** `docs/ral_writing_playbook.md`

**Document type:** Internal writing/process note for Codex and human authors.

**Purpose:** This file explains how to turn the existing **Block A** experiments into an **IEEE Robotics and Automation Letters (RA-L)** manuscript. It is not a paper draft. It is the writing playbook that every future paper-writing prompt to Codex should reference.

---

## 0. How this file should be used

For any paper-writing task, Codex should read these files first, in this order:

1. `plan.md`
2. `AGENTS.md`
3. `STATUS.md`
4. `docs/ral_writing_playbook.md` (this file)

Then follow these rules:

- Treat this file as the **paper-writing source of truth** for the current manuscript.
- If `plan.md` still names another venue in an older snapshot, follow the **latest explicit owner instruction** for manuscript drafting and use this file for RA-L-specific writing decisions unless asked to update the plan itself.
- Treat `plan.md` as the broader project source of truth, but **do not force the manuscript to cover all planned milestones**.
- This manuscript is currently scoped to **Block A only**.
- Do **not** start new experiments during paper drafting unless explicitly requested.
- Do **not** make claims beyond the evidence already in the processed results.
- Do **not** write the paper as a “new model” paper or an “overall embodied agent framework” paper.
- Do **not** silently change the venue target in repo metadata unless explicitly asked.

---

## 1. What this paper is, and what it is not

### 1.1 Recommended paper identity

Write this paper as a:

> **controlled systems study of embodied-agent execution design in Isaac Sim**

The core claim is **not** that we built the strongest embodied agent. The core claim is that:

> **prompt/interface structure and lightweight runtime validation have systematic effects on embodied-agent success, invalid actions, retries, and execution efficiency in controlled Isaac Sim tasks.**

This framing is the safest and strongest match to the current evidence.

### 1.2 What the manuscript should cover

The paper should cover **Block A only**:

- prompt variants: `P0`, `P1`, `P2`
- runtime variants: `R0`, `R1`
- task families:
  - navigation
  - manipulation
- difficulty slices:
  - easy/shared slice
  - harder navigation
  - harder manipulation
- analyses:
  - main factorial result
  - prompt-only ablation
  - runtime-only ablation
  - cross-family analysis
  - robustness / harder-task analysis

### 1.3 What the manuscript should *not* claim

Avoid all of the following unless new evidence is added later:

- “state of the art”
- “the first Isaac Sim embodied-agent benchmark”
- “general embodied intelligence”
- “real-world safety”
- “sim-to-real readiness”
- “memory/context/tool abstraction are solved”
- “we evaluate the full design space in the project plan”

This paper should be honest: it is a **well-controlled Block A study**, not the whole long-horizon roadmap.

---

## 2. Evidence base to use in the paper

### 2.1 Primary evidence source

For all final paper numbers, use:

- `results/processed/block_a_final_closure/block_a_final_closure_summary.json`
- `results/processed/block_a_final_closure/block_a_final_closure_summary.csv`
- `results/processed/block_a_final_closure/block_a_final_closure_summary.md`

This is the **current frozen master evidence base** for the manuscript.

### 2.2 Current Block A closure snapshot

At the time this playbook was written, the Block A final closure contains:

- **146 merged runs**
- **119 successes**
- **success rate = 0.815068**
- all six final closure questions evaluate to **yes**

These results integrate:

- navigation expanded
- manipulation pilot
- cross-family summary
- navigation robustness slice
- runtime-only ablation
- prompt-only ablation
- manipulation harder slice

### 2.3 Secondary evidence sources

Use the following only when a subsection needs the slice-specific breakdown:

- `results/processed/block_a_runtime_only_ablation/`
- `results/processed/block_a_prompt_only_ablation/`
- `results/processed/block_a_manipulation_harder/`
- `results/processed/block_a_navigation_prompt_runtime_robustness/`
- `results/processed/block_a_cross_family_summary/`

### 2.4 Important note about earlier paper packaging outputs

Earlier packaging outputs under `results/processed/block_a_master_summary/` were useful for intermediate writing, but they **predate** the final closure additions:

- runtime-only ablation
- prompt-only ablation
- manipulation harder slice

Therefore:

- do **not** treat the earlier packaged tables/figures as the final evidence base
- if paper tables/figures are regenerated, they should be refreshed **from `block_a_final_closure`**

---

## 3. The paper’s core story

### 3.1 One-sentence story

> In a controlled Isaac Sim setting, embodied-agent reliability depends strongly on prompt/interface structure and runtime validation, and these effects hold across navigation and manipulation as tasks become harder.

### 3.2 Main empirical findings to foreground

The paper should revolve around these findings:

1. **`P0/R0` is consistently the weakest condition.**
   Unstructured or minimally structured prompting without runtime checking leads to the highest invalid-action failures.

2. **`P0/R1` recovers reliably.**
   A lightweight runtime layer with validation and a single retry can convert fragile executions into successful ones.

3. **`P1` and `P2` are consistently strong.**
   Structured tool-oriented prompting sharply reduces invalid actions and removes the need for retries in the tested settings.

4. **`P2` is more efficient than `P1`.**
   Adding a brief self-check preserves success while reducing planner/tool calls.

5. **The ordering is stable across task families and harder tasks.**
   Harder tasks increase workload and cost, but do not change the qualitative ranking of conditions.

### 3.3 Suggested interpretation

The paper should interpret the above as:

- **interface structure matters** because it reduces invalid actions
- **runtime validation matters** because it repairs fragile action generation
- **brief self-check can improve execution efficiency** without needing a more complex runtime

---

## 4. Exact paper framing to use

### 4.1 Strong framing

Use wording close to:

> We present a controlled study of two embodied-agent design dimensions in Isaac Sim: prompt/interface structure and lightweight runtime validation. Across navigation and manipulation tasks, we measure how these choices affect success, invalid actions, retries, and planner/tool overhead.

### 4.2 Weak framing to avoid

Do **not** write the paper as:

- “we introduce a complete embodied-agent framework covering prompting, context, memory, tools, and runtime policies”
- “we solve embodied planning in Isaac Sim”
- “we benchmark many models across many environments”
- “we present a general-purpose embodied-agent architecture”

Those framings are larger than the current evidence and will make the paper easier to attack.

### 4.3 Best paper type label

If you need a concise identity sentence, use:

> **a controlled empirical study of system-design choices for embodied-agent execution**

---

## 5. RA-L constraints that matter for writing

These venue facts were checked against official IEEE RAS / RA-L pages:

- RA-L letters are **6 pages in letters format**, with **up to 2 extra pages for a fee**, for a practical maximum of **8 pages**.
- RA-L uses **double-anonymous review** and submissions must follow the RAS double-anonymous rules.
- RA-L does **not** allow simultaneous submission of the same paper to a conference.
- Accepted RA-L papers may later be **transferred for presentation** to certain RAS conferences within the allowed transfer window.
- RA-L emphasizes rapid decisions/publication, and the FAQ states that accepted papers are guaranteed online publication within **6 months**.

Practical consequences for this manuscript:

- The paper must be **tight**.
- The paper should contain only the highest-value figures/tables.
- The writing must be **results-first**.
- All manuscript drafts must be checked for **double-anonymous compliance**.

See the official pages listed in [Appendix A](#appendix-a-official-r-a-l-links).

---

## 6. Recommended paper structure

The manuscript should be written as a compact 6–8 page RA-L letter.

### 6.1 Suggested section order

1. **Introduction**
2. **Related Work**
3. **Experimental Setup**
4. **Study Design**
5. **Results**
6. **Discussion and Limitations**
7. **Conclusion**

### 6.2 Suggested page budget

A good 8-page target is:

- Introduction: **0.8–1.0 pages**
- Related Work: **0.5–0.7 pages**
- Experimental Setup: **0.6–0.8 pages**
- Study Design: **0.6–0.8 pages**
- Results: **2.8–3.4 pages**
- Discussion + Limitations: **0.5–0.8 pages**
- Conclusion: **0.2–0.3 pages**

Results should dominate the manuscript.

---

## 7. Section-by-section writing plan

### 7.1 Introduction

The introduction should do four jobs:

1. **Motivate the problem**
   Embodied agents fail not only because of high-level planning, but also because of invalid actions, weak execution interfaces, and brittle runtime control.

2. **State the gap**
   The literature is crowded with agents and benchmarks, but there is still room for controlled studies that isolate how **system design** choices affect embodied execution.

3. **State the method**
   This paper fixes the simulator setting and task families, and systematically varies prompt/interface structure and runtime validation.

4. **State the findings**
   Summarize the main effects directly: `P0/R0` fails, `P0/R1` recovers, `P1/P2` succeed, `P2` is cheaper, and the effects hold across task families and harder tasks.

### 7.2 Related Work

Keep related work short and purposeful. Cover only these themes:

- embodied / language-conditioned agent systems
- robotics runtime safety / validation / execution reliability
- controlled design studies or ablations in embodied settings

The goal of related work is not breadth. The goal is to justify why a **controlled systems study** matters.

### 7.3 Experimental Setup

This section should define the environment and measurement apparatus:

- Isaac Sim setting
- navigation and manipulation task families
- easy vs harder slices
- unified contracts / artifacts / metrics
- structured planner outputs
- runtime validation and dispatch path

Do not describe the full project roadmap here.

### 7.4 Study Design

This section defines the experimental variables.

Use a compact table to define:

- `P0`: direct / minimal action prompting
- `P1`: structured tool call
- `P2`: structured tool call + brief self-check
- `R0`: no validation, no retry
- `R1`: validation + single retry

Then explain the four analysis blocks:

- main factorial result
- runtime-only ablation
- prompt-only ablation
- cross-task / harder-task robustness

### 7.5 Results

This is the core section. Organize by research question, not by implementation order.

Recommended subsections:

#### 5.1 Main effect: Prompt × Runtime
Use the final closure summary to show the overall condition ordering.

#### 5.2 Runtime-only ablation
Show whether runtime validation has independent value when prompt structure is fixed.

#### 5.3 Prompt-only ablation
Show whether prompt structure has independent value when runtime policy is fixed.

#### 5.4 Cross-family consistency
Compare navigation and manipulation directly.

#### 5.5 Harder-task robustness
Show that harder tasks raise cost but preserve ranking.

### 7.6 Discussion and Limitations

This section is essential. It should explicitly state:

- the study is controlled and simulator-based
- the paper does not claim SOTA embodied intelligence
- the study does not cover memory/context/tool abstraction/randomization
- the planner backend is designed to isolate system variables, not to maximize benchmark score
- the conclusions support **design principles under controlled conditions**

### 7.7 Conclusion

Keep the conclusion short. Re-state the three strongest takeaways:

- structure reduces invalid actions
- lightweight validation recovers fragile runs
- brief self-check reduces execution overhead

---

## 8. What figures and tables to include

### 8.1 Essential figures

Include at most four figures.

#### Figure 1 — System diagram
A single pipeline diagram:

`Task/State -> Planner input -> Structured action -> Runtime validation -> Tool dispatch -> Logged artifacts`

This figure helps frame the paper as a systems study.

#### Figure 2 — Main success-rate figure
Show success rate for all six conditions:

- `P0/R0`
- `P0/R1`
- `P1/R0`
- `P1/R1`
- `P2/R0`
- `P2/R1`

Split or color by task family.

#### Figure 3 — Invalid actions / retries
Show why `R1` matters and where failures come from.

#### Figure 4 — Planner/tool cost
Show that `P2` achieves lower planner/tool calls than `P1`.

### 8.2 Essential tables

#### Table 1 — Experimental design summary
Include:

- task families
- slices
- number of tasks
- number of runs

#### Table 2 — Final closure summary
A compact table with grouped results by:

- task family
- difficulty
- prompt variant
- runtime variant

Include:

- run count
- success rate
- invalid actions
- retries
- planner calls
- tool calls

Optional if space permits:

#### Table 3 — Prompt-only and runtime-only ablation summary

---

## 9. Writing guardrails for Codex

Every paper-writing prompt to Codex should enforce these rules.

### 9.1 Always do

- always read `plan.md`, `AGENTS.md`, `STATUS.md`, and this file first
- always derive numbers from the processed summaries, not from memory
- always preserve double-anonymous wording in the manuscript draft
- always keep the paper focused on Block A only
- always distinguish between **main evidence** and **supporting slice-specific evidence**
- always write limitations explicitly

### 9.2 Never do

- never start new experiments unless explicitly requested
- never widen the manuscript to context, memory, tool abstraction, or randomization
- never call the paper a full embodied-agent framework paper
- never claim real-world transfer
- never imply that all roadmap dimensions were completed
- never invent numbers, significance claims, or failure categories
- never use stale tables/figures from pre-final-closure packaging without checking them against `block_a_final_closure`

### 9.3 Terminology to keep stable

Use these terms consistently:

- **prompt/interface structure**
- **runtime validation**
- **invalid actions**
- **single retry**
- **planner/tool calls**
- **task families**
- **harder tasks**
- **controlled study**
- **design principles**

Avoid drifting into unstable synonyms unless there is a good reason.

---

## 10. Claims that are safe vs risky

### 10.1 Safe claims

These are supported by current evidence:

- structured prompting reduces invalid actions relative to the weakest prompt condition
- lightweight runtime validation plus a single retry improves reliability for fragile executions
- brief self-check reduces planner/tool overhead relative to the structured baseline
- these trends hold across navigation and manipulation in the tested Isaac Sim setup
- harder tasks raise workload without changing the ordering of conditions in the tested setup

### 10.2 Risky claims

These need to be avoided or heavily qualified:

- these results generalize to all embodied agents
- these results prove real-robot benefits
- runtime is always more important than prompting
- prompting is always more important than runtime
- `P2` is universally optimal
- the conclusions extend to context, memory, or tool abstraction

---

## 11. Best writing workflow from here

### 11.1 Recommended drafting order

Do **not** start with the introduction.

Write in this order:

1. Results
2. Study Design
3. Experimental Setup
4. Discussion and Limitations
5. Introduction
6. Related Work
7. Abstract
8. Title

This is the fastest way to stay grounded in the actual evidence.

### 11.2 Suggested deliverable order for Codex

1. `paper/sections/results.tex`
2. `paper/sections/study_design.tex`
3. `paper/sections/experimental_setup.tex`
4. `paper/sections/discussion.tex`
5. `paper/sections/introduction.tex`
6. `paper/sections/related_work.tex`
7. `paper/abstract.md`
8. `paper/title_options.md`

### 11.3 Per-step validation rule

For each writing step, Codex should:

- name the exact processed summaries it used
- list the exact figures/tables it consumed
- list any still-open writing ambiguity
- avoid changing scientific claims outside the evidence

---

## 12. Copy-paste prompt preamble for future Codex writing tasks

Use the following preamble in every paper-writing prompt:

```text
Before doing any paper-writing work, read these files in order:
1. plan.md
2. AGENTS.md
3. STATUS.md
4. docs/ral_writing_playbook.md

Treat docs/ral_writing_playbook.md as the paper-writing source of truth.
This manuscript is Block A only.
Do not start new experiments.
Do not widen scope to memory, context, tool abstraction, randomization, or other future milestones.
Use only processed results already present in results/processed/.
Use block_a_final_closure as the primary evidence base unless the requested subsection explicitly needs a slice-specific summary.
Preserve double-anonymous wording.
Do not invent numbers or claims.
```

---

## 13. A practical checklist before submission drafting starts

Before asking Codex to write the full paper, verify these items manually:

- [ ] `block_a_final_closure_summary.{json,csv,md}` exists and is the intended final evidence base
- [ ] any new paper tables/figures have been regenerated from final closure, not older packaging
- [ ] all figure captions and table captions are anonymous
- [ ] the manuscript scope is explicitly Block A only
- [ ] the current title, abstract, and contributions do not over-claim beyond Block A
- [ ] limitations are explicit
- [ ] no concurrent conference submission plan conflicts with RA-L policy

---

## 14. Recommended next writing actions

The next paper-writing tasks should be:

1. draft a title shortlist
2. draft the abstract
3. draft the contributions list
4. write Results first from final closure
5. build the rest of the paper around the results

If space becomes tight, cut background and implementation detail **before** cutting results or limitations.

---

## Appendix A: Official R-A-L links

These were consulted when preparing this playbook and should be re-checked before submission in case IEEE updates policies.

- RA-L FAQ: <https://www.ieee-ras.org/publications/ra-l/faq>
- RA-L submission procedures: <https://www.ieee-ras.org/publications/ra-l/submission-procedures>
- RA-L page: <https://www.ieee-ras.org/publications/ra-l>
- RA-L final submission checklist: <https://www.ieee-ras.org/publications/ra-l/final-submission-checklist>
- IEEE RAS publications overview / double-anonymous links: <https://www.ieee-ras.org/publications/t-ro/information-for-authors>

