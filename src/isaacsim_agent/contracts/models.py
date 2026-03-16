"""Typed contract dataclasses for tasks, results, events, and manifests."""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any

from .enums import DifficultyLevel
from .enums import EventType
from .enums import TaskType
from .enums import TerminationReason


JsonValue = str | int | float | bool | None | dict[str, Any] | list[Any]


def _utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


@dataclass
class RuntimeOptions:
    planner_enabled: bool = False
    memory_enabled: bool = False
    tool_validation_enabled: bool = True
    recovery_enabled: bool = True
    collect_events: bool = True
    planner_timeout_sec: float | None = None
    planner_token_budget: int | None = None
    extra_options: dict[str, JsonValue] = field(default_factory=dict)


@dataclass
class NavigationSpec:
    goal_ref: str | None = None
    waypoint_refs: list[str] = field(default_factory=list)
    success_radius_m: float = 0.5
    goal_pose: dict[str, float] | None = None


@dataclass
class PickPlaceSpec:
    object_id: str | None = None
    source_id: str | None = None
    target_id: str | None = None
    target_pose: dict[str, float] | None = None


@dataclass
class InstructionFollowingSpec:
    instruction: str = ""
    expected_outcomes: list[str] = field(default_factory=list)
    constraint_refs: list[str] = field(default_factory=list)


@dataclass
class TaskConfig:
    task_type: TaskType
    task_id: str
    scene_id: str
    robot_id: str
    seed: int
    max_steps: int
    max_time_sec: float
    headless: bool
    render: bool
    difficulty: DifficultyLevel
    runtime_options: RuntimeOptions = field(default_factory=RuntimeOptions)
    description: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, JsonValue] = field(default_factory=dict)
    navigation: NavigationSpec | None = None
    pick_place: PickPlaceSpec | None = None
    instruction_following: InstructionFollowingSpec | None = None

    def __post_init__(self) -> None:
        if self.task_type == TaskType.NAVIGATION and self.navigation is None:
            raise ValueError("navigation task requires navigation spec")
        if self.task_type == TaskType.PICK_PLACE and self.pick_place is None:
            raise ValueError("pick_place task requires pick_place spec")
        if self.task_type == TaskType.INSTRUCTION_FOLLOWING and self.instruction_following is None:
            raise ValueError("instruction_following task requires instruction_following spec")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaskConfig":
        runtime_options = RuntimeOptions(**payload.get("runtime_options", {}))
        navigation = None
        pick_place = None
        instruction_following = None

        if payload.get("navigation") is not None:
            navigation = NavigationSpec(**payload["navigation"])
        if payload.get("pick_place") is not None:
            pick_place = PickPlaceSpec(**payload["pick_place"])
        if payload.get("instruction_following") is not None:
            instruction_following = InstructionFollowingSpec(**payload["instruction_following"])

        return cls(
            task_type=TaskType(payload["task_type"]),
            task_id=payload["task_id"],
            scene_id=payload["scene_id"],
            robot_id=payload["robot_id"],
            seed=payload["seed"],
            max_steps=payload["max_steps"],
            max_time_sec=payload["max_time_sec"],
            headless=payload["headless"],
            render=payload["render"],
            difficulty=DifficultyLevel(payload["difficulty"]),
            runtime_options=runtime_options,
            description=payload.get("description", ""),
            tags=payload.get("tags", []),
            metadata=payload.get("metadata", {}),
            navigation=navigation,
            pick_place=pick_place,
            instruction_following=instruction_following,
        )


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float | None = None

    def __post_init__(self) -> None:
        if self.total_tokens == 0:
            self.total_tokens = self.prompt_tokens + self.completion_tokens


@dataclass
class EpisodeResult:
    run_id: str
    task_type: TaskType
    task_id: str
    scene_id: str
    robot_id: str
    seed: int
    success: bool
    termination_reason: TerminationReason
    step_count: int
    elapsed_time_sec: float
    sim_time_sec: float
    invalid_action_count: int
    collision_count: int
    recovery_count: int
    tool_call_count: int
    planner_call_count: int
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    planner_latency_sec: float = 0.0
    notes: list[str] = field(default_factory=list)
    metrics: dict[str, JsonValue] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EventRecord:
    run_id: str
    event_index: int
    event_type: EventType
    step_index: int
    task_type: TaskType
    task_id: str
    scene_id: str
    robot_id: str
    seed: int
    timestamp_utc: str = field(default_factory=_utc_now)
    sim_time_sec: float = 0.0
    action_ref: str | None = None
    tool_name: str | None = None
    planner_latency_sec: float | None = None
    success: bool | None = None
    payload: dict[str, JsonValue] = field(default_factory=dict)
    metrics: dict[str, JsonValue] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunManifest:
    run_id: str
    task_type: TaskType
    task_id: str
    scene_id: str
    robot_id: str
    seed: int
    metadata: dict[str, JsonValue] = field(default_factory=dict)
    schema_version: str = "v1"
    created_at_utc: str = field(default_factory=_utc_now)
    artifact_convention: str = "results/runs/<run_id>/"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
