"""Unit tests for the phase-two external USD batch CLI behavior."""

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
RENDER_USD_ASSET_SCRIPT = REPO_ROOT / "scripts" / "render_usd_asset.py"
RENDER_USD_BATCH_SCRIPT = REPO_ROOT / "scripts" / "render_usd_batch.py"
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


def touch_skip_outputs(output_dir: Path, *, save_stage: bool = False) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
        b"\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01"
        b"\x0b\xe7\x02\x9d"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    for view_name in DEFAULT_VIEWS:
        (output_dir / f"{view_name}.png").write_bytes(png_bytes)
    if save_stage:
        (output_dir / "stage.usda").write_text("#usda 1.0\n", encoding="utf-8")


class RenderUsdBatchCliTest(unittest.TestCase):
    def test_render_usd_asset_skip_existing_short_circuits_without_isaac(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            usd_path = temp_path / "scene.usda"
            output_dir = temp_path / "renders"
            usd_path.write_text("#usda 1.0\n", encoding="utf-8")
            touch_skip_outputs(output_dir, save_stage=True)

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

    def test_render_usd_batch_skip_existing_writes_skipped_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_root = temp_path / "input"
            output_root = temp_path / "output"
            asset_path = input_root / "nested" / "scene.usda"
            asset_path.parent.mkdir(parents=True)
            asset_path.write_text("#usda 1.0\n", encoding="utf-8")
            touch_skip_outputs(output_root / "nested" / "scene", save_stage=True)

            completed = run_script(
                str(RENDER_USD_BATCH_SCRIPT),
                "--input-root",
                str(input_root),
                "--output-root",
                str(output_root),
                "--skip-existing",
                "--save-stage",
            )
            summary = json.loads((output_root / "batch_summary.json").read_text(encoding="utf-8"))

        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, 0, combined_output)
        self.assertEqual(summary["counts"]["skipped"], 1)
        self.assertEqual(summary["results"][0]["status"], "skipped")
        self.assertEqual(summary["results"][0]["output_dir"], str(output_root / "nested" / "scene"))

    def test_render_usd_batch_discovery_respects_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_root = temp_path / "input"
            output_root = temp_path / "output"
            asset_paths = [
                input_root / "a" / "one.usda",
                input_root / "b" / "two.usda",
                input_root / "c" / "three.usda",
            ]
            for asset_path in asset_paths:
                asset_path.parent.mkdir(parents=True, exist_ok=True)
                asset_path.write_text("#usda 1.0\n", encoding="utf-8")
                touch_skip_outputs(output_root / asset_path.relative_to(input_root).with_suffix(""))

            completed = run_script(
                str(RENDER_USD_BATCH_SCRIPT),
                "--input-root",
                str(input_root),
                "--output-root",
                str(output_root),
                "--skip-existing",
                "--limit",
                "2",
            )
            summary = json.loads((output_root / "batch_summary.json").read_text(encoding="utf-8"))

        combined_output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, 0, combined_output)
        self.assertEqual(len(summary["results"]), 2)
        self.assertEqual(summary["counts"]["failed"], 0)


if __name__ == "__main__":
    unittest.main()
