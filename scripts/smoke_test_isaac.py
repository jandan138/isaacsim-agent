#!/usr/bin/env python3
"""Minimal Isaac Sim smoke test with explicit missing-dependency diagnostics."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


EXPECTED_MISSING_DEPENDENCY = 3


def resolve_isaac_root() -> str | None:
    candidates: list[Path] = []

    env_root = os.environ.get("ISAAC_SIM_ROOT")
    if env_root:
        candidates.append(Path(env_root))

    candidates.append(Path("/isaac-sim"))

    ov_root = Path.home() / ".local" / "share" / "ov" / "pkg"
    if ov_root.is_dir():
        candidates.extend(sorted(ov_root.glob("isaac_sim-*"), reverse=True))

    candidates.extend(
        [
            Path("/opt/nvidia/isaac-sim"),
            Path("/opt/NVIDIA/isaac-sim"),
            Path("/opt/omniverse/isaac-sim"),
        ]
    )

    for candidate in candidates:
        if (candidate / "python.sh").is_file():
            return str(candidate)

    return None


def read_isaac_version(isaac_root: str | None) -> str | None:
    if isaac_root is None:
        return None

    version_path = Path(isaac_root) / "VERSION"
    if not version_path.is_file():
        return None

    return version_path.read_text(encoding="utf-8").strip()


def write_report(path: Path | None, report: dict[str, object]) -> None:
    if path is None:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def missing_dependency(message: str, args: argparse.Namespace, isaac_root: str | None, version: str | None) -> int:
    report = {
        "status": "expected_missing_dependency",
        "message": message,
        "isaac_sim_root": isaac_root,
        "isaac_sim_version": version,
        "python_executable": sys.executable,
        "hint": "Run via ./scripts/isaac_python.sh scripts/smoke_test_isaac.py",
    }
    write_report(args.json_out, report)
    print(f"EXPECTED_MISSING_DEPENDENCY: {message}", file=sys.stderr)
    if isaac_root:
        print(f"Detected Isaac Sim root: {isaac_root}", file=sys.stderr)
    print("Hint: run via ./scripts/isaac_python.sh scripts/smoke_test_isaac.py", file=sys.stderr)
    return EXPECTED_MISSING_DEPENDENCY


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a minimal Isaac Sim smoke test.")
    parser.add_argument("--json-out", type=Path, default=None, help="Optional path to write a JSON report.")
    args = parser.parse_args()

    isaac_root = resolve_isaac_root()
    isaac_version = read_isaac_version(isaac_root)

    if isaac_root is None:
        return missing_dependency("Isaac Sim installation was not found.", args, isaac_root, isaac_version)

    try:
        from isaacsim import SimulationApp  # type: ignore
    except ModuleNotFoundError:
        return missing_dependency(
            "Current Python interpreter cannot import Isaac Sim modules.",
            args,
            isaac_root,
            isaac_version,
        )

    simulation_app = None
    try:
        simulation_app = SimulationApp({"headless": True, "sync_loads": True})

        import omni.kit.app  # type: ignore
        import omni.usd  # type: ignore
        from pxr import UsdGeom  # type: ignore

        context = omni.usd.get_context()
        if not context.new_stage():
            raise RuntimeError("omni.usd.get_context().new_stage() returned False")

        stage = context.get_stage()
        if stage is None:
            raise RuntimeError("Isaac Sim returned no active USD stage")

        world_prim = UsdGeom.Xform.Define(stage, "/World")
        if not world_prim:
            raise RuntimeError("Failed to define /World on the stage")

        app = omni.kit.app.get_app()
        kit_version = app.get_build_version()
        report = {
            "status": "ok",
            "isaac_sim_root": isaac_root,
            "isaac_sim_version": isaac_version,
            "kit_version": kit_version,
            "python_executable": sys.executable,
            "world_prim_path": "/World",
        }
        write_report(args.json_out, report)

        print("Isaac Sim root:", isaac_root)
        print("Isaac Sim version:", isaac_version or "unknown")
        print("Kit version:", kit_version)
        print("World prim:", "/World")
        print("SMOKE_TEST_OK")
        return 0
    except Exception as exc:
        report = {
            "status": "error",
            "isaac_sim_root": isaac_root,
            "isaac_sim_version": isaac_version,
            "python_executable": sys.executable,
            "error": f"{type(exc).__name__}: {exc}",
        }
        write_report(args.json_out, report)
        print(f"ERROR: Isaac Sim smoke test failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    finally:
        if simulation_app is not None:
            simulation_app.close()


if __name__ == "__main__":
    raise SystemExit(main())
