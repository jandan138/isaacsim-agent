# STATUS.md

## Current status

- Date: 2026-03-19
- Plan source of truth: `plan.md`
- Paper-writing source of truth: `docs/ral_writing_playbook.md`
- Active milestone: `M13 phase-two external USD rendering kickoff`
- Milestone state:
  - this run completed the phase-two external USD render-package helpers
  - this run completed the single-asset external USD CLI
  - this run completed the batch external USD CLI, render smoke tests, and docs
  - this run completed a local fallback reviewer-style acceptance pass after a
    delegated reviewer became unavailable during interrupted-session recovery
- Completion level:
  - `src/isaacsim_agent/render/` now exposes
    `load_external_usd_stage(...)` and `build_bbox_camera_views(...)`
  - `scripts/render_usd_asset.py` now renders a real external `.usd` / `.usda`
    / `.usdc` asset to `front.png`, `three_quarter.png`, `top.png`, and
    `side.png`
  - `scripts/render_usd_asset.py --save-stage` now writes `stage.usda`
  - `scripts/render_usd_asset.py --skip-existing` now short-circuits only when
    every requested PNG already exists and, when requested, `stage.usda` also
    exists
  - `scripts/render_usd_asset.py` now returns `EXPECTED_MISSING_DEPENDENCY`
    exit code `3` when Isaac-backed imports are unavailable
  - `scripts/render_usd_batch.py` now discovers assets, shells out once per
    asset to `scripts/render_usd_asset.py`, writes
    `<output-root>/batch_summary.json`, and returns `1` when any asset fails
  - the phase-one project-demo render CLI remained working for both task
    families
  - a real external USD single-asset smoke passed with a temporary minimal
    asset under `/tmp/isaacsim-agent-m13-final-dx85mmew/input/nested/`
  - a real external USD batch smoke passed against that same temporary input

## Run context

- This run stayed within the requested boundaries:
  - phase-two external USD rendering only
  - no dataset-level pipeline expansion
  - no DLC, caption, with-background, or paper-path edits
  - no task-module refactor for external USD logic
- Source-of-truth docs consumed in this run:
  - `plan.md`
  - `AGENTS.md`
  - `STATUS.md`
  - `docs/render_phase1_cli.md`
  - `docs/setup.md`
  - `scripts/smoke_test_isaac.py`
  - `scripts/isaac_python.sh`
  - `src/isaacsim_agent/render/__init__.py`
  - `src/isaacsim_agent/render/session.py`
  - `src/isaacsim_agent/render/external_usd.py`
  - `scripts/render_demo_views.py`
  - `scripts/render_usd_asset.py`
  - `scripts/render_usd_batch.py`
  - `tests/test_render_cli_smoke.py`
  - `tests/test_render_usd_batch_cli.py`
- Agent teaming:
  - worker `019d049c-63be-7a12-b04e-065be2589334`
    was assigned the render-package slice
  - worker `019d049c-643b-7811-bd68-adc35e9a2114`
    was assigned the single-asset CLI slice
  - worker `019d049c-6457-7c71-a7e2-c31f917a7311`
    was assigned the batch/tests/docs slice
  - orchestrator waited two 10-minute windows with no completed worker
    responses, then sent one focused progress check
  - because the mainline was still blocked after those waits and the focused
    progress check, the orchestrator interrupted all three workers and
    collected their final handoffs
  - those worker handoffs were not reliable enough for close-out on their own,
    so the orchestrator re-ran the milestone validations locally and
    normalized the final records
  - reviewer `019d04c2-68d8-7a93-ade1-602f3b4bbec8` became unavailable after a
    user interruption during recovery; `wait_agent` later returned `not_found`
    and no usable reviewer output was available from that attempt
  - reviewer retry `019d04de-0778-78d2-8b51-68bcf8aa6f73` then completed with
    no blocking findings and confirmed the M13 acceptance state
  - final acceptance evidence is recorded in
    `.codex/worklogs/subagents/2026-03-19/m13-review.md`, with the retry
    attempt tracked separately in
    `.codex/worklogs/subagents/2026-03-19/m13-review-retry.md`

## Milestone summary

- Completed in this run:
  - added `src/isaacsim_agent/render/external_usd.py` with external-USD stage
    loading and bbox-driven camera helpers
  - updated `src/isaacsim_agent/render/__init__.py` so the shared render
    package exports the new external USD helpers
  - extended `src/isaacsim_agent/render/session.py` so the render backend keeps
    `Usd` available to the external-USD helpers
  - replaced the placeholder `scripts/render_usd_asset.py` path with a real
    render flow that consumes the shared helpers, exports `stage.usda`, and
    emits `EXPECTED_MISSING_DEPENDENCY` exit code `3` when Isaac is unavailable
  - replaced the placeholder `scripts/render_usd_batch.py` path with per-asset
    shell-out isolation, discovery, skip-existing propagation, and
    `batch_summary.json`
  - updated `tests/test_render_cli_smoke.py` to reflect phase-two behavior and
    preserve the phase-one blocked-path smoke
  - added `tests/test_render_usd_batch_cli.py` for additional batch/single-asset
    discovery and skip-existing coverage
  - updated `docs/render_phase1_cli.md` to document the current phase-two
    external USD behavior and remaining limitations
  - revalidated the milestone locally through py_compile, import smoke,
    unittest smoke suites, diff hygiene, and real Isaac-backed single/batch
    smokes
- Not completed in this run:
  - no dataset-level rendering pipeline
  - no DLC submission or remote execution
  - no caption, background, or broader art-direction work
  - no larger-scale multi-asset soak beyond the required smoke coverage

## Files changed in this run

- `STATUS.md`
- `docs/render_phase1_cli.md`
- `scripts/render_usd_asset.py`
- `scripts/render_usd_batch.py`
- `src/isaacsim_agent/render/__init__.py`
- `src/isaacsim_agent/render/session.py`
- `src/isaacsim_agent/render/external_usd.py`
- `tests/test_render_cli_smoke.py`
- `tests/test_render_usd_batch_cli.py`
- `.codex/worklogs/main/2026-03-19/m13-phase-two-understanding-session-research.md`
- `.codex/worklogs/main/2026-03-19/m13-phase-two-session-plan.md`
- `.codex/worklogs/main/2026-03-19/m13-phase-two-session-research.md`
- `.codex/worklogs/main/2026-03-19/m13-phase-two-session-handoff.md`
- `.codex/worklogs/subagents/2026-03-19/m13-worker1-render-package.md`
- `.codex/worklogs/subagents/2026-03-19/m13-worker2-single-asset-cli.md`
- `.codex/worklogs/subagents/2026-03-19/m13-worker3-batch-tests-docs.md`
- `.codex/worklogs/subagents/2026-03-19/m13-review.md`
- `.codex/worklogs/subagents/2026-03-19/m13-review-retry.md`

## Commands run

- Source-of-truth and repo-state reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,260p' STATUS.md`
  - `sed -n '1,260p' AGENTS.md`
  - `git status --short --untracked-files=all`
- Inspection:
  - `sed -n ...` over the current render package, phase-one render CLI,
    phase-two CLIs, docs, tests, and M13 worklogs
  - `git diff --stat`
  - `rg -n ...` over external USD markers, exit-code markers, and render hooks
  - `rg --files . | rg '\\.(usd|usda)$'`
- Runtime preparation:
  - `./scripts/isaac_python.sh scripts/smoke_test_isaac.py`
  - `python - <<'PY'` to create a temporary minimal external USD smoke asset
    under `/tmp/isaacsim-agent-m13-final-dx85mmew/input/nested/minimal_asset.usda`
- Lightweight validation:
  - `python -m py_compile src/isaacsim_agent/render/__init__.py src/isaacsim_agent/render/session.py src/isaacsim_agent/render/external_usd.py scripts/render_usd_asset.py scripts/render_usd_batch.py tests/test_render_cli_smoke.py tests/test_render_usd_batch_cli.py`
  - `PYTHONPATH=src python - <<'PY'` import smoke for
    `DEFAULT_EXTERNAL_USD_VIEWS`, `build_bbox_camera_views`, and
    `load_external_usd_stage`
  - `PYTHONPATH=src python -m unittest tests.test_render_cli_smoke tests.test_render_usd_batch_cli -q`
  - `PYTHONPATH=src python -m unittest tests.test_render_cli_smoke -q`
  - `PYTHONPATH=src python -m unittest tests.test_render_usd_batch_cli -q`
  - `PYTHONPATH=src python -m unittest tests.test_nav_smoke tests.test_pickplace_smoke -q`
  - `git diff --check`
- Real external USD smokes:
  - `./scripts/isaac_python.sh scripts/render_usd_asset.py --usd-path /tmp/isaacsim-agent-m13-final-dx85mmew/input/nested/minimal_asset.usda --output-dir /tmp/isaacsim-agent-m13-final-dx85mmew/output-asset --save-stage`
  - `./scripts/isaac_python.sh scripts/render_usd_batch.py --input-root /tmp/isaacsim-agent-m13-final-dx85mmew/input --output-root /tmp/isaacsim-agent-m13-final-dx85mmew/output-batch --save-stage`

## Validation results

- Isaac runtime smoke:
  - `./scripts/isaac_python.sh scripts/smoke_test_isaac.py`
    passed with:
    - exit code `0`
- Syntax validation:
  - `python -m py_compile src/isaacsim_agent/render/__init__.py src/isaacsim_agent/render/session.py src/isaacsim_agent/render/external_usd.py scripts/render_usd_asset.py scripts/render_usd_batch.py tests/test_render_cli_smoke.py tests/test_render_usd_batch_cli.py`
    passed with:
    - no output
- Import smoke:
  - `PYTHONPATH=src python - <<'PY'`
    passed with:
    - `IMPORT_SMOKE_OK ('front', 'three_quarter', 'top', 'side') True True`
- Combined render CLI smoke coverage:
  - `PYTHONPATH=src python -m unittest tests.test_render_cli_smoke tests.test_render_usd_batch_cli -q`
    passed with:
    - `Ran 12 tests in 1.520s`
    - `OK`
- Render CLI smoke suite:
  - `PYTHONPATH=src python -m unittest tests.test_render_cli_smoke -q`
    passed with:
    - `Ran 9 tests in 1.014s`
    - `OK`
- New external USD batch CLI smoke tests:
  - `PYTHONPATH=src python -m unittest tests.test_render_usd_batch_cli -q`
    passed with:
    - `Ran 3 tests in 0.505s`
    - `OK`
- Existing phase-one smoke suites:
  - `PYTHONPATH=src python -m unittest tests.test_nav_smoke tests.test_pickplace_smoke -q`
    passed with:
    - `Ran 4 tests in 19.009s`
    - `OK`
- Diff hygiene:
  - `git diff --check`
    passed with:
    - no output
- Real external USD single-asset smoke:
  - `./scripts/isaac_python.sh scripts/render_usd_asset.py --usd-path /tmp/isaacsim-agent-m13-final-dx85mmew/input/nested/minimal_asset.usda --output-dir /tmp/isaacsim-agent-m13-final-dx85mmew/output-asset --save-stage`
    passed with:
    - exit code `0`
    - output files:
      - `/tmp/isaacsim-agent-m13-final-dx85mmew/output-asset/front.png`
      - `/tmp/isaacsim-agent-m13-final-dx85mmew/output-asset/three_quarter.png`
      - `/tmp/isaacsim-agent-m13-final-dx85mmew/output-asset/top.png`
      - `/tmp/isaacsim-agent-m13-final-dx85mmew/output-asset/side.png`
      - `/tmp/isaacsim-agent-m13-final-dx85mmew/output-asset/stage.usda`
- Real external USD batch smoke:
  - `./scripts/isaac_python.sh scripts/render_usd_batch.py --input-root /tmp/isaacsim-agent-m13-final-dx85mmew/input --output-root /tmp/isaacsim-agent-m13-final-dx85mmew/output-batch --save-stage`
    passed with:
    - exit code `0`
    - summary:
      - `counts = {'discovered': 1, 'success': 1, 'skipped': 0, 'failed': 0}`
      - first asset status `success`
      - first asset relative path `nested/minimal_asset.usda`
      - first asset output dir `/tmp/isaacsim-agent-m13-final-dx85mmew/output-batch/nested/minimal_asset`
    - output files:
      - `/tmp/isaacsim-agent-m13-final-dx85mmew/output-batch/batch_summary.json`
      - `/tmp/isaacsim-agent-m13-final-dx85mmew/output-batch/nested/minimal_asset/front.png`
      - `/tmp/isaacsim-agent-m13-final-dx85mmew/output-batch/nested/minimal_asset/three_quarter.png`
      - `/tmp/isaacsim-agent-m13-final-dx85mmew/output-batch/nested/minimal_asset/top.png`
      - `/tmp/isaacsim-agent-m13-final-dx85mmew/output-batch/nested/minimal_asset/side.png`
      - `/tmp/isaacsim-agent-m13-final-dx85mmew/output-batch/nested/minimal_asset/stage.usda`
- Reviewer:
  - final judgement: `Accept`
  - recorded via local fallback review in
    `.codex/worklogs/subagents/2026-03-19/m13-review.md`
  - reviewer retry `019d04de-0778-78d2-8b51-68bcf8aa6f73` also returned
    `Accept` with no blocking findings
  - no blocking bugs or regressions found against the phase-two plan

## Remaining gaps

- add a checked-in minimal external USD fixture only if later phases want a
  deterministic repo-local smoke asset instead of a temporary one
- broaden performance or multi-asset stress validation only if a later
  milestone explicitly asks for it

## Next recommended sub-milestone

- `M13 follow-up external USD hardening`:
  - add a checked-in minimal external USD fixture for repeatable smoke coverage
  - only after that, explicitly choose whether to continue into broader render
    pipeline work or the next milestone beyond external USD kickoff
