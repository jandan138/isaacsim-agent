"""Smoke coverage for the minimal M6 block A prompt x runtime pilot subset."""

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
BLOCK_A_CONFIG = (
    REPO_ROOT / "configs" / "experiments" / "block_a" / "navigation_prompt_runtime_pilot.yaml"
)
BLOCK_A_EXPANDED_CONFIG = (
    REPO_ROOT / "configs" / "experiments" / "block_a" / "navigation_prompt_runtime_expanded.yaml"
)

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class BlockAPilotSmokeTest(unittest.TestCase):
    def test_load_block_a_expanded_config_plans_mixed_backend_matrix(self) -> None:
        from isaacsim_agent.experiments import load_pilot_experiment_config
        from isaacsim_agent.experiments import plan_pilot_runs

        config = load_pilot_experiment_config(BLOCK_A_EXPANDED_CONFIG)
        planned_runs = plan_pilot_runs(config)

        self.assertEqual(config.experiment_name, "block_a_navigation_prompt_runtime_expanded")
        self.assertEqual(config.backend, "mixed")
        self.assertEqual(config.summary_basename, "block_a_summary")
        self.assertEqual(len(config.tasks), 8)
        self.assertEqual({task.backend for task in config.tasks}, {"toy", "isaac"})
        self.assertEqual(len(planned_runs), 48)
        self.assertEqual({run.task.backend for run in planned_runs}, {"toy", "isaac"})
        self.assertEqual(sum(1 for run in planned_runs if run.task.backend == "toy"), 36)
        self.assertEqual(sum(1 for run in planned_runs if run.task.backend == "isaac"), 12)

    def test_run_block_a_pilot_writes_summary_and_retry_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            results_root = Path(temp_dir) / "results"
            output_dir = results_root / "processed" / "block_a_navigation_prompt_runtime_pilot"
            command = [
                sys.executable,
                str(SUITE_SCRIPT),
                "--config",
                str(BLOCK_A_CONFIG),
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
            self.assertTrue((output_dir / "block_a_pilot_summary.json").is_file())
            self.assertTrue((output_dir / "block_a_pilot_summary.md").is_file())

            summary_rows = [
                json.loads(line)
                for line in (output_dir / "run_summary.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(summary_rows), 18)
            self.assertEqual({row["prompt_variant"] for row in summary_rows}, {"P0", "P1", "P2"})
            self.assertEqual({row["runtime_variant"] for row in summary_rows}, {"R0", "R1"})
            self.assertTrue(all("retries" in row for row in summary_rows))
            self.assertTrue(all("runtime_policy" in row for row in summary_rows))

            p0_r0_row = next(
                row
                for row in summary_rows
                if row["task_id"] == "easy_nav_short_forward"
                and row["prompt_variant"] == "P0"
                and row["runtime_variant"] == "R0"
            )
            self.assertFalse(p0_r0_row["success"])
            self.assertEqual(p0_r0_row["termination_reason"], "invalid_action_limit")
            self.assertEqual(p0_r0_row["invalid_actions"], 1)
            self.assertEqual(p0_r0_row["retries"], 0)
            self.assertEqual(p0_r0_row["tool_calls"], 0)

            p0_r1_row = next(
                row
                for row in summary_rows
                if row["task_id"] == "easy_nav_short_forward"
                and row["prompt_variant"] == "P0"
                and row["runtime_variant"] == "R1"
            )
            self.assertTrue(p0_r1_row["success"])
            self.assertEqual(p0_r1_row["invalid_actions"], 1)
            self.assertEqual(p0_r1_row["retries"], 1)
            self.assertGreater(p0_r1_row["planner_calls"], p0_r1_row["tool_calls"])

            p2_r0_row = next(
                row
                for row in summary_rows
                if row["task_id"] == "easy_nav_short_forward"
                and row["prompt_variant"] == "P2"
                and row["runtime_variant"] == "R0"
            )
            p2_run_dir = results_root / "runs" / p2_r0_row["run_id"]
            manifest = json.loads((p2_run_dir / "manifest.json").read_text(encoding="utf-8"))
            planner_trace = json.loads(
                (p2_run_dir / "artifacts" / "planner_trace.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["metadata"]["prompt_variant"], "P2")
            self.assertEqual(manifest["metadata"]["runtime_variant"], "R0")
            self.assertEqual(manifest["metadata"]["runtime_policy"], "block_a_r0_bare")
            self.assertEqual(manifest["metadata"]["task_id"], "easy_nav_short_forward")
            self.assertEqual(manifest["metadata"]["scene_id"], "easy_empty_stage_a")
            self.assertTrue(any(item["parsed_action"].get("self_check") for item in planner_trace))

            pilot_summary = json.loads((output_dir / "block_a_pilot_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(pilot_summary["overall"]["planned_runs"], 18)
            self.assertEqual(pilot_summary["overall"]["successful_runs"], 15)
            self.assertEqual(pilot_summary["overall"]["total_retries"], 3)
            self.assertFalse(pilot_summary["missing_run_ids"])
            self.assertEqual(pilot_summary["backends"], ["toy"])

            p0_r0_summary = next(
                row
                for row in pilot_summary["by_prompt_runtime"]
                if row["prompt_variant"] == "P0" and row["runtime_variant"] == "R0"
            )
            self.assertEqual(p0_r0_summary["successful_runs"], 0)
            self.assertEqual(p0_r0_summary["total_invalid_actions"], 3)
            self.assertEqual(p0_r0_summary["total_retries"], 0)

            p0_r1_summary = next(
                row
                for row in pilot_summary["by_prompt_runtime"]
                if row["prompt_variant"] == "P0" and row["runtime_variant"] == "R1"
            )
            self.assertEqual(p0_r1_summary["successful_runs"], 3)
            self.assertEqual(p0_r1_summary["total_retries"], 3)

            by_backend = next(
                row
                for row in pilot_summary["by_backend_prompt_runtime"]
                if row["backend_variant"] == "toy"
                and row["prompt_variant"] == "P0"
                and row["runtime_variant"] == "R0"
            )
            self.assertEqual(by_backend["successful_runs"], 0)
            self.assertEqual(by_backend["total_invalid_actions"], 3)


if __name__ == "__main__":
    unittest.main()
