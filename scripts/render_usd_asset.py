#!/usr/bin/env python3
"""Render one external USD asset with the shared Isaac render package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


EXPECTED_MISSING_DEPENDENCY = 3


class RenderEntrypointBlocked(RuntimeError):
    """Raised when the Isaac-backed render path is unavailable."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render one external USD asset.")
    parser.add_argument("--usd-path", required=True, help="Path to the USD or USDA asset to render.")
    parser.add_argument("--output-dir", required=True, help="Directory where rendered outputs should be written.")
    parser.add_argument("--width", type=int, default=1280, help="Requested output width in pixels.")
    parser.add_argument("--height", type=int, default=720, help="Requested output height in pixels.")
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Launch the render session headless. Use --no-headless for local debugging.",
    )
    parser.add_argument("--skip-existing", action="store_true", help="Skip work if the requested outputs already exist.")
    parser.add_argument("--save-stage", action="store_true", help="Export `stage.usda` alongside the PNG output.")
    return parser


def _resolve_render_hooks():
    try:
        from isaacsim_agent.render import DEFAULT_EXTERNAL_USD_VIEWS  # type: ignore
        from isaacsim_agent.render import RenderBackendUnavailableError  # type: ignore
        from isaacsim_agent.render import RenderSessionConfig  # type: ignore
        from isaacsim_agent.render import build_bbox_camera_views  # type: ignore
        from isaacsim_agent.render import load_external_usd_stage  # type: ignore
        from isaacsim_agent.render import render_rgb_views  # type: ignore
        from isaacsim_agent.render import start_render_app  # type: ignore
    except ModuleNotFoundError as exc:
        raise RenderEntrypointBlocked(
            "isaacsim_agent.render is not importable from the current Python environment."
        ) from exc
    except ImportError as exc:
        raise RenderEntrypointBlocked(
            "The shared render package does not yet expose the external USD render hooks."
        ) from exc

    return (
        tuple(DEFAULT_EXTERNAL_USD_VIEWS),
        RenderBackendUnavailableError,
        RenderSessionConfig,
        build_bbox_camera_views,
        load_external_usd_stage,
        render_rgb_views,
        start_render_app,
    )


def _requested_views(default_views: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(default_views)


def _stage_output_path(output_dir: Path) -> Path:
    return output_dir / "stage.usda"


def _requested_output_paths(output_dir: Path, requested_views: tuple[str, ...], save_stage: bool) -> list[Path]:
    paths = [output_dir / f"{view_name}.png" for view_name in requested_views]
    if save_stage:
        paths.append(_stage_output_path(output_dir))
    return paths


def _should_skip_existing(output_dir: Path, requested_views: tuple[str, ...], save_stage: bool) -> bool:
    return all(path.is_file() for path in _requested_output_paths(output_dir, requested_views, save_stage))


def _export_stage(stage, output_dir: Path) -> Path:
    stage_path = _stage_output_path(output_dir)
    stage.Export(str(stage_path))
    return stage_path


def _render_asset(args: argparse.Namespace) -> dict[str, Any]:
    (
        default_views,
        RenderBackendUnavailableError,
        RenderSessionConfig,
        build_bbox_camera_views,
        load_external_usd_stage,
        render_rgb_views,
        start_render_app,
    ) = _resolve_render_hooks()
    requested_views = _requested_views(default_views)
    usd_path = Path(args.usd_path).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    if args.skip_existing and _should_skip_existing(output_dir, requested_views, args.save_stage):
        return {
            "status": "skipped",
            "output_dir": output_dir,
            "requested_views": requested_views,
            "session": None,
            "stage_path": _stage_output_path(output_dir) if args.save_stage else None,
            "usd_path": usd_path,
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    session_config = RenderSessionConfig(headless=args.headless)
    try:
        session = start_render_app(config=session_config)
    except RenderBackendUnavailableError as exc:
        raise RenderEntrypointBlocked(str(exc)) from exc

    stage = load_external_usd_stage(session=session, usd_path=usd_path)
    views = build_bbox_camera_views(
        stage=stage,
        width=args.width,
        height=args.height,
        selected_views=requested_views,
    )
    render_result = render_rgb_views(session=session, views=views, output_dir=output_dir)
    stage_path = _export_stage(stage, output_dir) if args.save_stage else None
    return {
        "status": "rendered",
        "output_dir": output_dir,
        "render_result": render_result,
        "requested_views": requested_views,
        "session": session,
        "stage_path": stage_path,
        "usd_path": usd_path,
    }


def main() -> int:
    args = build_parser().parse_args()
    payload: dict[str, Any] | None = None
    try:
        payload = _render_asset(args)
    except RenderEntrypointBlocked as exc:
        print(f"EXPECTED_MISSING_DEPENDENCY: {exc}", file=sys.stderr)
        return EXPECTED_MISSING_DEPENDENCY
    except Exception as exc:
        print(f"RENDER_USD_ASSET_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    try:
        print("USD path:", payload["usd_path"])
        print("Output directory:", payload["output_dir"])
        if payload["status"] == "skipped":
            print("Requested views:", ", ".join(payload["requested_views"]))
            print("RENDER_USD_ASSET_SKIPPED")
            return 0

        for artifact in payload["render_result"] or []:
            print("Rendered:", artifact.image_path)
        if payload["stage_path"] is not None:
            print("Stage export:", payload["stage_path"])
        print("RENDER_USD_ASSET_OK")
        return 0
    finally:
        session = payload.get("session") if payload is not None else None
        close_fn = getattr(session, "close", None)
        if callable(close_fn):
            close_fn()


if __name__ == "__main__":
    raise SystemExit(main())
