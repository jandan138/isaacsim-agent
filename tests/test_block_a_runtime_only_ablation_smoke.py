"""Smoke coverage for the mixed-family Block A runtime-only ablation."""

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
RUNTIME_ONLY_CONFIG = (
    REPO_ROOT / "configs" / "experiments" / "block_a" / "runtime_only_ablation.yaml"
)

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class BlockARuntimeOnlyAblationSmokeTest(unittest.TestCase):
    def test_runtime_only_config_plans_8_mixed_family_runs(self) -> None:
        from isaacsim_agent.experiments import load_pilot_experiment_config
        from isaacsim_agent.experiments import plan_pilot_runs

        config = load_pilot_experiment_config(RUNTIME_ONLY_CONFIG)
        planned_runs = plan_pilot_runs(config)

        self.assertEqual(config.experiment_name, "block_a_runtime_only_ablation")
        self.assertEqual(config.task_family, "mixed")
        self.assertEqual(config.backend, "toy")
        self.assertEqual(config.summary_basename, "block_a_runtime_only_summary")
        self.assertEqual(config.summary_title, "Block A Runtime-Only Summary")
        self.assertEqual(config.analysis_mode, "block_a_runtime_only_ablation")
        self.assertEqual(len(config.tasks), 4)
        self.assertEqual({task.task_family for task in config.tasks}, {"navigation", "manipulation"})
        self.assertEqual(len(planned_runs), 8)

        probe_runs = [
            run
            for run in planned_runs
            if run.task.runtime_probe_invalid_first_action and run.runtime_variant.variant_id == "R0"
        ]
        self.assertEqual(len(probe_runs), 2)
        self.assertEqual({run.task.task_family for run in probe_runs}, {"navigation", "manipulation"})

    def test_run_suite_writes_runtime_only_outputs_and_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            results_root = Path(temp_dir) / "results"
            output_dir = results_root / "processed" / "block_a_runtime_only_ablation"
            command = [
                sys.executable,
                str(SUITE_SCRIPT),
                "--config",
                str(RUNTIME_ONLY_CONFIG),
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
            self.assertIn("Planned runs: 8", combined_output)
            self.assertIn("Runs scanned: 8", combined_output)
            self.assertIn("Run-complete runs: 8", combined_output)
            self.assertIn("Successful runs: 6", combined_output)

            self.assertTrue((output_dir / "run_plan.json").is_file())
            self.assertTrue((output_dir / "run_summary.jsonl").is_file())
            self.assertTrue((output_dir / "run_summary.csv").is_file())
            self.assertTrue((output_dir / "aggregate.json").is_file())
            self.assertTrue((output_dir / "validation.json").is_file())
            self.assertTrue((output_dir / "block_a_runtime_only_summary.json").is_file())
            self.assertTrue((output_dir / "block_a_runtime_only_summary.md").is_file())

            summary_rows = [
                json.loads(line)
                for line in (output_dir / "run_summary.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(summary_rows), 8)
            self.assertEqual({row["task_family"] for row in summary_rows}, {"navigation", "pick_place"})
            self.assertEqual({row["prompt_variant"] for row in summary_rows}, {"P1"})
            self.assertEqual({row["runtime_variant"] for row in summary_rows}, {"R0", "R1"})

            probe_r0_rows = [
                row
                for row in summary_rows
                if row["runtime_variant"] == "R0" and row["task_id"] in {"runtime_nav_offset_probe", "runtime_pick_place_lateral_probe"}
            ]
            self.assertEqual(len(probe_r0_rows), 2)
            self.assertTrue(all(row["success"] is False for row in probe_r0_rows))
            self.assertTrue(all(row["termination_reason"] == "invalid_action_limit" for row in probe_r0_rows))
            self.assertTrue(all(row["invalid_actions"] == 1 for row in probe_r0_rows))
            self.assertTrue(all(row["retries"] == 0 for row in probe_r0_rows))

            probe_r1_rows = [
                row
                for row in summary_rows
                if row["runtime_variant"] == "R1" and row["task_id"] in {"runtime_nav_offset_probe", "runtime_pick_place_lateral_probe"}
            ]
            self.assertEqual(len(probe_r1_rows), 2)
            self.assertTrue(all(row["success"] is True for row in probe_r1_rows))
            self.assertTrue(all(row["invalid_actions"] == 1 for row in probe_r1_rows))
            self.assertTrue(all(row["retries"] == 1 for row in probe_r1_rows))

            summary_payload = json.loads(
                (output_dir / "block_a_runtime_only_summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(summary_payload["overall"]["planned_runs"], 8)
            self.assertEqual(summary_payload["overall"]["successful_runs"], 6)
            self.assertEqual(summary_payload["overall"]["total_retries"], 2)
            self.assertFalse(summary_payload["missing_run_ids"])
            self.assertEqual(set(summary_payload["task_families"]), {"navigation", "manipulation"})

            p1_r0 = next(
                row
                for row in summary_payload["by_prompt_runtime"]
                if row["prompt_variant"] == "P1" and row["runtime_variant"] == "R0"
            )
            p1_r1 = next(
                row
                for row in summary_payload["by_prompt_runtime"]
                if row["prompt_variant"] == "P1" and row["runtime_variant"] == "R1"
            )
            self.assertEqual(p1_r0["successful_runs"], 2)
            self.assertEqual(p1_r0["invalid_action_run_count"], 2)
            self.assertEqual(p1_r0["successful_invalid_action_runs"], 0)
            self.assertEqual(p1_r0["total_retries"], 0)
            self.assertEqual(p1_r1["successful_runs"], 4)
            self.assertEqual(p1_r1["invalid_action_run_count"], 2)
            self.assertEqual(p1_r1["successful_invalid_action_runs"], 2)
            self.assertEqual(p1_r1["total_retries"], 2)

            analysis = summary_payload["analysis"]
            self.assertEqual(analysis["mode"], "block_a_runtime_only_ablation")
            self.assertTrue(analysis["questions"]["q1_runtime_has_independent_value"]["answer"])
            self.assertTrue(analysis["questions"]["q2_value_concentrates_in_recovery"]["answer"])
            self.assertTrue(analysis["questions"]["q3_cross_family_consistency"]["answer"])

            markdown_summary = (output_dir / "block_a_runtime_only_summary.md").read_text(encoding="utf-8")
            self.assertIn("# Block A Runtime-Only Summary: block_a_runtime_only_ablation", markdown_summary)
            self.assertIn("## Runtime-Only Findings", markdown_summary)
            self.assertIn("## Task Family x Prompt x Runtime", markdown_summary)


if __name__ == "__main__":
    unittest.main()
