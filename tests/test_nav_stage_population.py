"""Direct helper-level tests for navigation stage population."""

from __future__ import annotations

import json
import unittest

from tests.isaac_stage_test_utils import resolve_isaac_root
from tests.isaac_stage_test_utils import run_stage_probe


class NavigationStagePopulationTest(unittest.TestCase):
    def _probe_or_assert_blocked(self, visualization: dict[str, object] | None = None) -> dict[str, object] | None:
        completed = run_stage_probe("navigation", visualization=visualization)
        combined_output = f"{completed.stdout}\n{completed.stderr}"

        if resolve_isaac_root() is None:
            self.assertNotEqual(completed.returncode, 0, combined_output)
            self.assertIn("EXPECTED_MISSING_DEPENDENCY", combined_output)
            return None

        self.assertEqual(completed.returncode, 0, combined_output)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["task_type"], "navigation")
        return payload

    def test_populate_navigation_stage_core_prims_and_handles_exist(self) -> None:
        payload = self._probe_or_assert_blocked()
        if payload is None:
            return

        prim_exists = payload["prim_exists"]
        self.assertTrue(prim_exists["world"])
        self.assertTrue(prim_exists["agent"])
        self.assertTrue(prim_exists["goal"])
        self.assertTrue(prim_exists["physics_scene"])
        self.assertFalse(prim_exists.get("trajectory", False))
        self.assertFalse(prim_exists.get("goal_region", False))

        handles_present = payload["handles_present"]
        self.assertTrue(handles_present["agent_translate_op"])
        self.assertTrue(handles_present["agent_rotate_op"])
        self.assertTrue(handles_present["goal_translate_op"])
        self.assertTrue(handles_present["goal_rotate_op"])

        metadata = payload["metadata"]
        self.assertEqual(metadata["backend"], "isaac")
        self.assertEqual(metadata["world_prim_path"], "/World")
        self.assertEqual(metadata["agent_prim_path"], "/World/Robot")
        self.assertEqual(metadata["goal_prim_path"], "/World/Goal")
        self.assertEqual(metadata["physics_scene_path"], "/World/PhysicsScene")
        self.assertEqual(metadata["stage_updates_per_action"], 2)
        self.assertNotIn("trajectory_prim_path", metadata)
        self.assertNotIn("goal_region_prim_path", metadata)

    def test_populate_navigation_stage_visualization_prims_exist_when_enabled(self) -> None:
        payload = self._probe_or_assert_blocked(
            visualization={"show_trajectory": True, "show_goal_region": True}
        )
        if payload is None:
            return

        prim_exists = payload["prim_exists"]
        self.assertTrue(prim_exists["world"])
        self.assertTrue(prim_exists["agent"])
        self.assertTrue(prim_exists["goal"])
        self.assertTrue(prim_exists["physics_scene"])
        self.assertTrue(prim_exists["trajectory"])
        self.assertTrue(prim_exists["goal_region"])

        handles_present = payload["handles_present"]
        self.assertTrue(handles_present["agent_translate_op"])
        self.assertTrue(handles_present["agent_rotate_op"])
        self.assertTrue(handles_present["goal_translate_op"])
        self.assertTrue(handles_present["goal_rotate_op"])

        metadata = payload["metadata"]
        self.assertEqual(metadata["backend"], "isaac")
        self.assertEqual(metadata["trajectory_prim_path"], "/World/Trajectory")
        self.assertEqual(metadata["goal_region_prim_path"], "/World/GoalRegion")


if __name__ == "__main__":
    unittest.main()
