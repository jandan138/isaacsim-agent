#!/usr/bin/env python3
"""Thin smoke wrapper for running GRScenes-style external USD render checks."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
ISAAC_WRAPPER = REPO_ROOT / "scripts" / "isaac_python.sh"
RENDER_USD_ASSET_SCRIPT = REPO_ROOT / "scripts" / "render_usd_asset.py"
RENDER_USD_BATCH_SCRIPT = REPO_ROOT / "scripts" / "render_usd_batch.py"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run thin single/batch render smokes against a GRScenes-style asset root."
    )
    parser.add_argument("--asset-root", required=True, help="Root containing GRScenes-style asset directories.")
    parser.add_argument("--output-root", required=True, help="Directory where smoke outputs should be written.")
    parser.add_argument(
        "--mode",
        choices=("single", "batch", "both"),
        default="both",
        help="Which smoke flow to run. Default: both.",
    )
    parser.add_argument("--batch-limit", type=int, default=None, help="Optional limit passed through to batch mode.")
    parser.add_argument("--save-stage", action="store_true", help="Request stage export for the delegated renders.")
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Launch delegated renders headless. Use --no-headless for local debugging.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the commands that would run without executing.")
    return parser


def discover_grscenes_usd_assets(asset_root: Path) -> list[Path]:
    return sorted(
        path
        for path in asset_root.glob("*/usd/*.usd")
        if path.is_file() and path.suffix.lower() == ".usd"
    )


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


def _command_prefix(script_path: Path) -> list[str]:
    if ISAAC_WRAPPER.is_file() and _running_in_isaac_runtime():
        return [str(ISAAC_WRAPPER), str(script_path)]
    return [sys.executable, str(script_path)]


def build_single_command(args: argparse.Namespace, asset_root: Path, selected_asset: Path, output_root: Path) -> list[str]:
    single_output_dir = output_root / "single" / selected_asset.relative_to(asset_root).with_suffix("")
    command = _command_prefix(RENDER_USD_ASSET_SCRIPT)
    command.extend(
        [
            "--usd-path",
            str(selected_asset),
            "--output-dir",
            str(single_output_dir),
            "--headless" if args.headless else "--no-headless",
        ]
    )
    if args.save_stage:
        command.append("--save-stage")
    return command


def build_batch_command(args: argparse.Namespace, asset_root: Path, output_root: Path) -> list[str]:
    command = _command_prefix(RENDER_USD_BATCH_SCRIPT)
    command.extend(
        [
            "--input-root",
            str(asset_root),
            "--output-root",
            str(output_root / "batch"),
            "--headless" if args.headless else "--no-headless",
        ]
    )
    if args.batch_limit is not None:
        command.extend(["--limit", str(args.batch_limit)])
    if args.save_stage:
        command.append("--save-stage")
    return command


def _run_command(command: list[str]) -> int:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        env={**os.environ, "PYTHONPATH": str(SRC_ROOT), "PYTHONUNBUFFERED": "1"},
    )
    return completed.returncode


def main() -> int:
    args = build_parser().parse_args()
    asset_root = Path(args.asset_root).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()

    if not asset_root.is_dir():
        print(f"RENDER_GRSCENES_SMOKE_FAILED: asset root was not a directory: {asset_root}", file=sys.stderr)
        return 1

    assets = discover_grscenes_usd_assets(asset_root)
    if not assets:
        print(f"RENDER_GRSCENES_SMOKE_FAILED: no GRScenes-style USD assets found under {asset_root}", file=sys.stderr)
        return 1

    print("Asset root:", asset_root)
    print("Output root:", output_root)
    print("Discovered USD assets:", len(assets))

    commands: list[tuple[str, list[str]]] = []
    if args.mode in {"single", "both"}:
        selected_asset = assets[0]
        print("Selected single asset:", selected_asset)
        commands.append(("single", build_single_command(args, asset_root, selected_asset, output_root)))
    if args.mode in {"batch", "both"}:
        commands.append(("batch", build_batch_command(args, asset_root, output_root)))

    for label, command in commands:
        print(f"{label.upper()} COMMAND:", " ".join(command))

    if args.dry_run:
        print("RENDER_GRSCENES_SMOKE_DRY_RUN")
        return 0

    output_root.mkdir(parents=True, exist_ok=True)
    exit_code = 0
    for label, command in commands:
        print(f"RUNNING_{label.upper()}_SMOKE")
        result_code = _run_command(command)
        if result_code != 0:
            exit_code = 1
            print(f"RENDER_GRSCENES_SMOKE_FAILED: {label} smoke returned {result_code}", file=sys.stderr)

    if exit_code == 0:
        print("RENDER_GRSCENES_SMOKE_OK")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
