# GRScenes Render Smoke

This note documents the local integration smoke for the GRScenes bottle subset.

## Purpose

This smoke exists to validate the phase-two external USD render path against a
small set of real local assets.

It is intentionally narrow:

- it is a local integration smoke, not a portable unit test
- it is not a dataset-level pipeline
- it is a thin wrapper over the existing phase-two CLIs:
  - `scripts/render_usd_asset.py`
  - `scripts/render_usd_batch.py`

## Lighting Behavior

- The GRScenes bottle assets can render fully black when the opened external
  USD stage has no effective lights.
- The external USD render path now treats that as a narrow fallback case:
  - if the asset stage already contains lights, those lights take precedence
  - if the asset stage has no effective lights, the external USD path may
    inject a minimal fallback light rig so the render is not fully black
- This is not a general look-development or art-direction system. It only
  addresses the no-light / black-render failure mode for the external USD path.

## Wrapper Interface

The wrapper entrypoint is:

- `scripts/run_grscenes_render_smoke.py`

The intended interface is:

- `--asset-root`
- `--output-root`
- `--mode {single,batch,both}`
- `--batch-limit`
- `--save-stage`
- `--headless` / `--no-headless`
- `--dry-run`

The wrapper discovers assets shaped like `*/usd/*.usd` under `--asset-root`
and then shells out to the existing phase-two CLIs.

## Local Asset Assumptions

This repo does not assume that the GRScenes bottle subset is checked in on
every machine.

In this environment, a known local asset root is:

```bash
/cpfs/shared/simulation/zhuzihou/dev/isaacsim-agent/asset/render_test/grscenes_uid_subset_10/GRScenes_assets/bottle
```

If that path is missing on another machine, pass a different local asset root
that contains per-asset directories with `usd/<uid>.usd`.

## Typical Commands

### 1. Dry run

Print the single-asset and batch commands without launching Isaac:

```bash
python scripts/run_grscenes_render_smoke.py \
  --asset-root /cpfs/shared/simulation/zhuzihou/dev/isaacsim-agent/asset/render_test/grscenes_uid_subset_10/GRScenes_assets/bottle \
  --output-root results/render_smokes/grscenes_bottle \
  --mode both \
  --batch-limit 10 \
  --save-stage \
  --dry-run
```

### 2. Single-asset smoke

Use one discovered USD asset and run the existing single-asset render CLI:

```bash
./scripts/isaac_python.sh scripts/run_grscenes_render_smoke.py \
  --asset-root /cpfs/shared/simulation/zhuzihou/dev/isaacsim-agent/asset/render_test/grscenes_uid_subset_10/GRScenes_assets/bottle \
  --output-root results/render_smokes/grscenes_bottle \
  --mode single \
  --save-stage
```

### 3. Batch smoke

Run the existing batch render CLI over the discovered bottle subset:

```bash
./scripts/isaac_python.sh scripts/run_grscenes_render_smoke.py \
  --asset-root /cpfs/shared/simulation/zhuzihou/dev/isaacsim-agent/asset/render_test/grscenes_uid_subset_10/GRScenes_assets/bottle \
  --output-root results/render_smokes/grscenes_bottle \
  --mode batch \
  --batch-limit 10 \
  --save-stage
```

## Expected Outputs

Single mode should ultimately produce the same outputs as
`scripts/render_usd_asset.py`, including:

- `<output-root>/single/.../front.png`
- `<output-root>/single/.../three_quarter.png`
- `<output-root>/single/.../top.png`
- `<output-root>/single/.../side.png`
- `<output-root>/single/.../stage.usda` when `--save-stage` is set

Batch mode should ultimately produce the same layout as
`scripts/render_usd_batch.py`, including:

- `<output-root>/batch/batch_summary.json`
- `<output-root>/batch/<relative_asset_path_without_ext>/...`

## Notes

- Keep using the synthetic unit tests for portable coverage.
- Use this GRScenes smoke only when you need real-asset validation.
- The dry-run example intentionally uses normal Python because it should not
  need Isaac imports; the real smoke examples use `scripts/isaac_python.sh`
  to keep the runtime assumptions explicit.
- A successful non-black render here means the fallback-lighting path did its
  job when the asset stage had no lights. It does not mean the output is
  automatically an ideal visual match to the asset's reference images.
- Existing reference PNGs inside the asset tree are useful for human sanity
  checks, but they are not treated here as a strict pixel-matching oracle.
