"""Smoke tests for the minimal deterministic navigation baseline."""

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
NAV_SCRIPT = REPO_ROOT / "scripts" / "run_nav_baseline.py"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class NavigationBaselineSmokeTest(unittest.TestCase):
    def test_execute_navigation_baseline_succeeds(self) -> None:
        from isaacsim_agent.tasks.navigation import build_minimal_navigation_task_config
        from isaacsim_agent.tasks.navigation import execute_navigation_baseline

        run_data = execute_navigation_baseline(
            config=build_minimal_navigation_task_config(),
            run_id="unit-nav-execute",
        )

        self.assertTrue(run_data.result.success)
        self.assertEqual(run_data.result.termination_reason.value, "success")
        self.assertEqual(run_data.result.planner_call_count, 0)
        self.assertEqual(run_data.result.tool_call_count, run_data.result.step_count)
        self.assertIn("navigation.goal_reached", run_data.result.metrics)
        self.assertIn("navigation.final_goal_distance_m", run_data.result.metrics)
        self.assertIn("navigation.path_length_m", run_data.result.metrics)
        self.assertIn("navigation.waypoints_completed", run_data.result.metrics)
        self.assertGreater(len(run_data.events), 0)
        self.assertEqual(run_data.events[0].event_type.value, "episode_start")
        self.assertEqual(run_data.events[-1].event_type.value, "episode_end")

    def test_nav_script_writes_contract_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            command = [
                sys.executable,
                str(NAV_SCRIPT),
                "--run-id",
                "test-nav-baseline",
                "--results-root",
                temp_dir,
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
            self.assertIn("NAV_BASELINE_OK", combined_output)

            run_dir = Path(temp_dir) / "runs" / "test-nav-baseline"
            self.assertTrue((run_dir / "manifest.json").is_file())
            self.assertTrue((run_dir / "task_config.json").is_file())
            self.assertTrue((run_dir / "episode_result.json").is_file())
            self.assertTrue((run_dir / "events.jsonl").is_file())
            self.assertTrue((run_dir / "artifacts" / "trajectory.json").is_file())

            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            task_config = json.loads((run_dir / "task_config.json").read_text(encoding="utf-8"))
            episode_result = json.loads((run_dir / "episode_result.json").read_text(encoding="utf-8"))
            event_lines = (run_dir / "events.jsonl").read_text(encoding="utf-8").strip().splitlines()
            trajectory = json.loads((run_dir / "artifacts" / "trajectory.json").read_text(encoding="utf-8"))

            self.assertEqual(manifest["run_id"], "test-nav-baseline")
            self.assertEqual(task_config["task_type"], "navigation")
            self.assertEqual(task_config["scene_id"], "minimal_empty_stage")
            self.assertTrue(episode_result["success"])
            self.assertEqual(episode_result["termination_reason"], "success")
            self.assertEqual(episode_result["planner_call_count"], 0)
            self.assertEqual(episode_result["tool_call_count"], episode_result["step_count"])
            self.assertTrue(episode_result["metrics"]["navigation.goal_reached"])
            self.assertGreaterEqual(len(event_lines), 6)
            self.assertEqual(trajectory["run_id"], "test-nav-baseline")
            self.assertEqual(len(trajectory["poses"]), episode_result["step_count"] + 1)


if __name__ == "__main__":
    unittest.main()
