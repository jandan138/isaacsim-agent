# STATUS.md

## Current status

- Date: 2026-03-19
- Plan source of truth: `plan.md`
- Paper-writing source of truth: `docs/ral_writing_playbook.md`
- Active milestone: `M13 external USD lighting fix`
- Milestone state:
  - this run completed a focused black-render investigation for the external
    USD path
  - this run completed an external-USD-only fallback lighting fix
  - this run completed portable tests and concise docs for the lighting fix
  - this run completed real Isaac-backed rerenders against the GRScenes bottle
    assets and reviewer acceptance
- Completion level:
  - the black-render root cause was identified as missing effective lights on
    opened external USD stages
  - `src/isaacsim_agent/render/external_usd.py` now detects whether an opened
    stage already has effective lights
  - `src/isaacsim_agent/render/external_usd.py` now injects a conservative
    fallback light rig only when the external USD stage has no lights
  - asset-provided lights still take precedence
  - phase-one behavior remains unchanged because the fix is scoped to the
    external USD path only
  - `tests/test_external_usd_lighting.py` now provides portable regression
    coverage for light detection and fallback invocation
  - `docs/render_phase1_cli.md` and `docs/render_grscenes_smoke.md` now
    document the fallback-lighting behavior honestly and narrowly
  - rerendered GRScenes bottle outputs are no longer black

## Run context

- This run stayed within the requested boundaries:
  - fix the black-render/no-light case for external USD assets only
  - no dataset-level pipeline expansion
  - no changes to the phase-one render path
  - no broader art-direction redesign
  - the local GRScenes validation tree remains machine-local and is ignored
    from version control
- Source-of-truth docs and inputs consumed in this run:
  - `plan.md`
  - `AGENTS.md`
  - `STATUS.md`
  - `src/isaacsim_agent/render/external_usd.py`
  - `results/render_smokes/grscenes_bottle_subset10_20260319/`
  - `docs/render_phase1_cli.md`
  - `docs/render_grscenes_smoke.md`
- Agent teaming:
  - worker `019d0518-4b73-7080-84ca-3e87d9c496e6`
    owned the render-package slice
  - worker `019d0518-4baf-7bd0-8c9c-85981ae3214f`
    owned the test slice
  - worker `019d0518-4bf6-76b1-bddb-56c51bb288d5`
    owned the docs slice
  - all three workers completed without requiring interruption or reassignment
  - orchestrator integrated the worker outputs, resolved one integration-level
    test mismatch, reran the validation sequence locally, and performed the
    real GRScenes rerenders
  - reviewer `019d0525-2a30-7130-adb6-000b4b92c3b0`
    accepted the milestone with no blocking findings

## Milestone summary

- Completed in this run:
  - confirmed via measurement that the pre-fix GRScenes renders were literally
    black:
    - single-asset `front`, `three_quarter`, `top`, and `side` all had
      `gray_mean = 0.0`
    - batch `front.png` outputs for all `10` bottle assets also had
      `gray_mean = 0.0`
  - confirmed that a one-off dome-light probe immediately produced non-black
    output, isolating missing lighting as the primary cause
  - extended `src/isaacsim_agent/render/session.py` so the cached render
    backend now keeps `UsdLux`
  - updated `src/isaacsim_agent/render/external_usd.py` with:
    - `stage_has_lights(...)`
    - `ensure_external_usd_lighting(...)`
    - `load_external_usd_stage(...)` fallback-lighting application
  - updated `tests/test_external_usd_lighting.py` for portable regression
    coverage
  - updated `docs/render_phase1_cli.md` and `docs/render_grscenes_smoke.md`
    for the fallback-lighting behavior
  - rerendered the same GRScenes bottle asset successfully with non-black
    outputs
  - rerendered the full `10`-asset bottle batch successfully with non-black
    outputs
- Not completed in this run:
  - no flattening of the wrapper output layout
  - no asset-quality repair for mesh-normal warnings inside the source assets
  - no reference-image comparison beyond brightness / non-black confirmation

## Files changed in this run

- `STATUS.md`
- `.gitignore`
- `src/isaacsim_agent/render/session.py`
- `src/isaacsim_agent/render/external_usd.py`
- `tests/test_external_usd_lighting.py`
- `docs/render_phase1_cli.md`
- `docs/render_grscenes_smoke.md`
- `.codex/worklogs/main/2026-03-19/black-render-investigation-session-research.md`
- `.codex/worklogs/main/2026-03-19/m13-lighting-fix-session-plan.md`
- `.codex/worklogs/main/2026-03-19/m13-lighting-fix-session-research.md`
- `.codex/worklogs/main/2026-03-19/m13-lighting-fix-session-handoff.md`
- `.codex/worklogs/subagents/2026-03-19/m13-lighting-worker1-render.md`
- `.codex/worklogs/subagents/2026-03-19/m13-lighting-worker2-tests.md`
- `.codex/worklogs/subagents/2026-03-19/m13-lighting-worker3-docs.md`
- `.codex/worklogs/subagents/2026-03-19/m13-lighting-review.md`

## Commands run

- Source-of-truth and repo-state reads:
  - `sed -n '1,220p' plan.md`
  - `sed -n '1,280p' STATUS.md`
  - `sed -n '1,260p' AGENTS.md`
  - `git status --short --untracked-files=all`
- Investigation:
  - `sed -n '1,240p'` over the exported `stage.usda`
  - `rg -n ...` over `single.log` for warnings and light-related clues
  - `/isaac-sim/python.sh - <<'PY'` brightness measurements for pre-fix PNGs
  - `./scripts/isaac_python.sh - <<'PY'` runtime dome-light probe against one
    bottle USD
  - `/isaac-sim/python.sh - <<'PY'` brightness measurement of the dome-light
    probe output
- Lightweight validation:
  - `python -m py_compile src/isaacsim_agent/render/session.py src/isaacsim_agent/render/external_usd.py tests/test_external_usd_lighting.py`
  - `PYTHONPATH=src python - <<'PY'` import smoke for
    `ensure_external_usd_lighting` and `stage_has_lights`
  - `PYTHONPATH=src python -m unittest tests.test_external_usd_lighting -q`
  - `PYTHONPATH=src python -m unittest tests.test_render_cli_smoke tests.test_render_usd_batch_cli tests.test_render_grscenes_smoke -q`
  - `./scripts/isaac_python.sh - <<'PY'` in-memory `UsdLux` schema probe for
    `stage_has_lights(...)`
  - `git diff --check`
- Real rerenders:
  - `./scripts/isaac_python.sh scripts/run_grscenes_render_smoke.py --asset-root /cpfs/shared/simulation/zhuzihou/dev/isaacsim-agent/asset/render_test/grscenes_uid_subset_10/GRScenes_assets/bottle --output-root results/render_smokes/grscenes_bottle_lightingfix2_20260319 --mode single --save-stage`
  - `./scripts/isaac_python.sh scripts/run_grscenes_render_smoke.py --asset-root /cpfs/shared/simulation/zhuzihou/dev/isaacsim-agent/asset/render_test/grscenes_uid_subset_10/GRScenes_assets/bottle --output-root results/render_smokes/grscenes_bottle_lightingfix2_20260319 --mode batch --batch-limit 10 --save-stage`
  - `/isaac-sim/python.sh - <<'PY'` brightness measurements for the rerendered
    single and batch PNGs

## Validation results

- Pre-fix black-render confirmation:
  - single-asset rendered PNGs all measured `gray_mean = 0.0`
  - batch `front.png` outputs for all `10` bottle assets also measured
    `gray_mean = 0.0`
- Lighting probe:
  - a one-off runtime probe with an injected dome light changed the same
    bottle `front.png` from `gray_mean = 0.0` to `gray_mean = 241.629`
- Syntax validation:
  - `python -m py_compile src/isaacsim_agent/render/session.py src/isaacsim_agent/render/external_usd.py tests/test_external_usd_lighting.py`
    passed with:
    - no output
- Import smoke:
  - `PYTHONPATH=src python - <<'PY'`
    passed with:
    - `IMPORT_OK True True`
- New lighting regression tests:
  - `PYTHONPATH=src python -m unittest tests.test_external_usd_lighting -q`
    passed with:
    - `Ran 3 tests in 0.001s`
    - `OK`
- Existing portable smoke suites:
  - `PYTHONPATH=src python -m unittest tests.test_render_cli_smoke tests.test_render_usd_batch_cli tests.test_render_grscenes_smoke -q`
    passed with:
    - `Ran 17 tests in 1.711s`
    - `OK`
- Diff hygiene:
  - `git diff --check`
    passed with:
    - no output
- Real GRScenes single-asset rerender:
  - `./scripts/isaac_python.sh scripts/run_grscenes_render_smoke.py --asset-root /cpfs/shared/simulation/zhuzihou/dev/isaacsim-agent/asset/render_test/grscenes_uid_subset_10/GRScenes_assets/bottle --output-root results/render_smokes/grscenes_bottle_lightingfix2_20260319 --mode single --save-stage`
    passed with:
    - exit code `0`
    - selected asset:
      - `/cpfs/shared/simulation/zhuzihou/dev/isaacsim-agent/asset/render_test/grscenes_uid_subset_10/GRScenes_assets/bottle/0309dcb2f1cff82e56b5928b8258b489/usd/0309dcb2f1cff82e56b5928b8258b489.usd`
    - brightness:
      - `front mean = 89.046`
      - `three_quarter mean = 79.715`
      - `top mean = 115.002`
      - `side mean = 98.006`
- Real GRScenes batch rerender:
  - `./scripts/isaac_python.sh scripts/run_grscenes_render_smoke.py --asset-root /cpfs/shared/simulation/zhuzihou/dev/isaacsim-agent/asset/render_test/grscenes_uid_subset_10/GRScenes_assets/bottle --output-root results/render_smokes/grscenes_bottle_lightingfix2_20260319 --mode batch --batch-limit 10 --save-stage`
    passed with:
    - exit code `0`
    - summary counts:
      - `{'discovered': 10, 'success': 10, 'skipped': 0, 'failed': 0}`
    - batch front-image brightness range:
      - `min_mean = 68.168`
      - `max_mean = 98.985`
- Reviewer:
  - final judgement: `Accept`
  - reviewer `019d0525-2a30-7130-adb6-000b4b92c3b0` reported no blocking findings
  - only low-severity residual notes:
    - some rerender logs still contain source-asset mesh-normal warnings
    - the wrapper still preserves nested delegated output paths

## Remaining gaps

- decide later whether the wrapper should keep the current nested output layout
- decide later whether to add a checked-in portable real-asset fixture
- address per-asset mesh-normal issues only if a later milestone explicitly
  wants asset-quality cleanup

## Next recommended sub-milestone

- `M13 post-lighting polish decision`:
  - decide whether to keep the current conservative fallback-light rig as-is
  - decide whether wrapper output layout should be flattened or left thin
