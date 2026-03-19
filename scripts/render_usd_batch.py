#!/usr/bin/env python3
"""Render batches of external USD assets with per-asset process isolation."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
ISAAC_WRAPPER = REPO_ROOT / "scripts" / "isaac_python.sh"
RENDER_USD_ASSET_SCRIPT = REPO_ROOT / "scripts" / "render_usd_asset.py"

SUMMARY_PATH_NAME = "batch_summary.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render a batch of external USD assets.")
    parser.add_argument("--input-root", required=True, help="Root directory containing USD assets.")
    parser.add_argument("--output-root", required=True, help="Directory where rendered outputs would be written.")
    parser.add_argument(
        "--glob",
        default="**/*.usd*",
        help="Glob pattern used to discover USD assets under the input root.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional cap on the number of assets to visit.")
    parser.add_argument("--skip-existing", action="store_true", help="Skip assets whose outputs already exist.")
    parser.add_argument("--save-stage", action="store_true", help="Request stage export for each rendered asset.")
    parser.add_argument("--width", type=int, default=1280, help="Requested output width in pixels.")
    parser.add_argument("--height", type=int, default=720, help="Requested output height in pixels.")
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Launch the render path headless. Use --no-headless for local debugging.",
    )
    return parser


def discover_assets(input_root: Path, pattern: str, limit: int | None = None) -> list[Path]:
    assets = sorted(
        path
        for path in input_root.glob(pattern)
        if path.is_file() and path.suffix.lower() in {".usd", ".usda", ".usdc"}
    )
    if limit is not None:
        return assets[:limit]
    return assets


def build_asset_output_dir(input_root: Path, output_root: Path, asset_path: Path) -> Path:
    relative_asset_path = asset_path.relative_to(input_root)
    return output_root / relative_asset_path.with_suffix("")


def _can_import_isaacsim() -> bool:
    try:
        import isaacsim  # type: ignore  # noqa: F401
    except ModuleNotFoundError:
        return False
    return True


def _running_in_isaac_runtime() -> bool:
    if _can_import_isaacsim():
        return True

    executable = Path(sys.executable).expanduser().resolve().as_posix().lower()
    if "isaac-sim" in executable or "isaac_sim-" in executable:
        return True

    carb_app_path = os.environ.get("CARB_APP_PATH", "").lower()
    if "isaac-sim" in carb_app_path or "isaac_sim-" in carb_app_path:
        return True

    return False


def build_asset_command(args: argparse.Namespace, asset_path: Path, asset_output_dir: Path) -> list[str]:
    if ISAAC_WRAPPER.is_file() and _running_in_isaac_runtime():
        command = [str(ISAAC_WRAPPER), str(RENDER_USD_ASSET_SCRIPT)]
    else:
        command = [sys.executable, str(RENDER_USD_ASSET_SCRIPT)]

    command.extend(
        [
            "--usd-path",
            str(asset_path),
            "--output-dir",
            str(asset_output_dir),
            "--width",
            str(args.width),
            "--height",
            str(args.height),
        ]
    )
    command.append("--headless" if args.headless else "--no-headless")
    if args.skip_existing:
        command.append("--skip-existing")
    if args.save_stage:
        command.append("--save-stage")
    return command


def classify_result(completed: subprocess.CompletedProcess[str]) -> str:
    combined_output = f"{completed.stdout}\n{completed.stderr}"
    if completed.returncode == 0 and "RENDER_USD_ASSET_SKIPPED" in combined_output:
        return "skipped"
    if completed.returncode == 0:
        return "success"
    return "failed"


def _summarize_stream(text: str, *, max_chars: int = 4000) -> str:
    if len(text) <= max_chars:
        return text
    truncated_chars = len(text) - max_chars
    return f"...[truncated {truncated_chars} chars]...\n{text[-max_chars:]}"


def write_summary(output_root: Path, summary: dict[str, Any]) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    summary_path = output_root / SUMMARY_PATH_NAME
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary_path


def main() -> int:
    args = build_parser().parse_args()
    input_root = Path(args.input_root).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()

    if not input_root.is_dir():
        summary = {
            "input_root": str(input_root),
            "output_root": str(output_root),
            "glob": args.glob,
            "limit": args.limit,
            "assets": [],
            "results": [],
            "counts": {"discovered": 0, "success": 0, "skipped": 0, "failed": 1},
            "error": f"Input root was not a directory: {input_root}",
        }
        summary_path = write_summary(output_root, summary)
        print("Input root:", input_root)
        print("Output root:", output_root)
        print(f"RENDER_USD_BATCH_FAILED: input root was not a directory: {input_root}", file=sys.stderr)
        print("Batch summary:", summary_path)
        return 1

    assets = discover_assets(input_root, args.glob, args.limit)
    results: list[dict[str, Any]] = []

    print("Input root:", input_root)
    print("Output root:", output_root)
    print("Discovered assets:", len(assets))

    for asset_path in assets:
        asset_output_dir = build_asset_output_dir(input_root, output_root, asset_path)
        command = build_asset_command(args, asset_path, asset_output_dir)
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "PYTHONPATH": str(SRC_ROOT), "PYTHONUNBUFFERED": "1"},
        )
        status = classify_result(completed)
        result = {
            "asset_path": str(asset_path.resolve()),
            "relative_asset_path": str(asset_path.relative_to(input_root)),
            "output_dir": str(asset_output_dir.resolve()),
            "status": status,
            "returncode": completed.returncode,
            "stdout": _summarize_stream(completed.stdout),
            "stderr": _summarize_stream(completed.stderr),
            "command": command,
        }
        results.append(result)
        print(f"Asset status: {status} :: {asset_path}")

    counts = {
        "discovered": len(results),
        "success": sum(1 for item in results if item["status"] == "success"),
        "skipped": sum(1 for item in results if item["status"] == "skipped"),
        "failed": sum(1 for item in results if item["status"] == "failed"),
    }
    summary = {
        "input_root": str(input_root),
        "output_root": str(output_root),
        "glob": args.glob,
        "limit": args.limit,
        "skip_existing": args.skip_existing,
        "save_stage": args.save_stage,
        "assets": results,
        "results": results,
        "counts": counts,
    }
    summary_path = write_summary(output_root, summary)
    exit_code = 0 if counts["failed"] == 0 else 1
    print("Batch summary:", summary_path)
    print("RENDER_USD_BATCH_OK" if exit_code == 0 else "RENDER_USD_BATCH_FAILED")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
