# STATUS.md

## Current status

- Date: 2026-03-16
- Plan source of truth: `plan.md`
- Active milestone: `M1.5 Unified Task and Result Contracts`
- Milestone state: completed for this repo run
- Completion level: shared contracts, metrics conventions, artifact layout, validation utility, dummy run output, tests, and initial git repository management are now in place; `M2` has not started

## Milestone summary

- Completed in this run: unified task config/result/event contracts, shared termination reasons, project-wide metrics contract, canonical run artifact layout, contract documentation, minimal serialization helpers, a dummy contract validation runner, and tests
- Not completed in this run: navigation logic, manipulation logic, instruction execution logic, planner/runtime logic, experiments, or M2 baseline work

## Repo git management update

- Initialized a local Git repository on branch `main`
- Added a stricter `.gitignore` that excludes Python envs, caches, build metadata, editor files, temp files, local env files, and generated `results/` artifacts
- Added `.gitattributes` with LF normalization for source/docs/config files and binary handling for common archives, images, PDFs, and Isaac-relevant `usdc`/`usdz` files
- Kept `results/README.md` and `results/schema.md` tracked while ignoring generated folders such as `results/setup/` and `results/runs/`
- Created the first commit: `a3a4986 chore: initialize repository scaffold`

## Contract decisions

- Canonical task config type: `TaskConfig` with common fields plus exactly one matching task-specific section: `NavigationSpec`, `PickPlaceSpec`, or `InstructionFollowingSpec`
- Canonical result type: `EpisodeResult` with required common rollout metrics and a namespaced `metrics` map for task-specific values
- Canonical event type: `EventRecord` written as JSONL in `events.jsonl`
- Canonical termination enum: `TerminationReason`
- Canonical task type enum: `TaskType`
- Canonical event enum: `EventType`
- Canonical output layout: `results/runs/<run_id>/manifest.json`, `task_config.json`, `episode_result.json`, `events.jsonl`, and `artifacts/`
- Planner latency contract: `planner_latency_sec` means total planner wall-clock latency accumulated across the episode
- Token accounting contract: stored in nested `TokenUsage` with prompt, completion, total, and optional estimated cost
- Task-specific metrics contract: store them in `EpisodeResult.metrics` using stable prefixes such as `navigation.*`, `pick_place.*`, and `instruction_following.*`

## Changed files

- `.gitattributes`
- `.gitignore`
- `README.md`
- `STATUS.md`
- `docs/contracts.md`
- `results/README.md`
- `results/schema.md`
- `scripts/README.md`
- `scripts/validate_contracts.py`
- `src/isaacsim_agent/__init__.py`
- `src/isaacsim_agent/contracts/__init__.py`
- `src/isaacsim_agent/contracts/enums.py`
- `src/isaacsim_agent/contracts/io.py`
- `src/isaacsim_agent/contracts/metrics.py`
- `src/isaacsim_agent/contracts/models.py`
- `tests/test_contracts.py`
- `results/runs/dummy-contract-run/manifest.json`
- `results/runs/dummy-contract-run/task_config.json`
- `results/runs/dummy-contract-run/episode_result.json`
- `results/runs/dummy-contract-run/events.jsonl`
- `results/runs/dummy-contract-run/artifacts/README.txt`
- `results/runs/dummy-contract-run.validation.log`
- `results/runs/unittest_contracts.log`

## Validation commands

- `uv run python scripts/validate_contracts.py --run-id dummy-contract-run`
- `uv run python -m unittest discover -s tests -p 'test_*.py'`
- `git init -b main`
- `git status --short --ignored`
- `git add .`
- `git status --short`
- `git -c user.name='Codex CLI' -c user.email='codex@example.com' commit -m 'chore: initialize repository scaffold'`
- `git log --oneline -1`

## Validation results

- Dummy contract run succeeded with `CONTRACT_VALIDATION_OK`
- Canonical artifact layout was created under `results/runs/dummy-contract-run/`
- `task_config.json` round-tripped successfully through serialization and loading
- `episode_result.json` and `events.jsonl` were written with the expected structure
- Test suite passed with `Ran 5 tests in 10.721s` and `OK`
- Git repository initialization succeeded
- `git status --short --ignored` confirmed that `.venv/`, `results/setup/`, `results/runs/`, and Python cache/build artifacts are ignored while source/docs remain tracked
- `git add .` staged the intended project files without pulling generated artifacts into version control
- The stricter `.gitignore` and `.gitattributes` rules were applied successfully
- The first commit was created successfully as `a3a4986`

## Open issues

- The current contract uses a single total `planner_latency_sec`; future aggregation code may also want derived mean/max latency fields, but those should be computed without breaking this base contract unless a central schema revision is recorded
- The current contract leaves task-specific payload details intentionally lightweight; future milestones must extend the documented namespaced `metrics` and task-specific spec sections rather than creating parallel schemas
- Multi-episode batch manifests and aggregate result tables are not defined yet; they should build on top of the per-run layout introduced here rather than replacing it
- No remote Git repository is configured yet

## Recommended next step

- Start `M2. Navigation baseline` with one deterministic scripted navigation task, and make all outputs conform to the shared contracts defined in this milestone
