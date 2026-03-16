"""Memory placeholders for future long-horizon runtime experiments."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryRecord:
    """Minimal memory record scaffold for later episodic storage work."""

    key: str
    value: str
    source: str = "placeholder"
