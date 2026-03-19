"""Smoke tests for the phase-one render CLI surfaces."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
RENDER_DEMO_SCRIPT = REPO_ROOT / "scripts" / "render_demo_views.py"
RENDER_USD_ASSET_SCRIPT = REPO_ROOT / "scripts" / "render_usd_asset.py"
RENDER_USD_BATCH_SCRIPT = REPO_ROOT / "scripts" / "render_usd_batch.py"
PHASE2_NOT_IMPLEMENTED_EXIT = 2


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(SRC_ROOT), "PYTHONUNBUFFERED": "1"},
    )


class RenderCliSmokeTest(unittest.TestCase):
    def test_render_demo_views_help(self) -> None:
        completed = run_script(str(RENDER_DEMO_SCRIPT), "--help")
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, 0, combined_output)
        self.assertIn("Render phase-one project demo views.", combined_output)
        self.assertIn("--task-type", combined_output)

    def test_render_usd_asset_help(self) -> None:
        completed = run_script(str(RENDER_USD_ASSET_SCRIPT), "--help")
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, 0, combined_output)
        self.assertIn("Render one external USD asset", combined_output)
        self.assertIn("--usd-path", combined_output)

    def test_render_usd_batch_help(self) -> None:
        completed = run_script(str(RENDER_USD_BATCH_SCRIPT), "--help")
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, 0, combined_output)
        self.assertIn("Render a batch of external USD assets", combined_output)
        self.assertIn("--input-root", combined_output)

    def test_render_demo_views_reports_blocked_without_isaac_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            completed = run_script(
                str(RENDER_DEMO_SCRIPT),
                "--task-type",
                "navigation",
                "--output-dir",
                temp_dir,
            )
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, PHASE2_NOT_IMPLEMENTED_EXIT, combined_output)
        self.assertIn("RENDER_DEMO_VIEWS_BLOCKED", combined_output)

    def test_render_usd_asset_reports_phase_two_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            completed = run_script(
                str(RENDER_USD_ASSET_SCRIPT),
                "--usd-path",
                str(Path(temp_dir) / "scene.usd"),
                "--output-dir",
                temp_dir,
            )
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, PHASE2_NOT_IMPLEMENTED_EXIT, combined_output)
        self.assertIn("PHASE2_NOT_IMPLEMENTED", combined_output)

    def test_render_usd_batch_reports_phase_two_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            completed = run_script(
                str(RENDER_USD_BATCH_SCRIPT),
                "--input-root",
                temp_dir,
                "--output-root",
                temp_dir,
            )
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, PHASE2_NOT_IMPLEMENTED_EXIT, combined_output)
        self.assertIn("PHASE2_NOT_IMPLEMENTED", combined_output)


if __name__ == "__main__":
    unittest.main()
