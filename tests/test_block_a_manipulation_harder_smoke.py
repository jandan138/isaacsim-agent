"""Smoke coverage for the harder manipulation Block A slice."""

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
MANIPULATION_HARDER_CONFIG = (
    REPO_ROOT / "configs" / "experiments" / "block_a" / "manipulation_prompt_runtime_harder.yaml"
)

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class BlockAManipulationHarderSmokeTest(unittest.TestCase):
    def test_manipulation_harder_config_plans_18_toy_runs(self) -> None:
        from isaacsim_agent.experiments import load_pilot_experiment_config
        from isaacsim_agent.experiments import plan_pilot_runs

        config = load_pilot_experiment_config(MANIPULATION_HARDER_CONFIG)
        planned_runs = plan_pilot_runs(config)

        self.assertEqual(config.experiment_name, "block_a_manipulation_harder")
        self.assertEqual(config.task_family, "manipulation")
        self.assertEqual(config.backend, "toy")
        self.assertEqual(config.summary_basename, "block_a_manipulation_harder_summary")
        self.assertEqual(config.summary_title, "Block A Manipulation Harder Summary")
        self.assertEqual(config.analysis_mode, "block_a_manipulation_harder")
        self.assertEqual(
            config.reference_summary_path,
            "results/processed/block_a_manipulation_prompt_runtime_pilot/block_a_summary.json",
        )
        self.assertEqual(len(config.tasks), 3)
        self.assertEqual(len(planned_runs), 18)
        self.assertTrue(all(task.task_family == "manipulation" for task in config.tasks))
        self.assertTrue(all(task.transfer_waypoints for task in config.tasks))

    def test_run_suite_writes_manipulation_harder_outputs_and_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            results_root = Path(temp_dir) / "results"
            output_dir = results_root / "processed" / "block_a_manipulation_harder"
            command = [
                sys.executable,
                str(SUITE_SCRIPT),
                "--config",
                str(MANIPULATION_HARDER_CONFIG),
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
            self.assertIn("Planned runs: 18", combined_output)
            self.assertIn("Runs scanned: 18", combined_output)
            self.assertIn("Run-complete runs: 18", combined_output)
            self.assertIn("Successful runs: 15", combined_output)

            self.assertTrue((output_dir / "run_plan.json").is_file())
            self.assertTrue((output_dir / "run_summary.jsonl").is_file())
            self.assertTrue((output_dir / "run_summary.csv").is_file())
            self.assertTrue((output_dir / "aggregate.json").is_file())
            self.assertTrue((output_dir / "validation.json").is_file())
            self.assertTrue((output_dir / "block_a_manipulation_harder_summary.json").is_file())
            self.assertTrue((output_dir / "block_a_manipulation_harder_summary.md").is_file())

            summary_rows = [
                json.loads(line)
                for line in (output_dir / "run_summary.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(summary_rows), 18)
            self.assertEqual({row["task_family"] for row in summary_rows}, {"pick_place"})
            self.assertEqual({row["task_id"] for row in summary_rows}, {
                "pick_place_harder_midpoint_forward",
                "pick_place_harder_lateral_detour",
                "pick_place_harder_cross_table",
            })

            p0_r0_rows = [
                row
                for row in summary_rows
                if row["prompt_variant"] == "P0" and row["runtime_variant"] == "R0"
            ]
            self.assertEqual(len(p0_r0_rows), 3)
            self.assertTrue(all(row["success"] is False for row in p0_r0_rows))
            self.assertTrue(all(row["termination_reason"] == "invalid_action_limit" for row in p0_r0_rows))

            p0_r1_rows = [
                row
                for row in summary_rows
                if row["prompt_variant"] == "P0" and row["runtime_variant"] == "R1"
            ]
            self.assertEqual(len(p0_r1_rows), 3)
            self.assertTrue(all(row["success"] is True for row in p0_r1_rows))
            self.assertTrue(all(row["retries"] == 1 for row in p0_r1_rows))

            p1_r0_rows = [
                row
                for row in summary_rows
                if row["prompt_variant"] == "P1" and row["runtime_variant"] == "R0"
            ]
            p2_r0_rows = [
                row
                for row in summary_rows
                if row["prompt_variant"] == "P2" and row["runtime_variant"] == "R0"
            ]
            self.assertEqual(
                sum(row["planner_calls"] for row in p2_r0_rows),
                sum(row["planner_calls"] for row in p1_r0_rows) - 6,
            )
            self.assertEqual(
                sum(row["tool_calls"] for row in p2_r0_rows),
                sum(row["tool_calls"] for row in p1_r0_rows) - 6,
            )

            summary_payload = json.loads(
                (output_dir / "block_a_manipulation_harder_summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(summary_payload["overall"]["planned_runs"], 18)
            self.assertEqual(summary_payload["overall"]["successful_runs"], 15)
            self.assertEqual(summary_payload["overall"]["total_retries"], 3)
            self.assertFalse(summary_payload["missing_run_ids"])

            analysis = summary_payload["analysis"]
            self.assertEqual(analysis["mode"], "block_a_manipulation_harder")
            self.assertTrue(analysis["questions"]["q1_p0_r0_worst"]["answer"])
            self.assertTrue(analysis["questions"]["q2_r1_recovers_p0"]["answer"])
            self.assertTrue(analysis["questions"]["q3_p1_p2_success"]["answer"])
            self.assertTrue(analysis["questions"]["q4_p2_more_efficient_than_p1"]["answer"])
            self.assertTrue(analysis["questions"]["q5_harder_tasks_amplify_differences"]["answer"])
            self.assertTrue(analysis["reference_summary_path"].endswith("block_a_summary.json"))

            markdown_summary = (output_dir / "block_a_manipulation_harder_summary.md").read_text(encoding="utf-8")
            self.assertIn("# Block A Manipulation Harder Summary: block_a_manipulation_harder", markdown_summary)
            self.assertIn("## Harder Manipulation Findings", markdown_summary)
            self.assertIn("P0/R0 remains the worst harder-manipulation cell", markdown_summary)


if __name__ == "__main__":
    unittest.main()
