"""Minimal M4 agent runtime with structured planner tool calls."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from isaacsim_agent.agent import build_retry_instruction
from isaacsim_agent.agent import normalize_prompt_variant
from isaacsim_agent.agent import prompt_variant_definition
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
from isaacsim_agent.tasks.manipulation import build_minimal_pickplace_task_config
from isaacsim_agent.tasks.manipulation.baseline import BasePickPlaceEnvironment
from isaacsim_agent.tasks.manipulation.baseline import ManipulationBackendUnavailableError
from isaacsim_agent.tasks.manipulation.baseline import MinimalPickPlaceEnvironment
from isaacsim_agent.tasks.manipulation.baseline import PickPlaceObservation
from isaacsim_agent.tasks.manipulation.baseline import PickPlaceStepResult
from isaacsim_agent.tasks.manipulation.baseline import _isaac_stage_settings_from_config as _manipulation_isaac_stage_settings_from_config
from isaacsim_agent.tasks.manipulation.baseline import _manipulation_backend_from_config
from isaacsim_agent.tasks.manipulation.baseline import _manipulation_definition_from_config
from isaacsim_agent.tasks.navigation import build_minimal_navigation_task_config
from isaacsim_agent.tasks.navigation.baseline import MinimalNavigationEnvironment
from isaacsim_agent.tasks.navigation.baseline import NavigationBackendUnavailableError
from isaacsim_agent.tasks.navigation.baseline import NavigationObservation
from isaacsim_agent.tasks.navigation.baseline import _isaac_stage_settings_from_config
from isaacsim_agent.tasks.navigation.baseline import _navigation_backend_from_config
from isaacsim_agent.tasks.navigation.baseline import _navigation_definition_from_config
from isaacsim_agent.tools import SCRIPTED_PICKPLACE_TOOL
from isaacsim_agent.tools import SCRIPTED_NAVIGATE_TOOL
from isaacsim_agent.tools import Pose3D
from isaacsim_agent.tools import compute_pose_path_length
from isaacsim_agent.tools import distance_between_poses_3d
from isaacsim_agent.tools import Pose2D
from isaacsim_agent.tools import compute_path_length
from isaacsim_agent.tools import distance_between_poses
from isaacsim_agent.tools.registry import ToolRegistry
from isaacsim_agent.tools.registry import ToolSpec
from isaacsim_agent.tools.registry import build_agent_v0_tool_registry
from isaacsim_agent.tools.registry import build_manipulation_tool_registry
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
    policy_name: str = "agent_runtime_v0"
    max_invalid_actions: int = 1
    validation_enabled: bool = True
    max_validation_retries: int = 0


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
    config.runtime_options.tool_validation_enabled = True
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


def build_minimal_agent_manipulation_task_config(
    backend: str = "toy",
    planner_backend: str = "mock_rule_based",
    **kwargs: Any,
) -> TaskConfig:
    """Build the default M4 manipulation task config while preserving the M1.5 schema."""

    config = build_minimal_pickplace_task_config(backend=backend, **kwargs)
    config.runtime_options.planner_enabled = True
    config.runtime_options.memory_enabled = False
    config.runtime_options.recovery_enabled = False
    config.runtime_options.tool_validation_enabled = True
    config.runtime_options.collect_events = True
    config.runtime_options.extra_options["planner_backend"] = planner_backend
    config.runtime_options.extra_options["runtime_policy"] = "agent_runtime_v0"

    metadata = dict(config.metadata)
    metadata["agent_runtime_v0"] = {
        "planner_backend": planner_backend,
        "supported_task_types": [TaskType.PICK_PLACE.value],
        "available_tools": build_manipulation_tool_registry().names_for_task(TaskType.PICK_PLACE),
        "structured_action_schema": {
            "tool_name": "string",
            "arguments": "object",
        },
    }
    config.metadata = metadata
    return config


def build_agent_v0_manipulation_task_config(
    backend: str = "toy",
    planner_backend: str = "mock_rule_based",
    **kwargs: Any,
) -> TaskConfig:
    """Backward-compatible public name for the M4 manipulation task builder."""

    return build_minimal_agent_manipulation_task_config(
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


def _build_pick_place_trajectory_entry(
    step_index: int,
    observation: PickPlaceObservation,
    phase_name: str,
    tool_name: str | None = None,
    gripper_moved_distance_m: float = 0.0,
    object_moved_distance_m: float = 0.0,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
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
    extra_options = config.runtime_options.extra_options
    prompt_text = extra_options.get("planner_prompt_text")
    if isinstance(prompt_text, str) and prompt_text.strip():
        return prompt_text.strip()

    prompting = config.metadata.get("prompting")
    if isinstance(prompting, dict):
        explicit_instruction = prompting.get("instruction")
        if isinstance(explicit_instruction, str) and explicit_instruction.strip():
            return explicit_instruction.strip()

        instruction_template = prompting.get("instruction_template")
        if isinstance(instruction_template, str) and instruction_template.strip():
            try:
                return instruction_template.format(**_navigation_prompt_values(config)).strip()
            except (KeyError, ValueError):
                return instruction_template.strip()

    agent_metadata = config.metadata.get("agent_runtime_v0")
    if isinstance(agent_metadata, dict):
        metadata_prompt = agent_metadata.get("prompt_text")
        if isinstance(metadata_prompt, str) and metadata_prompt.strip():
            return metadata_prompt.strip()

    if config.navigation is None or config.navigation.goal_pose is None:
        return "Navigate the robot to the configured goal pose."
    goal_pose = Pose2D.from_dict(config.navigation.goal_pose)
    return (
        "Navigate the robot to the configured goal pose "
        f"({goal_pose.x:.2f}, {goal_pose.y:.2f}, yaw={goal_pose.yaw:.2f})."
    )


def _manipulation_instruction(config: TaskConfig) -> str:
    extra_options = config.runtime_options.extra_options
    prompt_text = extra_options.get("planner_prompt_text")
    if isinstance(prompt_text, str) and prompt_text.strip():
        return prompt_text.strip()

    prompting = config.metadata.get("prompting")
    if isinstance(prompting, dict):
        explicit_instruction = prompting.get("instruction")
        if isinstance(explicit_instruction, str) and explicit_instruction.strip():
            return explicit_instruction.strip()

        instruction_template = prompting.get("instruction_template")
        if isinstance(instruction_template, str) and instruction_template.strip():
            try:
                return instruction_template.format(**_manipulation_prompt_values(config)).strip()
            except (KeyError, ValueError):
                return instruction_template.strip()

    agent_metadata = config.metadata.get("agent_runtime_v0")
    if isinstance(agent_metadata, dict):
        metadata_prompt = agent_metadata.get("prompt_text")
        if isinstance(metadata_prompt, str) and metadata_prompt.strip():
            return metadata_prompt.strip()

    if config.pick_place is None or config.pick_place.target_pose is None:
        return "Pick the configured object and place it at the configured target pose."
    target_pose = Pose3D.from_dict(config.pick_place.target_pose)
    return (
        "Pick the configured object and place it at the configured target pose "
        f"({target_pose.x:.2f}, {target_pose.y:.2f}, {target_pose.z:.2f})."
    )


def _prompt_variant(config: TaskConfig) -> str | None:
    extra_options = config.runtime_options.extra_options
    value = extra_options.get("prompt_variant")
    if isinstance(value, str) and value.strip():
        return value.strip()

    prompting = config.metadata.get("prompting")
    if isinstance(prompting, dict):
        metadata_value = prompting.get("prompt_variant")
        if isinstance(metadata_value, str) and metadata_value.strip():
            return metadata_value.strip()
    return None


def _runtime_variant(config: TaskConfig) -> str | None:
    extra_options = config.runtime_options.extra_options
    value = extra_options.get("runtime_variant")
    if isinstance(value, str) and value.strip():
        return value.strip()

    pilot_suite = config.metadata.get("pilot_suite")
    if isinstance(pilot_suite, dict):
        metadata_value = pilot_suite.get("runtime_variant")
        if isinstance(metadata_value, str) and metadata_value.strip():
            return metadata_value.strip()
    return None


def _runtime_policy_name(config: TaskConfig) -> str:
    extra_options = config.runtime_options.extra_options
    value = extra_options.get("runtime_policy")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "agent_runtime_v0"


def _runtime_probe_invalid_first_action(config: TaskConfig) -> bool:
    extra_options = config.runtime_options.extra_options
    value = extra_options.get("runtime_probe_invalid_first_action")
    if isinstance(value, bool):
        return value

    pilot_suite = config.metadata.get("pilot_suite")
    if isinstance(pilot_suite, dict):
        metadata_value = pilot_suite.get("runtime_probe_invalid_first_action")
        if isinstance(metadata_value, bool):
            return metadata_value
    return False


def _suite_experiment_name(config: TaskConfig) -> str | None:
    extra_options = config.runtime_options.extra_options
    value = extra_options.get("suite_experiment")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _repair_instruction_template(config: TaskConfig) -> str | None:
    extra_options = config.runtime_options.extra_options
    value = extra_options.get("prompt_repair_instruction_template")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _repair_instruction_template(config: TaskConfig) -> str | None:
    extra_options = config.runtime_options.extra_options
    value = extra_options.get("prompt_repair_instruction_template")
    if isinstance(value, str) and value.strip():
        return value.strip()

    prompting = config.metadata.get("prompting")
    if isinstance(prompting, dict):
        metadata_value = prompting.get("repair_instruction_template")
        if isinstance(metadata_value, str) and metadata_value.strip():
            return metadata_value.strip()
    return None


def _manifest_metadata(config: TaskConfig, planner_backend: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "planner_backend": planner_backend,
        "runtime_policy": _runtime_policy_name(config),
        "task_id": config.task_id,
        "scene_id": config.scene_id,
    }
    prompt_variant = _prompt_variant(config)
    runtime_variant = _runtime_variant(config)
    suite_experiment = _suite_experiment_name(config)
    if prompt_variant is not None:
        payload["prompt_variant"] = prompt_variant
    if runtime_variant is not None:
        payload["runtime_variant"] = runtime_variant
    if suite_experiment is not None:
        payload["suite_experiment"] = suite_experiment
    return payload


def _navigation_prompt_values(config: TaskConfig) -> dict[str, Any]:
    start_pose = Pose2D(x=0.0, y=0.0, yaw=0.0)
    navigation_metadata = config.metadata.get("navigation_baseline")
    if isinstance(navigation_metadata, dict):
        start_pose_payload = navigation_metadata.get("start_pose")
        if isinstance(start_pose_payload, dict):
            start_pose = Pose2D.from_dict(start_pose_payload)

    goal_pose = Pose2D(x=0.0, y=0.0, yaw=0.0)
    success_radius_m = 0.0
    if config.navigation is not None and config.navigation.goal_pose is not None:
        goal_pose = Pose2D.from_dict(config.navigation.goal_pose)
        success_radius_m = float(config.navigation.success_radius_m)

    return {
        "task_id": config.task_id,
        "scene_id": config.scene_id,
        "robot_id": config.robot_id,
        "seed": config.seed,
        "max_steps": config.max_steps,
        "max_time_sec": float(config.max_time_sec),
        "start_x": start_pose.x,
        "start_y": start_pose.y,
        "start_yaw": start_pose.yaw,
        "goal_x": goal_pose.x,
        "goal_y": goal_pose.y,
        "goal_yaw": goal_pose.yaw,
        "success_radius_m": success_radius_m,
    }


def _manipulation_prompt_values(config: TaskConfig) -> dict[str, Any]:
    definition = _manipulation_definition_from_config(config)
    current_phase = "reset"
    metadata = config.metadata.get("manipulation_baseline")
    if isinstance(metadata, dict):
        scripted_sequence = metadata.get("scripted_sequence")
        if isinstance(scripted_sequence, list) and scripted_sequence:
            current_phase = str(scripted_sequence[0])

    return {
        "task_id": config.task_id,
        "scene_id": config.scene_id,
        "robot_id": config.robot_id,
        "seed": config.seed,
        "max_steps": config.max_steps,
        "max_time_sec": float(config.max_time_sec),
        "gripper_start_x": definition.gripper_start_pose.x,
        "gripper_start_y": definition.gripper_start_pose.y,
        "gripper_start_z": definition.gripper_start_pose.z,
        "object_x": definition.object_start_pose.x,
        "object_y": definition.object_start_pose.y,
        "object_z": definition.object_start_pose.z,
        "target_x": definition.target_pose.x,
        "target_y": definition.target_pose.y,
        "target_z": definition.target_pose.z,
        "hover_offset_m": definition.hover_offset_m,
        "grasp_tolerance_m": definition.grasp_tolerance_m,
        "place_tolerance_m": definition.place_tolerance_m,
        "control_dt_sec": definition.control_dt_sec,
        "current_phase": current_phase,
    }


class AgentRuntime:
    """Small runtime loop for one structured planner-driven M4 episode."""

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
        self.tool_registry = tool_registry or build_agent_v0_tool_registry()

    def execute(self, config: TaskConfig, run_id: str) -> AgentRunData:
        """Execute one M4 agent runtime episode."""

        prepared_config = _clone_task_config(config)
        if prepared_config.task_type == TaskType.PICK_PLACE:
            return self._execute_pick_place(config=prepared_config, run_id=run_id)
        if prepared_config.task_type != TaskType.NAVIGATION:
            raise ValueError(
                "agent runtime v0 currently supports only navigation and pick_place tasks to keep M4 scope minimal"
            )
        prepared_config.runtime_options.planner_enabled = True
        prepared_config.runtime_options.memory_enabled = False
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
            metadata=_manifest_metadata(
                config=prepared_config,
                planner_backend=self.planner_backend.backend_name,
            ),
        )
        session = RuntimeSession(
            session_id=run_id,
            policy_name=self.runtime_config.policy_name or _runtime_policy_name(prepared_config),
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
            base_instruction = _navigation_instruction(prepared_config)
            prompt_variant = normalize_prompt_variant(_prompt_variant(prepared_config))
            prompt_definition = prompt_variant_definition(prompt_variant)
            runtime_variant = _runtime_variant(prepared_config)
            validation_enabled = bool(
                self.runtime_config.validation_enabled
                and prepared_config.runtime_options.tool_validation_enabled
            )
            max_validation_retries = (
                self.runtime_config.max_validation_retries
                if prepared_config.runtime_options.recovery_enabled
                else 0
            )
            start_payload: dict[str, Any] = {
                "runtime_session": {
                    "session_id": session.session_id,
                    "policy_name": session.policy_name,
                    "planner_backend": session.planner_backend,
                },
                "available_tools": available_tools,
                "instruction": base_instruction,
                "backend": backend,
                "start_pose": observation.pose.to_dict(),
                "goal_pose": prepared_config.navigation.goal_pose,
                "success_radius_m": prepared_config.navigation.success_radius_m,
                "prompt_variant": prompt_variant,
                "runtime_variant": runtime_variant,
                "runtime_probe_invalid_first_action": _runtime_probe_invalid_first_action(prepared_config),
                "validation_enabled": validation_enabled,
                "max_validation_retries": max_validation_retries,
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
            retry_count = 0
            runtime_step_count = 0
            planner_latency_sec = 0.0
            token_usage = TokenUsage()
            last_tool_result: dict[str, Any] | None = None
            tool_history: list[str] = []
            notes = [
                "Minimal M4 runtime v0 using structured JSON planner actions.",
                (
                    "Runtime policy: "
                    f"{session.policy_name}; validation={'on' if validation_enabled else 'off'}; "
                    f"max_validation_retries={max_validation_retries}."
                ),
                (
                    "Prompt variant: "
                    f"{prompt_variant} ({prompt_definition.response_format})."
                ),
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

                retry_index = 0
                retry_validation_error: str | None = None
                step_completed = False
                step_invalid = False

                while not step_completed:
                    instruction = base_instruction
                    if retry_index > 0 and retry_validation_error is not None:
                        instruction = build_retry_instruction(
                            base_instruction=base_instruction,
                            validation_error=retry_validation_error,
                            repair_instruction_template=_repair_instruction_template(prepared_config),
                        )

                    planner_request = PlannerRequest(
                        task_type=prepared_config.task_type,
                        instruction=instruction,
                        step_index=step_index,
                        available_tools=available_tools,
                        state={
                            "task_id": prepared_config.task_id,
                            "scene_id": prepared_config.scene_id,
                            "robot_pose": observation.pose.to_dict(),
                            "goal_pose": prepared_config.navigation.goal_pose,
                            "distance_to_goal_m": round(observation.distance_to_goal_m, 6),
                            "success_radius_m": round(prepared_config.navigation.success_radius_m, 6),
                            "sim_time_sec": round(observation.sim_time_sec, 6),
                            "runtime_probe_invalid_first_action": _runtime_probe_invalid_first_action(
                                prepared_config
                            ),
                        },
                        last_tool_result=last_tool_result,
                        tool_history=list(tool_history),
                        prompt_variant=prompt_variant,
                        runtime_variant=runtime_variant,
                        retry_index=retry_index,
                        validation_error=retry_validation_error,
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
                    action_error: str | None = None
                    try:
                        parsed_action = parse_planner_action(planner_raw_response.raw_response)
                        if validation_enabled:
                            action_error = self._validate_navigation_action(
                                action=parsed_action,
                                observation=observation,
                                config=prepared_config,
                            )
                    except PlannerResponseError as exc:
                        action_error = str(exc)

                    append_event(
                        EventType.PLANNER_RESPONSE,
                        step_index=step_index,
                        sim_time_sec=observation.sim_time_sec,
                        planner_latency_sec=call_latency_sec,
                        success=action_error is None,
                        payload={
                            "raw_response": planner_raw_response.raw_response,
                            "parsed_action": parsed_action.to_dict() if parsed_action is not None else None,
                            "retry_index": retry_index,
                        },
                    )

                    planner_trace.append(
                        {
                            "step_index": step_index,
                            "retry_index": retry_index,
                            "request": planner_request.to_dict(),
                            "raw_response": planner_raw_response.raw_response,
                            "parsed_action": parsed_action.to_dict() if parsed_action is not None else None,
                            "valid": action_error is None,
                            "validation_error": action_error,
                            "planner_latency_sec": call_latency_sec,
                            "token_usage": {
                                "prompt_tokens": planner_raw_response.token_usage.prompt_tokens,
                                "completion_tokens": planner_raw_response.token_usage.completion_tokens,
                                "total_tokens": planner_raw_response.token_usage.total_tokens,
                                "estimated_cost_usd": planner_raw_response.token_usage.estimated_cost_usd,
                            },
                        }
                    )

                    if action_error is not None:
                        invalid_action_count += 1
                        notes.append(action_error)
                        append_event(
                            EventType.VALIDATION_WARNING,
                            step_index=step_index,
                            sim_time_sec=observation.sim_time_sec,
                            success=False,
                            payload={
                                "reason": action_error,
                                "raw_response": planner_raw_response.raw_response,
                                "retry_index": retry_index,
                                "retry_planned": retry_index < max_validation_retries,
                            },
                            notes=[action_error],
                        )
                        if retry_index < max_validation_retries:
                            retry_count += 1
                            retry_validation_error = action_error
                            retry_index += 1
                            append_event(
                                EventType.RECOVERY,
                                step_index=step_index,
                                sim_time_sec=observation.sim_time_sec,
                                success=True,
                                payload={
                                    "recovery_type": "planner_retry",
                                    "retry_index": retry_index,
                                    "reason": action_error,
                                },
                            )
                            continue
                        step_invalid = True
                        break

                    assert parsed_action is not None
                    append_event(
                        EventType.TOOL_CALL,
                        step_index=step_index,
                        sim_time_sec=observation.sim_time_sec,
                        tool_name=parsed_action.tool_name,
                        success=True,
                        payload=parsed_action.to_dict(),
                    )
                    try:
                        tool_result, next_observation, state_changed = self._dispatch_navigation_action(
                            action=parsed_action,
                            observation=observation,
                            environment=environment,
                            config=prepared_config,
                        )
                    except (KeyError, TypeError, ValueError) as exc:
                        action_error = f"tool dispatch failed: {exc}"
                        invalid_action_count += 1
                        notes.append(action_error)
                        append_event(
                            EventType.TOOL_RESULT,
                            step_index=step_index,
                            sim_time_sec=observation.sim_time_sec,
                            tool_name=parsed_action.tool_name,
                            success=False,
                            payload={
                                "error": action_error,
                                "tool_name": parsed_action.tool_name,
                                "arguments": parsed_action.arguments,
                            },
                            notes=[action_error],
                        )
                        if retry_index < max_validation_retries:
                            retry_count += 1
                            retry_validation_error = action_error
                            retry_index += 1
                            append_event(
                                EventType.RECOVERY,
                                step_index=step_index,
                                sim_time_sec=observation.sim_time_sec,
                                success=True,
                                payload={
                                    "recovery_type": "planner_retry",
                                    "retry_index": retry_index,
                                    "reason": action_error,
                                },
                            )
                            continue
                        step_invalid = True
                        break

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
                    step_completed = True

                if step_invalid:
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
                recovery_count=retry_count,
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
                    "navigation.runtime_variant": runtime_variant,
                    "navigation.planner_backend": session.planner_backend,
                    "prompt_variant": prompt_variant,
                    "runtime.retry_count": retry_count,
                    "runtime.validation_enabled": validation_enabled,
                    "runtime.max_validation_retries": max_validation_retries,
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

    def _execute_pick_place(self, config: TaskConfig, run_id: str) -> AgentRunData:
        """Execute one M4 runtime episode over the minimal scripted pick-and-place baseline."""

        config.runtime_options.planner_enabled = True
        config.runtime_options.memory_enabled = False
        config.runtime_options.collect_events = True

        backend = _manipulation_backend_from_config(config)
        stage_settings: dict[str, Any] | None = None
        if backend == "isaac":
            from isaacsim_agent.tasks.manipulation.isaac_world import IsaacPickPlaceWorldConfig
            from isaacsim_agent.tasks.manipulation.isaac_world import MinimalIsaacPickPlaceEnvironment

            stage_settings = _manipulation_isaac_stage_settings_from_config(config)
            environment: BasePickPlaceEnvironment = MinimalIsaacPickPlaceEnvironment(
                definition=_manipulation_definition_from_config(config),
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
            environment = MinimalPickPlaceEnvironment(_manipulation_definition_from_config(config))

        manifest = RunManifest(
            run_id=run_id,
            task_type=config.task_type,
            task_id=config.task_id,
            scene_id=config.scene_id,
            robot_id=config.robot_id,
            seed=config.seed,
            metadata=_manifest_metadata(
                config=config,
                planner_backend=self.planner_backend.backend_name,
            ),
        )
        session = RuntimeSession(
            session_id=run_id,
            policy_name=self.runtime_config.policy_name or _runtime_policy_name(config),
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
                    task_type=config.task_type,
                    task_id=config.task_id,
                    scene_id=config.scene_id,
                    robot_id=config.robot_id,
                    seed=config.seed,
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
            trajectory_entries = [
                _build_pick_place_trajectory_entry(
                    step_index=0,
                    observation=observation,
                    phase_name="reset",
                )
            ]
            available_tools = [
                _tool_spec_to_payload(tool_spec)
                for tool_spec in self.tool_registry.specs_for_task(config.task_type)
            ]
            base_instruction = _manipulation_instruction(config)
            prompt_variant = normalize_prompt_variant(_prompt_variant(config))
            prompt_definition = prompt_variant_definition(prompt_variant)
            runtime_variant = _runtime_variant(config)
            validation_enabled = bool(
                self.runtime_config.validation_enabled
                and config.runtime_options.tool_validation_enabled
            )
            max_validation_retries = (
                self.runtime_config.max_validation_retries
                if config.runtime_options.recovery_enabled
                else 0
            )
            start_payload: dict[str, Any] = {
                "runtime_session": {
                    "session_id": session.session_id,
                    "policy_name": session.policy_name,
                    "planner_backend": session.planner_backend,
                },
                "available_tools": available_tools,
                "instruction": base_instruction,
                "backend": backend,
                "gripper_pose": observation.gripper_pose.to_dict(),
                "object_pose": observation.object_pose.to_dict(),
                "target_pose": config.pick_place.target_pose if config.pick_place is not None else None,
                "prompt_variant": prompt_variant,
                "runtime_variant": runtime_variant,
                "runtime_probe_invalid_first_action": _runtime_probe_invalid_first_action(config),
                "validation_enabled": validation_enabled,
                "max_validation_retries": max_validation_retries,
            }
            if stage_settings is not None:
                start_payload["isaac"] = stage_settings
            if environment.runtime_details:
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
            retry_count = 0
            runtime_step_count = 0
            planner_latency_sec = 0.0
            token_usage = TokenUsage()
            last_tool_result: dict[str, Any] | None = None
            tool_history: list[str] = []
            notes = [
                "Minimal M4 runtime v0 using structured JSON planner actions.",
                (
                    "Runtime policy: "
                    f"{session.policy_name}; validation={'on' if validation_enabled else 'off'}; "
                    f"max_validation_retries={max_validation_retries}."
                ),
                f"Prompt variant: {prompt_variant} ({prompt_definition.response_format}).",
            ]
            termination_reason: TerminationReason | None = None

            while termination_reason is None:
                if runtime_step_count >= config.max_steps:
                    termination_reason = TerminationReason.MAX_STEPS
                    notes.append(
                        f"runtime reached max_steps={config.max_steps} before task completion"
                    )
                    break

                environment_termination = environment.termination_reason()
                if environment_termination is not None:
                    termination_reason = environment_termination
                    break

                step_index = runtime_step_count + 1
                next_phase = environment.scripted_actions[environment.step_count].phase_name
                append_event(
                    EventType.STEP_START,
                    step_index=step_index,
                    sim_time_sec=observation.sim_time_sec,
                    payload={
                        "backend": backend,
                        "planner_backend": self.planner_backend.backend_name,
                        "next_phase": next_phase,
                    },
                )
                append_event(
                    EventType.OBSERVATION,
                    step_index=step_index,
                    sim_time_sec=observation.sim_time_sec,
                    payload=observation.to_dict(),
                    metrics={
                        "manipulation.final_object_to_target_distance_m": round(
                            observation.distance_to_target_m,
                            6,
                        ),
                    },
                )

                retry_index = 0
                retry_validation_error: str | None = None
                step_completed = False
                step_invalid = False

                while not step_completed:
                    instruction = base_instruction
                    if retry_index > 0 and retry_validation_error is not None:
                        instruction = build_retry_instruction(
                            base_instruction=base_instruction,
                            validation_error=retry_validation_error,
                            repair_instruction_template=_repair_instruction_template(config),
                        )

                    planner_request = PlannerRequest(
                        task_type=config.task_type,
                        instruction=instruction,
                        step_index=step_index,
                        available_tools=available_tools,
                        state={
                            "task_id": config.task_id,
                            "scene_id": config.scene_id,
                            "gripper_pose": observation.gripper_pose.to_dict(),
                            "object_pose": observation.object_pose.to_dict(),
                            "target_pose": config.pick_place.target_pose if config.pick_place is not None else None,
                            "current_phase": observation.current_phase,
                            "next_phase": next_phase,
                            "distance_to_object_m": round(observation.distance_to_object_m, 6),
                            "distance_to_target_m": round(observation.distance_to_target_m, 6),
                            "gripper_open": observation.gripper_open,
                            "object_attached": observation.object_attached,
                            "sim_time_sec": round(observation.sim_time_sec, 6),
                            "runtime_probe_invalid_first_action": _runtime_probe_invalid_first_action(config),
                        },
                        last_tool_result=last_tool_result,
                        tool_history=list(tool_history),
                        prompt_variant=prompt_variant,
                        runtime_variant=runtime_variant,
                        retry_index=retry_index,
                        validation_error=retry_validation_error,
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
                    action_error: str | None = None
                    try:
                        parsed_action = parse_planner_action(planner_raw_response.raw_response)
                        if validation_enabled:
                            action_error = self._validate_pick_place_action(
                                action=parsed_action,
                                config=config,
                                next_phase=next_phase,
                            )
                    except PlannerResponseError as exc:
                        action_error = str(exc)

                    append_event(
                        EventType.PLANNER_RESPONSE,
                        step_index=step_index,
                        sim_time_sec=observation.sim_time_sec,
                        planner_latency_sec=call_latency_sec,
                        success=action_error is None,
                        payload={
                            "raw_response": planner_raw_response.raw_response,
                            "parsed_action": parsed_action.to_dict() if parsed_action is not None else None,
                            "retry_index": retry_index,
                        },
                    )

                    planner_trace.append(
                        {
                            "step_index": step_index,
                            "retry_index": retry_index,
                            "request": planner_request.to_dict(),
                            "raw_response": planner_raw_response.raw_response,
                            "parsed_action": parsed_action.to_dict() if parsed_action is not None else None,
                            "valid": action_error is None,
                            "validation_error": action_error,
                            "planner_latency_sec": call_latency_sec,
                            "token_usage": {
                                "prompt_tokens": planner_raw_response.token_usage.prompt_tokens,
                                "completion_tokens": planner_raw_response.token_usage.completion_tokens,
                                "total_tokens": planner_raw_response.token_usage.total_tokens,
                                "estimated_cost_usd": planner_raw_response.token_usage.estimated_cost_usd,
                            },
                        }
                    )

                    if action_error is not None:
                        invalid_action_count += 1
                        notes.append(action_error)
                        append_event(
                            EventType.VALIDATION_WARNING,
                            step_index=step_index,
                            sim_time_sec=observation.sim_time_sec,
                            success=False,
                            payload={
                                "reason": action_error,
                                "raw_response": planner_raw_response.raw_response,
                                "retry_index": retry_index,
                                "retry_planned": retry_index < max_validation_retries,
                            },
                            notes=[action_error],
                        )
                        if retry_index < max_validation_retries:
                            retry_count += 1
                            retry_validation_error = action_error
                            retry_index += 1
                            append_event(
                                EventType.RECOVERY,
                                step_index=step_index,
                                sim_time_sec=observation.sim_time_sec,
                                success=True,
                                payload={
                                    "recovery_type": "planner_retry",
                                    "retry_index": retry_index,
                                    "reason": action_error,
                                },
                            )
                            continue
                        step_invalid = True
                        break

                    assert parsed_action is not None
                    append_event(
                        EventType.TOOL_CALL,
                        step_index=step_index,
                        sim_time_sec=observation.sim_time_sec,
                        tool_name=parsed_action.tool_name,
                        success=True,
                        payload=parsed_action.to_dict(),
                    )
                    try:
                        (
                            tool_result,
                            next_observation,
                            state_changed,
                            phase_name,
                            gripper_moved_distance_m,
                            object_moved_distance_m,
                        ) = self._dispatch_pick_place_action(
                            action=parsed_action,
                            observation=observation,
                            environment=environment,
                            config=config,
                        )
                    except (KeyError, TypeError, ValueError) as exc:
                        action_error = f"tool dispatch failed: {exc}"
                        invalid_action_count += 1
                        notes.append(action_error)
                        append_event(
                            EventType.TOOL_RESULT,
                            step_index=step_index,
                            sim_time_sec=observation.sim_time_sec,
                            tool_name=parsed_action.tool_name,
                            success=False,
                            payload={
                                "error": action_error,
                                "tool_name": parsed_action.tool_name,
                                "arguments": parsed_action.arguments,
                            },
                            notes=[action_error],
                        )
                        if retry_index < max_validation_retries:
                            retry_count += 1
                            retry_validation_error = action_error
                            retry_index += 1
                            append_event(
                                EventType.RECOVERY,
                                step_index=step_index,
                                sim_time_sec=observation.sim_time_sec,
                                success=True,
                                payload={
                                    "recovery_type": "planner_retry",
                                    "retry_index": retry_index,
                                    "reason": action_error,
                                },
                            )
                            continue
                        step_invalid = True
                        break

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
                            action_ref=SCRIPTED_PICKPLACE_TOOL.name,
                            tool_name=parsed_action.tool_name,
                            success=True,
                            payload={
                                "executor": SCRIPTED_PICKPLACE_TOOL.name,
                                "phase_name": phase_name,
                                "gripper_pose": next_observation.gripper_pose.to_dict(),
                                "object_pose": next_observation.object_pose.to_dict(),
                            },
                            metrics={
                                "manipulation.final_object_to_target_distance_m": round(
                                    next_observation.distance_to_target_m,
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
                            "manipulation.final_object_to_target_distance_m": round(
                                next_observation.distance_to_target_m,
                                6,
                            ),
                        },
                    )
                    trajectory_entries.append(
                        _build_pick_place_trajectory_entry(
                            step_index=step_index,
                            observation=next_observation,
                            phase_name=phase_name,
                            tool_name=parsed_action.tool_name,
                            gripper_moved_distance_m=gripper_moved_distance_m,
                            object_moved_distance_m=object_moved_distance_m,
                        )
                    )
                    observation = next_observation
                    runtime_step_count = step_index
                    step_completed = True

                if step_invalid:
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

            elapsed_time_sec = round(time.perf_counter() - start_time, 6)
            final_observation = environment.observe()
            success = termination_reason == TerminationReason.SUCCESS
            result = EpisodeResult(
                run_id=run_id,
                task_type=config.task_type,
                task_id=config.task_id,
                scene_id=config.scene_id,
                robot_id=config.robot_id,
                seed=config.seed,
                success=success,
                termination_reason=termination_reason or TerminationReason.UNKNOWN,
                step_count=runtime_step_count,
                elapsed_time_sec=elapsed_time_sec,
                sim_time_sec=final_observation.sim_time_sec,
                invalid_action_count=invalid_action_count,
                collision_count=0,
                recovery_count=retry_count,
                tool_call_count=tool_call_count,
                planner_call_count=planner_call_count,
                token_usage=token_usage,
                planner_latency_sec=planner_latency_sec,
                notes=notes,
                metrics={
                    "manipulation.grasp_completed": environment.grasp_completed,
                    "manipulation.object_placed": success,
                    "manipulation.final_object_to_target_distance_m": round(
                        final_observation.distance_to_target_m,
                        6,
                    ),
                    "manipulation.gripper_path_length_m": round(
                        compute_pose_path_length(environment.gripper_path),
                        6,
                    ),
                    "manipulation.object_path_length_m": round(
                        compute_pose_path_length(environment.object_path),
                        6,
                    ),
                    "manipulation.backend": backend,
                    "manipulation.stage_artifact_written": hasattr(environment, "stage_artifact_text"),
                    "manipulation.scripted_phase_count": len(environment.scripted_actions),
                    "manipulation.runtime_policy": session.policy_name,
                    "manipulation.runtime_variant": runtime_variant,
                    "manipulation.planner_backend": session.planner_backend,
                    "prompt_variant": prompt_variant,
                    "runtime.retry_count": retry_count,
                    "runtime.validation_enabled": validation_enabled,
                    "runtime.max_validation_retries": max_validation_retries,
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
                    "manipulation.final_object_to_target_distance_m": result.metrics[
                        "manipulation.final_object_to_target_distance_m"
                    ],
                    "manipulation.object_path_length_m": result.metrics[
                        "manipulation.object_path_length_m"
                    ],
                },
            )

            trajectory: dict[str, Any] = {
                "run_id": run_id,
                "task_id": config.task_id,
                "scene_id": config.scene_id,
                "backend": backend,
                "planner_backend": session.planner_backend,
                "available_tools": self.tool_registry.names_for_task(config.task_type),
                "tool_name": SCRIPTED_PICKPLACE_TOOL.name,
                "scripted_sequence": [action.phase_name for action in environment.scripted_actions],
                "states": trajectory_entries,
            }
            if stage_settings is not None:
                trajectory["isaac"] = stage_settings
            if environment.runtime_details:
                trajectory["runtime"] = environment.runtime_details

            text_artifacts: dict[str, str] = {}
            if hasattr(environment, "stage_artifact_text"):
                text_artifacts["stage.usda"] = environment.stage_artifact_text()

            return AgentRunData(
                config=config,
                manifest=manifest,
                result=result,
                events=events,
                trajectory=trajectory,
                planner_trace=planner_trace,
                tool_trace=tool_trace,
                text_artifacts=text_artifacts,
            )
        finally:
            environment.close()

    def _validate_pick_place_action(
        self,
        action: PlannerAction,
        config: TaskConfig,
        next_phase: str,
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

        if action.tool_name in {"get_gripper_state", "get_object_state", "get_target_state"}:
            return None

        if action.tool_name == SCRIPTED_PICKPLACE_TOOL.name:
            phase_name = action.arguments.get("phase_name")
            if not isinstance(phase_name, str) or not phase_name:
                return "tool 'scripted_pick_place_step' requires a non-empty phase_name"
            if phase_name != next_phase:
                return (
                    "tool 'scripted_pick_place_step' must target the next scripted phase in M4 runtime v0; "
                    f"planner proposed '{phase_name}' while next phase is '{next_phase}'"
                )
            return None

        return f"tool '{action.tool_name}' is not implemented by M4 runtime v0"

    def _dispatch_pick_place_action(
        self,
        action: PlannerAction,
        observation: PickPlaceObservation,
        environment: BasePickPlaceEnvironment,
        config: TaskConfig,
    ) -> tuple[dict[str, Any], PickPlaceObservation, bool, str, float, float]:
        if action.tool_name == "get_gripper_state":
            return (
                {
                    "tool_name": action.tool_name,
                    "gripper_state": {
                        "pose": observation.gripper_pose.to_dict(),
                        "gripper_open": observation.gripper_open,
                        "object_attached": observation.object_attached,
                    },
                },
                observation,
                False,
                observation.current_phase,
                0.0,
                0.0,
            )

        if action.tool_name == "get_object_state":
            return (
                {
                    "tool_name": action.tool_name,
                    "object_state": {
                        "pose": observation.object_pose.to_dict(),
                        "distance_to_target_m": round(observation.distance_to_target_m, 6),
                        "object_attached": observation.object_attached,
                    },
                },
                observation,
                False,
                observation.current_phase,
                0.0,
                0.0,
            )

        if action.tool_name == "get_target_state":
            return (
                {
                    "tool_name": action.tool_name,
                    "target_state": config.pick_place.target_pose if config.pick_place is not None else None,
                    "distance_to_target_m": round(observation.distance_to_target_m, 6),
                },
                observation,
                False,
                observation.current_phase,
                0.0,
                0.0,
            )

        if action.tool_name == SCRIPTED_PICKPLACE_TOOL.name:
            step_result: PickPlaceStepResult = environment.step_scripted()
            return (
                {
                    "tool_name": action.tool_name,
                    "executor": SCRIPTED_PICKPLACE_TOOL.name,
                    "phase_name": step_result.action.phase_name,
                    "applied_action": step_result.action.to_dict(),
                    "observation": step_result.observation.to_dict(),
                    "gripper_moved_distance_m": round(step_result.gripper_moved_distance_m, 6),
                    "object_moved_distance_m": round(step_result.object_moved_distance_m, 6),
                },
                step_result.observation,
                True,
                step_result.action.phase_name,
                step_result.gripper_moved_distance_m,
                step_result.object_moved_distance_m,
            )

        raise ValueError(f"unsupported tool dispatch: {action.tool_name}")

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
    metrics: dict[str, Any]
    trajectory_key = "poses"
    try:
        if config.task_type == TaskType.PICK_PLACE:
            backend = _manipulation_backend_from_config(config)
            definition = _manipulation_definition_from_config(config)
            metrics = {
                "manipulation.grasp_completed": False,
                "manipulation.object_placed": False,
                "manipulation.final_object_to_target_distance_m": round(
                    distance_between_poses_3d(definition.object_start_pose, definition.target_pose),
                    6,
                ),
                "manipulation.gripper_path_length_m": 0.0,
                "manipulation.object_path_length_m": 0.0,
                "manipulation.backend": backend,
                "manipulation.stage_artifact_written": False,
                "manipulation.scripted_phase_count": 0,
                "manipulation.runtime_policy": _runtime_policy_name(config),
                "manipulation.runtime_variant": _runtime_variant(config),
                "manipulation.planner_backend": planner_backend,
                "prompt_variant": _prompt_variant(config),
                "runtime.retry_count": 0,
                "runtime.validation_enabled": bool(config.runtime_options.tool_validation_enabled),
                "runtime.max_validation_retries": 0,
            }
            trajectory_key = "states"
        else:
            definition = _navigation_definition_from_config(config)
            backend = _navigation_backend_from_config(config)
            metrics = {
                "navigation.goal_reached": False,
                "navigation.final_goal_distance_m": round(
                    distance_between_poses(definition.start_pose, definition.goal_pose),
                    6,
                ),
                "navigation.path_length_m": 0.0,
                "navigation.waypoints_completed": len(config.navigation.waypoint_refs) if config.navigation else 0,
                "navigation.backend": backend,
                "navigation.motion_step_count": 0,
                "navigation.stage_artifact_written": False,
                "navigation.runtime_policy": _runtime_policy_name(config),
                "navigation.runtime_variant": _runtime_variant(config),
                "navigation.planner_backend": planner_backend,
                "prompt_variant": _prompt_variant(config),
                "runtime.retry_count": 0,
                "runtime.validation_enabled": bool(config.runtime_options.tool_validation_enabled),
                "runtime.max_validation_retries": 0,
            }
    except Exception:
        if config.task_type == TaskType.PICK_PLACE:
            metrics = {
                "manipulation.grasp_completed": False,
                "manipulation.object_placed": False,
                "manipulation.final_object_to_target_distance_m": None,
                "manipulation.gripper_path_length_m": 0.0,
                "manipulation.object_path_length_m": 0.0,
                "manipulation.backend": backend,
                "manipulation.stage_artifact_written": False,
                "manipulation.scripted_phase_count": 0,
                "manipulation.runtime_policy": _runtime_policy_name(config),
                "manipulation.runtime_variant": _runtime_variant(config),
                "manipulation.planner_backend": planner_backend,
                "prompt_variant": _prompt_variant(config),
                "runtime.retry_count": 0,
                "runtime.validation_enabled": bool(config.runtime_options.tool_validation_enabled),
                "runtime.max_validation_retries": 0,
            }
            trajectory_key = "states"
        else:
            metrics = {
                "navigation.goal_reached": False,
                "navigation.final_goal_distance_m": None,
                "navigation.path_length_m": 0.0,
                "navigation.waypoints_completed": len(config.navigation.waypoint_refs) if config.navigation else 0,
                "navigation.backend": backend,
                "navigation.motion_step_count": 0,
                "navigation.stage_artifact_written": False,
                "navigation.runtime_policy": _runtime_policy_name(config),
                "navigation.runtime_variant": _runtime_variant(config),
                "navigation.planner_backend": planner_backend,
                "prompt_variant": _prompt_variant(config),
                "runtime.retry_count": 0,
                "runtime.validation_enabled": bool(config.runtime_options.tool_validation_enabled),
                "runtime.max_validation_retries": 0,
            }

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
        metrics=metrics,
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
            trajectory_key: [],
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
    prepared_config.runtime_options.collect_events = True
    prepared_config.runtime_options.extra_options["planner_backend"] = planner_backend.backend_name
    if runtime.runtime_config.policy_name:
        prepared_config.runtime_options.extra_options["runtime_policy"] = runtime.runtime_config.policy_name
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
        metadata=_manifest_metadata(
            config=prepared_config,
            planner_backend=planner_backend.backend_name,
        ),
    )
    layout = RunArtifactsLayout(run_id=run_id, results_root=results_root)
    if layout.run_dir.exists() and any(layout.run_dir.iterdir()):
        raise FileExistsError(f"run directory already exists and is not empty: {layout.run_dir}")

    layout.ensure()
    write_run_manifest(layout.manifest_path, manifest)
    write_task_config(layout.task_config_path, prepared_config)

    try:
        run_data = runtime.execute(config=prepared_config, run_id=run_id)
    except (NavigationBackendUnavailableError, ManipulationBackendUnavailableError) as exc:
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
