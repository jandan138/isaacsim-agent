# plan.md

## Project
**Paper title (working):** System Design and Evaluation of Embodied Agents in NVIDIA Isaac Sim: A Study of Prompting, Context, Memory, Tool Use, and Runtime Policies

**Target venue:** IEEE Access  
**Primary execution agent:** Codex  
**Primary simulator:** NVIDIA Isaac Sim  
**Primary language:** Python  
**Document purpose:** This file is the source of truth for building the codebase, running experiments, analyzing results, and drafting the paper. Codex should follow this file milestone by milestone.

---

## 0. Executive Decision

### 0.1 Go / No-Go
**Go**, but only with a controlled scope.

This paper is feasible **if** we frame it as a **system design + controlled ablation study** rather than a claim of a brand-new foundation model, a massive benchmark, or a full sim-to-real paper.

### 0.2 Recommended paper claim
> We present a modular embodied-agent framework for NVIDIA Isaac Sim and systematically study how prompting, context management, memory, tool abstraction, and runtime policies affect task success, efficiency, and robustness.

### 0.3 Scope freeze
This project **must not** try to do all of the following at once:
- no fine-tuning of a frontier model in the main paper
- no sim-to-real transfer claims in the main paper
- no multi-robot / multi-agent paper in v1
- no “first ever” claims unless explicitly validated by a fresh literature review at writing time
- no giant cross-simulator benchmark

### 0.4 Minimum publishable unit (MPU)
The smallest publishable version is:
- 2 task families
  - mobile navigation
  - tabletop pick-and-place
- 4 design dimensions
  - prompting
  - context
  - memory
  - runtime policy
- 1 primary model backend
- 1 optional cheaper / weaker comparison backend
- 1 reproducible evaluation harness
- at least 3 main tables + 4 figures + 1 failure analysis section

### 0.5 Stretch goals (only after MPU succeeds)
- add a skill abstraction comparison (primitive tools vs composed skills)
- add Replicator-driven domain randomization
- add safety / risk metrics
- add optional RAG from task manuals or scene metadata
- add IEEE Access supplemental video

---

## 1. Validated External Constraints and Why This Project Is Feasible

### 1.1 Isaac Sim feasibility
Isaac Sim is a high-fidelity robotics simulator and an extensible OpenUSD-based framework for simulating and testing AI-driven robotics in physically based virtual environments. It supports:
- mobile robot navigation workflows via ROS 2 / Nav2
- manipulation examples with Franka and UR10
- camera, depth, RTX lidar, contact, IMU, and other sensors
- Replicator workflows for synthetic data generation and domain randomization
- extension-based Python APIs and standalone workflows

### 1.2 Hardware / OS feasibility constraints
Use these as hard planning constraints:
- x86_64 minimum spec includes Ubuntu 22.04/24.04 or Windows 10/11, 32GB RAM, RTX 4080-class GPU, and 16GB VRAM minimum
- GPUs without RT Cores (e.g. A100/H100) are not supported
- complex scenes with many sensors can exceed 16GB VRAM
- the Isaac Sim container is Linux-only
- ROS 2 launch support for Isaac Sim is Linux-only

**Implication:** The safest environment for this project is **Linux + RTX GPU + at least 16GB VRAM**, ideally with more memory if we run multiple sensors or heavier scenes.

### 1.3 Publication feasibility for IEEE Access
IEEE Access is compatible with a system-paper framing. The key constraints we must satisfy are:
- original writing that adds knowledge to the field
- technically sound experiments and analyses
- conclusions clearly supported by data
- appropriate related work coverage
- manuscript prepared in the required IEEE Access template
- both Word/LaTeX and matching PDF are required at submission
- no page limit, but under 20 pages is strongly recommended
- supplemental material (code, data, video) is allowed

**Implication:** A strong system study with rigorous experiments, good ablations, and reproducible artifacts is a credible IEEE Access submission.

### 1.4 Codex workflow feasibility
Codex is suitable for this project because it can read, edit, and run code, and its workflow can be improved with:
- `AGENTS.md` for repo-level guidance
- skills for reusable workflows
- plan-driven execution for long-horizon tasks
- optional MCP integration if needed later

**Implication:** Codex should be treated as the execution agent for engineering, analysis, and paper drafting, but the paper itself must remain about the embodied agent framework, not about Codex.

---

## 2. Literature-Grounded Positioning

### 2.1 What recent work already covers
The project must explicitly acknowledge that the space is getting crowded:

1. **EmbodiedBench (2025)** evaluates multimodal embodied agents across four environments, 1,128 tasks, and six capability subsets. It shows strong models still struggle badly on low-level manipulation.
2. **FindingDory (2025)** focuses specifically on long-horizon memory in embodied agents.
3. **IS-Bench (2025)** focuses on interactive safety in embodied household tasks.
4. **Kitchen-R / Mind and Motion Aligned (2025)** is directly relevant because it is Isaac-Sim-based and jointly evaluates task planning and low-level control in mobile manipulation.

### 2.2 What gap we should target
Our paper **should not** try to compete with these by being bigger. Instead, we should target this gap:

> There is still room for a focused, reproducible **system design study** in Isaac Sim that isolates runtime design choices—prompting, context compression, memory, tool abstraction, retry/validation/fallback, and caching—and measures their effects on success, latency, and robustness.

### 2.3 Safe novelty statement
Use a conservative, defensible novelty statement:

> Rather than proposing a new foundation model or a broad benchmark across many environments, this work studies the design space of embodied-agent runtimes in a controlled Isaac Sim setting and quantifies the impact of key system components on performance and efficiency.

### 2.4 Claims we must avoid
Do **not** write any of the following unless later verified:
- “the first Isaac Sim embodied agent benchmark”
- “the first system to …”
- “state of the art”
- “general embodied intelligence”
- “real-world safety”
- “sim-to-real readiness”

---

## 3. Paper Objective, Contributions, and Hypotheses

### 3.1 Primary objective
Build a modular Isaac Sim embodied-agent framework and use it to answer:

1. How much do prompt design and structured outputs matter?
2. How much does context compression hurt or help?
3. When does memory improve success enough to justify extra complexity?
4. Do tool abstraction and skill composition reduce invalid actions?
5. Which runtime policies most improve robustness and efficiency?

### 3.2 Planned contributions
**C1.** A modular embodied-agent framework in Isaac Sim with clear separation between perception/state construction, planner, memory, tools/skills, and runtime policies.  
**C2.** A controlled experiment suite over 2 task families with reproducible seeds and logging.  
**C3.** A systematic study of at least 4 runtime design dimensions.  
**C4.** A failure analysis showing where embodied agents break: invalid actions, stale memory, missing context, recovery loops, latency spikes, etc.  

### 3.3 Hypotheses
**H1.** Structured tool-oriented prompting improves success and reduces invalid actions relative to direct free-form action generation.  
**H2.** Context compression can reduce token/latency cost substantially with only moderate performance loss when summaries preserve task-relevant state.  
**H3.** Episodic memory helps long-horizon tasks more than short tasks.  
**H4.** Runtime validation + retry + fallback improves robustness more than swapping between similarly strong models.  
**H5.** Primitive tool access alone is not enough; some task families benefit from skill-level abstraction.

---

## 4. Scope Definition

### 4.1 Task families
#### Task family A: Mobile navigation
Use official ROS 2 / Nav2-compatible workflows around Nova Carter or equivalent mobile robot assets.

**Target task types:**
- navigate to a named target
- navigate through waypoints
- navigate while avoiding obstacle regions
- simple language-conditioned route selection

#### Task family B: Tabletop pick-and-place
Use Franka Panda or UR10-based examples and controller support already documented in Isaac Sim.

**Target task types:**
- pick a named object and place it in a target zone
- pick among distractors
- multi-step instruction: identify, grasp, move, place
- simple sequential pick-place (optional)

### 4.2 Scene count
Keep the environment count modest.

**MVP:**
- navigation: 2–3 scenes
- manipulation: 2–3 scenes

### 4.3 Difficulty levels
For each task family define 3 levels:
- **easy:** minimal distractors, short horizon
- **medium:** some distractors, longer instruction or route
- **hard:** partial observability / distractors / multi-step dependencies

### 4.4 What not to include in v1
- dynamic humanoids
- deformables
- multi-robot cooperation
- sim-to-real robot execution
- training low-level RL policies from scratch
- end-to-end vision-language-action model training

---

## 5. System Architecture to Build

### 5.1 High-level architecture
```text
Isaac Sim Scene
  -> Observations / State Builder
  -> Context Manager
  -> Memory Manager
  -> Planner LLM/VLM Backend
  -> Tool / Skill Executor
  -> Runtime Policy Layer
  -> Logger / Evaluator
```

### 5.2 Core modules
#### A. Observation / State Builder
Inputs:
- robot pose/state
- object list
- target/task instruction
- sensor observations (at least structured scene state; optionally RGB/depth/lidar)
- event feedback (collision, grasp success, path failure)

Outputs:
- structured state JSON
- text summary for planner
- serialized context bundle for logs

#### B. Context Manager
Responsibilities:
- maintain current episode context window
- choose between full history / truncated history / summary / state-only
- enforce token budget
- emit exact planner input for reproducibility

#### C. Memory Manager
Memory types:
- **working memory:** current goal, subgoal, latest observations
- **episodic memory:** prior actions, outcomes, failures, summaries
- **semantic memory (optional):** object affordances, scene metadata, task rules

#### D. Planner
Responsibilities:
- parse instruction
- select next tool or skill
- emit structured action schema
- optionally explain a short rationale internally for logs, but paper should not depend on hidden chain-of-thought

#### E. Tool Layer
Primitive tools should be explicit, typed, and validated.

**Required primitives:**
- `get_robot_state()`
- `get_scene_objects()`
- `get_goal_state()`
- `navigate_to(target)`
- `move_arm(target_pose)`
- `open_gripper()`
- `close_gripper()`
- `grasp(object_id)`
- `place(target_id | pose)`
- `check_collision()`
- `reset_episode()`

#### F. Skill Layer (optional but recommended)
Composed skills built over primitives.

**Candidate skills:**
- `go_to_named_location(name)`
- `pick_named_object(name)`
- `place_in_container(name)`
- `inspect_and_recover()`

#### G. Runtime Policy Layer
Policies to test:
- output schema validation
- argument validation
- retry with repair prompt
- timeout / maximum planning steps
- failure-triggered fallback policy
- cache-first policy (optional)
- loop detection

#### H. Logger / Evaluator
Must record:
- episode metadata
- config snapshot
- git SHA
- prompt/context variant
- memory variant
- tool calls
- latencies
- token usage if available
- result and failure reason

---

## 6. Experimental Design

### 6.1 Design philosophy
Do **not** run a huge full-factorial experiment. Use staged ablations.

### 6.2 Factor definitions
#### Prompting
- **P0 Direct:** planner outputs next action directly
- **P1 Structured-tool:** planner chooses tool + typed arguments in JSON
- **P2 Structured-tool + brief self-check:** same as P1 plus a short explicit validation step before action

#### Context
- **C0 Full history**
- **C1 Recent-K turns**
- **C2 State-only compact summary**
- **C3 Event-summary + latest observation**

#### Memory
- **M0 None**
- **M1 Episodic summary memory**
- **M2 Episodic + semantic retrieval** (stretch)

#### Tool abstraction
- **T0 Primitive tools only**
- **T1 Mixed primitive + skills**

#### Runtime policies
- **R0 Bare:** no validation, no retry
- **R1 Validate + single retry**
- **R2 Validate + retry + fallback + loop detection**
- **R3 R2 + caching** (stretch)

### 6.3 Experiment blocks
#### Block A: Prompting × Runtime on both task families
Goal: measure invalid action reduction and success improvement.

Run:
- P0, P1, P2 × R0, R1, R2

#### Block B: Context × Memory on longer-horizon tasks
Goal: measure efficiency vs success tradeoff.

Run:
- C0, C1, C2, C3 × M0, M1

#### Block C: Tool abstraction
Goal: measure whether skills improve success and shorten plans.

Run:
- T0 vs T1 with the best prompt/context/runtime setting from earlier blocks

#### Block D: Model backend sensitivity (optional but useful)
Goal: show whether system design matters beyond simple model swaps.

Run:
- best system config with primary model
- best system config with cheaper / weaker model

### 6.4 Evaluation budget
Use a fixed per-condition budget.

**Recommended:**
- 15–25 episodes per condition
- 3 random seeds if episode generation involves stochasticity

**Fallback if compute is tight:**
- 10 episodes per condition for pilot
- expand only the most promising settings

### 6.5 Metrics
#### Primary metrics
- task success rate
- average completion time
- average planner latency per step
- invalid action rate
- recovery success rate

#### Secondary metrics
- number of tool calls
- number of planner calls
- number of retries
- collision count / safety violation count
- average episode steps
- token usage / estimated API cost (if available)
- timeout rate

#### Diagnostic metrics
- context length
- summary compression ratio
- stale-memory error rate
- repeated-loop count
- hallucinated-argument count

### 6.6 Statistics
At minimum report:
- mean
- standard deviation or standard error
- bootstrap confidence intervals if feasible

Do not overcomplicate statistical testing. Clean descriptive statistics plus confidence intervals are enough for IEEE Access if the study is clearly designed.

---

## 7. Feasibility Assessment by Step

| Step | Feasibility | Why feasible | Main blockers | Mitigation |
|---|---|---|---|---|
| Environment setup | High | Official installation paths and compatibility checker exist | driver / GPU mismatch | use Linux + tested drivers; smoke-test first |
| Navigation tasks | High | Isaac Sim documents Nav2 workflows and Nova Carter examples | ROS2 setup complexity | start from official tutorial and freeze versions |
| Manipulation tasks | High | Franka / UR10 / pick-place examples exist | grasp stability / control tuning | start with official controller examples, not custom control |
| Sensor integration | High | camera / depth / RTX lidar / contact sensors are documented | VRAM pressure | use minimum sensor set for v1 |
| Prompt/context experiments | Very high | mostly software-level changes | prompt instability | enforce structured outputs and logging |
| Memory experiments | High | software-level memory modules are easy to implement | measuring benefit clearly | use long-horizon tasks and explicit memory-dependent cases |
| Runtime policy experiments | Very high | validation/retry/fallback are straightforward | confounded configs | isolate changes block-by-block |
| Randomization | Medium | Replicator supports domain randomization | experiment explosion | use only for robustness subset |
| Fine-tuning | Low for v1 | not required for publication | compute + complexity | exclude from main plan |
| Paper writing | High | clear study framing + system figures + ablations fit IEEE Access | poor novelty wording | keep claims narrow and precise |

---

## 8. Milestones for Codex

Codex must execute these milestones **in order**. Do not skip validation.

### M0. Repository bootstrap
**Goal:** create the project skeleton and reproducibility scaffolding.

**Deliverables**
- `README.md`
- `AGENTS.md`
- `plan.md` (this file copied into repo root)
- `src/`
- `configs/`
- `scripts/`
- `tests/`
- `paper/`
- `results/`
- `docs/`
- `skills/` (optional but recommended)

**Acceptance criteria**
- repo tree exists
- README explains setup and goals
- AGENTS.md explains milestone-by-milestone workflow

**Validation**
- list files
- run a trivial test suite if created

---

### M1. Reproducible environment setup
**Goal:** make the environment installable and testable.

**Deliverables**
- environment file(s): `requirements.txt`, `pyproject.toml`, or conda yaml
- `docs/setup.md`
- `scripts/smoke_test_env.py`
- `scripts/smoke_test_isaac.py`

**Acceptance criteria**
- environment install instructions are explicit
- Isaac Sim can launch in the intended mode
- smoke test prints simulator version and passes basic API calls

**Validation**
- run smoke tests
- capture logs to `results/setup/`

**Stop condition**
If Isaac Sim cannot launch or basic APIs fail, stop and fix before moving on.

---

### M2. Navigation baseline
**Goal:** create a working scripted baseline for navigation without LLM planning.

**Deliverables**
- `src/tasks/navigation/`
- `src/tools/navigation.py`
- `scripts/run_nav_baseline.py`
- `tests/test_nav_smoke.py`

**Acceptance criteria**
- robot can reach at least one target in each navigation scene under a scripted baseline
- reset and episode termination work correctly

**Validation**
- run at least 3 successful scripted episodes
- save trajectories/logs

**Stop condition**
If the deterministic baseline is not stable, do not start LLM experiments.

---

### M3. Manipulation baseline
**Goal:** create a working scripted baseline for pick-and-place.

**Deliverables**
- `src/tasks/manipulation/`
- `src/tools/manipulation.py`
- `scripts/run_pickplace_baseline.py`
- `tests/test_pickplace_smoke.py`

**Acceptance criteria**
- robot can pick and place under a scripted controller in at least one scene
- failures are logged with clear reason codes

**Validation**
- run at least 3 successful scripted episodes

**Stop condition**
If grasping or placing is too unstable, simplify the scene before proceeding.

---

### M4. Agent runtime v0
**Goal:** implement the minimal LLM-based planner with structured tool calls.

**Deliverables**
- `src/agent/planner.py`
- `src/agent/context_manager.py`
- `src/agent/runtime.py`
- `src/agent/schemas.py`
- `src/agent/models/` (backend adapters)
- `configs/agent/base.yaml`

**Acceptance criteria**
- planner produces JSON actions matching schema
- tool executor can consume planner outputs
- agent completes at least a few easy tasks end-to-end

**Validation**
- run 5 easy navigation episodes
- run 5 easy manipulation episodes
- save raw planner I/O and parsed actions

---

### M5. Logging and evaluation harness
**Goal:** make every run measurable and reproducible.

**Deliverables**
- `src/eval/metrics.py`
- `src/eval/logger.py`
- `scripts/run_suite.py`
- `scripts/summarize_results.py`
- `results/schema.md`

**Acceptance criteria**
- every run writes structured JSON/CSV logs
- each run records config, seed, git SHA, timestamps, and outcome
- results can be aggregated automatically

**Validation**
- produce one summary CSV from multiple runs

---

### M6. Prompting and runtime ablations
**Goal:** implement P0/P1/P2 and R0/R1/R2 variants.

**Deliverables**
- `configs/experiments/block_a/*.yaml`
- `src/agent/prompting.py`
- validation/retry/fallback modules
- scripts to launch block A runs

**Acceptance criteria**
- each variant is controlled only by config and not by hand edits
- block A results export to tables automatically

**Validation**
- run pilot subset first
- inspect invalid action counts and success rates

---

### M7. Context and memory ablations
**Goal:** implement C0/C1/C2/C3 and M0/M1.

**Deliverables**
- memory module
- summarization / context policies
- `configs/experiments/block_b/*.yaml`

**Acceptance criteria**
- context policy can be switched by config
- memory can be disabled cleanly
- logs show context length and compression stats

**Validation**
- run pilot on long-horizon tasks
- confirm memory-dependent tasks exist and are actually harder without memory

---

### M8. Skill abstraction ablation
**Goal:** compare primitive tools vs higher-level skills.

**Deliverables**
- `src/skills/`
- `configs/experiments/block_c/*.yaml`
- comparison table script

**Acceptance criteria**
- skill wrappers reuse primitive tools
- skill failures are observable and logged

**Validation**
- run 10+ episodes for T0 vs T1 in each task family

---

### M9. Robustness subset with randomization (optional but recommended)
**Goal:** use Replicator or simple scene randomization for robustness testing.

**Deliverables**
- `src/randomization/`
- `configs/randomization/*.yaml`
- `scripts/run_robustness.py`

**Acceptance criteria**
- randomized runs are repeatable from seed/config
- randomization does not silently alter task semantics

**Validation**
- run small robustness subset only

---

### M10. Result analysis, figures, and tables
**Goal:** convert logs into paper-ready artifacts.

**Deliverables**
- `scripts/make_figures.py`
- `scripts/make_tables.py`
- `paper/figures/`
- `paper/tables/`
- `docs/failure_analysis.md`

**Acceptance criteria**
- every figure/table is generated from logs, not hand-made
- figure scripts are rerunnable
- failure cases include screenshots or selected logs where possible

**Validation**
- rerun figure/table scripts from scratch

---

### M11. Paper drafting
**Goal:** draft the full paper in IEEE Access format.

**Deliverables**
- `paper/latex/` or `paper/word/`
- `paper/main.tex` or equivalent
- `paper/abstract.md`
- `paper/related_work.md`
- `paper/cover_letter.md` (optional)
- `paper/reproducibility_checklist.md`

**Acceptance criteria**
- all claims tied to actual experimental outputs
- figures/tables referenced correctly
- limitations section is honest and specific
- no unsupported novelty claims

**Validation**
- compile PDF
- run grammar/style pass
- cross-check paper numbers against result tables

---

### M12. Submission package
**Goal:** create a complete IEEE Access submission package.

**Deliverables**
- final manuscript source
- final matching PDF
- supplementary code/data/video package if desired
- graphical abstract candidate

**Acceptance criteria**
- template-compliant manuscript
- all citations resolved
- matching source and PDF content

**Validation**
- manual checklist

---

## 9. Repository Layout to Create

```text
project-root/
  AGENTS.md
  plan.md
  README.md
  pyproject.toml / requirements.txt
  docs/
    setup.md
    design.md
    related_work.md
    experiment_log.md
    failure_analysis.md
  configs/
    agent/
      base.yaml
    tasks/
      nav_*.yaml
      manip_*.yaml
    experiments/
      block_a/
      block_b/
      block_c/
      block_d/
    randomization/
  src/
    agent/
      planner.py
      runtime.py
      context_manager.py
      memory_manager.py
      prompting.py
      schemas.py
      cache.py
      fallback.py
      retry.py
      loop_detection.py
      models/
    tools/
      navigation.py
      manipulation.py
      scene_query.py
      validation.py
    skills/
      nav_skills.py
      manip_skills.py
    tasks/
      navigation/
      manipulation/
    eval/
      logger.py
      metrics.py
      aggregate.py
      stats.py
    randomization/
  scripts/
    smoke_test_env.py
    smoke_test_isaac.py
    run_suite.py
    run_ablation.py
    summarize_results.py
    make_figures.py
    make_tables.py
  tests/
    test_nav_smoke.py
    test_pickplace_smoke.py
    test_schema_validation.py
    test_logging.py
  results/
    raw/
    processed/
    figures/
    tables/
  paper/
    figures/
    tables/
    latex/
      main.tex
      refs.bib
  skills/
    run-ablation/
      SKILL.md
    make-paper-figures/
      SKILL.md
    verify-results/
      SKILL.md
```

---

## 10. Configuration Principles

### 10.1 Everything must be config-driven
Do not hardcode experimental conditions in code.

Each run config must specify:
- task family
- scene
- seed
- model backend
- prompt variant
- context variant
- memory variant
- tool abstraction variant
- runtime policy variant
- max steps / timeout
- logging directory

### 10.2 Every result row must be reproducible
Each run must save:
- exact config file copy
- git SHA
- timestamp
- simulator version
- model/backend identifier
- any environment variables needed for reproduction (excluding secrets)

---

## 11. Implementation Rules for Codex

### 11.1 General workflow
- follow this file milestone-by-milestone
- keep diffs scoped to the current milestone
- run validation after each milestone
- fix failures before proceeding
- update `docs/experiment_log.md` continuously

### 11.2 Truthfulness rules
- never fabricate a result, figure, table, or successful run
- never write “significant improvement” unless data supports it
- never make claims not grounded in logs
- if a run fails, record the failure honestly
- if a module is stubbed, mark it clearly as TODO or NOT IMPLEMENTED

### 11.3 Writing rules
- write code comments and paper text in English
- write commit messages and progress logs in concise English
- use precise, non-hype scientific language
- prefer “improves in our tested settings” over absolute claims

### 11.4 Paper-writing guardrails
The paper must always include:
- limitations
- failure analysis
- reproducibility details
- ablation methodology
- baseline description

The paper must never:
- imply real-world deployment without real-world tests
- imply safety guarantees
- imply generality outside tested settings
- hide unstable baselines or failed conditions

---

## 12. AGENTS.md to Create in the Repo Root

Codex should create an `AGENTS.md` with at least the following rules:
- `plan.md` is the source of truth
- work one milestone at a time
- run validations after each milestone
- write structured logs under `results/`
- never alter past result files in place; create new run folders
- update `docs/experiment_log.md` after every meaningful change
- stop and report if blocked by missing credentials, unsupported hardware, or Isaac Sim launch failures

---

## 13. Skills to Create for Codex

Create repo-local skills to improve reliability.

### Skill 1: `run-ablation`
Purpose:
- launch a config sweep safely
- write all outputs to timestamped directories
- generate an aggregate CSV after completion

### Skill 2: `verify-results`
Purpose:
- check that every table/figure is backed by raw logs
- verify no missing seeds/configs
- detect broken / empty result rows

### Skill 3: `make-paper-figures`
Purpose:
- regenerate all figures/tables from processed results
- export paper-ready assets

### Skill 4: `paper-consistency-check`
Purpose:
- compare numbers in manuscript text against generated tables
- flag mismatches before submission

---

## 14. Baselines

### 14.1 Required baselines
- **B0 Scripted baseline:** deterministic controller-based baseline for each task family
- **B1 Minimal LLM agent:** direct action generation with minimal runtime safeguards
- **B2 Structured LLM agent:** structured tool-calling without advanced memory/runtime additions
- **B3 Best full system:** structured tool-calling + best context/memory/runtime policy discovered

### 14.2 Optional baselines
- weaker/cheaper model backend under the same runtime
- primitive tools only vs skill abstraction

### 14.3 Why scripted baselines matter
If scripted baselines do not work, then simulator integration is not stable enough and all LLM results become ambiguous.

---

## 15. Task Design Details

### 15.1 Navigation tasks
Each task record should contain:
- scene id
- start pose
- target(s)
- natural language instruction
- success condition
- timeout / max steps
- difficulty level

**Examples**
- “Go to the charging station.”
- “Visit the storage area and then stop near the exit.”
- “Reach the desk without entering the blocked region.”

### 15.2 Manipulation tasks
Each task record should contain:
- scene id
- object set
- target object
- target receptacle or target pose
- natural language instruction
- success condition
- timeout / max steps
- difficulty level

**Examples**
- “Pick the red cube and place it in the left tray.”
- “Move the mug next to the plate.”
- “Pick the smallest blue object and place it in the bin.”

### 15.3 Long-horizon / memory-dependent tasks
Design some tasks to truly require memory, for example:
- instruction contains multiple ordered steps
- object must be revisited after another action
- earlier observation must be recalled later

If memory is not actually needed, the memory study will look weak.

---

## 16. Logging Schema

Each episode should log at least:

```json
{
  "run_id": "...",
  "git_sha": "...",
  "timestamp": "...",
  "seed": 0,
  "task_family": "navigation|manipulation",
  "scene_id": "...",
  "task_id": "...",
  "difficulty": "easy|medium|hard",
  "model_backend": "...",
  "prompt_variant": "P1",
  "context_variant": "C2",
  "memory_variant": "M1",
  "tool_variant": "T1",
  "runtime_variant": "R2",
  "success": true,
  "failure_reason": null,
  "steps": 14,
  "planner_calls": 9,
  "tool_calls": 12,
  "retries": 1,
  "invalid_actions": 0,
  "collisions": 0,
  "planner_latency_ms_mean": 820.4,
  "episode_time_s": 61.2,
  "token_input": 0,
  "token_output": 0,
  "context_chars_mean": 3250,
  "notes": "..."
}
```

Add richer per-step logs separately if possible.

---

## 17. Analysis Plan

### 17.1 Primary comparisons
- P0 vs P1 vs P2
- R0 vs R1 vs R2
- C0/C1/C2/C3 under M0 or M1
- M0 vs M1 on memory-dependent tasks
- T0 vs T1
- Best minimal system vs best full system

### 17.2 Core plots
Create at least these figures:
1. Success rate by runtime variant across tasks
2. Invalid action rate by prompt/runtime variant
3. Success vs latency (Pareto-style scatter)
4. Success vs context cost / token cost
5. Failure mode breakdown bar chart
6. Optional robustness plot under randomization

### 17.3 Core tables
Create at least these tables:
1. Main aggregate result table across conditions
2. Context/memory tradeoff table
3. Tool abstraction comparison table
4. Error / failure taxonomy table

### 17.4 Failure analysis taxonomy
Track failures as:
- navigation path failure
- manipulation grasp failure
- hallucinated object / argument
- invalid action schema
- stale or missing memory
- tool selection mistake
- recovery loop
- timeout / latency overload
- collision or unsafe intermediate action

---

## 18. Paper Outline

### 18.1 Title
Use the current working title unless later refined.

### 18.2 Abstract structure
1. Problem: embodied agent performance depends heavily on runtime system design
2. Gap: existing work often benchmarks models or specific capabilities, but runtime design tradeoffs remain underexplored in controlled Isaac Sim studies
3. Method: modular framework + controlled ablations across prompt/context/memory/tool/runtime policies
4. Results: summarize 2–3 strongest findings only after real data exists
5. Impact: practical guidance for designing embodied-agent runtimes in simulation

### 18.3 Section outline
1. Introduction
2. Related Work
3. System Overview
4. Agent Design Dimensions
5. Isaac Sim Integration and Task Suite
6. Experimental Protocol
7. Results
8. Failure Analysis and Discussion
9. Limitations
10. Conclusion

### 18.4 Introduction checklist
Introduction must explain:
- why runtime design matters
- why Isaac Sim is a good platform
- why a system study is useful even without a new foundation model
- what is measured and what is not claimed

### 18.5 Related work buckets
Cover at least:
- embodied agents / embodied benchmarks
- memory in embodied agents
- safety in embodied agents
- simulation platforms and Isaac Sim-based robotics evaluation
- tool-using LLM/VLM agents

### 18.6 Limitations section requirements
Must include:
- limited task families
- simulator-only evaluation
- limited model backends
- no real-world validation
- dependence on scene design and API/tool interfaces

---

## 19. IEEE Access Submission Checklist

Before submission, ensure all of the following are satisfied:
- manuscript uses IEEE Access template
- source file (Word or LaTeX) matches the PDF exactly
- paper is under ~20 pages unless there is a strong reason not to
- English is polished
- all claims supported by data
- related work is sufficient
- figures/tables are legible
- supplemental code/video package prepared if useful
- graphical abstract candidate selected

Optional but recommended:
- provide a short demo video of simulator rollouts
- provide a code/data repository link if allowed by authorship and release policy

---

## 20. Concrete Run Order

Use this exact run order.

### Phase 1: Stabilize environment and baselines
1. M0 repo bootstrap
2. M1 environment
3. M2 navigation baseline
4. M3 manipulation baseline

### Phase 2: End-to-end agent MVP
5. M4 agent runtime v0
6. M5 logging/eval harness
7. easy task pilot runs

### Phase 3: Main ablations
8. M6 block A (prompting × runtime)
9. analyze pilots
10. M7 block B (context × memory)
11. analyze pilots
12. M8 block C (tool abstraction)

### Phase 4: Optional robustness
13. M9 randomization subset

### Phase 5: Paper assets and writing
14. M10 figures/tables/failure analysis
15. M11 draft paper
16. consistency review
17. M12 submission package

---

## 21. Time Budget (Rough)

This is a rough planning estimate, not a guaranteed schedule.

- M0–M1: 1–3 days
- M2–M3: 3–7 days
- M4–M5: 3–7 days
- M6–M8: 1–3 weeks depending on compute and debugging
- M9: 2–5 days optional
- M10–M12: 1–2 weeks

Total realistic range: **3–6 weeks** of focused work if the simulator setup is stable.

---

## 22. Risk Register

### Risk A: Isaac Sim instability or hardware mismatch
**Mitigation:** verify on supported Linux + RTX hardware first; use smoke tests before all else.

### Risk B: Manipulation baseline too brittle
**Mitigation:** simplify scenes, object set, and grasp conditions; use controller examples before custom logic.

### Risk C: Too many experiment combinations
**Mitigation:** staged ablations only; pilot first; expand only promising conditions.

### Risk D: Weak novelty due to recent benchmarks
**Mitigation:** position as a system design study, not a giant benchmark or “first” claim.

### Risk E: Memory experiments look fake because tasks do not need memory
**Mitigation:** design explicit memory-dependent tasks and document why they need recall.

### Risk F: Paper becomes a tool/product story
**Mitigation:** keep Codex in the engineering workflow, not the scientific claim.

### Risk G: Result drift due to manual edits
**Mitigation:** auto-generate tables and figures from logs only.

---

## 23. Human Review Gates

Codex should stop for human review at these points:
1. after M1, to confirm the environment is correct
2. after M3, to confirm baselines are stable enough
3. after the first pilot block A results
4. before launching any large sweep
5. after figure/table generation
6. before finalizing novelty wording in the manuscript

---

## 24. Final Deliverables

### Code deliverables
- reproducible codebase
- config-driven experiments
- logs + processed results
- figure/table generation scripts

### Paper deliverables
- full IEEE Access manuscript
- figures and tables
- related work and limitations sections
- optional supplementary video

### Scientific deliverables
- clear answer to which runtime design choices matter most in this Isaac Sim setting
- honest boundaries of the findings
- reusable framework for future experiments

---

## 25. References to Keep Handy

### Simulator and tooling
1. NVIDIA Isaac Sim documentation: installation, sensors, ROS 2 navigation, manipulator tutorials, Replicator, requirements.  
   - https://docs.isaacsim.omniverse.nvidia.com/
2. NVIDIA Isaac Sim developer page.  
   - https://developer.nvidia.com/isaac/sim
3. OpenAI Codex docs: AGENTS.md, skills, plan workflows, MCP.  
   - https://developers.openai.com/codex/
   - https://developers.openai.com/codex/guides/agents-md/
   - https://developers.openai.com/codex/skills/
   - https://developers.openai.com/codex/guides/agents-sdk/
   - https://developers.openai.com/blog/run-long-horizon-tasks-with-codex/

### Venue
4. IEEE Access author guidance, acceptance requirements, template, submission checklist, APC.  
   - https://ieeeaccess.ieee.org/authors/
   - https://ieeeaccess.ieee.org/authors/preparing-your-article/
   - https://ieeeaccess.ieee.org/authors/submission-guidelines/
   - https://ieeeaccess.ieee.org/about/article-processing-charges/

### Related work anchors
5. EmbodiedBench (2025).  
   - https://arxiv.org/abs/2502.09560
6. FindingDory (2025).  
   - https://arxiv.org/abs/2506.15635
7. IS-Bench (2025).  
   - https://arxiv.org/abs/2506.16402
8. Mind and Motion Aligned / Kitchen-R (2025).  
   - https://arxiv.org/abs/2508.15663

---

## 26. Final Instruction to Codex

Follow this document as the authoritative plan.

Rules:
1. Execute one milestone at a time.
2. Validate every milestone before proceeding.
3. Keep all results reproducible and logged.
4. Do not fabricate success.
5. Prefer the smallest stable implementation that answers the research question.
6. Update docs continuously.
7. When in doubt, reduce scope instead of expanding it.
8. The paper is about **embodied-agent runtime design in Isaac Sim**, not about Codex.

