# Render CLI

This note documents the current CLI surface for the Isaac Sim 4.5
render-migration work.

## Scope

Phase 1 focuses on project-owned demo scenes rendered from procedurally built
stages. The intended entrypoint is:

- `scripts/render_demo_views.py`

Phase 2 covers external USD inputs with two entrypoints:

- `scripts/render_usd_asset.py`
- `scripts/render_usd_batch.py`

## Phase 1 assumptions

- The stage-population helpers will be provided by the task ownership slice:
  - `populate_navigation_stage(stage, definition, world_config, visualization_config=None)`
  - `populate_pickplace_stage(stage, definition, world_config, visualization_config=None)`
- The shared render lifecycle will be provided by the render package:
  - `VisualizationConfig`
  - `start_render_app(...)`
  - `render_rgb_views(...)`
- `scripts/render_demo_views.py` keeps those imports delayed until execution so
  its help surface remains available even before the worker-owned backends are
  integrated.

## Phase 2 external USD behavior

- `render_usd_asset.py` renders one real external `.usd` / `.usda` / `.usdc`
  asset to the canonical four views:
  - `<output-dir>/front.png`
  - `<output-dir>/three_quarter.png`
  - `<output-dir>/top.png`
  - `<output-dir>/side.png`
- `--save-stage` writes `<output-dir>/stage.usda`
- `--skip-existing` short-circuits only when every requested PNG already
  exists, and when `--save-stage` is set, `stage.usda` also exists
- if Isaac Sim is unavailable from the current interpreter, the single-asset
  CLI exits with `EXPECTED_MISSING_DEPENDENCY` code `3`
- `render_usd_batch.py` discovers assets under `--input-root`, shells out to
  `render_usd_asset.py` once per asset, and writes outputs under:
  - `<output-root>/<relative_asset_path_without_ext>/...`
- batch always writes:
  - `<output-root>/batch_summary.json`
- batch exit codes:
  - `0` when every asset is `success` or `skipped`
  - `1` when any asset fails

## Current limitations

- `render_demo_views.py` is now wired to the phase-one task helpers and render
  package, but it still requires launching via `scripts/isaac_python.sh` for
  real Isaac-backed rendering.
- The render session pre-creates the Isaac/Replicator cache directories under
  `~/.cache/` because missing `warp` / `ov/texturecache` paths can prevent PNG
  artifacts from being written.
- The external USD flow uses bbox-driven camera placement, so it is general for
  arbitrary assets but does not attempt task-specific art direction.
- This pass does not add heavy Isaac validation on its own; it only establishes
  the user-facing CLI, smoke test, and documentation surface plus a minimal
  external-USD render path.
