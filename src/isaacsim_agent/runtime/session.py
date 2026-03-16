"""Runtime placeholders for agent execution policies and orchestration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeSession:
    """Minimal runtime session metadata scaffold."""

    session_id: str
    policy_name: str = "placeholder"
