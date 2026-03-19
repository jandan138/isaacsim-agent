"""Tests for the optional GRScenes real-asset smoke wrapper."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
RENDER_GRSCENES_SMOKE_SCRIPT = REPO_ROOT / "scripts" / "run_grscenes_render_smoke.py"


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(SRC_ROOT), "PYTHONUNBUFFERED": "1"},
    )


def create_dataset_style_asset(asset_root: Path, uid: str) -> Path:
    usd_path = asset_root / uid / "usd" / f"{uid}.usd"
    usd_path.parent.mkdir(parents=True, exist_ok=True)
    usd_path.write_text("#usda 1.0\n", encoding="utf-8")
    return usd_path


@unittest.skipUnless(
    RENDER_GRSCENES_SMOKE_SCRIPT.is_file(),
    "run_grscenes_render_smoke.py is not integrated in this workspace",
)
class RenderGrscenesSmokeTest(unittest.TestCase):
    def test_help_surface(self) -> None:
        completed = run_script(str(RENDER_GRSCENES_SMOKE_SCRIPT), "--help")
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, 0, combined_output)
        self.assertIn("--asset-root", combined_output)
        self.assertIn("--output-root", combined_output)
        self.assertIn("--mode", combined_output)
        self.assertIn("--dry-run", combined_output)

    def test_missing_asset_root_reports_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_root = Path(temp_dir) / "does-not-exist"
            output_root = Path(temp_dir) / "output"
            completed = run_script(
                str(RENDER_GRSCENES_SMOKE_SCRIPT),
                "--asset-root",
                str(missing_root),
                "--output-root",
                str(output_root),
                "--mode",
                "single",
            )
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertNotEqual(completed.returncode, 0, combined_output)
        self.assertIn(str(missing_root), combined_output)

    def test_dry_run_single_mode_discovers_nested_usd_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            asset_root = Path(temp_dir) / "assets"
            output_root = Path(temp_dir) / "output"
            first_usd = create_dataset_style_asset(asset_root, "asset_a")
            create_dataset_style_asset(asset_root, "asset_b")

            completed = run_script(
                str(RENDER_GRSCENES_SMOKE_SCRIPT),
                "--asset-root",
                str(asset_root),
                "--output-root",
                str(output_root),
                "--mode",
                "single",
                "--dry-run",
            )

        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, 0, combined_output)
        self.assertIn("render_usd_asset.py", combined_output)
        self.assertIn(str(first_usd), combined_output)
        self.assertIn(str(output_root), combined_output)

    def test_dry_run_batch_mode_preserves_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            asset_root = Path(temp_dir) / "assets"
            output_root = Path(temp_dir) / "output"
            create_dataset_style_asset(asset_root, "asset_a")
            create_dataset_style_asset(asset_root, "asset_b")

            completed = run_script(
                str(RENDER_GRSCENES_SMOKE_SCRIPT),
                "--asset-root",
                str(asset_root),
                "--output-root",
                str(output_root),
                "--mode",
                "batch",
                "--batch-limit",
                "2",
                "--dry-run",
                "--save-stage",
            )

        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, 0, combined_output)
        self.assertIn("render_usd_batch.py", combined_output)
        self.assertIn("--limit", combined_output)
        self.assertIn("2", combined_output)
        self.assertIn("--save-stage", combined_output)

    def test_empty_asset_root_reports_no_usd_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            asset_root = Path(temp_dir) / "assets"
            asset_root.mkdir(parents=True, exist_ok=True)
            output_root = Path(temp_dir) / "output"

            completed = run_script(
                str(RENDER_GRSCENES_SMOKE_SCRIPT),
                "--asset-root",
                str(asset_root),
                "--output-root",
                str(output_root),
                "--mode",
                "both",
                "--dry-run",
            )

        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertNotEqual(completed.returncode, 0, combined_output)
        self.assertIn(str(asset_root), combined_output)


if __name__ == "__main__":
    unittest.main()
