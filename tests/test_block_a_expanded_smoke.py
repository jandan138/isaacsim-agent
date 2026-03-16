"""Focused coverage for the expanded M6 block A navigation sweep config."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
EXPANDED_CONFIG = (
    REPO_ROOT / "configs" / "experiments" / "block_a" / "navigation_prompt_runtime_expanded.yaml"
)

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class BlockAExpandedSmokeTest(unittest.TestCase):
    def test_expanded_config_plans_48_mixed_backend_runs(self) -> None:
        from isaacsim_agent.experiments.pilot import load_pilot_experiment_config
        from isaacsim_agent.experiments.pilot import plan_pilot_runs

        config = load_pilot_experiment_config(EXPANDED_CONFIG)
        planned_runs = plan_pilot_runs(config)

        self.assertEqual(config.experiment_name, "block_a_navigation_prompt_runtime_expanded")
        self.assertEqual(config.backend, "mixed")
        self.assertEqual(config.summary_basename, "block_a_summary")
        self.assertEqual(config.summary_title, "Block A Summary")
        self.assertEqual(len(config.tasks), 8)
        self.assertEqual(sum(task.backend == "toy" for task in config.tasks), 6)
        self.assertEqual(sum(task.backend == "isaac" for task in config.tasks), 2)
        self.assertEqual(len(planned_runs), 48)
        self.assertEqual({run.task.backend for run in planned_runs}, {"toy", "isaac"})

        isaac_run = next(
            run
            for run in planned_runs
            if run.task.task_id == "isaac_nav_short_forward"
            and run.prompt_variant.variant_id == "P2"
            and run.runtime_variant.variant_id == "R1"
        )
        self.assertEqual(isaac_run.to_dict()["backend"], "isaac")
        self.assertEqual(isaac_run.to_dict()["runtime_policy"], "block_a_r1_validate_retry")

    def test_run_pilot_suite_keeps_mixed_backend_rows_and_summary(self) -> None:
        from isaacsim_agent.experiments.pilot import run_pilot_suite

        config_payload = {
            "experiment_name": "mixed_backend_suite_unit",
            "description": "Small mixed-backend suite used only for unit coverage.",
            "task_family": "navigation",
            "execution_mode": "sequential",
            "backend": "mixed",
            "planner_backend": "mock_block_a",
            "summary_basename": "mixed_backend_summary",
            "summary_title": "Mixed Backend Summary",
            "defaults": {
                "backend": "toy",
                "robot_id": "agent_point_robot",
                "seed": 0,
                "success_radius_m": 0.2,
                "step_size_m": 0.5,
                "control_dt_sec": 0.5,
            },
            "prompt_variants": [
                {
                    "id": "P1",
                    "label": "structured_tool_json",
                    "response_mode": "tool_json",
                    "self_check_required": False,
                    "instruction_template": (
                        "Prompt variant: P1. Task: navigation. Start pose: ({start_x:.2f}, {start_y:.2f}, "
                        "yaw={start_yaw:.2f}). Goal pose: ({goal_x:.2f}, {goal_y:.2f}, yaw={goal_yaw:.2f}). "
                        "Choose one tool from the provided tools and emit typed JSON with tool_name and arguments."
                    ),
                }
            ],
            "runtime_variants": [
                {
                    "id": "R0",
                    "label": "bare_no_validation_no_retry",
                    "runtime_policy": "block_a_r0_bare",
                    "validate_actions": False,
                    "max_retries_per_step": 0,
                    "max_invalid_actions": 1,
                }
            ],
            "tasks": [
                {
                    "task_id": "toy_nav_forward_unit",
                    "scene_id": "toy_stage_unit",
                    "start_pose": {"x": 0.0, "y": 0.0, "yaw": 0.0},
                    "goal_pose": {"x": 1.0, "y": 0.0, "yaw": 0.0},
                    "max_steps": 6,
                    "max_time_sec": 6.0,
                },
                {
                    "task_id": "isaac_nav_forward_unit",
                    "scene_id": "isaac_stage_unit",
                    "backend": "isaac",
                    "start_pose": {"x": 0.0, "y": 0.0, "yaw": 0.0},
                    "goal_pose": {"x": 1.0, "y": 0.0, "yaw": 0.0},
                    "max_steps": 6,
                    "max_time_sec": 6.0,
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "mixed_backend_suite.json"
            results_root = temp_path / "results"
            output_dir = temp_path / "processed"
            config_path.write_text(json.dumps(config_payload, indent=2) + "\n", encoding="utf-8")

            with patch(
                "isaacsim_agent.experiments.pilot._resolve_isaac_python_executable",
                return_value=None,
            ):
                result = run_pilot_suite(
                    config_path=config_path,
                    results_root=results_root,
                    output_dir=output_dir,
                )

            self.assertEqual(len(result.planned_runs), 2)
            self.assertTrue((output_dir / "run_summary.jsonl").is_file())
            self.assertTrue((output_dir / "run_summary.csv").is_file())
            self.assertTrue((output_dir / "aggregate.json").is_file())
            self.assertTrue((output_dir / "validation.json").is_file())
            self.assertTrue((output_dir / "mixed_backend_summary.json").is_file())
            self.assertTrue((output_dir / "mixed_backend_summary.md").is_file())

            summary_rows = [
                json.loads(line)
                for line in (output_dir / "run_summary.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(summary_rows), 2)
            self.assertEqual({row["backend_variant"] for row in summary_rows}, {"toy", "isaac"})

            toy_row = next(row for row in summary_rows if row["backend_variant"] == "toy")
            self.assertTrue(toy_row["success"])
            self.assertEqual(toy_row["prompt_variant"], "P1")
            self.assertEqual(toy_row["runtime_variant"], "R0")
            self.assertEqual(toy_row["runtime_policy"], "block_a_r0_bare")

            isaac_row = next(row for row in summary_rows if row["backend_variant"] == "isaac")
            self.assertTrue(isaac_row["contract_complete"])
            self.assertEqual(isaac_row["prompt_variant"], "P1")
            self.assertEqual(isaac_row["runtime_variant"], "R0")
            self.assertEqual(isaac_row["runtime_policy"], "block_a_r0_bare")
            self.assertIn(isaac_row["termination_reason"], {"success", "task_precondition_failed"})
            if isaac_row["success"]:
                self.assertTrue(isaac_row["run_complete"])
            else:
                self.assertFalse(isaac_row["run_complete"])

            summary_payload = json.loads(
                (output_dir / "mixed_backend_summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(summary_payload["summary_title"], "Mixed Backend Summary")
            self.assertEqual(
                {row["backend_variant"] for row in summary_payload["by_backend_prompt_runtime"]},
                {"toy", "isaac"},
            )

            markdown_summary = (output_dir / "mixed_backend_summary.md").read_text(encoding="utf-8")
            self.assertIn("# Mixed Backend Summary: mixed_backend_suite_unit", markdown_summary)
            self.assertIn("## Backend x Prompt x Runtime", markdown_summary)


if __name__ == "__main__":
    unittest.main()
