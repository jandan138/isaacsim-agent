"""Enumerations shared across future task families and runtime layers."""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """String enum base for stable JSON serialization."""


class TaskType(StrEnum):
    NAVIGATION = "navigation"
    PICK_PLACE = "pick_place"
    INSTRUCTION_FOLLOWING = "instruction_following"


class DifficultyLevel(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TerminationReason(StrEnum):
    SUCCESS = "success"
    MAX_STEPS = "max_steps"
    TIMEOUT = "timeout"
    COLLISION_LIMIT = "collision_limit"
    INVALID_ACTION_LIMIT = "invalid_action_limit"
    PLANNER_FAILURE = "planner_failure"
    TOOL_FAILURE = "tool_failure"
    RECOVERY_FAILURE = "recovery_failure"
    ROBOT_STUCK = "robot_stuck"
    TASK_PRECONDITION_FAILED = "task_precondition_failed"
    SCENE_LOAD_FAILURE = "scene_load_failure"
    RUNTIME_ERROR = "runtime_error"
    USER_ABORT = "user_abort"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class EventType(StrEnum):
    EPISODE_START = "episode_start"
    STEP_START = "step_start"
    OBSERVATION = "observation"
    PLANNER_CALL = "planner_call"
    PLANNER_RESPONSE = "planner_response"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ACTION_APPLIED = "action_applied"
    COLLISION = "collision"
    RECOVERY = "recovery"
    VALIDATION_WARNING = "validation_warning"
    STEP_END = "step_end"
    EPISODE_END = "episode_end"
