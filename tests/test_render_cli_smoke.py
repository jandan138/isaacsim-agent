"""Smoke tests for render CLI entrypoints."""

from __future__ import annotations

import json
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

EXPECTED_MISSING_DEPENDENCY = 3
RENDER_DEMO_BLOCKED_EXIT = 2
BATCH_FAILURE_EXIT = 1
DEFAULT_VIEWS = ("front", "three_quarter", "top", "side")


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(SRC_ROOT), "PYTHONUNBUFFERED": "1"},
    )


def create_usda_asset(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """#usda 1.0
(
    defaultPrim = "World"
)

def Xform "World"
{
    def Cube "Asset"
    {
        double size = 1
    }
}
""",
        encoding="utf-8",
    )


def populate_expected_asset_outputs(output_dir: Path, *, save_stage: bool = False) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for view_name in DEFAULT_VIEWS:
        (output_dir / f"{view_name}.png").write_bytes(b"fake-png")
    if save_stage:
        (output_dir / "stage.usda").write_text("#usda 1.0\n", encoding="utf-8")


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
        self.assertEqual(completed.returncode, RENDER_DEMO_BLOCKED_EXIT, combined_output)
        self.assertIn("RENDER_DEMO_VIEWS_BLOCKED", combined_output)

    def test_render_usd_asset_reports_expected_missing_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            usd_path = Path(temp_dir) / "scene.usda"
            create_usda_asset(usd_path)
            completed = run_script(
                str(RENDER_USD_ASSET_SCRIPT),
                "--usd-path",
                str(usd_path),
                "--output-dir",
                temp_dir,
            )
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, EXPECTED_MISSING_DEPENDENCY, combined_output)
        self.assertIn("EXPECTED_MISSING_DEPENDENCY", combined_output)

    def test_render_usd_asset_skip_existing_short_circuits_without_isaac(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            usd_path = Path(temp_dir) / "scene.usda"
            output_dir = Path(temp_dir) / "renders"
            create_usda_asset(usd_path)
            populate_expected_asset_outputs(output_dir, save_stage=True)
            completed = run_script(
                str(RENDER_USD_ASSET_SCRIPT),
                "--usd-path",
                str(usd_path),
                "--output-dir",
                str(output_dir),
                "--skip-existing",
                "--save-stage",
            )
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, 0, combined_output)
        self.assertIn("RENDER_USD_ASSET_SKIPPED", combined_output)

    def test_render_usd_batch_records_failed_asset_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_root = Path(temp_dir) / "input"
            output_root = Path(temp_dir) / "output"
            asset_path = input_root / "scene.usda"
            create_usda_asset(asset_path)

            completed = run_script(
                str(RENDER_USD_BATCH_SCRIPT),
                "--input-root",
                str(input_root),
                "--output-root",
                str(output_root),
            )
            summary = json.loads((output_root / "batch_summary.json").read_text(encoding="utf-8"))

        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, BATCH_FAILURE_EXIT, combined_output)
        self.assertEqual(summary["counts"], {"discovered": 1, "success": 0, "skipped": 0, "failed": 1})
        self.assertEqual(summary["assets"][0]["returncode"], EXPECTED_MISSING_DEPENDENCY)
        self.assertEqual(summary["assets"][0]["status"], "failed")

    def test_render_usd_batch_discovers_nested_assets_and_preserves_isolation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_root = Path(temp_dir) / "input"
            output_root = Path(temp_dir) / "output"
            skipped_asset = input_root / "nested" / "skip_me.usda"
            failed_asset = input_root / "nested" / "fail_me.usda"
            create_usda_asset(skipped_asset)
            create_usda_asset(failed_asset)
            populate_expected_asset_outputs(output_root / "nested" / "skip_me")

            completed = run_script(
                str(RENDER_USD_BATCH_SCRIPT),
                "--input-root",
                str(input_root),
                "--output-root",
                str(output_root),
                "--skip-existing",
            )
            summary = json.loads((output_root / "batch_summary.json").read_text(encoding="utf-8"))

        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, BATCH_FAILURE_EXIT, combined_output)
        self.assertEqual(summary["counts"], {"discovered": 2, "success": 0, "skipped": 1, "failed": 1})
        self.assertEqual(len(summary["assets"]), 2)
        self.assertEqual(summary["assets"][0]["output_dir"], str((output_root / "nested" / "fail_me").resolve()))
        self.assertEqual(summary["assets"][1]["output_dir"], str((output_root / "nested" / "skip_me").resolve()))
        self.assertEqual({entry["status"] for entry in summary["assets"]}, {"failed", "skipped"})

    def test_render_usd_batch_all_skipped_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_root = Path(temp_dir) / "input"
            output_root = Path(temp_dir) / "output"
            first_asset = input_root / "asset_a.usda"
            second_asset = input_root / "subdir" / "asset_b.usda"
            create_usda_asset(first_asset)
            create_usda_asset(second_asset)
            populate_expected_asset_outputs(output_root / "asset_a")
            populate_expected_asset_outputs(output_root / "subdir" / "asset_b")

            completed = run_script(
                str(RENDER_USD_BATCH_SCRIPT),
                "--input-root",
                str(input_root),
                "--output-root",
                str(output_root),
                "--skip-existing",
            )
            summary = json.loads((output_root / "batch_summary.json").read_text(encoding="utf-8"))

        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, 0, combined_output)
        self.assertEqual(summary["counts"], {"discovered": 2, "success": 0, "skipped": 2, "failed": 0})
        self.assertEqual([entry["status"] for entry in summary["assets"]], ["skipped", "skipped"])
        self.assertIn("RENDER_USD_BATCH_OK", combined_output)


if __name__ == "__main__":
    unittest.main()
