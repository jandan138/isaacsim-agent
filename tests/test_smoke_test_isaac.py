"""Entry-point tests for the Isaac Sim smoke test script."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SMOKE_TEST = REPO_ROOT / "scripts" / "smoke_test_isaac.py"
ISAAC_WRAPPER = REPO_ROOT / "scripts" / "isaac_python.sh"
EXPECTED_MISSING_DEPENDENCY = 3


def resolve_isaac_root() -> Path | None:
    env_root = os.environ.get("ISAAC_SIM_ROOT")
    candidates = []
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
            return candidate
    return None


class IsaacSmokeEntrypointTest(unittest.TestCase):
    def test_smoke_test_entrypoint(self) -> None:
        report_path = REPO_ROOT / "results" / "setup" / "test_smoke_test_isaac.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        isaac_root = resolve_isaac_root()

        if isaac_root is not None and ISAAC_WRAPPER.is_file():
            command = [str(ISAAC_WRAPPER), str(SMOKE_TEST), "--json-out", str(report_path)]
            expected_code = 0
            expected_marker = "SMOKE_TEST_OK"
        else:
            command = [sys.executable, str(SMOKE_TEST), "--json-out", str(report_path)]
            expected_code = EXPECTED_MISSING_DEPENDENCY
            expected_marker = "EXPECTED_MISSING_DEPENDENCY"

        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )

        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, expected_code, combined_output)
        self.assertIn(expected_marker, combined_output)
        self.assertTrue(report_path.is_file(), "Expected JSON report was not created")


if __name__ == "__main__":
    unittest.main()
