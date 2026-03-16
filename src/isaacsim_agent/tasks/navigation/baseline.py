"""Minimal deterministic navigation baseline with contract-compliant outputs."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from isaacsim_agent.contracts import DifficultyLevel
from isaacsim_agent.contracts import EpisodeResult
from isaacsim_agent.contracts import EventRecord
from isaacsim_agent.contracts import EventType
from isaacsim_agent.contracts import NavigationSpec
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
from isaacsim_agent.tools.navigation import SCRIPTED_NAVIGATE_TOOL
from isaacsim_agent.tools.navigation import DirectNavigationAction
from isaacsim_agent.tools.navigation import Pose2D
from isaacsim_agent.tools.navigation import compute_direct_navigation_step
from isaacsim_agent.tools.navigation import compute_path_length
from isaacsim_agent.tools.navigation import distance_between_poses


@dataclass(frozen=True)
class NavigationTaskDefinition:
    """Resolved task definition for the minimal deterministic navigation baseline."""

    start_pose: Pose2D
    goal_pose: Pose2D
    success_radius_m: float
    step_size_m: float
    control_dt_sec: float
    max_steps: int
    max_time_sec: float
    max_stuck_steps: int
    stuck_distance_epsilon_m: float


@dataclass(frozen=True)
class NavigationObservation:
    """Current robot pose and distance-to-goal observation."""

    pose: Pose2D
    distance_to_goal_m: float
    sim_time_sec: float

    def to_dict(self) -> dict[str, float | dict[str, float]]:
        return {
            "pose": self.pose.to_dict(),
            "distance_to_goal_m": round(self.distance_to_goal_m, 6),
            "sim_time_sec": round(self.sim_time_sec, 6),
        }


@dataclass(frozen=True)
class NavigationStepResult:
    """Outcome of one scripted navigation step."""

    action: DirectNavigationAction
    observation: NavigationObservation
    moved_distance_m: float
    progress_m: float
    stuck_steps: int


@dataclass(frozen=True)
class NavigationRunData:
    """In-memory representation of one baseline run and its artifacts."""

    config: TaskConfig
    manifest: RunManifest
    result: EpisodeResult
    events: list[EventRecord]
    trajectory: dict[str, Any]


class MinimalNavigationEnvironment:
    """Deterministic planar navigation task with reset and termination rules."""

    def __init__(self, definition: NavigationTaskDefinition) -> None:
        self.definition = definition
        self.current_pose = definition.start_pose
        self.path: list[Pose2D] = []
        self.step_count = 0
        self.sim_time_sec = 0.0
        self.stuck_steps = 0

    def reset(self) -> NavigationObservation:
        self.current_pose = self.definition.start_pose
        self.path = [self.current_pose]
        self.step_count = 0
        self.sim_time_sec = 0.0
        self.stuck_steps = 0
        return self.observe()

    def observe(self) -> NavigationObservation:
        return NavigationObservation(
            pose=self.current_pose,
            distance_to_goal_m=distance_between_poses(self.current_pose, self.definition.goal_pose),
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
            current_pose=self.current_pose,
            goal_pose=self.definition.goal_pose,
            step_size_m=self.definition.step_size_m,
        )

        self.current_pose = action.target_pose
        self.path.append(self.current_pose)
        self.step_count += 1
        self.sim_time_sec = round(self.step_count * self.definition.control_dt_sec, 6)

        observation_after = self.observe()
        progress_m = observation_before.distance_to_goal_m - observation_after.distance_to_goal_m
        if progress_m <= self.definition.stuck_distance_epsilon_m:
            self.stuck_steps += 1
        else:
            self.stuck_steps = 0

        return NavigationStepResult(
            action=action,
            observation=observation_after,
            moved_distance_m=action.step_distance_m,
            progress_m=progress_m,
            stuck_steps=self.stuck_steps,
        )


def build_minimal_navigation_task_config(
    task_id: str = "minimal_deterministic_navigation",
    scene_id: str = "minimal_empty_stage",
    robot_id: str = "point_robot",
    seed: int = 0,
    max_steps: int = 10,
    max_time_sec: float = 10.0,
    start_pose: Pose2D | None = None,
    goal_pose: Pose2D | None = None,
    success_radius_m: float = 0.2,
    step_size_m: float = 0.5,
    control_dt_sec: float = 0.5,
    max_stuck_steps: int = 3,
    stuck_distance_epsilon_m: float = 1e-6,
) -> TaskConfig:
    """Build the default task config used for the M2 navigation baseline."""

    start_pose = start_pose or Pose2D(x=0.0, y=0.0, yaw=0.0)
    goal_pose = goal_pose or Pose2D(x=2.0, y=0.0, yaw=0.0)

    return TaskConfig(
        task_type=TaskType.NAVIGATION,
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
        description=(
            "Minimal deterministic navigation baseline: reset a point robot to a fixed start pose and move "
            "it in a straight line toward one fixed goal pose until success or a termination limit is hit."
        ),
        tags=["m2", "navigation", "scripted", "deterministic"],
        metadata={
            "navigation_baseline": {
                "task_name": "minimal_point_navigation",
                "reset_behavior": "set robot pose to start_pose and clear step, time, and stuck counters",
                "start_pose": start_pose.to_dict(),
                "success_condition": "distance_to_goal_m <= success_radius_m",
                "termination_conditions": [
                    "success",
                    "max_steps",
                    "max_time_sec",
                    "robot_stuck",
                ],
                "controller": {
                    "type": SCRIPTED_NAVIGATE_TOOL.name,
                    "step_size_m": step_size_m,
                    "control_dt_sec": control_dt_sec,
                    "max_stuck_steps": max_stuck_steps,
                    "stuck_distance_epsilon_m": stuck_distance_epsilon_m,
                },
            }
        },
        navigation=NavigationSpec(
            goal_ref="goal_marker_A",
            waypoint_refs=[],
            success_radius_m=success_radius_m,
            goal_pose=goal_pose.to_dict(),
        ),
    )


def _navigation_definition_from_config(config: TaskConfig) -> NavigationTaskDefinition:
    if config.task_type != TaskType.NAVIGATION or config.navigation is None:
        raise ValueError("task config must be a navigation task with a navigation spec")
    if config.navigation.goal_pose is None:
        raise ValueError("navigation.goal_pose is required for the deterministic navigation baseline")

    metadata = config.metadata.get("navigation_baseline")
    if not isinstance(metadata, dict):
        raise ValueError("metadata.navigation_baseline is required for the deterministic navigation baseline")

    start_pose_payload = metadata.get("start_pose")
    if not isinstance(start_pose_payload, dict):
        raise ValueError("metadata.navigation_baseline.start_pose must be a pose dictionary")

    controller = metadata.get("controller", {})
    if not isinstance(controller, dict):
        raise ValueError("metadata.navigation_baseline.controller must be a dictionary")

    success_radius_m = float(config.navigation.success_radius_m)
    step_size_m = float(controller.get("step_size_m", 0.5))
    control_dt_sec = float(controller.get("control_dt_sec", 0.5))
    max_stuck_steps = int(controller.get("max_stuck_steps", 3))
    stuck_distance_epsilon_m = float(controller.get("stuck_distance_epsilon_m", 1e-6))

    if success_radius_m <= 0:
        raise ValueError("navigation.success_radius_m must be positive")
    if step_size_m <= 0:
        raise ValueError("controller.step_size_m must be positive")
    if control_dt_sec <= 0:
        raise ValueError("controller.control_dt_sec must be positive")
    if config.max_steps < 0:
        raise ValueError("max_steps must be non-negative")
    if config.max_time_sec < 0:
        raise ValueError("max_time_sec must be non-negative")
    if max_stuck_steps <= 0:
        raise ValueError("controller.max_stuck_steps must be positive")

    return NavigationTaskDefinition(
        start_pose=Pose2D.from_dict(start_pose_payload),
        goal_pose=Pose2D.from_dict(config.navigation.goal_pose),
        success_radius_m=success_radius_m,
        step_size_m=step_size_m,
        control_dt_sec=control_dt_sec,
        max_steps=config.max_steps,
        max_time_sec=float(config.max_time_sec),
        max_stuck_steps=max_stuck_steps,
        stuck_distance_epsilon_m=stuck_distance_epsilon_m,
    )


def _build_trajectory_entry(
    step_index: int,
    observation: NavigationObservation,
    moved_distance_m: float = 0.0,
) -> dict[str, float]:
    return {
        "step_index": step_index,
        "sim_time_sec": round(observation.sim_time_sec, 6),
        "distance_to_goal_m": round(observation.distance_to_goal_m, 6),
        "moved_distance_m": round(moved_distance_m, 6),
        **observation.pose.to_dict(),
    }


def _build_failure_run_data(
    config: TaskConfig,
    run_id: str,
    manifest: RunManifest,
    termination_reason: TerminationReason,
    message: str,
) -> NavigationRunData:
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
            notes=["Baseline run terminated before the first control step."],
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
            "navigation.goal_reached": False,
            "navigation.final_goal_distance_m": None,
            "navigation.path_length_m": 0.0,
            "navigation.waypoints_completed": 0,
        },
    )

    trajectory = {
        "run_id": run_id,
        "task_id": config.task_id,
        "scene_id": config.scene_id,
        "status": "blocked",
        "error": message,
        "poses": [],
    }
    return NavigationRunData(
        config=config,
        manifest=manifest,
        result=result,
        events=events,
        trajectory=trajectory,
    )


def execute_navigation_baseline(config: TaskConfig, run_id: str) -> NavigationRunData:
    """Execute the deterministic navigation baseline in memory."""

    definition = _navigation_definition_from_config(config)
    environment = MinimalNavigationEnvironment(definition)
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
    observation = environment.reset()
    trajectory_entries = [_build_trajectory_entry(step_index=0, observation=observation)]

    append_event(
        EventType.EPISODE_START,
        step_index=0,
        payload={
            "start_pose": definition.start_pose.to_dict(),
            "goal_pose": definition.goal_pose.to_dict(),
            "success_radius_m": definition.success_radius_m,
            "step_size_m": definition.step_size_m,
            "control_dt_sec": definition.control_dt_sec,
        },
        notes=["Reset completed."],
    )

    termination_reason: TerminationReason | None = None
    while termination_reason is None:
        termination_reason = environment.termination_reason()
        if termination_reason is not None:
            break

        step_index = environment.step_count + 1
        append_event(
            EventType.STEP_START,
            step_index=step_index,
            sim_time_sec=environment.sim_time_sec,
            payload={"controller": SCRIPTED_NAVIGATE_TOOL.name},
        )
        append_event(
            EventType.OBSERVATION,
            step_index=step_index,
            sim_time_sec=environment.sim_time_sec,
            payload=observation.to_dict(),
            metrics={"navigation.final_goal_distance_m": round(observation.distance_to_goal_m, 6)},
        )

        step_result = environment.step_toward_goal()
        append_event(
            EventType.TOOL_CALL,
            step_index=step_index,
            sim_time_sec=environment.sim_time_sec,
            tool_name=SCRIPTED_NAVIGATE_TOOL.name,
            success=True,
            payload=step_result.action.to_dict(),
        )
        append_event(
            EventType.ACTION_APPLIED,
            step_index=step_index,
            sim_time_sec=environment.sim_time_sec,
            action_ref=SCRIPTED_NAVIGATE_TOOL.name,
            tool_name=SCRIPTED_NAVIGATE_TOOL.name,
            success=True,
            payload={"pose": step_result.observation.pose.to_dict()},
            metrics={
                "navigation.final_goal_distance_m": round(step_result.observation.distance_to_goal_m, 6),
                "navigation.progress_m": round(step_result.progress_m, 6),
            },
        )
        append_event(
            EventType.STEP_END,
            step_index=step_index,
            sim_time_sec=environment.sim_time_sec,
            success=True,
            payload={
                "stuck_steps": step_result.stuck_steps,
                "moved_distance_m": round(step_result.moved_distance_m, 6),
            },
            metrics={
                "navigation.final_goal_distance_m": round(step_result.observation.distance_to_goal_m, 6),
            },
        )

        trajectory_entries.append(
            _build_trajectory_entry(
                step_index=environment.step_count,
                observation=step_result.observation,
                moved_distance_m=step_result.moved_distance_m,
            )
        )
        observation = step_result.observation

    elapsed_time_sec = round(time.perf_counter() - start_time, 6)
    final_observation = environment.observe()
    success = termination_reason == TerminationReason.SUCCESS
    path_length_m = compute_path_length(environment.path)

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
        invalid_action_count=0,
        collision_count=0,
        recovery_count=0,
        tool_call_count=environment.step_count,
        planner_call_count=0,
        token_usage=TokenUsage(),
        planner_latency_sec=0.0,
        notes=[
            "Minimal deterministic point-navigation baseline with no planner or memory.",
            "Reset pose, success condition, and termination conditions are encoded in task metadata.",
        ],
        metrics={
            "navigation.goal_reached": success,
            "navigation.final_goal_distance_m": round(final_observation.distance_to_goal_m, 6),
            "navigation.path_length_m": round(path_length_m, 6),
            "navigation.waypoints_completed": len(config.navigation.waypoint_refs),
        },
    )

    append_event(
        EventType.EPISODE_END,
        step_index=result.step_count,
        sim_time_sec=result.sim_time_sec,
        success=result.success,
        payload={"termination_reason": result.termination_reason.value},
        metrics={
            "navigation.final_goal_distance_m": result.metrics["navigation.final_goal_distance_m"],
            "navigation.path_length_m": result.metrics["navigation.path_length_m"],
        },
    )

    trajectory = {
        "run_id": run_id,
        "task_id": config.task_id,
        "scene_id": config.scene_id,
        "tool_name": SCRIPTED_NAVIGATE_TOOL.name,
        "success_radius_m": definition.success_radius_m,
        "poses": trajectory_entries,
    }
    return NavigationRunData(
        config=config,
        manifest=manifest,
        result=result,
        events=events,
        trajectory=trajectory,
    )


def _write_trajectory(path: Path, trajectory: dict[str, Any]) -> None:
    path.write_text(json.dumps(trajectory, indent=2) + "\n", encoding="utf-8")


def run_and_write_navigation_baseline(
    config: TaskConfig,
    run_id: str,
    results_root: str | Path = "results",
) -> tuple[NavigationRunData, RunArtifactsLayout]:
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
        run_data = execute_navigation_baseline(config=config, run_id=run_id)
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
    return run_data, layout
