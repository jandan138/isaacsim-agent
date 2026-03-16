"""Contract-compliant minimal pick-and-place baselines with toy and Isaac backends."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from isaacsim_agent.contracts import DifficultyLevel
from isaacsim_agent.contracts import EpisodeResult
from isaacsim_agent.contracts import EventRecord
from isaacsim_agent.contracts import EventType
from isaacsim_agent.contracts import PickPlaceSpec
from isaacsim_agent.contracts import RunArtifactsLayout
from isaacsim_agent.contracts import RunManifest
from isaacsim_agent.contracts import RuntimeOptions
from isaacsim_agent.contracts import TaskConfig
from isaacsim_agent.contracts import TaskType
from isaacsim_agent.contracts import TerminationReason
from isaacsim_agent.contracts import TokenUsage
from isaacsim_agent.contracts import write_episode_result
from isaacsim_agent.contracts import write_event_log
from isaacsim_agent.contracts import write_run_manifest
from isaacsim_agent.contracts import write_task_config
from isaacsim_agent.tools.manipulation import Pose3D
from isaacsim_agent.tools.manipulation import SCRIPTED_PICKPLACE_TOOL
from isaacsim_agent.tools.manipulation import ScriptedPickPlaceAction
from isaacsim_agent.tools.manipulation import compute_pose_path_length
from isaacsim_agent.tools.manipulation import distance_between_poses


class ManipulationBackendUnavailableError(RuntimeError):
    """Raised when the requested manipulation backend cannot be initialized."""


@dataclass(frozen=True)
class PickPlaceTaskDefinition:
    """Execution parameters for the minimal pick-and-place sequence."""

    gripper_start_pose: Pose3D
    object_start_pose: Pose3D
    target_pose: Pose3D
    hover_offset_m: float
    grasp_tolerance_m: float
    place_tolerance_m: float
    control_dt_sec: float
    max_steps: int
    max_time_sec: float

    def source_hover_pose(self) -> Pose3D:
        return Pose3D(
            x=self.object_start_pose.x,
            y=self.object_start_pose.y,
            z=self.object_start_pose.z + self.hover_offset_m,
            roll=self.gripper_start_pose.roll,
            pitch=self.gripper_start_pose.pitch,
            yaw=self.gripper_start_pose.yaw,
        )

    def target_hover_pose(self) -> Pose3D:
        return Pose3D(
            x=self.target_pose.x,
            y=self.target_pose.y,
            z=self.target_pose.z + self.hover_offset_m,
            roll=self.gripper_start_pose.roll,
            pitch=self.gripper_start_pose.pitch,
            yaw=self.gripper_start_pose.yaw,
        )


@dataclass(frozen=True)
class PickPlaceObservation:
    """Current deterministic state of the minimal manipulation task."""

    gripper_pose: Pose3D
    object_pose: Pose3D
    sim_time_sec: float
    gripper_open: bool
    object_attached: bool
    current_phase: str
    distance_to_object_m: float
    distance_to_target_m: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "gripper_pose": self.gripper_pose.to_dict(),
            "object_pose": self.object_pose.to_dict(),
            "sim_time_sec": round(self.sim_time_sec, 6),
            "gripper_open": self.gripper_open,
            "object_attached": self.object_attached,
            "current_phase": self.current_phase,
            "distance_to_object_m": round(self.distance_to_object_m, 6),
            "distance_to_target_m": round(self.distance_to_target_m, 6),
        }


@dataclass(frozen=True)
class PickPlaceStepResult:
    """One deterministic scripted pick-and-place step and its resulting observation."""

    action: ScriptedPickPlaceAction
    observation: PickPlaceObservation
    gripper_moved_distance_m: float
    object_moved_distance_m: float


@dataclass(frozen=True)
class PickPlaceRunData:
    """In-memory representation of a baseline run before disk serialization."""

    config: TaskConfig
    manifest: RunManifest
    result: EpisodeResult
    events: list[EventRecord]
    trajectory: dict[str, Any]
    text_artifacts: dict[str, str] = field(default_factory=dict)


def _build_scripted_sequence(definition: PickPlaceTaskDefinition) -> list[ScriptedPickPlaceAction]:
    source_hover_pose = definition.source_hover_pose()
    target_hover_pose = definition.target_hover_pose()

    return [
        ScriptedPickPlaceAction(
            phase_name="move_to_pregrasp",
            target_gripper_pose=source_hover_pose,
        ),
        ScriptedPickPlaceAction(
            phase_name="descend_to_grasp",
            target_gripper_pose=definition.object_start_pose,
        ),
        ScriptedPickPlaceAction(
            phase_name="close_gripper_and_attach",
            target_gripper_pose=definition.object_start_pose,
            gripper_command="close",
            attach_object=True,
        ),
        ScriptedPickPlaceAction(
            phase_name="lift_object",
            target_gripper_pose=source_hover_pose,
        ),
        ScriptedPickPlaceAction(
            phase_name="transfer_to_target",
            target_gripper_pose=target_hover_pose,
        ),
        ScriptedPickPlaceAction(
            phase_name="descend_to_place",
            target_gripper_pose=definition.target_pose,
        ),
        ScriptedPickPlaceAction(
            phase_name="open_gripper_and_release",
            target_gripper_pose=definition.target_pose,
            gripper_command="open",
            release_object=True,
        ),
        ScriptedPickPlaceAction(
            phase_name="retreat_from_place",
            target_gripper_pose=target_hover_pose,
        ),
    ]


class BasePickPlaceEnvironment:
    """Shared scripted pick-and-place state machine for toy and Isaac backends."""

    def __init__(self, definition: PickPlaceTaskDefinition) -> None:
        self.definition = definition
        self.scripted_actions = _build_scripted_sequence(definition)
        self.step_count = 0
        self.sim_time_sec = 0.0
        self.current_phase = "reset"
        self.gripper_path: list[Pose3D] = []
        self.object_path: list[Pose3D] = []
        self.runtime_details: dict[str, object] = {}
        self.failure_reason: TerminationReason | None = None
        self.failure_message: str | None = None
        self.grasp_completed = False
        self._gripper_open = True
        self._object_attached = False

    @property
    def gripper_open(self) -> bool:
        return self._gripper_open

    @property
    def object_attached(self) -> bool:
        return self._object_attached

    def reset(self) -> PickPlaceObservation:
        self.step_count = 0
        self.sim_time_sec = 0.0
        self.current_phase = "reset"
        self.failure_reason = None
        self.failure_message = None
        self.grasp_completed = False
        self._gripper_open = True
        self._object_attached = False
        self._set_gripper_pose(self.definition.gripper_start_pose)
        self._set_object_pose(self.definition.object_start_pose)
        observation = self.observe()
        self.gripper_path = [observation.gripper_pose]
        self.object_path = [observation.object_pose]
        return observation

    def observe(self) -> PickPlaceObservation:
        gripper_pose = self._read_gripper_pose()
        object_pose = self._read_object_pose()
        return PickPlaceObservation(
            gripper_pose=gripper_pose,
            object_pose=object_pose,
            sim_time_sec=self.sim_time_sec,
            gripper_open=self._gripper_open,
            object_attached=self._object_attached,
            current_phase=self.current_phase,
            distance_to_object_m=distance_between_poses(gripper_pose, object_pose),
            distance_to_target_m=distance_between_poses(object_pose, self.definition.target_pose),
        )

    def termination_reason(self) -> TerminationReason | None:
        if self.step_count >= len(self.scripted_actions) and self._object_is_placed():
            return TerminationReason.SUCCESS
        if self.failure_reason is not None:
            return self.failure_reason
        if self.step_count >= self.definition.max_steps:
            return TerminationReason.MAX_STEPS
        if self.sim_time_sec >= self.definition.max_time_sec:
            return TerminationReason.TIMEOUT
        if self.step_count >= len(self.scripted_actions):
            return TerminationReason.TOOL_FAILURE
        return None

    def step_scripted(self) -> PickPlaceStepResult:
        if self.step_count >= len(self.scripted_actions):
            raise RuntimeError("scripted pick-and-place sequence is already complete")

        action = self.scripted_actions[self.step_count]
        observation_before = self.observe()

        self._set_gripper_pose(action.target_gripper_pose)
        gripper_pose = self._read_gripper_pose()

        if self._object_attached:
            self._set_object_pose(gripper_pose)

        if action.gripper_command == "close":
            self._gripper_open = False
            object_pose = self._read_object_pose()
            grasp_distance = distance_between_poses(gripper_pose, object_pose)
            if action.attach_object:
                if grasp_distance <= self.definition.grasp_tolerance_m:
                    self._object_attached = True
                    self.grasp_completed = True
                    self._set_object_pose(gripper_pose)
                else:
                    self.failure_reason = TerminationReason.TOOL_FAILURE
                    self.failure_message = (
                        f"grasp failed during phase '{action.phase_name}' because gripper-to-object distance "
                        f"{round(grasp_distance, 6)} exceeded tolerance {round(self.definition.grasp_tolerance_m, 6)}"
                    )
        elif action.gripper_command == "open":
            self._gripper_open = True
            if action.release_object:
                if not self._object_attached:
                    self.failure_reason = TerminationReason.TOOL_FAILURE
                    self.failure_message = (
                        f"place failed during phase '{action.phase_name}' because no object was attached to the gripper"
                    )
                else:
                    self._object_attached = False
                    release_pose = Pose3D(
                        x=gripper_pose.x,
                        y=gripper_pose.y,
                        z=self.definition.target_pose.z,
                        roll=self.definition.target_pose.roll,
                        pitch=self.definition.target_pose.pitch,
                        yaw=self.definition.target_pose.yaw,
                    )
                    self._set_object_pose(release_pose)
                    place_distance = distance_between_poses(self._read_object_pose(), self.definition.target_pose)
                    if place_distance > self.definition.place_tolerance_m:
                        self.failure_reason = TerminationReason.TOOL_FAILURE
                        self.failure_message = (
                            f"place failed during phase '{action.phase_name}' because object-to-target distance "
                            f"{round(place_distance, 6)} exceeded tolerance {round(self.definition.place_tolerance_m, 6)}"
                        )
        elif action.gripper_command != "hold":
            raise ValueError(f"unsupported gripper command: {action.gripper_command}")

        self.step_count += 1
        self.sim_time_sec = round(self.step_count * self.definition.control_dt_sec, 6)
        self.current_phase = action.phase_name
        observation_after = self.observe()
        self.gripper_path.append(observation_after.gripper_pose)
        self.object_path.append(observation_after.object_pose)

        return PickPlaceStepResult(
            action=action,
            observation=observation_after,
            gripper_moved_distance_m=distance_between_poses(
                observation_before.gripper_pose,
                observation_after.gripper_pose,
            ),
            object_moved_distance_m=distance_between_poses(
                observation_before.object_pose,
                observation_after.object_pose,
            ),
        )

    def _object_is_placed(self) -> bool:
        object_pose = self._read_object_pose()
        return (not self._object_attached) and (
            distance_between_poses(object_pose, self.definition.target_pose) <= self.definition.place_tolerance_m
        )

    def _set_gripper_pose(self, pose: Pose3D) -> None:
        raise NotImplementedError

    def _read_gripper_pose(self) -> Pose3D:
        raise NotImplementedError

    def _set_object_pose(self, pose: Pose3D) -> None:
        raise NotImplementedError

    def _read_object_pose(self) -> Pose3D:
        raise NotImplementedError

    def close(self) -> None:
        """Optional backend teardown hook."""


class MinimalPickPlaceEnvironment(BasePickPlaceEnvironment):
    """Deterministic in-memory pick-and-place environment for lightweight testing."""

    def __init__(self, definition: PickPlaceTaskDefinition) -> None:
        super().__init__(definition=definition)
        self._gripper_pose = definition.gripper_start_pose
        self._object_pose = definition.object_start_pose

    def _set_gripper_pose(self, pose: Pose3D) -> None:
        self._gripper_pose = pose

    def _read_gripper_pose(self) -> Pose3D:
        return self._gripper_pose

    def _set_object_pose(self, pose: Pose3D) -> None:
        self._object_pose = pose

    def _read_object_pose(self) -> Pose3D:
        return self._object_pose


def build_minimal_pickplace_task_config(
    task_id: str = "minimal_isaac_pick_place",
    scene_id: str | None = None,
    robot_id: str = "gripper_marker",
    seed: int = 0,
    max_steps: int = 12,
    max_time_sec: float = 12.0,
    gripper_start_pose: Pose3D | None = None,
    object_start_pose: Pose3D | None = None,
    target_pose: Pose3D | None = None,
    hover_offset_m: float = 0.12,
    grasp_tolerance_m: float = 0.01,
    place_tolerance_m: float = 0.02,
    control_dt_sec: float = 0.5,
    backend: str = "isaac",
) -> TaskConfig:
    """Build the default task config for the minimal pick-and-place baseline."""

    if backend not in {"toy", "isaac"}:
        raise ValueError(f"unsupported manipulation backend: {backend}")

    gripper_start_pose = gripper_start_pose or Pose3D(x=-0.2, y=-0.25, z=0.18)
    object_start_pose = object_start_pose or Pose3D(x=0.0, y=0.0, z=0.03)
    target_pose = target_pose or Pose3D(x=0.35, y=0.0, z=0.03)
    definition = PickPlaceTaskDefinition(
        gripper_start_pose=gripper_start_pose,
        object_start_pose=object_start_pose,
        target_pose=target_pose,
        hover_offset_m=hover_offset_m,
        grasp_tolerance_m=grasp_tolerance_m,
        place_tolerance_m=place_tolerance_m,
        control_dt_sec=control_dt_sec,
        max_steps=max_steps,
        max_time_sec=max_time_sec,
    )

    if scene_id is None:
        scene_id = "minimal_isaac_tabletop_stage" if backend == "isaac" else "minimal_tabletop_reference"

    description = (
        "Minimal Isaac-backed pick-and-place baseline: create a procedural headless USD stage with one gripper "
        "marker, one object cube, and fixed source/target zones, then execute a deterministic scripted pick, "
        "lift, transfer, place, and retreat sequence."
        if backend == "isaac"
        else "Minimal deterministic reference pick-and-place baseline: execute a fixed scripted sequence over one "
        "gripper pose and one movable object state with no planner, perception stack, or policy learning."
    )

    isaac_metadata: dict[str, Any] = {}
    if backend == "isaac":
        isaac_metadata = {
            "world_prim_path": "/World",
            "physics_scene_path": "/World/PhysicsScene",
            "gripper_prim_path": "/World/Gripper",
            "object_prim_path": "/World/Object",
            "source_zone_prim_path": "/World/SourceZone",
            "target_zone_prim_path": "/World/TargetZone",
            "gripper_radius_m": 0.03,
            "object_size_m": 0.04,
            "zone_size_m": 0.12,
            "zone_height_m": 0.02,
            "ticks_per_step": 2,
        }

    scripted_sequence = [action.phase_name for action in _build_scripted_sequence(definition)]
    tags = ["m3", "manipulation", "pick_place", "scripted", "deterministic", backend]

    return TaskConfig(
        task_type=TaskType.PICK_PLACE,
        task_id=task_id,
        scene_id=scene_id,
        robot_id=robot_id,
        seed=seed,
        max_steps=max_steps,
        max_time_sec=max_time_sec,
        headless=True,
        render=False,
        difficulty=DifficultyLevel.EASY,
        runtime_options=RuntimeOptions(
            planner_enabled=False,
            memory_enabled=False,
            tool_validation_enabled=True,
            recovery_enabled=False,
            collect_events=True,
        ),
        description=description,
        tags=tags,
        metadata={
            "manipulation_baseline": {
                "task_name": "minimal_isaac_pick_place" if backend == "isaac" else "minimal_reference_pick_place",
                "backend": backend,
                "reset_behavior": (
                    "set gripper pose and object pose to fixed start state, open the gripper, "
                    "clear the phase counter, and detach the object"
                ),
                "start_state": {
                    "gripper_pose": gripper_start_pose.to_dict(),
                    "object_pose": object_start_pose.to_dict(),
                    "gripper_open": True,
                    "object_attached": False,
                },
                "source_pose": object_start_pose.to_dict(),
                "success_condition": "object released within place_tolerance_m of pick_place.target_pose",
                "termination_conditions": ["success", "max_steps", "max_time_sec", "tool_failure"],
                "scripted_sequence": scripted_sequence,
                "controller": {
                    "type": SCRIPTED_PICKPLACE_TOOL.name,
                    "hover_offset_m": hover_offset_m,
                    "grasp_tolerance_m": grasp_tolerance_m,
                    "place_tolerance_m": place_tolerance_m,
                    "control_dt_sec": control_dt_sec,
                },
                "isaac": isaac_metadata,
                "artifacts": {
                    "trajectory": "artifacts/trajectory.json",
                    "stage": "artifacts/stage.usda" if backend == "isaac" else None,
                },
            }
        },
        pick_place=PickPlaceSpec(
            object_id="block_A",
            source_id="source_zone_A",
            target_id="target_zone_B",
            target_pose=target_pose.to_dict(),
        ),
    )


def _manipulation_metadata_from_config(config: TaskConfig) -> dict[str, Any]:
    metadata = config.metadata.get("manipulation_baseline")
    if not isinstance(metadata, dict):
        raise ValueError("metadata.manipulation_baseline is required for the deterministic manipulation baseline")
    return metadata


def _manipulation_definition_from_config(config: TaskConfig) -> PickPlaceTaskDefinition:
    if config.task_type != TaskType.PICK_PLACE or config.pick_place is None:
        raise ValueError("task config must be a pick_place task with a pick_place spec")
    if config.pick_place.target_pose is None:
        raise ValueError("pick_place.target_pose is required for the deterministic manipulation baseline")

    metadata = _manipulation_metadata_from_config(config)
    start_state = metadata.get("start_state")
    if not isinstance(start_state, dict):
        raise ValueError("metadata.manipulation_baseline.start_state must be a dictionary")
    controller = metadata.get("controller", {})
    if not isinstance(controller, dict):
        raise ValueError("metadata.manipulation_baseline.controller must be a dictionary")

    gripper_start_pose = start_state.get("gripper_pose")
    object_start_pose = start_state.get("object_pose")
    if not isinstance(gripper_start_pose, dict):
        raise ValueError("metadata.manipulation_baseline.start_state.gripper_pose must be a pose dictionary")
    if not isinstance(object_start_pose, dict):
        raise ValueError("metadata.manipulation_baseline.start_state.object_pose must be a pose dictionary")

    hover_offset_m = float(controller.get("hover_offset_m", 0.12))
    grasp_tolerance_m = float(controller.get("grasp_tolerance_m", 0.01))
    place_tolerance_m = float(controller.get("place_tolerance_m", 0.02))
    control_dt_sec = float(controller.get("control_dt_sec", 0.5))

    if hover_offset_m <= 0:
        raise ValueError("controller.hover_offset_m must be positive")
    if grasp_tolerance_m <= 0:
        raise ValueError("controller.grasp_tolerance_m must be positive")
    if place_tolerance_m <= 0:
        raise ValueError("controller.place_tolerance_m must be positive")
    if control_dt_sec <= 0:
        raise ValueError("controller.control_dt_sec must be positive")
    if config.max_steps < 0:
        raise ValueError("max_steps must be non-negative")
    if config.max_time_sec < 0:
        raise ValueError("max_time_sec must be non-negative")

    return PickPlaceTaskDefinition(
        gripper_start_pose=Pose3D.from_dict(gripper_start_pose),
        object_start_pose=Pose3D.from_dict(object_start_pose),
        target_pose=Pose3D.from_dict(config.pick_place.target_pose),
        hover_offset_m=hover_offset_m,
        grasp_tolerance_m=grasp_tolerance_m,
        place_tolerance_m=place_tolerance_m,
        control_dt_sec=control_dt_sec,
        max_steps=config.max_steps,
        max_time_sec=float(config.max_time_sec),
    )


def _manipulation_backend_from_config(config: TaskConfig) -> str:
    backend = str(_manipulation_metadata_from_config(config).get("backend", "isaac"))
    if backend not in {"toy", "isaac"}:
        raise ValueError(f"unsupported manipulation backend: {backend}")
    return backend


def _isaac_stage_settings_from_config(config: TaskConfig) -> dict[str, Any]:
    isaac_payload = _manipulation_metadata_from_config(config).get("isaac", {})
    if not isinstance(isaac_payload, dict):
        raise ValueError("metadata.manipulation_baseline.isaac must be a dictionary")

    settings = {
        "world_prim_path": str(isaac_payload.get("world_prim_path", "/World")),
        "physics_scene_path": str(isaac_payload.get("physics_scene_path", "/World/PhysicsScene")),
        "gripper_prim_path": str(isaac_payload.get("gripper_prim_path", "/World/Gripper")),
        "object_prim_path": str(isaac_payload.get("object_prim_path", "/World/Object")),
        "source_zone_prim_path": str(isaac_payload.get("source_zone_prim_path", "/World/SourceZone")),
        "target_zone_prim_path": str(isaac_payload.get("target_zone_prim_path", "/World/TargetZone")),
        "gripper_radius_m": float(isaac_payload.get("gripper_radius_m", 0.03)),
        "object_size_m": float(isaac_payload.get("object_size_m", 0.04)),
        "zone_size_m": float(isaac_payload.get("zone_size_m", 0.12)),
        "zone_height_m": float(isaac_payload.get("zone_height_m", 0.02)),
        "ticks_per_step": int(isaac_payload.get("ticks_per_step", 2)),
    }
    if settings["gripper_radius_m"] <= 0:
        raise ValueError("metadata.manipulation_baseline.isaac.gripper_radius_m must be positive")
    if settings["object_size_m"] <= 0:
        raise ValueError("metadata.manipulation_baseline.isaac.object_size_m must be positive")
    if settings["zone_size_m"] <= 0:
        raise ValueError("metadata.manipulation_baseline.isaac.zone_size_m must be positive")
    if settings["zone_height_m"] <= 0:
        raise ValueError("metadata.manipulation_baseline.isaac.zone_height_m must be positive")
    if settings["ticks_per_step"] <= 0:
        raise ValueError("metadata.manipulation_baseline.isaac.ticks_per_step must be positive")
    return settings


def _build_trajectory_entry(
    step_index: int,
    phase_name: str,
    observation: PickPlaceObservation,
    gripper_moved_distance_m: float = 0.0,
    object_moved_distance_m: float = 0.0,
) -> dict[str, Any]:
    return {
        "step_index": step_index,
        "phase_name": phase_name,
        "sim_time_sec": round(observation.sim_time_sec, 6),
        "gripper_open": observation.gripper_open,
        "object_attached": observation.object_attached,
        "distance_to_object_m": round(observation.distance_to_object_m, 6),
        "distance_to_target_m": round(observation.distance_to_target_m, 6),
        "gripper_moved_distance_m": round(gripper_moved_distance_m, 6),
        "object_moved_distance_m": round(object_moved_distance_m, 6),
        "gripper_pose": observation.gripper_pose.to_dict(),
        "object_pose": observation.object_pose.to_dict(),
    }


def _build_failure_run_data(
    config: TaskConfig,
    run_id: str,
    manifest: RunManifest,
    termination_reason: TerminationReason,
    message: str,
) -> PickPlaceRunData:
    metadata = _manipulation_metadata_from_config(config)
    scripted_sequence = metadata.get("scripted_sequence", [])
    phase_count = len(scripted_sequence) if isinstance(scripted_sequence, list) else 0
    events = [
        EventRecord(
            run_id=run_id,
            event_index=0,
            event_type=EventType.EPISODE_START,
            step_index=0,
            task_type=config.task_type,
            task_id=config.task_id,
            scene_id=config.scene_id,
            robot_id=config.robot_id,
            seed=config.seed,
            payload={"headless": config.headless, "render": config.render},
            notes=["Baseline run started."],
        ),
        EventRecord(
            run_id=run_id,
            event_index=1,
            event_type=EventType.VALIDATION_WARNING,
            step_index=0,
            task_type=config.task_type,
            task_id=config.task_id,
            scene_id=config.scene_id,
            robot_id=config.robot_id,
            seed=config.seed,
            success=False,
            payload={"error": message},
            notes=["Baseline run terminated before the first scripted phase."],
        ),
        EventRecord(
            run_id=run_id,
            event_index=2,
            event_type=EventType.EPISODE_END,
            step_index=0,
            task_type=config.task_type,
            task_id=config.task_id,
            scene_id=config.scene_id,
            robot_id=config.robot_id,
            seed=config.seed,
            success=False,
            payload={"termination_reason": termination_reason.value},
            notes=[message],
        ),
    ]
    result = EpisodeResult(
        run_id=run_id,
        task_type=config.task_type,
        task_id=config.task_id,
        scene_id=config.scene_id,
        robot_id=config.robot_id,
        seed=config.seed,
        success=False,
        termination_reason=termination_reason,
        step_count=0,
        elapsed_time_sec=0.0,
        sim_time_sec=0.0,
        invalid_action_count=0,
        collision_count=0,
        recovery_count=0,
        tool_call_count=0,
        planner_call_count=0,
        token_usage=TokenUsage(),
        planner_latency_sec=0.0,
        notes=[message],
        metrics={
            "manipulation.grasp_completed": False,
            "manipulation.object_placed": False,
            "manipulation.final_object_to_target_distance_m": None,
            "manipulation.gripper_path_length_m": 0.0,
            "manipulation.object_path_length_m": 0.0,
            "manipulation.backend": _manipulation_backend_from_config(config),
            "manipulation.stage_artifact_written": False,
            "manipulation.scripted_phase_count": phase_count,
        },
    )
    return PickPlaceRunData(
        config=config,
        manifest=manifest,
        result=result,
        events=events,
        trajectory={
            "run_id": run_id,
            "task_id": config.task_id,
            "scene_id": config.scene_id,
            "backend": _manipulation_backend_from_config(config),
            "status": "blocked",
            "error": message,
            "states": [],
        },
        text_artifacts={},
    )


def _notes_for_backend(backend: str) -> list[str]:
    if backend == "isaac":
        return [
            "Minimal Isaac-backed pick-and-place baseline using procedural stage primitives and a fixed scripted sequence.",
            "The baseline does not include a complex robot arm stack, perception pipeline, LLM planner, memory, or learned policy.",
        ]
    return [
        "Minimal reference pick-and-place baseline with fixed scripted phases and no planner or memory.",
        "The toy backend exists only to support lightweight validation of the M3 contract and event flow.",
    ]


def execute_pickplace_baseline(config: TaskConfig, run_id: str) -> PickPlaceRunData:
    """Execute the deterministic manipulation baseline using the configured backend."""

    definition = _manipulation_definition_from_config(config)
    backend = _manipulation_backend_from_config(config)
    stage_settings: dict[str, Any] | None = None
    environment: BasePickPlaceEnvironment | None = None

    if backend == "isaac":
        from .isaac_world import IsaacPickPlaceWorldConfig
        from .isaac_world import MinimalIsaacPickPlaceEnvironment

        stage_settings = _isaac_stage_settings_from_config(config)
        environment: BasePickPlaceEnvironment = MinimalIsaacPickPlaceEnvironment(
            definition=definition,
            world_config=IsaacPickPlaceWorldConfig(
                world_prim_path=stage_settings["world_prim_path"],
                gripper_prim_path=stage_settings["gripper_prim_path"],
                object_prim_path=stage_settings["object_prim_path"],
                source_zone_prim_path=stage_settings["source_zone_prim_path"],
                target_zone_prim_path=stage_settings["target_zone_prim_path"],
                physics_scene_path=stage_settings["physics_scene_path"],
                gripper_radius_m=stage_settings["gripper_radius_m"],
                object_size_m=stage_settings["object_size_m"],
                zone_size_m=stage_settings["zone_size_m"],
                zone_height_m=stage_settings["zone_height_m"],
                stage_updates_per_action=stage_settings["ticks_per_step"],
            ),
        )
    else:
        environment = MinimalPickPlaceEnvironment(definition)

    manifest = RunManifest(
        run_id=run_id,
        task_type=config.task_type,
        task_id=config.task_id,
        scene_id=config.scene_id,
        robot_id=config.robot_id,
        seed=config.seed,
    )
    event_index = 0
    events: list[EventRecord] = []

    def append_event(
        event_type: EventType,
        step_index: int,
        sim_time_sec: float = 0.0,
        action_ref: str | None = None,
        tool_name: str | None = None,
        success: bool | None = None,
        payload: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
        notes: list[str] | None = None,
    ) -> None:
        nonlocal event_index
        events.append(
            EventRecord(
                run_id=run_id,
                event_index=event_index,
                event_type=event_type,
                step_index=step_index,
                task_type=config.task_type,
                task_id=config.task_id,
                scene_id=config.scene_id,
                robot_id=config.robot_id,
                seed=config.seed,
                sim_time_sec=round(sim_time_sec, 6),
                action_ref=action_ref,
                tool_name=tool_name,
                success=success,
                payload=payload or {},
                metrics=metrics or {},
                notes=notes or [],
            )
        )
        event_index += 1

    start_time = time.perf_counter()
    try:
        observation = environment.reset()
        trajectory_entries = [_build_trajectory_entry(step_index=0, phase_name="reset", observation=observation)]
        start_payload: dict[str, Any] = {
            "backend": backend,
            "gripper_start_pose": definition.gripper_start_pose.to_dict(),
            "object_start_pose": definition.object_start_pose.to_dict(),
            "target_pose": definition.target_pose.to_dict(),
            "hover_offset_m": definition.hover_offset_m,
            "grasp_tolerance_m": definition.grasp_tolerance_m,
            "place_tolerance_m": definition.place_tolerance_m,
            "control_dt_sec": definition.control_dt_sec,
            "scripted_sequence": [action.phase_name for action in environment.scripted_actions],
        }
        if stage_settings is not None:
            start_payload["isaac"] = stage_settings
        if environment.runtime_details:
            start_payload["runtime"] = environment.runtime_details
        append_event(EventType.EPISODE_START, step_index=0, payload=start_payload, notes=["Reset completed."])

        termination_reason: TerminationReason | None = None
        while termination_reason is None:
            termination_reason = environment.termination_reason()
            if termination_reason is not None:
                break

            step_index = environment.step_count + 1
            next_action = environment.scripted_actions[environment.step_count]
            append_event(
                EventType.STEP_START,
                step_index=step_index,
                sim_time_sec=environment.sim_time_sec,
                payload={
                    "backend": backend,
                    "controller": SCRIPTED_PICKPLACE_TOOL.name,
                    "phase_name": next_action.phase_name,
                },
            )
            append_event(
                EventType.OBSERVATION,
                step_index=step_index,
                sim_time_sec=environment.sim_time_sec,
                payload=observation.to_dict(),
                metrics={
                    "manipulation.final_object_to_target_distance_m": round(observation.distance_to_target_m, 6),
                },
            )

            step_result = environment.step_scripted()
            append_event(
                EventType.TOOL_CALL,
                step_index=step_index,
                sim_time_sec=environment.sim_time_sec,
                tool_name=SCRIPTED_PICKPLACE_TOOL.name,
                success=environment.failure_reason is None,
                payload=step_result.action.to_dict(),
            )
            append_event(
                EventType.ACTION_APPLIED,
                step_index=step_index,
                sim_time_sec=environment.sim_time_sec,
                action_ref=SCRIPTED_PICKPLACE_TOOL.name,
                tool_name=SCRIPTED_PICKPLACE_TOOL.name,
                success=environment.failure_reason is None,
                payload={
                    "backend": backend,
                    "phase_name": step_result.action.phase_name,
                    "gripper_pose": step_result.observation.gripper_pose.to_dict(),
                    "object_pose": step_result.observation.object_pose.to_dict(),
                    "gripper_open": step_result.observation.gripper_open,
                    "object_attached": step_result.observation.object_attached,
                },
                metrics={
                    "manipulation.final_object_to_target_distance_m": round(
                        step_result.observation.distance_to_target_m,
                        6,
                    ),
                },
            )
            if environment.failure_message is not None and environment.failure_reason is not None:
                append_event(
                    EventType.VALIDATION_WARNING,
                    step_index=step_index,
                    sim_time_sec=environment.sim_time_sec,
                    success=False,
                    payload={
                        "termination_reason": environment.failure_reason.value,
                        "message": environment.failure_message,
                    },
                    notes=[environment.failure_message],
                )
            append_event(
                EventType.STEP_END,
                step_index=step_index,
                sim_time_sec=environment.sim_time_sec,
                success=environment.failure_reason is None,
                payload={
                    "phase_name": step_result.action.phase_name,
                    "gripper_moved_distance_m": round(step_result.gripper_moved_distance_m, 6),
                    "object_moved_distance_m": round(step_result.object_moved_distance_m, 6),
                },
                metrics={
                    "manipulation.final_object_to_target_distance_m": round(
                        step_result.observation.distance_to_target_m,
                        6,
                    ),
                },
            )
            trajectory_entries.append(
                _build_trajectory_entry(
                    step_index=environment.step_count,
                    phase_name=step_result.action.phase_name,
                    observation=step_result.observation,
                    gripper_moved_distance_m=step_result.gripper_moved_distance_m,
                    object_moved_distance_m=step_result.object_moved_distance_m,
                )
            )
            observation = step_result.observation

        elapsed_time_sec = round(time.perf_counter() - start_time, 6)
        final_observation = environment.observe()
        success = termination_reason == TerminationReason.SUCCESS
        notes = _notes_for_backend(backend)
        if environment.failure_message is not None:
            notes.append(environment.failure_message)

        result = EpisodeResult(
            run_id=run_id,
            task_type=config.task_type,
            task_id=config.task_id,
            scene_id=config.scene_id,
            robot_id=config.robot_id,
            seed=config.seed,
            success=success,
            termination_reason=termination_reason or TerminationReason.UNKNOWN,
            step_count=environment.step_count,
            elapsed_time_sec=elapsed_time_sec,
            sim_time_sec=final_observation.sim_time_sec,
            invalid_action_count=1 if termination_reason == TerminationReason.TOOL_FAILURE else 0,
            collision_count=0,
            recovery_count=0,
            tool_call_count=environment.step_count,
            planner_call_count=0,
            token_usage=TokenUsage(),
            planner_latency_sec=0.0,
            notes=notes,
            metrics={
                "manipulation.grasp_completed": environment.grasp_completed,
                "manipulation.object_placed": success,
                "manipulation.final_object_to_target_distance_m": round(final_observation.distance_to_target_m, 6),
                "manipulation.gripper_path_length_m": round(compute_pose_path_length(environment.gripper_path), 6),
                "manipulation.object_path_length_m": round(compute_pose_path_length(environment.object_path), 6),
                "manipulation.backend": backend,
                "manipulation.stage_artifact_written": hasattr(environment, "stage_artifact_text"),
                "manipulation.scripted_phase_count": len(environment.scripted_actions),
            },
        )
        append_event(
            EventType.EPISODE_END,
            step_index=result.step_count,
            sim_time_sec=result.sim_time_sec,
            success=result.success,
            payload={"backend": backend, "termination_reason": result.termination_reason.value},
            metrics={
                "manipulation.final_object_to_target_distance_m": result.metrics[
                    "manipulation.final_object_to_target_distance_m"
                ],
                "manipulation.object_path_length_m": result.metrics["manipulation.object_path_length_m"],
            },
        )

        trajectory = {
            "run_id": run_id,
            "task_id": config.task_id,
            "scene_id": config.scene_id,
            "backend": backend,
            "tool_name": SCRIPTED_PICKPLACE_TOOL.name,
            "scripted_sequence": [action.phase_name for action in environment.scripted_actions],
            "artifacts": {
                "trajectory": "trajectory.json",
                "stage": "stage.usda" if hasattr(environment, "stage_artifact_text") else None,
            },
            "states": trajectory_entries,
        }
        if stage_settings is not None:
            trajectory["isaac"] = stage_settings
        if environment.runtime_details:
            trajectory["runtime"] = environment.runtime_details

        text_artifacts: dict[str, str] = {}
        if hasattr(environment, "stage_artifact_text"):
            text_artifacts["stage.usda"] = environment.stage_artifact_text()

        return PickPlaceRunData(
            config=config,
            manifest=manifest,
            result=result,
            events=events,
            trajectory=trajectory,
            text_artifacts=text_artifacts,
        )
    finally:
        if environment is not None:
            environment.close()


def _write_trajectory(path: Path, trajectory: dict[str, Any]) -> None:
    path.write_text(json.dumps(trajectory, indent=2) + "\n", encoding="utf-8")


def run_and_write_pickplace_baseline(
    config: TaskConfig,
    run_id: str,
    results_root: str | Path = "results",
) -> tuple[PickPlaceRunData, RunArtifactsLayout]:
    """Execute the baseline and write canonical run artifacts to disk."""

    manifest = RunManifest(
        run_id=run_id,
        task_type=config.task_type,
        task_id=config.task_id,
        scene_id=config.scene_id,
        robot_id=config.robot_id,
        seed=config.seed,
    )
    layout = RunArtifactsLayout(run_id=run_id, results_root=results_root)
    if layout.run_dir.exists() and any(layout.run_dir.iterdir()):
        raise FileExistsError(f"run directory already exists and is not empty: {layout.run_dir}")

    layout.ensure()
    write_run_manifest(layout.manifest_path, manifest)
    write_task_config(layout.task_config_path, config)

    try:
        run_data = execute_pickplace_baseline(config=config, run_id=run_id)
    except ManipulationBackendUnavailableError as exc:
        run_data = _build_failure_run_data(
            config=config,
            run_id=run_id,
            manifest=manifest,
            termination_reason=TerminationReason.TASK_PRECONDITION_FAILED,
            message=f"{type(exc).__name__}: {exc}",
        )
    except ValueError as exc:
        run_data = _build_failure_run_data(
            config=config,
            run_id=run_id,
            manifest=manifest,
            termination_reason=TerminationReason.TASK_PRECONDITION_FAILED,
            message=f"{type(exc).__name__}: {exc}",
        )
    except Exception as exc:
        run_data = _build_failure_run_data(
            config=config,
            run_id=run_id,
            manifest=manifest,
            termination_reason=TerminationReason.RUNTIME_ERROR,
            message=f"{type(exc).__name__}: {exc}",
        )

    write_episode_result(layout.episode_result_path, run_data.result)
    write_event_log(layout.event_log_path, run_data.events)
    _write_trajectory(layout.artifacts_dir / "trajectory.json", run_data.trajectory)
    for artifact_name, payload in run_data.text_artifacts.items():
        (layout.artifacts_dir / artifact_name).write_text(payload, encoding="utf-8")
    return run_data, layout
