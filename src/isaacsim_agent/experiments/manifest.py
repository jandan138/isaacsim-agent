"""Experiment placeholders for future ablation and evaluation configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExperimentManifest:
    """Minimal experiment manifest scaffold."""

    name: str
    task_family: str
    seed: int = 0
