"""Smoke tests for the minimal post-M5 pilot suite runner."""

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
SUITE_SCRIPT = REPO_ROOT / "scripts" / "run_suite.py"
PILOT_CONFIG = REPO_ROOT / "configs" / "experiments" / "pilot" / "easy_navigation_minimal.yaml"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class RunSuiteSmokeTest(unittest.TestCase):
    def test_run_suite_cli_writes_pilot_and_summary_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            results_root = Path(temp_dir) / "results"
            output_dir = results_root / "processed" / "easy_navigation_pilot_v0"
            command = [
                sys.executable,
                str(SUITE_SCRIPT),
                "--config",
                str(PILOT_CONFIG),
                "--results-root",
                str(results_root),
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
            self.assertIn("Planned runs: 6", combined_output)
            self.assertIn("Runs scanned: 6", combined_output)
            self.assertIn("Run-complete runs: 6", combined_output)
            self.assertIn("Successful runs: 6", combined_output)

            self.assertTrue((output_dir / "run_plan.json").is_file())
            self.assertTrue((output_dir / "run_summary.jsonl").is_file())
            self.assertTrue((output_dir / "run_summary.csv").is_file())
            self.assertTrue((output_dir / "aggregate.json").is_file())
            self.assertTrue((output_dir / "validation.json").is_file())
            self.assertTrue((output_dir / "pilot_summary.json").is_file())
            self.assertTrue((output_dir / "pilot_summary.md").is_file())

            run_dirs = sorted((results_root / "runs").iterdir())
            self.assertEqual(len(run_dirs), 6)

            summary_rows = [
                json.loads(line)
                for line in (output_dir / "run_summary.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(summary_rows), 6)
            self.assertEqual({row["prompt_variant"] for row in summary_rows}, {"P0", "P1"})
            self.assertEqual({row["runtime_variant"] for row in summary_rows}, {"R0"})
            self.assertTrue(all(row["task_family"] == "navigation" for row in summary_rows))
            self.assertTrue(all(row["contract_complete"] for row in summary_rows))
            self.assertTrue(all(row["run_complete"] for row in summary_rows))
            self.assertTrue(all(row["success"] is True for row in summary_rows))

            pilot_summary = json.loads((output_dir / "pilot_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(pilot_summary["overall"]["planned_runs"], 6)
            self.assertEqual(pilot_summary["overall"]["summarized_runs"], 6)
            self.assertEqual(pilot_summary["overall"]["successful_runs"], 6)
            self.assertFalse(pilot_summary["missing_run_ids"])
            self.assertFalse(pilot_summary["incomplete_runs"])
            self.assertEqual(len(pilot_summary["by_prompt_runtime"]), 2)

            sample_run = next(row for row in summary_rows if row["prompt_variant"] == "P1")
            sample_run_dir = results_root / "runs" / sample_run["run_id"]
            task_config = json.loads((sample_run_dir / "task_config.json").read_text(encoding="utf-8"))
            planner_trace = json.loads((sample_run_dir / "artifacts" / "planner_trace.json").read_text(encoding="utf-8"))
            self.assertEqual(task_config["runtime_options"]["extra_options"]["prompt_variant"], "P1")
            self.assertEqual(task_config["runtime_options"]["extra_options"]["runtime_variant"], "R0")
            self.assertIn("Use only the provided tools", task_config["runtime_options"]["extra_options"]["planner_prompt_text"])
            self.assertEqual(task_config["metadata"]["pilot_suite"]["experiment_name"], "easy_navigation_pilot_v0")
            self.assertIn("Use only the provided tools", task_config["metadata"]["agent_runtime_v0"]["prompt_text"])
            self.assertIn("Use only the provided tools", planner_trace[0]["request"]["instruction"])

            markdown_summary = (output_dir / "pilot_summary.md").read_text(encoding="utf-8")
            self.assertIn("# Pilot Summary: easy_navigation_pilot_v0", markdown_summary)


if __name__ == "__main__":
    unittest.main()
