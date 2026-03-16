#!/usr/bin/env python3
"""Repo-facing environment smoke test for the uv workflow."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def resolve_isaac_root() -> str | None:
    candidates = []
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the uv-based repo environment.")
    parser.add_argument("--json-out", type=Path, default=None, help="Optional path to write a JSON report.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    uv_path = shutil.which("uv")
    uv_version = None
    if uv_path:
        completed = subprocess.run([uv_path, "--version"], capture_output=True, text=True, check=False)
        uv_version = completed.stdout.strip() or completed.stderr.strip()

    report = {
        "repo_root": str(repo_root),
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "python_ok": sys.version_info[:2] == (3, 10),
        "uv_found": bool(uv_path),
        "uv_path": uv_path,
        "uv_version": uv_version,
        "isaac_sim_root_detected": resolve_isaac_root(),
    }

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Repo root:", report["repo_root"])
    print("Python executable:", report["python_executable"])
    print("Python version:", report["python_version"])
    print("uv found:", report["uv_found"])
    if uv_version:
        print("uv version:", uv_version)
    print("Isaac Sim root detected:", report["isaac_sim_root_detected"] or "not found")

    if not report["uv_found"]:
        print("ERROR: uv is not available in PATH.", file=sys.stderr)
        return 1

    if not report["python_ok"]:
        print("ERROR: expected Python 3.10 for this project.", file=sys.stderr)
        return 1

    print("SMOKE_TEST_ENV_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
