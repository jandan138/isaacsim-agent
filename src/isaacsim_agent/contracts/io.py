"""Serialization and artifact layout helpers for shared contracts."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import EpisodeResult
from .models import EventRecord
from .models import RunManifest
from .models import TaskConfig


class RunArtifactsLayout:
    """Canonical output layout for a single run."""

    def __init__(self, run_id: str, results_root: str | Path = "results") -> None:
        self.run_id = run_id
        self.results_root = Path(results_root)

    @property
    def run_dir(self) -> Path:
        return self.results_root / "runs" / self.run_id

    @property
    def manifest_path(self) -> Path:
        return self.run_dir / "manifest.json"

    @property
    def task_config_path(self) -> Path:
        return self.run_dir / "task_config.json"

    @property
    def episode_result_path(self) -> Path:
        return self.run_dir / "episode_result.json"

    @property
    def event_log_path(self) -> Path:
        return self.run_dir / "events.jsonl"

    @property
    def artifacts_dir(self) -> Path:
        return self.run_dir / "artifacts"

    def ensure(self) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_task_config(path: str | Path, config: TaskConfig) -> None:
    _write_json(Path(path), config.to_dict())


def read_task_config(path: str | Path) -> TaskConfig:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return TaskConfig.from_dict(payload)


def write_episode_result(path: str | Path, result: EpisodeResult) -> None:
    _write_json(Path(path), result.to_dict())


def write_run_manifest(path: str | Path, manifest: RunManifest) -> None:
    _write_json(Path(path), manifest.to_dict())


def write_event_log(path: str | Path, events: list[EventRecord]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(asdict(event)) + "\n")
