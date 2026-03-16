# Unified Task and Result Contracts

This document defines the shared contracts that every later milestone must follow for task configuration, episode results, per-step events, metrics, and output artifacts.

## Why this exists

Future milestones will add navigation, pick-and-place, instruction following, runtime policies, and experiments. Those components must write data in a consistent way so that:

- runs remain reproducible
- results can be aggregated automatically
- paper tables and figures can be built from one stable schema
- future Codex runs do not invent incompatible formats

## Contract module

Implementation lives under:

- `src/isaacsim_agent/contracts/__init__.py`
- `src/isaacsim_agent/contracts/enums.py`
- `src/isaacsim_agent/contracts/models.py`
- `src/isaacsim_agent/contracts/metrics.py`
- `src/isaacsim_agent/contracts/io.py`

## Unified task configuration contract

The project-wide task config is `TaskConfig`.

### Common required fields

- `task_type`
- `task_id`
- `scene_id`
- `robot_id`
- `seed`
- `max_steps`
- `max_time_sec`
- `headless`
- `render`
- `difficulty`
- `runtime_options`

### Supported task families now

- `navigation`
- `pick_place`
- `instruction_following`

### Task-specific sections

- `navigation` uses `NavigationSpec`
- `pick_place` uses `PickPlaceSpec`
- `instruction_following` uses `InstructionFollowingSpec`

Exactly one task-specific section must match `task_type`.

### Runtime options

`RuntimeOptions` is the shared place for options that later milestones can reuse without redefining the schema:

- planner enable/disable
- memory enable/disable
- tool validation enable/disable
- recovery enable/disable
- event collection enable/disable
- planner timeout
- planner token budget
- `extra_options` for milestone-specific flags that should not fork the base schema

## Unified episode result contract

The project-wide episode result is `EpisodeResult`.

### Common required fields

- `run_id`
- `task_type`
- `task_id`
- `scene_id`
- `robot_id`
- `seed`
- `success`
- `termination_reason`
- `step_count`
- `elapsed_time_sec`
- `sim_time_sec`
- `invalid_action_count`
- `collision_count`
- `recovery_count`
- `tool_call_count`
- `planner_call_count`
- `token_usage`
- `planner_latency_sec`
- `notes`

### Additional contract decision

- `planner_latency_sec` is defined as **total planner wall-clock latency accumulated over the episode**
- task-specific or derived metrics belong in `EpisodeResult.metrics`
- token accounting is nested under `TokenUsage` with:
  - `prompt_tokens`
  - `completion_tokens`
  - `total_tokens`
  - `estimated_cost_usd`

## Unified step/event log contract

The project-wide per-step log record is `EventRecord`.

### Required event identity fields

- `run_id`
- `event_index`
- `event_type`
- `step_index`
- `task_type`
- `task_id`
- `scene_id`
- `robot_id`
- `seed`
- `timestamp_utc`

### Shared optional event fields

- `sim_time_sec`
- `action_ref`
- `tool_name`
- `planner_latency_sec`
- `success`
- `payload`
- `metrics`
- `notes`

### Event type enum

The shared `EventType` values are:

- `episode_start`
- `step_start`
- `observation`
- `planner_call`
- `planner_response`
- `tool_call`
- `tool_result`
- `action_applied`
- `collision`
- `recovery`
- `validation_warning`
- `step_end`
- `episode_end`

Future milestones may add event payload keys, but should avoid inventing a parallel event schema.

## Shared termination reasons

The shared `TerminationReason` enum is:

- `success`
- `max_steps`
- `timeout`
- `collision_limit`
- `invalid_action_limit`
- `planner_failure`
- `tool_failure`
- `recovery_failure`
- `robot_stuck`
- `task_precondition_failed`
- `scene_load_failure`
- `runtime_error`
- `user_abort`
- `cancelled`
- `unknown`

### Contract rule

All future baselines and agent runs must end with one of these reasons. New reasons should be added centrally to the enum and documented here rather than invented ad hoc in result files.

## Project-wide metrics contract

Metric definitions live in `src/isaacsim_agent/contracts/metrics.py`.

### Always expected episode metrics

These must always exist in every episode result row:

- `success`
- `termination_reason`
- `step_count`
- `elapsed_time_sec`
- `sim_time_sec`
- `invalid_action_count`
- `collision_count`
- `recovery_count`
- `tool_call_count`
- `planner_call_count`

### Optional but standard metrics

These should be present when the runtime can measure them:

- token usage fields
- estimated API cost
- `planner_latency_sec`
- free-form `notes`

### Task-specific metrics

Task-specific metrics must be stored in `EpisodeResult.metrics` using stable namespaced keys:

- Navigation: `navigation.*`
- Pick-place: `pick_place.*`
- Instruction following: `instruction_following.*`

This namespacing matters for later result aggregation and paper tables.

## Output directory and artifact conventions

Canonical run output layout:

```text
results/
  runs/
    <run_id>/
      manifest.json
      task_config.json
      episode_result.json
      events.jsonl
      artifacts/
```

### File roles

- `manifest.json`: minimal run identity, schema version, and artifact convention
- `task_config.json`: full resolved task config used for the run
- `episode_result.json`: final episode result
- `events.jsonl`: per-event log, one JSON object per line
- `artifacts/`: optional extra files such as images, traces, debug dumps, or plots

### Contract rules

- never overwrite older run folders in place when preserving historical results matters
- every run folder must be self-describing from `manifest.json` and `task_config.json`
- future scripts should prefer adding files under `artifacts/` rather than inventing new top-level names without documentation

## Minimal validation path

The contract validation script is:

- `scripts/validate_contracts.py`

It proves that:

- a task config can be instantiated and serialized
- a result object can be created
- an event log can be written
- the documented run artifact layout is produced under `results/runs/<run_id>/`
