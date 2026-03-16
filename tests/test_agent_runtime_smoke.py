"""Smoke tests for the minimal M4 agent runtime v0."""

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
AGENT_SCRIPT = REPO_ROOT / "scripts" / "run_agent_v0.py"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class AgentRuntimeSmokeTest(unittest.TestCase):
    def test_execute_agent_runtime_pick_place_succeeds(self) -> None:
        from isaacsim_agent.runtime import build_agent_v0_manipulation_task_config
        from isaacsim_agent.runtime import execute_agent_v0

        run_data = execute_agent_v0(
            config=build_agent_v0_manipulation_task_config(backend="toy"),
            run_id="unit-agent-runtime-pick-place",
        )

        self.assertTrue(run_data.result.success)
        self.assertEqual(run_data.result.termination_reason.value, "success")
        self.assertEqual(run_data.config.task_type.value, "pick_place")
        self.assertTrue(run_data.config.runtime_options.planner_enabled)
        self.assertEqual(run_data.result.invalid_action_count, 0)
        self.assertGreater(run_data.result.planner_call_count, 0)
        self.assertEqual(run_data.result.tool_call_count, run_data.result.step_count)
        self.assertEqual(len(run_data.planner_trace), run_data.result.planner_call_count)
        self.assertEqual(len(run_data.tool_trace), run_data.result.tool_call_count)
        self.assertEqual(run_data.events[0].event_type.value, "episode_start")
        self.assertEqual(run_data.events[-1].event_type.value, "episode_end")
        event_types = [event.event_type.value for event in run_data.events]
        self.assertIn("planner_call", event_types)
        self.assertIn("planner_response", event_types)
        self.assertIn("tool_call", event_types)
        self.assertIn("tool_result", event_types)
        self.assertTrue(run_data.result.metrics["manipulation.grasp_completed"])
        self.assertTrue(run_data.result.metrics["manipulation.object_placed"])
        self.assertEqual(run_data.result.metrics["manipulation.planner_backend"], "mock_rule_based")
        self.assertEqual(len(run_data.trajectory["states"]), run_data.result.step_count + 1)
        self.assertEqual(run_data.planner_trace[0]["parsed_action"]["tool_name"], "get_object_state")
        self.assertEqual(run_data.tool_trace[-1]["tool_name"], "scripted_pick_place_step")

    def test_execute_agent_runtime_succeeds(self) -> None:
        from isaacsim_agent.runtime import build_agent_v0_navigation_task_config
        from isaacsim_agent.runtime import execute_agent_v0

        run_data = execute_agent_v0(
            config=build_agent_v0_navigation_task_config(backend="toy"),
            run_id="unit-agent-runtime-execute",
        )

        self.assertTrue(run_data.result.success)
        self.assertEqual(run_data.result.termination_reason.value, "success")
        self.assertEqual(run_data.config.task_type.value, "navigation")
        self.assertTrue(run_data.config.runtime_options.planner_enabled)
        self.assertEqual(run_data.result.invalid_action_count, 0)
        self.assertGreater(run_data.result.planner_call_count, 0)
        self.assertEqual(run_data.result.tool_call_count, run_data.result.step_count)
        self.assertEqual(len(run_data.planner_trace), run_data.result.planner_call_count)
        self.assertEqual(len(run_data.tool_trace), run_data.result.tool_call_count)
        self.assertEqual(run_data.events[0].event_type.value, "episode_start")
        self.assertEqual(run_data.events[-1].event_type.value, "episode_end")
        event_types = [event.event_type.value for event in run_data.events]
        self.assertIn("planner_call", event_types)
        self.assertIn("planner_response", event_types)
        self.assertIn("tool_call", event_types)
        self.assertIn("tool_result", event_types)
        self.assertEqual(run_data.result.metrics["navigation.final_goal_distance_m"], 0.0)
        self.assertEqual(run_data.result.metrics["navigation.planner_backend"], "mock_rule_based")
        self.assertEqual(len(run_data.trajectory["poses"]), run_data.result.step_count + 1)
        self.assertEqual(run_data.planner_trace[0]["parsed_action"]["tool_name"], "get_robot_state")
        self.assertEqual(run_data.tool_trace[-1]["tool_name"], "navigate_to")

    def test_execute_agent_runtime_invalid_action_fails_cleanly(self) -> None:
        from isaacsim_agent.planner import SequencePlannerBackend
        from isaacsim_agent.runtime import build_agent_v0_navigation_task_config
        from isaacsim_agent.runtime import execute_agent_v0

        run_data = execute_agent_v0(
            config=build_agent_v0_navigation_task_config(backend="toy"),
            run_id="unit-agent-runtime-invalid",
            planner_backend=SequencePlannerBackend(
                responses=[{"tool_name": "fly_to", "arguments": {}}],
            ),
        )

        self.assertFalse(run_data.result.success)
        self.assertEqual(run_data.result.termination_reason.value, "invalid_action_limit")
        self.assertEqual(run_data.result.step_count, 1)
        self.assertEqual(run_data.result.planner_call_count, 1)
        self.assertEqual(run_data.result.tool_call_count, 0)
        self.assertEqual(run_data.result.invalid_action_count, 1)
        self.assertIn("unknown tool: fly_to", run_data.result.notes[-1])
        self.assertFalse(run_data.planner_trace[-1]["valid"])
        self.assertEqual(run_data.planner_trace[-1]["validation_error"], "unknown tool: fly_to")
        event_types = [event.event_type.value for event in run_data.events]
        self.assertIn("validation_warning", event_types)
        self.assertNotIn("tool_result", event_types)

    def test_agent_runtime_script_writes_canonical_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            command = [
                sys.executable,
                str(AGENT_SCRIPT),
                "--backend",
                "toy",
                "--run-id",
                "test-agent-runtime",
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
            self.assertIn("AGENT_RUNTIME_V0_OK", combined_output)

            run_dir = Path(temp_dir) / "runs" / "test-agent-runtime"
            self.assertTrue((run_dir / "manifest.json").is_file())
            self.assertTrue((run_dir / "task_config.json").is_file())
            self.assertTrue((run_dir / "episode_result.json").is_file())
            self.assertTrue((run_dir / "events.jsonl").is_file())
            self.assertTrue((run_dir / "artifacts" / "trajectory.json").is_file())
            self.assertTrue((run_dir / "artifacts" / "planner_trace.json").is_file())
            self.assertTrue((run_dir / "artifacts" / "tool_trace.json").is_file())

            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            task_config = json.loads((run_dir / "task_config.json").read_text(encoding="utf-8"))
            episode_result = json.loads((run_dir / "episode_result.json").read_text(encoding="utf-8"))
            event_lines = (run_dir / "events.jsonl").read_text(encoding="utf-8").strip().splitlines()
            trajectory = json.loads((run_dir / "artifacts" / "trajectory.json").read_text(encoding="utf-8"))
            planner_trace = json.loads((run_dir / "artifacts" / "planner_trace.json").read_text(encoding="utf-8"))
            tool_trace = json.loads((run_dir / "artifacts" / "tool_trace.json").read_text(encoding="utf-8"))

            self.assertEqual(manifest["run_id"], "test-agent-runtime")
            self.assertEqual(task_config["task_type"], "navigation")
            self.assertTrue(task_config["runtime_options"]["planner_enabled"])
            self.assertEqual(task_config["metadata"]["agent_runtime_v0"]["planner_backend"], "mock_rule_based")
            self.assertEqual(episode_result["termination_reason"], "success")
            self.assertTrue(episode_result["success"])
            self.assertGreater(episode_result["planner_call_count"], 0)
            self.assertEqual(episode_result["tool_call_count"], episode_result["step_count"])
            self.assertEqual(episode_result["invalid_action_count"], 0)
            self.assertEqual(episode_result["metrics"]["navigation.planner_backend"], "mock_rule_based")
            self.assertGreaterEqual(len(event_lines), 8)
            self.assertEqual(len(trajectory["poses"]), episode_result["step_count"] + 1)
            self.assertEqual(len(planner_trace), episode_result["planner_call_count"])
            self.assertEqual(len(tool_trace), episode_result["tool_call_count"])
            self.assertEqual(planner_trace[0]["parsed_action"]["tool_name"], "get_robot_state")
            self.assertEqual(tool_trace[-1]["tool_name"], "navigate_to")


if __name__ == "__main__":
    unittest.main()
