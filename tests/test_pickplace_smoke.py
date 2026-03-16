"""Smoke tests for the minimal deterministic pick-and-place baseline."""

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
PICKPLACE_SCRIPT = REPO_ROOT / "scripts" / "run_pickplace_baseline.py"
ISAAC_WRAPPER = REPO_ROOT / "scripts" / "isaac_python.sh"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def resolve_isaac_root() -> Path | None:
    env_root = os.environ.get("ISAAC_SIM_ROOT")
    candidates = []
    if env_root:
        candidates.append(Path(env_root))
    candidates.append(Path("/isaac-sim"))

    ov_root = Path.home() / ".local" / "share" / "ov" / "pkg"
    if ov_root.is_dir():
        candidates.extend(sorted(ov_root.glob("isaac_sim-*"), reverse=True))

    candidates.extend(
        [
            Path("/opt/nvidia/isaac-sim"),
            Path("/opt/NVIDIA/isaac-sim"),
            Path("/opt/omniverse/isaac-sim"),
        ]
    )

    for candidate in candidates:
        if (candidate / "python.sh").is_file():
            return candidate
    return None


class PickPlaceBaselineSmokeTest(unittest.TestCase):
    def test_execute_pickplace_baseline_succeeds(self) -> None:
        from isaacsim_agent.tasks.manipulation import build_minimal_pickplace_task_config
        from isaacsim_agent.tasks.manipulation import execute_pickplace_baseline

        run_data = execute_pickplace_baseline(
            config=build_minimal_pickplace_task_config(backend="toy"),
            run_id="unit-pickplace-execute",
        )

        self.assertTrue(run_data.result.success)
        self.assertEqual(run_data.config.metadata["manipulation_baseline"]["backend"], "toy")
        self.assertEqual(run_data.result.termination_reason.value, "success")
        self.assertEqual(run_data.result.planner_call_count, 0)
        self.assertEqual(run_data.result.tool_call_count, run_data.result.step_count)
        self.assertTrue(run_data.result.metrics["manipulation.grasp_completed"])
        self.assertTrue(run_data.result.metrics["manipulation.object_placed"])
        self.assertIn("manipulation.final_object_to_target_distance_m", run_data.result.metrics)
        self.assertIn("manipulation.gripper_path_length_m", run_data.result.metrics)
        self.assertIn("manipulation.object_path_length_m", run_data.result.metrics)
        self.assertGreater(len(run_data.events), 0)
        self.assertEqual(run_data.events[0].event_type.value, "episode_start")
        self.assertEqual(run_data.events[-1].event_type.value, "episode_end")

    def test_pickplace_script_prefers_isaac_and_reports_blocker_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            isaac_root = resolve_isaac_root()
            if isaac_root is not None and ISAAC_WRAPPER.is_file():
                command = [
                    str(ISAAC_WRAPPER),
                    str(PICKPLACE_SCRIPT),
                    "--backend",
                    "isaac",
                    "--run-id",
                    "test-pickplace-baseline",
                    "--results-root",
                    temp_dir,
                ]
                expected_code = 0
                expected_backend = "isaac"
            else:
                command = [
                    sys.executable,
                    str(PICKPLACE_SCRIPT),
                    "--backend",
                    "isaac",
                    "--run-id",
                    "test-pickplace-baseline",
                    "--results-root",
                    temp_dir,
                ]
                expected_code = 1
                expected_backend = "isaac"

            completed = subprocess.run(
                command,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PYTHONPATH": str(SRC_ROOT), "PYTHONUNBUFFERED": "1"},
            )

            combined_output = f"{completed.stdout}\n{completed.stderr}"
            self.assertEqual(completed.returncode, expected_code, combined_output)

            run_dir = Path(temp_dir) / "runs" / "test-pickplace-baseline"
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

            self.assertEqual(manifest["run_id"], "test-pickplace-baseline")
            self.assertEqual(task_config["task_type"], "pick_place")
            self.assertEqual(task_config["metadata"]["manipulation_baseline"]["backend"], expected_backend)
            self.assertEqual(task_config["scene_id"], "minimal_isaac_tabletop_stage")
            self.assertEqual(trajectory["run_id"], "test-pickplace-baseline")
            self.assertEqual(trajectory["backend"], expected_backend)

            if expected_code == 0:
                self.assertIn("PICKPLACE_BASELINE_OK", combined_output)
                self.assertTrue((run_dir / "artifacts" / "stage.usda").is_file())
                self.assertTrue(episode_result["success"])
                self.assertEqual(episode_result["termination_reason"], "success")
                self.assertEqual(episode_result["planner_call_count"], 0)
                self.assertEqual(episode_result["tool_call_count"], episode_result["step_count"])
                self.assertTrue(episode_result["metrics"]["manipulation.grasp_completed"])
                self.assertTrue(episode_result["metrics"]["manipulation.object_placed"])
                self.assertGreaterEqual(len(event_lines), 10)
                self.assertEqual(len(trajectory["states"]), episode_result["step_count"] + 1)
                self.assertEqual(trajectory["runtime"]["backend"], "isaac")
                self.assertEqual(trajectory["runtime"]["gripper_prim_path"], "/World/Gripper")
            else:
                self.assertIn("PICKPLACE_BASELINE_FAILED", combined_output)
                self.assertFalse(episode_result["success"])
                self.assertEqual(episode_result["termination_reason"], "task_precondition_failed")
                self.assertEqual(trajectory["status"], "blocked")
                self.assertIn("Isaac-backed pick-and-place", episode_result["notes"][0])
                self.assertGreaterEqual(len(event_lines), 3)


if __name__ == "__main__":
    unittest.main()
