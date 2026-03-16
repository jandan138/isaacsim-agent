"""Mock planner backends for deterministic M4 validation and smoke tests."""

from __future__ import annotations

import json
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from isaacsim_agent.agent import normalize_prompt_variant
from isaacsim_agent.contracts import TaskType
from isaacsim_agent.contracts import TokenUsage

from .base import PlannerAction
from .base import PlannerBackend
from .base import PlannerRawResponse
from .base import PlannerRequest
from .base import estimate_token_count


def _token_usage_for_request(request: PlannerRequest, raw_response: str) -> TokenUsage:
    request_json = json.dumps(request.to_dict(), sort_keys=True)
    return TokenUsage(
        prompt_tokens=estimate_token_count(request_json),
        completion_tokens=estimate_token_count(raw_response),
    )


@dataclass
class MockPlannerBackend(PlannerBackend):
    """Small rule-based backend that mimics an LLM returning JSON actions."""

    planner_name: str = "mock_rule_based"

    @property
    def backend_name(self) -> str:
        return self.planner_name

    def plan(self, request: PlannerRequest) -> PlannerRawResponse:
        if request.task_type != TaskType.NAVIGATION:
            raise ValueError(f"{self.backend_name} only supports navigation tasks in M4")

        goal_pose = request.state.get("goal_pose")
        if "get_robot_state" not in request.tool_history:
            action = PlannerAction(tool_name="get_robot_state")
        elif "get_goal_state" not in request.tool_history:
            action = PlannerAction(tool_name="get_goal_state")
        else:
            if not isinstance(goal_pose, dict):
                raise ValueError("mock planner requires state.goal_pose")
            action = PlannerAction(tool_name="navigate_to", arguments={"target_pose": goal_pose})
        raw_response = json.dumps(action.to_dict(), sort_keys=True)
        return PlannerRawResponse(
            raw_response=raw_response,
            token_usage=_token_usage_for_request(request=request, raw_response=raw_response),
        )


@dataclass
class BlockAPilotPlannerBackend(PlannerBackend):
    """Prompt-sensitive backend used only by the minimal block A pilot."""

    planner_name: str = "mock_block_a"

    @property
    def backend_name(self) -> str:
        return self.planner_name

    def plan(self, request: PlannerRequest) -> PlannerRawResponse:
        if request.task_type != TaskType.NAVIGATION:
            raise ValueError(f"{self.backend_name} only supports navigation tasks in block A")

        goal_pose = request.state.get("goal_pose")
        if not isinstance(goal_pose, dict):
            raise ValueError("block A planner requires state.goal_pose")

        prompt_variant = normalize_prompt_variant(request.prompt_variant)
        if prompt_variant == "P0":
            if request.retry_index == 0 and not request.tool_history:
                payload = {"tool_name": "move_to_goal", "arguments": {}}
            else:
                payload = {"tool_name": "navigate_to", "arguments": {"target_pose": goal_pose}}
            raw_response = json.dumps(payload, sort_keys=True)
            return PlannerRawResponse(
                raw_response=raw_response,
                token_usage=_token_usage_for_request(request=request, raw_response=raw_response),
            )

        if prompt_variant == "P2":
            if "get_robot_state" not in request.tool_history:
                payload = {
                    "tool_name": "get_robot_state",
                    "arguments": {},
                    "self_check": "tool exists and requires no arguments",
                }
            else:
                payload = {
                    "tool_name": "navigate_to",
                    "arguments": {"target_pose": goal_pose},
                    "self_check": "target_pose matches the configured goal pose",
                }
            raw_response = json.dumps(payload, sort_keys=True)
            return PlannerRawResponse(
                raw_response=raw_response,
                token_usage=_token_usage_for_request(request=request, raw_response=raw_response),
            )

        if "get_robot_state" not in request.tool_history:
            action = PlannerAction(tool_name="get_robot_state")
        elif "get_goal_state" not in request.tool_history:
            action = PlannerAction(tool_name="get_goal_state")
        else:
            action = PlannerAction(tool_name="navigate_to", arguments={"target_pose": goal_pose})
        raw_response = json.dumps(action.to_dict(), sort_keys=True)
        return PlannerRawResponse(
            raw_response=raw_response,
            token_usage=_token_usage_for_request(request=request, raw_response=raw_response),
        )


@dataclass
class SequencePlannerBackend(PlannerBackend):
    """Deterministic backend used by tests to inject fixed planner responses."""

    responses: list[str | dict[str, Any] | PlannerAction] = field(default_factory=list)
    planner_name: str = "mock_sequence"
    _cursor: int = 0

    @property
    def backend_name(self) -> str:
        return self.planner_name

    def plan(self, request: PlannerRequest) -> PlannerRawResponse:
        if self._cursor >= len(self.responses):
            raise ValueError("sequence planner exhausted all configured responses")

        raw_item = self.responses[self._cursor]
        self._cursor += 1
        if isinstance(raw_item, PlannerAction):
            raw_response = json.dumps(raw_item.to_dict(), sort_keys=True)
        elif isinstance(raw_item, dict):
            raw_response = json.dumps(raw_item, sort_keys=True)
        elif isinstance(raw_item, str):
            raw_response = raw_item
        else:
            raise TypeError(f"unsupported sequence planner response type: {type(raw_item)!r}")

        return PlannerRawResponse(
            raw_response=raw_response,
            token_usage=_token_usage_for_request(request=request, raw_response=raw_response),
        )
