"""Typed tool registry helpers for minimal agent-runtime tool dispatch."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from isaacsim_agent.contracts import TaskType


@dataclass(frozen=True)
class ToolSpec:
    """Description of a planner-callable tool."""

    name: str
    description: str
    allowed_task_types: tuple[TaskType, ...] = ()
    required_arguments: tuple[str, ...] = ()

    def supports_task(self, task_type: TaskType) -> bool:
        if not self.allowed_task_types:
            return True
        return task_type in self.allowed_task_types


class ToolRegistry:
    """Minimal immutable-feeling registry used by the M4 runtime."""

    def __init__(self, tool_specs: Iterable[ToolSpec] = ()) -> None:
        self._tool_specs: dict[str, ToolSpec] = {}
        for tool_spec in tool_specs:
            self.register(tool_spec)

    def register(self, tool_spec: ToolSpec) -> None:
        if tool_spec.name in self._tool_specs:
            raise ValueError(f"duplicate tool registration: {tool_spec.name}")
        self._tool_specs[tool_spec.name] = tool_spec

    def get(self, name: str) -> ToolSpec | None:
        return self._tool_specs.get(name)

    def require(self, name: str) -> ToolSpec:
        tool_spec = self.get(name)
        if tool_spec is None:
            raise KeyError(f"unknown tool: {name}")
        return tool_spec

    def names_for_task(self, task_type: TaskType) -> list[str]:
        return [
            tool_spec.name
            for tool_spec in self._tool_specs.values()
            if tool_spec.supports_task(task_type)
        ]

    def specs_for_task(self, task_type: TaskType) -> list[ToolSpec]:
        return [
            tool_spec
            for tool_spec in self._tool_specs.values()
            if tool_spec.supports_task(task_type)
        ]


def build_navigation_tool_registry() -> ToolRegistry:
    """Return the minimal navigation tool surface for agent runtime v0."""

    return ToolRegistry(
        [
            ToolSpec(
                name="get_robot_state",
                description="Return the current robot pose and navigation observation.",
                allowed_task_types=(TaskType.NAVIGATION,),
            ),
            ToolSpec(
                name="get_goal_state",
                description="Return the configured navigation goal pose and success radius.",
                allowed_task_types=(TaskType.NAVIGATION,),
            ),
            ToolSpec(
                name="navigate_to",
                description="Advance one deterministic navigation step toward the configured goal.",
                allowed_task_types=(TaskType.NAVIGATION,),
                required_arguments=("target_pose",),
            ),
        ]
    )


def build_manipulation_tool_registry() -> ToolRegistry:
    """Return the minimal pick-and-place tool surface for agent runtime v0."""

    return ToolRegistry(
        [
            ToolSpec(
                name="get_gripper_state",
                description="Return the current gripper pose and open/closed state.",
                allowed_task_types=(TaskType.PICK_PLACE,),
            ),
            ToolSpec(
                name="get_object_state",
                description="Return the current object pose and attachment state.",
                allowed_task_types=(TaskType.PICK_PLACE,),
            ),
            ToolSpec(
                name="get_target_state",
                description="Return the configured pick-and-place target pose and tolerances.",
                allowed_task_types=(TaskType.PICK_PLACE,),
            ),
            ToolSpec(
                name="scripted_pick_place_step",
                description="Advance one scripted pick-and-place phase for the current task.",
                allowed_task_types=(TaskType.PICK_PLACE,),
                required_arguments=("phase_name",),
            ),
        ]
    )


def build_agent_v0_tool_registry() -> ToolRegistry:
    """Return the combined M4 runtime tool registry across supported task families."""

    return ToolRegistry(
        [
            *build_navigation_tool_registry().specs_for_task(TaskType.NAVIGATION),
            *build_manipulation_tool_registry().specs_for_task(TaskType.PICK_PLACE),
        ]
    )
