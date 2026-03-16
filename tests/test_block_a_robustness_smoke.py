"""Smoke coverage for the Block A navigation robustness slice."""

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
ROBUSTNESS_CONFIG = (
    REPO_ROOT / "configs" / "experiments" / "block_a" / "navigation_prompt_runtime_robustness.yaml"
)

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class BlockARobustnessSmokeTest(unittest.TestCase):
    def test_robustness_config_plans_24_toy_runs(self) -> None:
        from isaacsim_agent.experiments import load_pilot_experiment_config
        from isaacsim_agent.experiments import plan_pilot_runs

        config = load_pilot_experiment_config(ROBUSTNESS_CONFIG)
        planned_runs = plan_pilot_runs(config)

        self.assertEqual(config.experiment_name, "block_a_navigation_prompt_runtime_robustness")
        self.assertEqual(config.backend, "toy")
        self.assertEqual(config.summary_basename, "block_a_robustness_summary")
        self.assertEqual(config.summary_title, "Block A Robustness Summary")
        self.assertEqual(config.analysis_mode, "block_a_navigation_robustness")
        self.assertEqual(
            config.reference_summary_path,
            "results/processed/block_a_navigation_prompt_runtime_expanded/block_a_summary.json",
        )
        self.assertEqual(len(config.tasks), 4)
        self.assertEqual({task.backend for task in config.tasks}, {"toy"})
        self.assertEqual(len(planned_runs), 24)

        reverse_cross_run = next(
            run
            for run in planned_runs
            if run.task.task_id == "robust_nav_reverse_cross"
            and run.prompt_variant.variant_id == "P2"
            and run.runtime_variant.variant_id == "R1"
        )
        self.assertEqual(reverse_cross_run.to_dict()["backend"], "toy")
        self.assertEqual(reverse_cross_run.to_dict()["runtime_policy"], "block_a_r1_validate_retry")

    def test_run_suite_writes_robustness_outputs_and_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            results_root = Path(temp_dir) / "results"
            output_dir = results_root / "processed" / "block_a_navigation_prompt_runtime_robustness"
            command = [
                sys.executable,
                str(SUITE_SCRIPT),
                "--config",
                str(ROBUSTNESS_CONFIG),
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
            self.assertIn("Planned runs: 24", combined_output)
            self.assertIn("Runs scanned: 24", combined_output)
            self.assertIn("Run-complete runs: 24", combined_output)
            self.assertIn("Successful runs: 20", combined_output)

            self.assertTrue((output_dir / "run_plan.json").is_file())
            self.assertTrue((output_dir / "run_summary.jsonl").is_file())
            self.assertTrue((output_dir / "run_summary.csv").is_file())
            self.assertTrue((output_dir / "aggregate.json").is_file())
            self.assertTrue((output_dir / "validation.json").is_file())
            self.assertTrue((output_dir / "block_a_robustness_summary.json").is_file())
            self.assertTrue((output_dir / "block_a_robustness_summary.md").is_file())

            summary_rows = [
                json.loads(line)
                for line in (output_dir / "run_summary.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(summary_rows), 24)
            self.assertEqual({row["task_id"] for row in summary_rows}, {
                "robust_nav_far_forward",
                "robust_nav_far_diagonal",
                "robust_nav_cross_quadrant",
                "robust_nav_reverse_cross",
            })

            p0_r0_rows = [
                row
                for row in summary_rows
                if row["prompt_variant"] == "P0" and row["runtime_variant"] == "R0"
            ]
            self.assertEqual(len(p0_r0_rows), 4)
            self.assertTrue(all(row["success"] is False for row in p0_r0_rows))
            self.assertTrue(all(row["termination_reason"] == "invalid_action_limit" for row in p0_r0_rows))

            p0_r1_rows = [
                row
                for row in summary_rows
                if row["prompt_variant"] == "P0" and row["runtime_variant"] == "R1"
            ]
            self.assertEqual(len(p0_r1_rows), 4)
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
                sum(row["planner_calls"] for row in p1_r0_rows) - len(p1_r0_rows),
            )
            self.assertEqual(
                sum(row["tool_calls"] for row in p2_r0_rows),
                sum(row["tool_calls"] for row in p1_r0_rows) - len(p1_r0_rows),
            )

            summary_payload = json.loads(
                (output_dir / "block_a_robustness_summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(summary_payload["overall"]["planned_runs"], 24)
            self.assertEqual(summary_payload["overall"]["successful_runs"], 20)
            self.assertEqual(summary_payload["overall"]["total_retries"], 4)
            self.assertFalse(summary_payload["missing_run_ids"])
            self.assertEqual(summary_payload["backends"], ["toy"])

            analysis = summary_payload["analysis"]
            self.assertEqual(analysis["mode"], "block_a_navigation_robustness")
            self.assertTrue(analysis["questions"]["q1_p0_r0_worst"]["answer"])
            self.assertTrue(analysis["questions"]["q2_r1_recovers_p0"]["answer"])
            self.assertTrue(analysis["questions"]["q3_p1_p2_success"]["answer"])
            self.assertTrue(analysis["questions"]["q4_p2_more_efficient_than_p1"]["answer"])
            self.assertTrue(analysis["questions"]["q5_harder_tasks_amplify_differences"]["answer"])
            self.assertTrue(analysis["reference_summary_path"].endswith("block_a_summary.json"))

            markdown_summary = (output_dir / "block_a_robustness_summary.md").read_text(encoding="utf-8")
            self.assertIn("# Block A Robustness Summary: block_a_navigation_prompt_runtime_robustness", markdown_summary)
            self.assertIn("## Robustness Findings", markdown_summary)
            self.assertIn("P0/R0 remains the worst cell", markdown_summary)
            self.assertIn("P2 keeps the planner/tool efficiency edge over P1", markdown_summary)


if __name__ == "__main__":
    unittest.main()
