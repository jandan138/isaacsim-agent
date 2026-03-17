"""Smoke coverage for the mixed-family Block A prompt-only ablation."""

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
PROMPT_ONLY_CONFIG = (
    REPO_ROOT / "configs" / "experiments" / "block_a" / "prompt_only_ablation.yaml"
)

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class BlockAPromptOnlyAblationSmokeTest(unittest.TestCase):
    def test_prompt_only_config_plans_12_mixed_family_runs(self) -> None:
        from isaacsim_agent.experiments import load_pilot_experiment_config
        from isaacsim_agent.experiments import plan_pilot_runs

        config = load_pilot_experiment_config(PROMPT_ONLY_CONFIG)
        planned_runs = plan_pilot_runs(config)

        self.assertEqual(config.experiment_name, "block_a_prompt_only_ablation")
        self.assertEqual(config.task_family, "mixed")
        self.assertEqual(config.backend, "toy")
        self.assertEqual(config.summary_basename, "block_a_prompt_only_summary")
        self.assertEqual(config.summary_title, "Block A Prompt-Only Summary")
        self.assertEqual(config.analysis_mode, "block_a_prompt_only_ablation")
        self.assertEqual(len(config.tasks), 4)
        self.assertEqual(len(planned_runs), 12)
        self.assertEqual({task.task_family for task in config.tasks}, {"navigation", "manipulation"})
        self.assertTrue(all(run.runtime_variant.variant_id == "R0" for run in planned_runs))

    def test_run_suite_writes_prompt_only_outputs_and_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            results_root = Path(temp_dir) / "results"
            output_dir = results_root / "processed" / "block_a_prompt_only_ablation"
            command = [
                sys.executable,
                str(SUITE_SCRIPT),
                "--config",
                str(PROMPT_ONLY_CONFIG),
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
            self.assertIn("Planned runs: 12", combined_output)
            self.assertIn("Runs scanned: 12", combined_output)
            self.assertIn("Run-complete runs: 12", combined_output)
            self.assertIn("Successful runs: 8", combined_output)

            self.assertTrue((output_dir / "run_plan.json").is_file())
            self.assertTrue((output_dir / "run_summary.jsonl").is_file())
            self.assertTrue((output_dir / "run_summary.csv").is_file())
            self.assertTrue((output_dir / "aggregate.json").is_file())
            self.assertTrue((output_dir / "validation.json").is_file())
            self.assertTrue((output_dir / "block_a_prompt_only_summary.json").is_file())
            self.assertTrue((output_dir / "block_a_prompt_only_summary.md").is_file())

            summary_rows = [
                json.loads(line)
                for line in (output_dir / "run_summary.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(summary_rows), 12)
            self.assertEqual({row["task_family"] for row in summary_rows}, {"navigation", "pick_place"})
            self.assertEqual({row["prompt_variant"] for row in summary_rows}, {"P0", "P1", "P2"})
            self.assertEqual({row["runtime_variant"] for row in summary_rows}, {"R0"})

            p0_rows = [row for row in summary_rows if row["prompt_variant"] == "P0"]
            p1_rows = [row for row in summary_rows if row["prompt_variant"] == "P1"]
            p2_rows = [row for row in summary_rows if row["prompt_variant"] == "P2"]
            self.assertEqual(len(p0_rows), 4)
            self.assertEqual(len(p1_rows), 4)
            self.assertEqual(len(p2_rows), 4)
            self.assertTrue(all(row["success"] is False for row in p0_rows))
            self.assertTrue(all(row["termination_reason"] == "invalid_action_limit" for row in p0_rows))
            self.assertTrue(all(row["success"] is True for row in p1_rows))
            self.assertTrue(all(row["success"] is True for row in p2_rows))
            self.assertLess(sum(row["planner_calls"] for row in p2_rows), sum(row["planner_calls"] for row in p1_rows))
            self.assertLess(sum(row["tool_calls"] for row in p2_rows), sum(row["tool_calls"] for row in p1_rows))

            summary_payload = json.loads(
                (output_dir / "block_a_prompt_only_summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(summary_payload["overall"]["planned_runs"], 12)
            self.assertEqual(summary_payload["overall"]["successful_runs"], 8)
            self.assertEqual(summary_payload["overall"]["total_retries"], 0)
            self.assertFalse(summary_payload["missing_run_ids"])
            self.assertEqual(set(summary_payload["task_families"]), {"navigation", "manipulation"})

            p0_r0 = next(
                row
                for row in summary_payload["by_prompt_runtime"]
                if row["prompt_variant"] == "P0" and row["runtime_variant"] == "R0"
            )
            p1_r0 = next(
                row
                for row in summary_payload["by_prompt_runtime"]
                if row["prompt_variant"] == "P1" and row["runtime_variant"] == "R0"
            )
            p2_r0 = next(
                row
                for row in summary_payload["by_prompt_runtime"]
                if row["prompt_variant"] == "P2" and row["runtime_variant"] == "R0"
            )
            self.assertEqual(p0_r0["successful_runs"], 0)
            self.assertEqual(p0_r0["total_invalid_actions"], 4)
            self.assertEqual(p1_r0["successful_runs"], 4)
            self.assertEqual(p1_r0["total_invalid_actions"], 0)
            self.assertEqual(p2_r0["successful_runs"], 4)
            self.assertEqual(p2_r0["total_invalid_actions"], 0)
            self.assertLess(p2_r0["average_planner_calls"], p1_r0["average_planner_calls"])
            self.assertLess(p2_r0["average_tool_calls"], p1_r0["average_tool_calls"])

            analysis = summary_payload["analysis"]
            self.assertEqual(analysis["mode"], "block_a_prompt_only_ablation")
            self.assertTrue(analysis["questions"]["q1_prompt_structure_reduces_invalid_actions"]["answer"])
            self.assertTrue(analysis["questions"]["q2_p2_more_efficient_than_p1"]["answer"])
            self.assertTrue(analysis["questions"]["q3_cross_family_consistency"]["answer"])

            markdown_summary = (output_dir / "block_a_prompt_only_summary.md").read_text(encoding="utf-8")
            self.assertIn("# Block A Prompt-Only Summary: block_a_prompt_only_ablation", markdown_summary)
            self.assertIn("## Prompt-Only Findings", markdown_summary)
            self.assertIn("## Task Family x Prompt x Runtime", markdown_summary)


if __name__ == "__main__":
    unittest.main()
