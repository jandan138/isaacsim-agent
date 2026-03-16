"""Tests for shared contracts, serialization, and artifact layout."""

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

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class ContractsTest(unittest.TestCase):
    def test_task_config_round_trip(self) -> None:
        from isaacsim_agent.contracts import DifficultyLevel
        from isaacsim_agent.contracts import NavigationSpec
        from isaacsim_agent.contracts import PickPlaceSpec
        from isaacsim_agent.contracts import RuntimeOptions
        from isaacsim_agent.contracts import TaskConfig
        from isaacsim_agent.contracts import TaskType

        config = TaskConfig(
            task_type=TaskType.NAVIGATION,
            task_id="nav_round_trip",
            scene_id="scene_A",
            robot_id="robot_A",
            seed=1,
            max_steps=10,
            max_time_sec=5.0,
            headless=True,
            render=False,
            difficulty=DifficultyLevel.EASY,
            runtime_options=RuntimeOptions(planner_enabled=False),
            navigation=NavigationSpec(goal_ref="goal_A"),
        )

        payload = config.to_dict()
        loaded = TaskConfig.from_dict(payload)

        self.assertEqual(loaded.task_type.value, "navigation")
        self.assertEqual(loaded.navigation.goal_ref, "goal_A")

        pick_place_config = TaskConfig(
            task_type=TaskType.PICK_PLACE,
            task_id="pick_place_round_trip",
            scene_id="scene_B",
            robot_id="robot_B",
            seed=2,
            max_steps=12,
            max_time_sec=6.0,
            headless=True,
            render=False,
            difficulty=DifficultyLevel.EASY,
            runtime_options=RuntimeOptions(planner_enabled=False),
            pick_place=PickPlaceSpec(
                object_id="block_A",
                source_id="source_zone_A",
                target_id="target_zone_B",
                target_pose={"x": 0.4, "y": 0.0, "z": 0.03},
            ),
        )

        pick_place_loaded = TaskConfig.from_dict(pick_place_config.to_dict())
        self.assertEqual(pick_place_loaded.task_type.value, "pick_place")
        self.assertEqual(pick_place_loaded.pick_place.object_id, "block_A")
        self.assertEqual(pick_place_loaded.pick_place.target_pose["z"], 0.03)

    def test_validation_script_writes_canonical_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            command = [
                sys.executable,
                str(REPO_ROOT / "scripts" / "validate_contracts.py"),
                "--run-id",
                "test-contract-run",
                "--results-root",
                temp_dir,
            ]
            completed = subprocess.run(
                command,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PYTHONPATH": str(SRC_ROOT)},
            )

            combined_output = f"{completed.stdout}\n{completed.stderr}"
            self.assertEqual(completed.returncode, 0, combined_output)
            self.assertIn("CONTRACT_VALIDATION_OK", combined_output)

            run_dir = Path(temp_dir) / "runs" / "test-contract-run"
            self.assertTrue((run_dir / "manifest.json").is_file())
            self.assertTrue((run_dir / "task_config.json").is_file())
            self.assertTrue((run_dir / "episode_result.json").is_file())
            self.assertTrue((run_dir / "events.jsonl").is_file())
            self.assertTrue((run_dir / "artifacts").is_dir())

            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            result = json.loads((run_dir / "episode_result.json").read_text(encoding="utf-8"))
            event_lines = (run_dir / "events.jsonl").read_text(encoding="utf-8").strip().splitlines()

            self.assertEqual(manifest["run_id"], "test-contract-run")
            self.assertEqual(result["termination_reason"], "success")
            self.assertGreaterEqual(len(event_lines), 3)


if __name__ == "__main__":
    unittest.main()
