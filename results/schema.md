# Results Schema

This repo uses the shared contracts in `src/isaacsim_agent/contracts/` for all future run outputs.

## Canonical run layout

```text
results/
  runs/
    <run_id>/
      manifest.json
      task_config.json
      episode_result.json
      events.jsonl
      artifacts/
  processed/
    <summary_batch>/
      run_summary.jsonl
      run_summary.csv
      aggregate.json
      validation.json
      pilot_summary.json
      pilot_summary.md
      block_a_pilot_summary.json
      block_a_pilot_summary.md
      block_a_summary.json
      block_a_summary.md
      run_plan.json
```

## Required files

- `manifest.json`
- `task_config.json`
- `episode_result.json`
- `events.jsonl`

## Conventions

- `run_id` is the stable directory name for a single run
- each file must be valid JSON or JSONL
- per-task metrics should use namespaced keys in `episode_result.json`
- ad hoc artifacts go under `artifacts/`
- M5 processed summaries must not rewrite the canonical per-run layout; derived tables belong under `results/processed/`
- post-M5 pilot workflows may add derived files such as `pilot_summary.{json,md}`, `block_a_pilot_summary.{json,md}`, `block_a_summary.{json,md}`, and `run_plan.json` under `results/processed/`, but they must continue to reuse the canonical per-run layout under `runs/`
- future result processors should assume this layout unless `STATUS.md` explicitly records a later schema revision
