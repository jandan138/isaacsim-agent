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
- future result processors should assume this layout unless `STATUS.md` explicitly records a later schema revision
