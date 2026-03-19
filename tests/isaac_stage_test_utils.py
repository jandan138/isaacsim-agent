"""Shared helpers for helper-level Isaac stage population tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
ISAAC_WRAPPER = REPO_ROOT / "scripts" / "isaac_python.sh"
EXPECTED_MISSING_DEPENDENCY = 3


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


def _expected_missing_dependency_result(task_type: str) -> subprocess.CompletedProcess[str]:
    payload = {
        "status": "expected_missing_dependency",
        "task_type": task_type,
        "prim_exists": {},
        "handles_present": {},
        "metadata": {},
    }
    return subprocess.CompletedProcess(
        args=[str(ISAAC_WRAPPER), "-", task_type],
        returncode=EXPECTED_MISSING_DEPENDENCY,
        stdout=json.dumps(payload),
        stderr="EXPECTED_MISSING_DEPENDENCY: Isaac Sim installation not found.",
    )


def _probe_script() -> str:
    return """\
import json
import sys
from pathlib import Path

report_path = Path(sys.argv[1])
task_type = sys.argv[2]
visualization_payload = json.loads(sys.argv[3])

payload = {
    "status": "error",
    "task_type": task_type,
    "prim_exists": {},
    "handles_present": {},
    "metadata": {},
}

simulation_app = None
try:
    from isaacsim import SimulationApp  # type: ignore

    simulation_app = SimulationApp({"headless": True, "sync_loads": True})

    import omni.usd  # type: ignore

    context = omni.usd.get_context()
    if not context.new_stage():
        raise RuntimeError("omni.usd.get_context().new_stage() returned False")

    stage = context.get_stage()
    if stage is None:
        raise RuntimeError("Isaac Sim returned no active USD stage")

    if task_type == "navigation":
        from isaacsim_agent.tasks.navigation.baseline import NavigationTaskDefinition
        from isaacsim_agent.tasks.navigation.isaac_world import IsaacNavigationWorldConfig
        from isaacsim_agent.tasks.navigation.isaac_world import VisualizationConfig
        from isaacsim_agent.tasks.navigation.isaac_world import populate_navigation_stage
        from isaacsim_agent.tools.navigation import Pose2D

        definition = NavigationTaskDefinition(
            start_pose=Pose2D(x=0.0, y=0.0, yaw=0.0),
            goal_pose=Pose2D(x=2.0, y=0.0, yaw=0.0),
            success_radius_m=0.2,
            step_size_m=0.5,
            control_dt_sec=0.5,
            max_steps=10,
            max_time_sec=10.0,
            max_stuck_steps=3,
            stuck_distance_epsilon_m=1e-6,
        )
        world_config = IsaacNavigationWorldConfig()
        visualization_config = (
            VisualizationConfig(**visualization_payload) if visualization_payload else None
        )
        handles = populate_navigation_stage(
            stage=stage,
            definition=definition,
            world_config=world_config,
            visualization_config=visualization_config,
        )
        payload = {
            "status": "ok",
            "task_type": task_type,
            "prim_exists": {
                "world": stage.GetPrimAtPath(world_config.world_prim_path).IsValid(),
                "agent": stage.GetPrimAtPath(world_config.agent_prim_path).IsValid(),
                "goal": stage.GetPrimAtPath(world_config.goal_prim_path).IsValid(),
                "physics_scene": stage.GetPrimAtPath(world_config.physics_scene_path).IsValid(),
                "trajectory": stage.GetPrimAtPath(world_config.trajectory_prim_path).IsValid(),
                "goal_region": stage.GetPrimAtPath(world_config.goal_region_prim_path).IsValid(),
            },
            "handles_present": {
                "agent_translate_op": handles.agent_translate_op is not None,
                "agent_rotate_op": handles.agent_rotate_op is not None,
                "goal_translate_op": handles.goal_translate_op is not None,
                "goal_rotate_op": handles.goal_rotate_op is not None,
            },
            "metadata": handles.metadata,
        }
    elif task_type == "pick_place":
        from isaacsim_agent.tasks.manipulation.baseline import PickPlaceTaskDefinition
        from isaacsim_agent.tasks.manipulation.isaac_world import IsaacPickPlaceWorldConfig
        from isaacsim_agent.tasks.manipulation.isaac_world import VisualizationConfig
        from isaacsim_agent.tasks.manipulation.isaac_world import populate_pickplace_stage
        from isaacsim_agent.tools.manipulation import Pose3D

        definition = PickPlaceTaskDefinition(
            gripper_start_pose=Pose3D(x=0.0, y=0.0, z=0.18),
            object_start_pose=Pose3D(x=0.0, y=0.0, z=0.02),
            target_pose=Pose3D(x=0.25, y=0.0, z=0.02),
            hover_offset_m=0.08,
            grasp_tolerance_m=0.03,
            place_tolerance_m=0.04,
            control_dt_sec=0.5,
            max_steps=10,
            max_time_sec=10.0,
        )
        world_config = IsaacPickPlaceWorldConfig()
        visualization_config = (
            VisualizationConfig(**visualization_payload) if visualization_payload else None
        )
        handles = populate_pickplace_stage(
            stage=stage,
            definition=definition,
            world_config=world_config,
            visualization_config=visualization_config,
        )
        payload = {
            "status": "ok",
            "task_type": task_type,
            "prim_exists": {
                "world": stage.GetPrimAtPath(world_config.world_prim_path).IsValid(),
                "gripper": stage.GetPrimAtPath(world_config.gripper_prim_path).IsValid(),
                "object": stage.GetPrimAtPath(world_config.object_prim_path).IsValid(),
                "source_zone": stage.GetPrimAtPath(world_config.source_zone_prim_path).IsValid(),
                "target_zone": stage.GetPrimAtPath(world_config.target_zone_prim_path).IsValid(),
                "physics_scene": stage.GetPrimAtPath(world_config.physics_scene_path).IsValid(),
            },
            "handles_present": {
                "gripper_translate_op": handles.gripper_translate_op is not None,
                "gripper_rotate_op": handles.gripper_rotate_op is not None,
                "object_translate_op": handles.object_translate_op is not None,
                "object_rotate_op": handles.object_rotate_op is not None,
                "source_zone_translate_op": handles.source_zone_translate_op is not None,
                "source_zone_rotate_op": handles.source_zone_rotate_op is not None,
                "source_zone_scale_op": handles.source_zone_scale_op is not None,
                "target_zone_translate_op": handles.target_zone_translate_op is not None,
                "target_zone_rotate_op": handles.target_zone_rotate_op is not None,
                "target_zone_scale_op": handles.target_zone_scale_op is not None,
            },
            "metadata": handles.metadata,
        }
    else:
        raise ValueError(f"Unsupported task_type: {task_type}")
except Exception as exc:  # pragma: no cover - probe-side error marshaling
    payload["status"] = "error"
    payload["error"] = f"{type(exc).__name__}: {exc}"
finally:
    report_path.write_text(json.dumps(payload), encoding="utf-8")
    if simulation_app is not None:
        simulation_app.close()
"""


def run_stage_probe(
    task_type: str,
    visualization: dict[str, object] | None = None,
) -> subprocess.CompletedProcess[str]:
    if resolve_isaac_root() is None or not ISAAC_WRAPPER.is_file():
        return _expected_missing_dependency_result(task_type=task_type)

    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = Path(temp_dir) / "stage_probe.json"
        completed = subprocess.run(
            [
                str(ISAAC_WRAPPER),
                "-",
                str(report_path),
                task_type,
                json.dumps(visualization or {}),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            input=_probe_script(),
            check=False,
            env={
                **os.environ,
                "PYTHONPATH": str(SRC_ROOT),
                "PYTHONUNBUFFERED": "1",
            },
        )
        stdout = report_path.read_text(encoding="utf-8") if report_path.is_file() else completed.stdout
        return subprocess.CompletedProcess(
            args=completed.args,
            returncode=completed.returncode,
            stdout=stdout,
            stderr=completed.stderr,
        )
