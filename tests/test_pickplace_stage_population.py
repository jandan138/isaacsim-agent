"""Direct helper-level tests for pick-place stage population."""

from __future__ import annotations

import json
import unittest


class PickPlaceStagePopulationTest(unittest.TestCase):
    def _load_shared_helper(self):
        try:
            from tests.isaac_stage_test_utils import resolve_isaac_root
            from tests.isaac_stage_test_utils import run_stage_probe
        except ModuleNotFoundError as exc:
            self.skipTest(f"Shared Isaac stage helper is not available in this workspace yet: {exc}")
        return resolve_isaac_root, run_stage_probe

    def _run_probe(self, visualization: dict[str, object] | None = None) -> dict[str, object] | None:
        resolve_isaac_root, run_stage_probe = self._load_shared_helper()
        completed = run_stage_probe("pick_place", visualization=visualization)
        combined_output = f"{completed.stdout}\n{completed.stderr}"

        if resolve_isaac_root() is None:
            self.assertNotEqual(completed.returncode, 0, combined_output)
            self.assertIn("EXPECTED_MISSING_DEPENDENCY", combined_output)
            return None

        self.assertEqual(completed.returncode, 0, combined_output)
        payload = json.loads(completed.stdout.strip())
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["task_type"], "pick_place")
        return payload

    def test_pickplace_stage_population_default_scene(self) -> None:
        payload = self._run_probe()
        if payload is None:
            return

        prim_exists = payload["prim_exists"]
        self.assertTrue(prim_exists["world"])
        self.assertTrue(prim_exists["gripper"])
        self.assertTrue(prim_exists["object"])
        self.assertTrue(prim_exists["source_zone"])
        self.assertTrue(prim_exists["target_zone"])
        self.assertTrue(prim_exists["physics_scene"])

        handles_present = payload["handles_present"]
        self.assertTrue(handles_present["gripper_translate_op"])
        self.assertTrue(handles_present["gripper_rotate_op"])
        self.assertTrue(handles_present["object_translate_op"])
        self.assertTrue(handles_present["object_rotate_op"])
        self.assertTrue(handles_present["source_zone_translate_op"])
        self.assertTrue(handles_present["source_zone_rotate_op"])
        self.assertTrue(handles_present["source_zone_scale_op"])
        self.assertTrue(handles_present["target_zone_translate_op"])
        self.assertTrue(handles_present["target_zone_rotate_op"])
        self.assertTrue(handles_present["target_zone_scale_op"])

        metadata = payload["metadata"]
        self.assertEqual(metadata["backend"], "isaac")
        self.assertEqual(metadata["world_prim_path"], "/World")
        self.assertEqual(metadata["gripper_prim_path"], "/World/Gripper")
        self.assertEqual(metadata["object_prim_path"], "/World/Object")
        self.assertEqual(metadata["source_zone_prim_path"], "/World/SourceZone")
        self.assertEqual(metadata["target_zone_prim_path"], "/World/TargetZone")
        self.assertEqual(metadata["physics_scene_path"], "/World/PhysicsScene")
        self.assertEqual(metadata["stage_updates_per_action"], 2)

    def test_pickplace_stage_population_accepts_palette_override(self) -> None:
        payload = self._run_probe(
            visualization={
                "palette": {
                    "gripper": [0.3, 0.5, 0.95],
                    "object": [0.9, 0.55, 0.15],
                    "source_zone": [0.2, 0.75, 0.35],
                    "target_zone": [0.9, 0.25, 0.35],
                }
            }
        )
        if payload is None:
            return

        prim_exists = payload["prim_exists"]
        self.assertTrue(prim_exists["world"])
        self.assertTrue(prim_exists["gripper"])
        self.assertTrue(prim_exists["object"])
        self.assertTrue(prim_exists["source_zone"])
        self.assertTrue(prim_exists["target_zone"])
        self.assertTrue(prim_exists["physics_scene"])

        handles_present = payload["handles_present"]
        self.assertTrue(handles_present["gripper_translate_op"])
        self.assertTrue(handles_present["gripper_rotate_op"])
        self.assertTrue(handles_present["object_translate_op"])
        self.assertTrue(handles_present["object_rotate_op"])
        self.assertTrue(handles_present["source_zone_translate_op"])
        self.assertTrue(handles_present["source_zone_rotate_op"])
        self.assertTrue(handles_present["source_zone_scale_op"])
        self.assertTrue(handles_present["target_zone_translate_op"])
        self.assertTrue(handles_present["target_zone_rotate_op"])
        self.assertTrue(handles_present["target_zone_scale_op"])

        metadata = payload["metadata"]
        self.assertEqual(metadata["backend"], "isaac")
        self.assertEqual(metadata["stage_updates_per_action"], 2)


if __name__ == "__main__":
    unittest.main()
