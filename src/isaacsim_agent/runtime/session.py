"""Minimal M4 agent runtime with structured planner tool calls."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from isaacsim_agent.contracts import EpisodeResult
from isaacsim_agent.contracts import EventRecord
from isaacsim_agent.contracts import EventType
from isaacsim_agent.contracts import RunArtifactsLayout
from isaacsim_agent.contracts import RunManifest
from isaacsim_agent.contracts import TaskConfig
from isaacsim_agent.contracts import TaskType
from isaacsim_agent.contracts import TerminationReason
from isaacsim_agent.contracts import TokenUsage
from isaacsim_agent.contracts import write_episode_result
from isaacsim_agent.contracts import write_event_log
from isaacsim_agent.contracts import write_run_manifest
from isaacsim_agent.contracts import write_task_config
from isaacsim_agent.planner import MockPlannerBackend
from isaacsim_agent.planner import PlannerAction
from isaacsim_agent.planner import PlannerBackend
from isaacsim_agent.planner import PlannerConfig
from isaacsim_agent.planner import PlannerRawResponse
from isaacsim_agent.planner import PlannerRequest
from isaacsim_agent.planner import PlannerResponseError
from isaacsim_agent.planner import parse_planner_action
from isaacsim_agent.tasks.navigation import build_minimal_navigation_task_config
from isaacsim_agent.tasks.navigation.baseline import MinimalNavigationEnvironment
from isaacsim_agent.tasks.navigation.baseline import NavigationBackendUnavailableError
from isaacsim_agent.tasks.navigation.baseline import NavigationObservation
from isaacsim_agent.tasks.navigation.baseline import _isaac_stage_settings_from_config
from isaacsim_agent.tasks.navigation.baseline import _navigation_backend_from_config
from isaacsim_agent.tasks.navigation.baseline import _navigation_definition_from_config
from isaacsim_agent.tools import SCRIPTED_NAVIGATE_TOOL
from isaacsim_agent.tools import Pose2D
from isaacsim_agent.tools import compute_path_length
from isaacsim_agent.tools import distance_between_poses
from isaacsim_agent.tools.registry import ToolRegistry
from isaacsim_agent.tools.registry import ToolSpec
from isaacsim_agent.tools.registry import build_navigation_tool_registry


@dataclass(frozen=True)
class RuntimeSession:
    """Session metadata for one M4 agent runtime episode."""

    session_id: str
    policy_name: str = "agent_runtime_v0"
    planner_backend: str = "mock_rule_based"


@dataclass(frozen=True)
class AgentRuntimeConfig:
    """Minimal runtime policy knobs for M4."""

    planner_config: PlannerConfig = field(default_factory=PlannerConfig)
    max_invalid_actions: int = 1


@dataclass(frozen=True)
class AgentRunData:
    """In-memory result bundle before canonical artifact writing."""

    config: TaskConfig
    manifest: RunManifest
    result: EpisodeResult
    events: list[EventRecord]
    trajectory: dict[str, Any]
    planner_trace: list[dict[str, Any]]
    tool_trace: list[dict[str, Any]]
    text_artifacts: dict[str, str] = field(default_factory=dict)


def build_minimal_agent_navigation_task_config(
    backend: str = "toy",
    planner_backend: str = "mock_rule_based",
    **kwargs: Any,
) -> TaskConfig:
    """Build the default M4 task config while preserving the M1.5 schema."""

    config = build_minimal_navigation_task_config(backend=backend, **kwargs)
    config.runtime_options.planner_enabled = True
    config.runtime_options.memory_enabled = False
    config.runtime_options.recovery_enabled = False
    config.runtime_options.collect_events = True
    config.runtime_options.extra_options["planner_backend"] = planner_backend
    config.runtime_options.extra_options["runtime_policy"] = "agent_runtime_v0"

    metadata = dict(config.metadata)
    metadata["agent_runtime_v0"] = {
        "planner_backend": planner_backend,
        "supported_task_types": [TaskType.NAVIGATION.value],
        "available_tools": build_navigation_tool_registry().names_for_task(TaskType.NAVIGATION),
        "structured_action_schema": {
            "tool_name": "string",
            "arguments": "object",
        },
    }
    config.metadata = metadata
    return config


def build_agent_v0_navigation_task_config(
    backend: str = "toy",
    planner_backend: str = "mock_rule_based",
    **kwargs: Any,
) -> TaskConfig:
    """Backward-compatible public name for the M4 navigation task builder."""

    return build_minimal_agent_navigation_task_config(
        backend=backend,
        planner_backend=planner_backend,
        **kwargs,
    )


def _clone_task_config(config: TaskConfig) -> TaskConfig:
    return TaskConfig.from_dict(config.to_dict())


def _tool_spec_to_payload(tool_spec: ToolSpec) -> dict[str, object]:
    return {
        "name": tool_spec.name,
        "description": tool_spec.description,
        "required_arguments": list(tool_spec.required_arguments),
    }


def _build_trajectory_entry(
    step_index: int,
    observation: NavigationObservation,
    tool_name: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "step_index": step_index,
        "sim_time_sec": round(observation.sim_time_sec, 6),
        "distance_to_goal_m": round(observation.distance_to_goal_m, 6),
        "pose": observation.pose.to_dict(),
    }
    if tool_name is not None:
        payload["tool_name"] = tool_name
    return payload


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _add_token_usage(total: TokenUsage, increment: TokenUsage) -> TokenUsage:
    return TokenUsage(
        prompt_tokens=total.prompt_tokens + increment.prompt_tokens,
        completion_tokens=total.completion_tokens + increment.completion_tokens,
        total_tokens=(total.prompt_tokens + increment.prompt_tokens)
        + (total.completion_tokens + increment.completion_tokens),
        estimated_cost_usd=None,
    )


def _navigation_instruction(config: TaskConfig) -> str:
    if config.navigation is None or config.navigation.goal_pose is None:
        return "Navigate the robot to the configured goal pose."
    goal_pose = Pose2D.from_dict(config.navigation.goal_pose)
    return (
        "Navigate the robot to the configured goal pose "
        f"({goal_pose.x:.2f}, {goal_pose.y:.2f}, yaw={goal_pose.yaw:.2f})."
    )


class AgentRuntime:
    """Small runtime loop for one structured planner-driven navigation episode."""

    def __init__(
        self,
        planner_backend: PlannerBackend | None = None,
        runtime_config: AgentRuntimeConfig | None = None,
        tool_registry: ToolRegistry | None = None,
    ) -> None:
        self.planner_backend = planner_backend or MockPlannerBackend()
        self.runtime_config = runtime_config or AgentRuntimeConfig(
            planner_config=PlannerConfig(backend=self.planner_backend.backend_name)
        )
        self.tool_registry = tool_registry or build_navigation_tool_registry()

    def execute(self, config: TaskConfig, run_id: str) -> AgentRunData:
        """Execute one M4 agent runtime episode."""

        prepared_config = _clone_task_config(config)
        if prepared_config.task_type != TaskType.NAVIGATION:
            raise ValueError(
                "agent runtime v0 currently supports only navigation tasks to keep M4 scope minimal"
            )
        prepared_config.runtime_options.planner_enabled = True
        prepared_config.runtime_options.memory_enabled = False
        prepared_config.runtime_options.recovery_enabled = False
        prepared_config.runtime_options.collect_events = True

        backend = _navigation_backend_from_config(prepared_config)
        stage_settings: dict[str, Any] | None = None
        if backend == "isaac":
            from isaacsim_agent.tasks.navigation.isaac_world import IsaacNavigationWorldConfig
            from isaacsim_agent.tasks.navigation.isaac_world import MinimalIsaacNavigationEnvironment

            stage_settings = _isaac_stage_settings_from_config(prepared_config)
            environment: Any = MinimalIsaacNavigationEnvironment(
                definition=_navigation_definition_from_config(prepared_config),
                world_config=IsaacNavigationWorldConfig(
                    agent_prim_path=stage_settings["agent_prim_path"],
                    goal_prim_path=stage_settings["goal_prim_path"],
                    physics_scene_path=stage_settings["physics_scene_path"],
                    robot_radius_m=stage_settings["agent_radius_m"],
                    goal_marker_size_m=stage_settings["goal_marker_size_m"],
                    stage_updates_per_action=stage_settings["ticks_per_step"],
                ),
            )
        else:
            environment = MinimalNavigationEnvironment(_navigation_definition_from_config(prepared_config))

        manifest = RunManifest(
            run_id=run_id,
            task_type=prepared_config.task_type,
            task_id=prepared_config.task_id,
            scene_id=prepared_config.scene_id,
            robot_id=prepared_config.robot_id,
            seed=prepared_config.seed,
        )
        session = RuntimeSession(
            session_id=run_id,
            planner_backend=self.planner_backend.backend_name,
        )

        event_index = 0
        events: list[EventRecord] = []

        def append_event(
            event_type: EventType,
            step_index: int,
            sim_time_sec: float = 0.0,
            action_ref: str | None = None,
            tool_name: str | None = None,
            planner_latency_sec: float | None = None,
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
                    task_type=prepared_config.task_type,
                    task_id=prepared_config.task_id,
                    scene_id=prepared_config.scene_id,
                    robot_id=prepared_config.robot_id,
                    seed=prepared_config.seed,
                    sim_time_sec=round(sim_time_sec, 6),
                    action_ref=action_ref,
                    tool_name=tool_name,
                    planner_latency_sec=planner_latency_sec,
                    success=success,
                    payload=payload or {},
                    metrics=metrics or {},
                    notes=notes or [],
                )
            )
            event_index += 1

        start_time = time.perf_counter()
        planner_trace: list[dict[str, Any]] = []
        tool_trace: list[dict[str, Any]] = []
        try:
            observation = environment.reset()
            trajectory_entries = [_build_trajectory_entry(step_index=0, observation=observation)]
            available_tools = [
                _tool_spec_to_payload(tool_spec)
                for tool_spec in self.tool_registry.specs_for_task(prepared_config.task_type)
            ]
            start_payload: dict[str, Any] = {
                "runtime_session": {
                    "session_id": session.session_id,
                    "policy_name": session.policy_name,
                    "planner_backend": session.planner_backend,
                },
                "available_tools": available_tools,
                "instruction": _navigation_instruction(prepared_config),
                "backend": backend,
                "start_pose": observation.pose.to_dict(),
                "goal_pose": prepared_config.navigation.goal_pose,
                "success_radius_m": prepared_config.navigation.success_radius_m,
            }
            if stage_settings is not None:
                start_payload["isaac"] = stage_settings
            if getattr(environment, "runtime_details", None):
                start_payload["runtime"] = environment.runtime_details
            append_event(
                EventType.EPISODE_START,
                step_index=0,
                payload=start_payload,
                notes=["Reset completed."],
            )

            planner_call_count = 0
            tool_call_count = 0
            invalid_action_count = 0
            runtime_step_count = 0
            planner_latency_sec = 0.0
            token_usage = TokenUsage()
            last_tool_result: dict[str, Any] | None = None
            tool_history: list[str] = []
            notes = [
                "Minimal M4 runtime v0 using structured JSON planner actions.",
                "No memory manager, retry policy, or complex recovery policy is enabled.",
            ]
            termination_reason: TerminationReason | None = None

            while termination_reason is None:
                if runtime_step_count >= prepared_config.max_steps:
                    termination_reason = TerminationReason.MAX_STEPS
                    notes.append(
                        f"runtime reached max_steps={prepared_config.max_steps} before task completion"
                    )
                    break

                environment_termination = environment.termination_reason()
                if environment_termination is not None:
                    termination_reason = environment_termination
                    break

                step_index = runtime_step_count + 1
                append_event(
                    EventType.STEP_START,
                    step_index=step_index,
                    sim_time_sec=observation.sim_time_sec,
                    payload={
                        "backend": backend,
                        "planner_backend": self.planner_backend.backend_name,
                    },
                )
                append_event(
                    EventType.OBSERVATION,
                    step_index=step_index,
                    sim_time_sec=observation.sim_time_sec,
                    payload=observation.to_dict(),
                    metrics={
                        "navigation.final_goal_distance_m": round(observation.distance_to_goal_m, 6),
                    },
                )

                planner_request = PlannerRequest(
                    task_type=prepared_config.task_type,
                    instruction=_navigation_instruction(prepared_config),
                    step_index=step_index,
                    available_tools=available_tools,
                    state={
                        "robot_pose": observation.pose.to_dict(),
                        "goal_pose": prepared_config.navigation.goal_pose,
                        "distance_to_goal_m": round(observation.distance_to_goal_m, 6),
                        "success_radius_m": round(prepared_config.navigation.success_radius_m, 6),
                        "sim_time_sec": round(observation.sim_time_sec, 6),
                    },
                    last_tool_result=last_tool_result,
                    tool_history=list(tool_history),
                )
                append_event(
                    EventType.PLANNER_CALL,
                    step_index=step_index,
                    sim_time_sec=observation.sim_time_sec,
                    payload=planner_request.to_dict(),
                )

                planner_started = time.perf_counter()
                planner_raw_response: PlannerRawResponse = self.planner_backend.plan(planner_request)
                call_latency_sec = round(time.perf_counter() - planner_started, 6)
                planner_latency_sec = round(planner_latency_sec + call_latency_sec, 6)
                planner_call_count += 1
                token_usage = _add_token_usage(token_usage, planner_raw_response.token_usage)

                parsed_action: PlannerAction | None = None
                validation_error: str | None = None
                try:
                    parsed_action = parse_planner_action(planner_raw_response.raw_response)
                    validation_error = self._validate_navigation_action(
                        action=parsed_action,
                        observation=observation,
                        config=prepared_config,
                    )
                except PlannerResponseError as exc:
                    validation_error = str(exc)

                append_event(
                    EventType.PLANNER_RESPONSE,
                    step_index=step_index,
                    sim_time_sec=observation.sim_time_sec,
                    planner_latency_sec=call_latency_sec,
                    success=validation_error is None,
                    payload={
                        "raw_response": planner_raw_response.raw_response,
                        "parsed_action": parsed_action.to_dict() if parsed_action is not None else None,
                    },
                )

                planner_trace_entry = {
                    "step_index": step_index,
                    "request": planner_request.to_dict(),
                    "raw_response": planner_raw_response.raw_response,
                    "parsed_action": parsed_action.to_dict() if parsed_action is not None else None,
                    "valid": validation_error is None,
                    "validation_error": validation_error,
                    "planner_latency_sec": call_latency_sec,
                    "token_usage": {
                        "prompt_tokens": planner_raw_response.token_usage.prompt_tokens,
                        "completion_tokens": planner_raw_response.token_usage.completion_tokens,
                        "total_tokens": planner_raw_response.token_usage.total_tokens,
                        "estimated_cost_usd": planner_raw_response.token_usage.estimated_cost_usd,
                    },
                }
                planner_trace.append(planner_trace_entry)

                if validation_error is not None:
                    invalid_action_count += 1
                    notes.append(validation_error)
                    append_event(
                        EventType.VALIDATION_WARNING,
                        step_index=step_index,
                        sim_time_sec=observation.sim_time_sec,
                        success=False,
                        payload={
                            "reason": validation_error,
                            "raw_response": planner_raw_response.raw_response,
                        },
                        notes=[validation_error],
                    )
                    append_event(
                        EventType.STEP_END,
                        step_index=step_index,
                        sim_time_sec=observation.sim_time_sec,
                        success=False,
                        payload={"status": "invalid_action"},
                    )
                    runtime_step_count = step_index
                    if invalid_action_count >= self.runtime_config.max_invalid_actions:
                        termination_reason = TerminationReason.INVALID_ACTION_LIMIT
                        break
                    continue

                assert parsed_action is not None
                append_event(
                    EventType.TOOL_CALL,
                    step_index=step_index,
                    sim_time_sec=observation.sim_time_sec,
                    tool_name=parsed_action.tool_name,
                    success=True,
                    payload=parsed_action.to_dict(),
                )
                tool_result, next_observation, state_changed = self._dispatch_navigation_action(
                    action=parsed_action,
                    observation=observation,
                    environment=environment,
                    config=prepared_config,
                )
                tool_call_count += 1
                tool_history.append(parsed_action.tool_name)
                last_tool_result = tool_result
                tool_trace.append(
                    {
                        "step_index": step_index,
                        "tool_name": parsed_action.tool_name,
                        "arguments": parsed_action.arguments,
                        "success": True,
                        "result": tool_result,
                    }
                )
                append_event(
                    EventType.TOOL_RESULT,
                    step_index=step_index,
                    sim_time_sec=next_observation.sim_time_sec,
                    tool_name=parsed_action.tool_name,
                    success=True,
                    payload=tool_result,
                )
                if state_changed:
                    append_event(
                        EventType.ACTION_APPLIED,
                        step_index=step_index,
                        sim_time_sec=next_observation.sim_time_sec,
                        action_ref=SCRIPTED_NAVIGATE_TOOL.name,
                        tool_name=parsed_action.tool_name,
                        success=True,
                        payload={
                            "executor": SCRIPTED_NAVIGATE_TOOL.name,
                            "pose": next_observation.pose.to_dict(),
                        },
                        metrics={
                            "navigation.final_goal_distance_m": round(
                                next_observation.distance_to_goal_m,
                                6,
                            ),
                        },
                    )
                append_event(
                    EventType.STEP_END,
                    step_index=step_index,
                    sim_time_sec=next_observation.sim_time_sec,
                    success=True,
                    payload={"tool_name": parsed_action.tool_name},
                    metrics={
                        "navigation.final_goal_distance_m": round(next_observation.distance_to_goal_m, 6),
                    },
                )
                trajectory_entries.append(
                    _build_trajectory_entry(
                        step_index=step_index,
                        observation=next_observation,
                        tool_name=parsed_action.tool_name,
                    )
                )
                observation = next_observation
                runtime_step_count = step_index

            elapsed_time_sec = round(time.perf_counter() - start_time, 6)
            final_observation = environment.observe()
            success = termination_reason == TerminationReason.SUCCESS
            result = EpisodeResult(
                run_id=run_id,
                task_type=prepared_config.task_type,
                task_id=prepared_config.task_id,
                scene_id=prepared_config.scene_id,
                robot_id=prepared_config.robot_id,
                seed=prepared_config.seed,
                success=success,
                termination_reason=termination_reason or TerminationReason.UNKNOWN,
                step_count=runtime_step_count,
                elapsed_time_sec=elapsed_time_sec,
                sim_time_sec=final_observation.sim_time_sec,
                invalid_action_count=invalid_action_count,
                collision_count=0,
                recovery_count=0,
                tool_call_count=tool_call_count,
                planner_call_count=planner_call_count,
                token_usage=token_usage,
                planner_latency_sec=planner_latency_sec,
                notes=notes,
                metrics={
                    "navigation.goal_reached": success,
                    "navigation.final_goal_distance_m": round(final_observation.distance_to_goal_m, 6),
                    "navigation.path_length_m": round(compute_path_length(environment.path), 6),
                    "navigation.waypoints_completed": len(prepared_config.navigation.waypoint_refs),
                    "navigation.backend": backend,
                    "navigation.motion_step_count": environment.step_count,
                    "navigation.stage_artifact_written": hasattr(environment, "stage_artifact_text"),
                    "navigation.runtime_policy": session.policy_name,
                    "navigation.planner_backend": session.planner_backend,
                },
            )
            append_event(
                EventType.EPISODE_END,
                step_index=result.step_count,
                sim_time_sec=result.sim_time_sec,
                success=result.success,
                payload={
                    "backend": backend,
                    "termination_reason": result.termination_reason.value,
                    "planner_backend": session.planner_backend,
                },
                metrics={
                    "navigation.final_goal_distance_m": result.metrics["navigation.final_goal_distance_m"],
                    "navigation.path_length_m": result.metrics["navigation.path_length_m"],
                },
            )

            trajectory: dict[str, Any] = {
                "run_id": run_id,
                "task_id": prepared_config.task_id,
                "scene_id": prepared_config.scene_id,
                "backend": backend,
                "planner_backend": session.planner_backend,
                "available_tools": self.tool_registry.names_for_task(prepared_config.task_type),
                "poses": trajectory_entries,
            }
            if stage_settings is not None:
                trajectory["isaac"] = stage_settings
            if getattr(environment, "runtime_details", None):
                trajectory["runtime"] = environment.runtime_details

            text_artifacts: dict[str, str] = {}
            if hasattr(environment, "stage_artifact_text"):
                text_artifacts["stage.usda"] = environment.stage_artifact_text()

            return AgentRunData(
                config=prepared_config,
                manifest=manifest,
                result=result,
                events=events,
                trajectory=trajectory,
                planner_trace=planner_trace,
                tool_trace=tool_trace,
                text_artifacts=text_artifacts,
            )
        finally:
            if hasattr(environment, "close"):
                environment.close()

    def _validate_navigation_action(
        self,
        action: PlannerAction,
        observation: NavigationObservation,
        config: TaskConfig,
    ) -> str | None:
        try:
            tool_spec = self.tool_registry.require(action.tool_name)
        except KeyError:
            return f"unknown tool: {action.tool_name}"

        if not tool_spec.supports_task(config.task_type):
            return f"tool '{action.tool_name}' is not valid for task type '{config.task_type.value}'"

        argument_names = set(action.arguments.keys())
        required_names = set(tool_spec.required_arguments)
        if argument_names != required_names:
            return (
                f"tool '{action.tool_name}' requires arguments {sorted(required_names)}, "
                f"got {sorted(argument_names)}"
            )

        if action.tool_name in {"get_robot_state", "get_goal_state"}:
            return None

        if action.tool_name == "navigate_to":
            target_pose_payload = action.arguments.get("target_pose")
            if not isinstance(target_pose_payload, dict):
                return "tool 'navigate_to' requires a target_pose dictionary"
            try:
                target_pose = Pose2D.from_dict(target_pose_payload)
                goal_pose = Pose2D.from_dict(config.navigation.goal_pose)
            except (KeyError, TypeError, ValueError) as exc:
                return f"tool 'navigate_to' target_pose is invalid: {exc}"

            if distance_between_poses(target_pose, goal_pose) > 1e-6:
                return (
                    "tool 'navigate_to' must target the configured goal_pose in M4 runtime v0; "
                    f"planner proposed ({target_pose.x}, {target_pose.y}) while goal is "
                    f"({goal_pose.x}, {goal_pose.y})"
                )
            return None

        return f"tool '{action.tool_name}' is not implemented by M4 runtime v0"

    def _dispatch_navigation_action(
        self,
        action: PlannerAction,
        observation: NavigationObservation,
        environment: Any,
        config: TaskConfig,
    ) -> tuple[dict[str, Any], NavigationObservation, bool]:
        if action.tool_name == "get_robot_state":
            return (
                {
                    "tool_name": action.tool_name,
                    "robot_state": observation.to_dict(),
                },
                observation,
                False,
            )

        if action.tool_name == "get_goal_state":
            return (
                {
                    "tool_name": action.tool_name,
                    "goal_state": config.navigation.goal_pose,
                    "success_radius_m": round(config.navigation.success_radius_m, 6),
                },
                observation,
                False,
            )

        if action.tool_name == "navigate_to":
            step_result = environment.step_toward_goal()
            return (
                {
                    "tool_name": action.tool_name,
                    "executor": SCRIPTED_NAVIGATE_TOOL.name,
                    "applied_action": step_result.action.to_dict(),
                    "observation": step_result.observation.to_dict(),
                    "progress_m": round(step_result.progress_m, 6),
                    "moved_distance_m": round(step_result.moved_distance_m, 6),
                    "stuck_steps": step_result.stuck_steps,
                },
                step_result.observation,
                True,
            )

        raise ValueError(f"unsupported tool dispatch: {action.tool_name}")


def _build_failure_run_data(
    config: TaskConfig,
    run_id: str,
    manifest: RunManifest,
    planner_backend: str,
    termination_reason: TerminationReason,
    message: str,
) -> AgentRunData:
    """Build a contract-compliant failure bundle when execution cannot start."""

    backend = "unknown"
    goal_distance: float | None = None
    try:
        backend = _navigation_backend_from_config(config)
        definition = _navigation_definition_from_config(config)
        goal_distance = round(distance_between_poses(definition.start_pose, definition.goal_pose), 6)
    except Exception:
        pass

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
            payload={
                "planner_backend": planner_backend,
                "backend": backend,
            },
            notes=["Run directory initialized before execution."],
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
            payload={"message": message},
            notes=[message],
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
        notes=[
            "Agent runtime v0 failed before entering the planner/tool execution loop.",
            message,
        ],
        metrics={
            "navigation.goal_reached": False,
            "navigation.final_goal_distance_m": goal_distance,
            "navigation.path_length_m": 0.0,
            "navigation.waypoints_completed": len(config.navigation.waypoint_refs) if config.navigation else 0,
            "navigation.backend": backend,
            "navigation.motion_step_count": 0,
            "navigation.stage_artifact_written": False,
            "navigation.runtime_policy": "agent_runtime_v0",
            "navigation.planner_backend": planner_backend,
        },
    )
    return AgentRunData(
        config=config,
        manifest=manifest,
        result=result,
        events=events,
        trajectory={
            "run_id": run_id,
            "task_id": config.task_id,
            "scene_id": config.scene_id,
            "backend": backend,
            "planner_backend": planner_backend,
            "status": "blocked",
            "error": message,
            "poses": [],
        },
        planner_trace=[],
        tool_trace=[],
        text_artifacts={},
    )


def execute_agent_v0(
    config: TaskConfig,
    run_id: str,
    planner_backend: PlannerBackend | None = None,
    runtime_config: AgentRuntimeConfig | None = None,
) -> AgentRunData:
    """Execute one in-memory M4 runtime episode."""

    runtime = AgentRuntime(
        planner_backend=planner_backend,
        runtime_config=runtime_config,
    )
    return runtime.execute(config=config, run_id=run_id)


def run_and_write_agent_v0(
    config: TaskConfig,
    run_id: str,
    results_root: str | Path = "results",
    planner_backend: PlannerBackend | None = None,
    runtime_config: AgentRuntimeConfig | None = None,
) -> tuple[AgentRunData, RunArtifactsLayout]:
    """Execute the M4 runtime and write canonical artifacts."""

    planner_backend = planner_backend or MockPlannerBackend()
    runtime = AgentRuntime(
        planner_backend=planner_backend,
        runtime_config=runtime_config,
    )
    prepared_config = _clone_task_config(config)
    prepared_config.runtime_options.planner_enabled = True
    prepared_config.runtime_options.memory_enabled = False
    prepared_config.runtime_options.recovery_enabled = False
    prepared_config.runtime_options.collect_events = True
    prepared_config.runtime_options.extra_options["planner_backend"] = planner_backend.backend_name
    metadata = dict(prepared_config.metadata)
    agent_metadata = dict(metadata.get("agent_runtime_v0", {}))
    agent_metadata["planner_backend"] = planner_backend.backend_name
    agent_metadata["available_tools"] = runtime.tool_registry.names_for_task(prepared_config.task_type)
    metadata["agent_runtime_v0"] = agent_metadata
    prepared_config.metadata = metadata

    manifest = RunManifest(
        run_id=run_id,
        task_type=prepared_config.task_type,
        task_id=prepared_config.task_id,
        scene_id=prepared_config.scene_id,
        robot_id=prepared_config.robot_id,
        seed=prepared_config.seed,
    )
    layout = RunArtifactsLayout(run_id=run_id, results_root=results_root)
    if layout.run_dir.exists() and any(layout.run_dir.iterdir()):
        raise FileExistsError(f"run directory already exists and is not empty: {layout.run_dir}")

    layout.ensure()
    write_run_manifest(layout.manifest_path, manifest)
    write_task_config(layout.task_config_path, prepared_config)

    try:
        run_data = runtime.execute(config=prepared_config, run_id=run_id)
    except NavigationBackendUnavailableError as exc:
        run_data = _build_failure_run_data(
            config=prepared_config,
            run_id=run_id,
            manifest=manifest,
            planner_backend=planner_backend.backend_name,
            termination_reason=TerminationReason.TASK_PRECONDITION_FAILED,
            message=f"{type(exc).__name__}: {exc}",
        )
    except ValueError as exc:
        run_data = _build_failure_run_data(
            config=prepared_config,
            run_id=run_id,
            manifest=manifest,
            planner_backend=planner_backend.backend_name,
            termination_reason=TerminationReason.TASK_PRECONDITION_FAILED,
            message=f"{type(exc).__name__}: {exc}",
        )
    except Exception as exc:
        run_data = _build_failure_run_data(
            config=prepared_config,
            run_id=run_id,
            manifest=manifest,
            planner_backend=planner_backend.backend_name,
            termination_reason=TerminationReason.RUNTIME_ERROR,
            message=f"{type(exc).__name__}: {exc}",
        )

    write_episode_result(layout.episode_result_path, run_data.result)
    write_event_log(layout.event_log_path, run_data.events)
    _write_json(layout.artifacts_dir / "trajectory.json", run_data.trajectory)
    _write_json(layout.artifacts_dir / "planner_trace.json", run_data.planner_trace)
    _write_json(layout.artifacts_dir / "tool_trace.json", run_data.tool_trace)
    for artifact_name, payload in run_data.text_artifacts.items():
        (layout.artifacts_dir / artifact_name).write_text(payload, encoding="utf-8")
    return run_data, layout
