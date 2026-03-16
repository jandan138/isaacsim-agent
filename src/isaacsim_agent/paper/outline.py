"""Paper-planning placeholders for manuscript structure tracking."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PaperSection:
    """Minimal paper section scaffold."""

    title: str
    status: str = "placeholder"
