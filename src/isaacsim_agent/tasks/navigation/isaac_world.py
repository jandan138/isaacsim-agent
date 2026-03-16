"""Minimal Isaac-backed navigation environment built on stage primitives."""

from __future__ import annotations

import math
import tempfile
from dataclasses import dataclass
from pathlib import Path

from isaacsim_agent.contracts import TerminationReason
from isaacsim_agent.tools.navigation import Pose2D
from isaacsim_agent.tools.navigation import compute_direct_navigation_step
from isaacsim_agent.tools.navigation import distance_between_poses

from .baseline import NavigationBackendUnavailableError
from .baseline import NavigationObservation
from .baseline import NavigationStepResult
from .baseline import NavigationTaskDefinition


@dataclass(frozen=True)
class IsaacNavigationWorldConfig:
    """Settings for the minimal Isaac stage used by the navigation baseline."""

    agent_prim_path: str = "/World/Robot"
    goal_prim_path: str = "/World/Goal"
    physics_scene_path: str = "/World/PhysicsScene"
    robot_radius_m: float = 0.15
    goal_marker_size_m: float = 0.25
    stage_updates_per_action: int = 2


class MinimalIsaacNavigationEnvironment:
    """Deterministic navigation baseline backed by a minimal Isaac Sim stage."""

    def __init__(self, definition: NavigationTaskDefinition, world_config: IsaacNavigationWorldConfig) -> None:
        self.definition = definition
        self.world_config = world_config
        self.path: list[Pose2D] = []
        self.step_count = 0
        self.sim_time_sec = 0.0
        self.stuck_steps = 0
        self.runtime_details: dict[str, object] = {}

        self._simulation_app = None
        self._stage = None
        self._agent_translate_op = None
        self._agent_rotate_op = None
        self._goal_translate_op = None
        self._goal_rotate_op = None

        self._initialize_stage()

    def _initialize_stage(self) -> None:
        try:
            from isaacsim import SimulationApp  # type: ignore
        except ModuleNotFoundError as exc:
            raise NavigationBackendUnavailableError(
                "Isaac-backed navigation requires launching via ./scripts/isaac_python.sh."
            ) from exc

        self._simulation_app = SimulationApp({"headless": True, "sync_loads": True})

        try:
            import omni.kit.app  # type: ignore
            import omni.usd  # type: ignore
            from pxr import Gf  # type: ignore
            from pxr import UsdGeom  # type: ignore
            from pxr import UsdPhysics  # type: ignore
        except ModuleNotFoundError as exc:
            self.close()
            raise NavigationBackendUnavailableError(
                "Isaac Sim modules were not importable after starting SimulationApp."
            ) from exc
        try:
            context = omni.usd.get_context()
            if not context.new_stage():
                raise RuntimeError("omni.usd.get_context().new_stage() returned False")

            stage = context.get_stage()
            if stage is None:
                raise RuntimeError("Isaac Sim returned no active USD stage")

            self._stage = stage
            UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
            UsdGeom.SetStageMetersPerUnit(stage, 1.0)

            UsdGeom.Xform.Define(stage, "/World")
            UsdPhysics.Scene.Define(stage, self.world_config.physics_scene_path)

            robot = UsdGeom.Sphere.Define(stage, self.world_config.agent_prim_path)
            robot.GetRadiusAttr().Set(float(self.world_config.robot_radius_m))
            robot.CreateDisplayColorPrimvar(UsdGeom.Tokens.constant).Set([(0.1, 0.4, 0.9)])
            robot_xformable = UsdGeom.Xformable(robot.GetPrim())
            self._agent_translate_op = robot_xformable.AddTranslateOp()
            self._agent_rotate_op = robot_xformable.AddRotateXYZOp()

            goal = UsdGeom.Cube.Define(stage, self.world_config.goal_prim_path)
            goal.GetSizeAttr().Set(float(self.world_config.goal_marker_size_m))
            goal.CreateDisplayColorPrimvar(UsdGeom.Tokens.constant).Set([(0.1, 0.75, 0.2)])
            goal_xformable = UsdGeom.Xformable(goal.GetPrim())
            self._goal_translate_op = goal_xformable.AddTranslateOp()
            self._goal_rotate_op = goal_xformable.AddRotateXYZOp()

            self._apply_pose(
                translate_op=self._goal_translate_op,
                rotate_op=self._goal_rotate_op,
                pose=self.definition.goal_pose,
                z_height=self.world_config.goal_marker_size_m / 2.0,
                Gf=Gf,
            )
            self._apply_pose(
                translate_op=self._agent_translate_op,
                rotate_op=self._agent_rotate_op,
                pose=self.definition.start_pose,
                z_height=self.world_config.robot_radius_m,
                Gf=Gf,
            )
            self._advance_updates()

            app = omni.kit.app.get_app()
            self.runtime_details = {
                "backend": "isaac",
                "kit_version": app.get_build_version(),
                "agent_prim_path": self.world_config.agent_prim_path,
                "goal_prim_path": self.world_config.goal_prim_path,
                "physics_scene_path": self.world_config.physics_scene_path,
                "stage_updates_per_action": self.world_config.stage_updates_per_action,
            }
        except Exception:
            self.close()
            raise

    def _advance_updates(self) -> None:
        if self._simulation_app is None:
            raise RuntimeError("SimulationApp is not initialized")
        for _ in range(self.world_config.stage_updates_per_action):
            self._simulation_app.update()

    @staticmethod
    def _apply_pose(translate_op, rotate_op, pose: Pose2D, z_height: float, Gf) -> None:
        translate_op.Set(Gf.Vec3d(float(pose.x), float(pose.y), float(z_height)))
        rotate_op.Set(Gf.Vec3f(0.0, 0.0, float(math.degrees(pose.yaw))))

    def _set_agent_pose(self, pose: Pose2D) -> None:
        if self._agent_translate_op is None or self._agent_rotate_op is None:
            raise RuntimeError("Agent prim transform ops are not initialized")

        from pxr import Gf  # type: ignore

        self._apply_pose(
            translate_op=self._agent_translate_op,
            rotate_op=self._agent_rotate_op,
            pose=pose,
            z_height=self.world_config.robot_radius_m,
            Gf=Gf,
        )
        self._advance_updates()

    def _read_agent_pose(self) -> Pose2D:
        if self._agent_translate_op is None or self._agent_rotate_op is None:
            raise RuntimeError("Agent prim transform ops are not initialized")

        translation = self._agent_translate_op.Get()
        rotation_deg = self._agent_rotate_op.Get()
        return Pose2D(
            x=float(translation[0]),
            y=float(translation[1]),
            yaw=float(math.radians(rotation_deg[2])),
        )

    def reset(self) -> NavigationObservation:
        self.step_count = 0
        self.sim_time_sec = 0.0
        self.stuck_steps = 0
        self._set_agent_pose(self.definition.start_pose)
        observation = self.observe()
        self.path = [observation.pose]
        return observation

    def observe(self) -> NavigationObservation:
        pose = self._read_agent_pose()
        return NavigationObservation(
            pose=pose,
            distance_to_goal_m=distance_between_poses(pose, self.definition.goal_pose),
            sim_time_sec=self.sim_time_sec,
        )

    def termination_reason(self) -> TerminationReason | None:
        observation = self.observe()
        if observation.distance_to_goal_m <= self.definition.success_radius_m:
            return TerminationReason.SUCCESS
        if self.step_count >= self.definition.max_steps:
            return TerminationReason.MAX_STEPS
        if self.sim_time_sec >= self.definition.max_time_sec:
            return TerminationReason.TIMEOUT
        if self.stuck_steps >= self.definition.max_stuck_steps:
            return TerminationReason.ROBOT_STUCK
        return None

    def step_toward_goal(self) -> NavigationStepResult:
        observation_before = self.observe()
        action = compute_direct_navigation_step(
            current_pose=observation_before.pose,
            goal_pose=self.definition.goal_pose,
            step_size_m=self.definition.step_size_m,
        )

        self._set_agent_pose(action.target_pose)
        self.step_count += 1
        self.sim_time_sec = round(self.step_count * self.definition.control_dt_sec, 6)

        observation_after = self.observe()
        progress_m = observation_before.distance_to_goal_m - observation_after.distance_to_goal_m
        if progress_m <= self.definition.stuck_distance_epsilon_m:
            self.stuck_steps += 1
        else:
            self.stuck_steps = 0

        self.path.append(observation_after.pose)
        return NavigationStepResult(
            action=action,
            observation=observation_after,
            moved_distance_m=action.step_distance_m,
            progress_m=progress_m,
            stuck_steps=self.stuck_steps,
        )

    def stage_artifact_text(self) -> str:
        if self._stage is None:
            raise RuntimeError("USD stage is not initialized")

        root_layer = self._stage.GetRootLayer()
        try:
            return root_layer.ExportToString()
        except AttributeError:
            with tempfile.TemporaryDirectory() as temp_dir:
                export_path = Path(temp_dir) / "stage.usda"
                self._stage.Export(str(export_path))
                return export_path.read_text(encoding="utf-8")

    def close(self) -> None:
        # Let the short-lived wrapper process own SimulationApp teardown.
        # Closing it here can terminate the interpreter before run artifacts are written.
        self._stage = None
