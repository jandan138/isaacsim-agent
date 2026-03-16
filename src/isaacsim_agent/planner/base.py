"""Planner placeholders for future embodied-agent runtime work."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlannerConfig:
    """Minimal planner configuration scaffold.

    This class exists only to establish a stable import surface for later
    milestone work on structured planning, prompting, and tool calls.
    """

    backend: str = "placeholder"
    output_mode: str = "structured"
