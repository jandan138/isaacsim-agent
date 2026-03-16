"""Minimal Isaac-backed pick-and-place environment built on stage primitives."""

from __future__ import annotations

import math
import tempfile
from dataclasses import dataclass
from pathlib import Path

from isaacsim_agent.tools.manipulation import Pose3D

from .baseline import BasePickPlaceEnvironment
from .baseline import ManipulationBackendUnavailableError
from .baseline import PickPlaceTaskDefinition


@dataclass(frozen=True)
class IsaacPickPlaceWorldConfig:
    """Settings for the minimal Isaac stage used by the pick-and-place baseline."""

    world_prim_path: str = "/World"
    gripper_prim_path: str = "/World/Gripper"
    object_prim_path: str = "/World/Object"
    source_zone_prim_path: str = "/World/SourceZone"
    target_zone_prim_path: str = "/World/TargetZone"
    physics_scene_path: str = "/World/PhysicsScene"
    gripper_radius_m: float = 0.03
    object_size_m: float = 0.04
    zone_size_m: float = 0.12
    zone_height_m: float = 0.02
    stage_updates_per_action: int = 2


class MinimalIsaacPickPlaceEnvironment(BasePickPlaceEnvironment):
    """Deterministic pick-and-place baseline backed by a minimal Isaac Sim stage."""

    def __init__(self, definition: PickPlaceTaskDefinition, world_config: IsaacPickPlaceWorldConfig) -> None:
        super().__init__(definition=definition)
        self.world_config = world_config

        self._simulation_app = None
        self._stage = None
        self._gripper_translate_op = None
        self._gripper_rotate_op = None
        self._object_translate_op = None
        self._object_rotate_op = None

        self._initialize_stage()

    def _initialize_stage(self) -> None:
        try:
            from isaacsim import SimulationApp  # type: ignore
        except ModuleNotFoundError as exc:
            raise ManipulationBackendUnavailableError(
                "Isaac-backed pick-and-place requires launching via ./scripts/isaac_python.sh."
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
            raise ManipulationBackendUnavailableError(
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

            UsdGeom.Xform.Define(stage, self.world_config.world_prim_path)
            UsdPhysics.Scene.Define(stage, self.world_config.physics_scene_path)

            gripper = UsdGeom.Sphere.Define(stage, self.world_config.gripper_prim_path)
            gripper.GetRadiusAttr().Set(float(self.world_config.gripper_radius_m))
            gripper.CreateDisplayColorPrimvar(UsdGeom.Tokens.constant).Set([(0.1, 0.35, 0.9)])
            gripper_xformable = UsdGeom.Xformable(gripper.GetPrim())
            self._gripper_translate_op = gripper_xformable.AddTranslateOp()
            self._gripper_rotate_op = gripper_xformable.AddRotateXYZOp()

            cube = UsdGeom.Cube.Define(stage, self.world_config.object_prim_path)
            cube.GetSizeAttr().Set(float(self.world_config.object_size_m))
            cube.CreateDisplayColorPrimvar(UsdGeom.Tokens.constant).Set([(0.95, 0.45, 0.1)])
            cube_xformable = UsdGeom.Xformable(cube.GetPrim())
            self._object_translate_op = cube_xformable.AddTranslateOp()
            self._object_rotate_op = cube_xformable.AddRotateXYZOp()

            source_zone = UsdGeom.Cube.Define(stage, self.world_config.source_zone_prim_path)
            source_zone.GetSizeAttr().Set(1.0)
            source_zone.CreateDisplayColorPrimvar(UsdGeom.Tokens.constant).Set([(0.15, 0.65, 0.2)])
            source_zone_xformable = UsdGeom.Xformable(source_zone.GetPrim())
            source_zone_translate = source_zone_xformable.AddTranslateOp()
            source_zone_rotate = source_zone_xformable.AddRotateXYZOp()
            source_zone_scale = source_zone_xformable.AddScaleOp()

            target_zone = UsdGeom.Cube.Define(stage, self.world_config.target_zone_prim_path)
            target_zone.GetSizeAttr().Set(1.0)
            target_zone.CreateDisplayColorPrimvar(UsdGeom.Tokens.constant).Set([(0.8, 0.2, 0.2)])
            target_zone_xformable = UsdGeom.Xformable(target_zone.GetPrim())
            target_zone_translate = target_zone_xformable.AddTranslateOp()
            target_zone_rotate = target_zone_xformable.AddRotateXYZOp()
            target_zone_scale = target_zone_xformable.AddScaleOp()

            source_zone_pose = Pose3D(
                x=self.definition.object_start_pose.x,
                y=self.definition.object_start_pose.y,
                z=(
                    self.definition.object_start_pose.z
                    - (self.world_config.object_size_m / 2.0)
                    - (self.world_config.zone_height_m / 2.0)
                ),
            )
            target_zone_pose = Pose3D(
                x=self.definition.target_pose.x,
                y=self.definition.target_pose.y,
                z=(
                    self.definition.target_pose.z
                    - (self.world_config.object_size_m / 2.0)
                    - (self.world_config.zone_height_m / 2.0)
                ),
            )

            self._apply_pose(
                translate_op=source_zone_translate,
                rotate_op=source_zone_rotate,
                pose=source_zone_pose,
                Gf=Gf,
            )
            self._apply_scale(
                scale_op=source_zone_scale,
                scale_xyz=(
                    self.world_config.zone_size_m,
                    self.world_config.zone_size_m,
                    self.world_config.zone_height_m,
                ),
                Gf=Gf,
            )
            self._apply_pose(
                translate_op=target_zone_translate,
                rotate_op=target_zone_rotate,
                pose=target_zone_pose,
                Gf=Gf,
            )
            self._apply_scale(
                scale_op=target_zone_scale,
                scale_xyz=(
                    self.world_config.zone_size_m,
                    self.world_config.zone_size_m,
                    self.world_config.zone_height_m,
                ),
                Gf=Gf,
            )
            self._apply_pose(
                translate_op=self._object_translate_op,
                rotate_op=self._object_rotate_op,
                pose=self.definition.object_start_pose,
                Gf=Gf,
            )
            self._apply_pose(
                translate_op=self._gripper_translate_op,
                rotate_op=self._gripper_rotate_op,
                pose=self.definition.gripper_start_pose,
                Gf=Gf,
            )
            self._advance_updates()

            app = omni.kit.app.get_app()
            self.runtime_details = {
                "backend": "isaac",
                "kit_version": app.get_build_version(),
                "world_prim_path": self.world_config.world_prim_path,
                "gripper_prim_path": self.world_config.gripper_prim_path,
                "object_prim_path": self.world_config.object_prim_path,
                "source_zone_prim_path": self.world_config.source_zone_prim_path,
                "target_zone_prim_path": self.world_config.target_zone_prim_path,
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
    def _apply_pose(translate_op, rotate_op, pose: Pose3D, Gf) -> None:
        translate_op.Set(Gf.Vec3d(float(pose.x), float(pose.y), float(pose.z)))
        rotate_op.Set(
            Gf.Vec3f(
                float(math.degrees(pose.roll)),
                float(math.degrees(pose.pitch)),
                float(math.degrees(pose.yaw)),
            )
        )

    @staticmethod
    def _apply_scale(scale_op, scale_xyz: tuple[float, float, float], Gf) -> None:
        scale_op.Set(Gf.Vec3f(float(scale_xyz[0]), float(scale_xyz[1]), float(scale_xyz[2])))

    def _set_gripper_pose(self, pose: Pose3D) -> None:
        if self._gripper_translate_op is None or self._gripper_rotate_op is None:
            raise RuntimeError("Gripper prim transform ops are not initialized")

        from pxr import Gf  # type: ignore

        self._apply_pose(
            translate_op=self._gripper_translate_op,
            rotate_op=self._gripper_rotate_op,
            pose=pose,
            Gf=Gf,
        )
        self._advance_updates()

    def _read_gripper_pose(self) -> Pose3D:
        if self._gripper_translate_op is None or self._gripper_rotate_op is None:
            raise RuntimeError("Gripper prim transform ops are not initialized")

        translation = self._gripper_translate_op.Get()
        rotation_deg = self._gripper_rotate_op.Get()
        return Pose3D(
            x=float(translation[0]),
            y=float(translation[1]),
            z=float(translation[2]),
            roll=float(math.radians(rotation_deg[0])),
            pitch=float(math.radians(rotation_deg[1])),
            yaw=float(math.radians(rotation_deg[2])),
        )

    def _set_object_pose(self, pose: Pose3D) -> None:
        if self._object_translate_op is None or self._object_rotate_op is None:
            raise RuntimeError("Object prim transform ops are not initialized")

        from pxr import Gf  # type: ignore

        self._apply_pose(
            translate_op=self._object_translate_op,
            rotate_op=self._object_rotate_op,
            pose=pose,
            Gf=Gf,
        )
        self._advance_updates()

    def _read_object_pose(self) -> Pose3D:
        if self._object_translate_op is None or self._object_rotate_op is None:
            raise RuntimeError("Object prim transform ops are not initialized")

        translation = self._object_translate_op.Get()
        rotation_deg = self._object_rotate_op.Get()
        return Pose3D(
            x=float(translation[0]),
            y=float(translation[1]),
            z=float(translation[2]),
            roll=float(math.radians(rotation_deg[0])),
            pitch=float(math.radians(rotation_deg[1])),
            yaw=float(math.radians(rotation_deg[2])),
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
