# Auto Review Log

## Round 3 (2026-04-04)

### Assessment (Summary)
- Score: 7.5/10 → 8.0/10 (after fixes)
- Verdict: Almost → Almost (close to Yes)
- Reviewer: GPT-5.4 via Codex CLI (xhigh reasoning)

### Key Changes Made (Round 3)

**Framing overhaul (Isaac Sim overclaim fix):**
1. Title: "...in Isaac Sim" → "...in a Lightweight Simulator Setup"
2. Abstract: added backend composition disclosure + mock planner variance isolation sentence
3. Intro: softened all "Isaac Sim" exclusive references
4. Setup §3.1: renamed to "Controlled Simulator Setting", added two-backend disclosure (primary lightweight Python, secondary minimal Isaac Sim on 2 nav instances)
5. Setup §3.3: added "injected boundary probes" paragraph for P0
6. Related work: "fixed Isaac Sim setting" → "fixed simulator setting" (2 locations)
7. Discussion/Limitations: honest backend composition + mock planner disclosure + LLM future work
8. Conclusion: reframed to "controlled simulator boundary study"
9. Fig 1 caption: "Isaac Sim executor" → "lightweight deterministic backend... with minimal Isaac Sim slice"
10. reviewer_submission/main.tex: title synced

**Results additions:**
11. New "Isaac Sim validation slice" paragraph confirming same ordering under physics-backed execution
12. P0 failure trace: added boundary-probe reminder
13. P2 efficiency: added disclaimer that call counts are not latency/wall-clock

**Bug fixes:**
14. `\\emph` → `\emph` (double-escape typo in setup.tex)
15. "all failures were task-complete successes" → "all runs reached task-complete success"

**Internal docs:**
16. core_claim.md, limitations.md updated to match new framing

### Round 3a Review (GPT-5.4 xhigh)

<details>
<summary>Click to expand full reviewer response</summary>

**Score**: 7.5/10

**Isaac Sim overclaim**: mostly fixed in main section prose, but not fully fixed in submission package. reviewer_submission/main.tex still had old title, fig1 caption still said "Isaac Sim executor", related_work still said "fixed Isaac Sim setting".

**Mock planner circularity**: largely fixed as transparency problem. Setup now explicitly states deterministic mock planner, injected boundary probes, and P0→P1 vs P1→P2 causal split. Limitations language is honest. No longer hidden circularity. Still a major limitation that main effect is demonstrated on designed boundary probes.

**Remaining weaknesses**:
1. CRITICAL: reviewer-visible package internally inconsistent (old title in reviewer_submission, fig1, related_work)
2. MAJOR: Isaac Sim validation slice not shown in Results
3. MAJOR: engineered probes limit scientific reach
4. MAJOR: physics-backed evidence too thin for broad architecture language
5. MINOR: P2 efficiency only call counts, not real efficiency
6. MINOR: shared authoring guides still had old Isaac Sim identity

**Verdict**: Almost

</details>

### Round 3b Verification Review (GPT-5.4 xhigh)

<details>
<summary>Click to expand full reviewer response</summary>

**Score**: 8.0/10

All seven Round 3 issues resolved. The title is fixed in reviewer_submission/main.tex. Fig 1 caption fixed. Related work corrected. Isaac Sim validation slice now appears in Results. P0 boundary-probe reminder present. Efficiency-proxy disclaimer present. Shared files aligned.

Internal consistency: materially yes. No remaining Isaac Sim overclaim of the kind flagged in Round 3.

New issues found:
1. `\\emph` typesetting regression in setup.tex lines 71, 77 → FIXED
2. Contradictory "failures were task-complete successes" in setup.tex line 124 → FIXED

**Verdict**: Almost. Scientific positioning is submission-grade. Local regressions cleaned up.

</details>

### Status
- Round 3 complete
- Score progression: 5/10 → 8/10 → 8/10+ → 7.5/10 → 8.0/10

---

## Round 4 (2026-04-04)

### Assessment
- Score: 8.2/10
- Verdict: Almost
- Reviewer: GPT-5.4 via Codex CLI (xhigh)

### Fixes Applied
1. **MAJOR**: "validates/confirms" → "limited qualitative cross-backend check" (abstract, setup, results, conclusion, fig1)
2. **MAJOR**: repair-probe cohort fixed ("two navigation and two tabletop-manipulation tasks")
3. **MINOR**: deterministic caveat compressed in abstract/conclusion
4. **MINOR**: contribution 1 split into two sentences
5. **MINOR**: failure-trace paragraph tightened
6. **MINOR**: ROS/BT analogy split for readability
7. **MINOR**: title shortened to colon format
8. **NITPICK**: "across...across" → "in both"; passive → active

---

## Round 5 (2026-04-04)

### Assessment
- Score: 8.4/10
- Verdict: Almost

### Fixes Applied
1. discussion.tex: "confirming..." → "limited qualitative cross-backend check"
2. intro.tex: "for validation" → "for qualitative cross-backend checking"
3. results.tex: "validation slice" → "cross-backend check"

---

## Round 6 — FINAL (2026-04-04)

### Assessment
- Score: **8.6/10**
- Verdict: **Yes — READY for submission**
- Isaac Sim caveat fully normalized: Yes
- Remaining reviewer flags: None (narrow scope is honestly framed as limitation)

### Score Progression
5/10 → 8/10 → 8/10+ → 7.5 → 8.0 → 8.2 → 8.4 → **8.6**

### Status: COMPLETE
- Paper compiles to 8 pages
- All sections internally consistent
- No remaining Isaac Sim overclaim
- Mock planner / boundary-probe nature fully disclosed
- Submission-ready

## Method Description

This paper studies the planner-to-executor execution boundary in embodied-agent systems using a controlled factorial design. The architecture has three components: (1) a deterministic mock planner that emits JSON action requests under three contract variants (P0: under-specified direct-action, P1: typed tool-call, P2: typed + self-check), (2) a runtime layer that either dispatches bare (R0) or validates-and-retries once (R1), and (3) a task executor exposing typed tool primitives for navigation and manipulation. The main evaluation runs on a lightweight deterministic Python backend, with a minimal Isaac Sim slice for cross-backend validation.
