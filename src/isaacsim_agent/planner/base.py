"""Typed planner abstractions for the minimal M4 structured-action runtime."""

from __future__ import annotations

import json
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from isaacsim_agent.contracts import JsonValue
from isaacsim_agent.contracts import TaskType
from isaacsim_agent.contracts import TokenUsage


def estimate_token_count(text: str) -> int:
    """Return a deterministic rough token estimate without external deps."""

    stripped = text.strip()
    if not stripped:
        return 0
    return max(1, len(stripped) // 4)


class PlannerResponseError(ValueError):
    """Raised when a planner response cannot be parsed into a structured action."""


@dataclass(frozen=True)
class PlannerConfig:
    """Minimal planner configuration reused by the M4 runtime."""

    backend: str = "mock"
    model_name: str = "mock-rule-based-v0"
    output_mode: str = "json"


@dataclass(frozen=True)
class PlannerAction:
    """One planner-emitted structured tool call."""

    tool_name: str
    arguments: dict[str, JsonValue] = field(default_factory=dict)

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PlannerAction":
        tool_name = payload.get("tool_name")
        arguments = payload.get("arguments", {})
        if not isinstance(tool_name, str) or not tool_name:
            raise PlannerResponseError("planner action must include a non-empty string tool_name")
        if not isinstance(arguments, dict):
            raise PlannerResponseError("planner action arguments must be a JSON object")
        return cls(tool_name=tool_name, arguments=arguments)


@dataclass(frozen=True)
class PlannerRequest:
    """Structured planner input built from task config and runtime state."""

    task_type: TaskType
    instruction: str
    step_index: int
    available_tools: list[dict[str, JsonValue]]
    state: dict[str, JsonValue]
    last_tool_result: dict[str, JsonValue] | None = None
    tool_history: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, JsonValue]:
        payload: dict[str, JsonValue] = {
            "task_type": self.task_type.value,
            "instruction": self.instruction,
            "step_index": self.step_index,
            "available_tools": self.available_tools,
            "state": self.state,
            "tool_history": self.tool_history,
        }
        if self.last_tool_result is not None:
            payload["last_tool_result"] = self.last_tool_result
        return payload


@dataclass(frozen=True)
class PlannerRawResponse:
    """Raw model output before structured-action parsing."""

    raw_response: str
    token_usage: TokenUsage = field(default_factory=TokenUsage)


class PlannerBackend(ABC):
    """Abstract planner backend used by the minimal runtime."""

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Human-readable backend identifier."""

    @abstractmethod
    def plan(self, request: PlannerRequest) -> PlannerRawResponse:
        """Return one raw JSON response for the supplied planner request."""


def parse_planner_action(raw_response: str) -> PlannerAction:
    """Parse one JSON planner response into a typed action."""

    try:
        payload = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise PlannerResponseError(f"planner response is not valid JSON: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise PlannerResponseError("planner response must be a JSON object")
    return PlannerAction.from_dict(payload)
