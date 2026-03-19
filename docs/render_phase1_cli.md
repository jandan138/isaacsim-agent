# Render Phase 1 CLI

This note documents the first-pass CLI surface for the Isaac Sim 4.5
render-migration work.

## Scope

Phase 1 focuses on project-owned demo scenes rendered from procedurally built
stages. The intended entrypoint is:

- `scripts/render_demo_views.py`

Phase 2 will cover external USD inputs. The two external USD scripts exist now
only as honest placeholders with stable `--help` surfaces:

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

## Current limitations

- `render_demo_views.py` is now wired to the phase-one task helpers and render
  package, but it still requires launching via `scripts/isaac_python.sh` for
  real Isaac-backed rendering.
- The render session pre-creates the Isaac/Replicator cache directories under
  `~/.cache/` because missing `warp` / `ov/texturecache` paths can prevent PNG
  artifacts from being written.
- `render_usd_asset.py` and `render_usd_batch.py` deliberately return a
  phase-two placeholder exit code instead of pretending the external USD flow
  already exists.
- This pass does not add heavy Isaac validation on its own; it only establishes
  the user-facing CLI, smoke test, and documentation surface for later
  integration.
