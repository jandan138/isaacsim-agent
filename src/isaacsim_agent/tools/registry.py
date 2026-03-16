"""Tool registry placeholders for future simulator and agent actions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolSpec:
    """Minimal tool description scaffold."""

    name: str
    description: str
