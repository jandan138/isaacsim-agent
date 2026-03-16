"""Coverage for Block A paper-facing packaging from the canonical master summary."""

from __future__ import annotations

import csv
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
PAPER_SCRIPT = REPO_ROOT / "scripts" / "package_block_a_paper.py"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from isaacsim_agent.eval import package_block_a_master_for_paper
from isaacsim_agent.eval import summarize_block_a_master_processed_dirs
from tests.test_block_a_master_summary import _build_source_rows
from tests.test_block_a_master_summary import _write_cross_family_reference
from tests.test_block_a_master_summary import _write_processed_input


def _read_png_size(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"not a PNG file: {path}")
    width, height = struct.unpack("!II", raw[16:24])
    return width, height


def _build_master_summary_fixture(temp_path: Path) -> Path:
    navigation_pilot_dir = temp_path / "navigation_pilot"
    navigation_expanded_dir = temp_path / "navigation_expanded"
    manipulation_pilot_dir = temp_path / "manipulation_pilot"
    cross_family_dir = temp_path / "cross_family"
    navigation_robustness_dir = temp_path / "navigation_robustness"
    output_dir = temp_path / "processed" / "block_a_master_summary"

    _write_processed_input(
        navigation_pilot_dir,
        _build_source_rows(
            prefix="nav-pilot-paper",
            task_family="navigation",
            planner_base=4,
            tool_base=3,
            episode_time_base=1.0,
        ),
    )
    _write_processed_input(
        navigation_expanded_dir,
        _build_source_rows(
            prefix="nav-expanded-paper",
            task_family="navigation",
            planner_base=5,
            tool_base=4,
            episode_time_base=1.2,
        ),
    )
    _write_processed_input(
        manipulation_pilot_dir,
        _build_source_rows(
            prefix="pick-pilot-paper",
            task_family="pick_place",
            planner_base=8,
            tool_base=7,
            episode_time_base=1.4,
        ),
    )
    _write_processed_input(
        navigation_robustness_dir,
        _build_source_rows(
            prefix="nav-robust-paper",
            task_family="navigation",
            planner_base=7,
            tool_base=6,
            episode_time_base=1.6,
        ),
    )
    _write_cross_family_reference(cross_family_dir)

    summarize_block_a_master_processed_dirs(
        navigation_pilot_dir=navigation_pilot_dir,
        navigation_expanded_dir=navigation_expanded_dir,
        manipulation_pilot_dir=manipulation_pilot_dir,
        cross_family_dir=cross_family_dir,
        navigation_robustness_dir=navigation_robustness_dir,
        output_dir=output_dir,
    )
    return output_dir


class BlockAPaperPackagingTest(unittest.TestCase):
    def test_library_packages_tables_figures_and_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = _build_master_summary_fixture(temp_path)
            master_summary_path = output_dir / "block_a_master_summary.json"

            result = package_block_a_master_for_paper(
                master_summary_json_path=master_summary_path,
                output_dir=output_dir,
            )

            self.assertTrue(result.validation["all_consistent"])
            self.assertEqual(result.validation["table_validation"]["checks"], 180)
            self.assertEqual(result.validation["figure_validation"]["checks"], 72)

            success_table = output_dir / "paper_tables" / "block_a_success_table.csv"
            invalid_table = output_dir / "paper_tables" / "block_a_invalid_actions_table.csv"
            efficiency_table = output_dir / "paper_tables" / "block_a_efficiency_table.csv"
            success_figure = output_dir / "paper_figures" / "block_a_success_rate.png"
            invalid_figure = output_dir / "paper_figures" / "block_a_invalid_actions.png"
            planner_figure = output_dir / "paper_figures" / "block_a_planner_calls.png"
            tool_figure = output_dir / "paper_figures" / "block_a_tool_calls.png"
            analysis_md = output_dir / "analysis" / "block_a_analysis.md"

            for path in (
                success_table,
                invalid_table,
                efficiency_table,
                success_figure,
                invalid_figure,
                planner_figure,
                tool_figure,
                analysis_md,
            ):
                self.assertTrue(path.is_file(), path)

            with success_table.open("r", encoding="utf-8", newline="") as handle:
                success_rows = list(csv.DictReader(handle))
            self.assertEqual(len(success_rows), 6)
            p0_r0_row = next(
                row
                for row in success_rows
                if row["prompt_variant"] == "P0" and row["runtime_variant"] == "R0"
            )
            self.assertEqual(p0_r0_row["navigation_easy_success_rate"], "0.0")
            self.assertEqual(p0_r0_row["manipulation_easy_success_rate"], "0.0")

            with efficiency_table.open("r", encoding="utf-8", newline="") as handle:
                efficiency_rows = list(csv.DictReader(handle))
            p2_r0_row = next(
                row
                for row in efficiency_rows
                if row["prompt_variant"] == "P2" and row["runtime_variant"] == "R0"
            )
            self.assertEqual(p2_r0_row["manipulation_easy_average_planner_calls"], "8.0")
            self.assertEqual(p2_r0_row["navigation_harder_average_tool_calls"], "7.0")

            for figure_path in (success_figure, invalid_figure, planner_figure, tool_figure):
                self.assertGreater(figure_path.stat().st_size, 0)
                self.assertEqual(_read_png_size(figure_path), (1680, 920))

            analysis_text = analysis_md.read_text(encoding="utf-8")
            self.assertIn("# Block A Analysis", analysis_text)
            self.assertIn("The remaining symmetry gap is still Manipulation Harder.", analysis_text)
            self.assertIn("All consistency checks passed before the figures and analysis were written.", analysis_text)

    def test_cli_smoke_writes_paper_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = _build_master_summary_fixture(temp_path)
            master_summary_path = output_dir / "block_a_master_summary.json"

            command = [
                sys.executable,
                str(PAPER_SCRIPT),
                "--master-summary-json",
                str(master_summary_path),
                "--output-dir",
                str(output_dir),
            ]
            completed = subprocess.run(
                command,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PYTHONPATH": str(SRC_ROOT), "PYTHONUNBUFFERED": "1"},
            )

            combined_output = f"{completed.stdout}\n{completed.stderr}"
            self.assertEqual(completed.returncode, 0, combined_output)
            self.assertIn("All consistency checks passed: True", combined_output)
            self.assertTrue((output_dir / "paper_tables" / "block_a_success_table.csv").is_file())
            self.assertTrue((output_dir / "paper_figures" / "block_a_success_rate.png").is_file())
            self.assertTrue((output_dir / "analysis" / "block_a_analysis.md").is_file())


if __name__ == "__main__":
    unittest.main()
