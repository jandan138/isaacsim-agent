"""Load canonical run artifacts for the minimal M5 eval harness."""

from __future__ import annotations

import json
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any


REQUIRED_RUN_FILES = (
    "manifest.json",
    "task_config.json",
    "episode_result.json",
    "events.jsonl",
)

_AGENT_RUNTIME_ARTIFACTS = (
    "artifacts/trajectory.json",
    "artifacts/planner_trace.json",
    "artifacts/tool_trace.json",
)


@dataclass
class RunFileStatus:
    """Load status for one required contract file."""

    relative_path: str
    path: Path
    exists: bool = False
    parsed: bool = False
    error: str | None = None


@dataclass
class RunRecord:
    """Loaded run payloads plus file-status metadata."""

    run_id: str
    run_dir: Path
    files: dict[str, RunFileStatus]
    manifest: dict[str, Any] | None = None
    task_config: dict[str, Any] | None = None
    episode_result: dict[str, Any] | None = None
    events: list[dict[str, Any]] | None = None
    discovered_artifacts: list[str] = field(default_factory=list)
    referenced_artifacts: list[str] = field(default_factory=list)


def resolve_runs_root(results_root: str | Path) -> Path:
    """Resolve either a results root or a direct `runs/` directory."""

    candidate = Path(results_root)
    if (candidate / "runs").is_dir():
        return candidate / "runs"
    return candidate


def scan_results_root(results_root: str | Path) -> list[RunRecord]:
    """Load every run directory under the resolved results root."""

    runs_root = resolve_runs_root(results_root)
    if not runs_root.exists():
        return []
    return [load_run_record(run_dir) for run_dir in sorted(path for path in runs_root.iterdir() if path.is_dir())]


def load_run_record(run_dir: str | Path) -> RunRecord:
    """Load one run directory without enforcing schema completeness."""

    run_dir = Path(run_dir)
    if not run_dir.is_dir():
        raise ValueError(f"run directory does not exist: {run_dir}")

    file_status = {
        relative_path: RunFileStatus(
            relative_path=relative_path,
            path=run_dir / relative_path,
            exists=(run_dir / relative_path).is_file(),
        )
        for relative_path in REQUIRED_RUN_FILES
    }
    record = RunRecord(
        run_id=run_dir.name,
        run_dir=run_dir,
        files=file_status,
    )

    for relative_path, status in file_status.items():
        if not status.exists:
            continue
        try:
            if relative_path == "events.jsonl":
                payload = _load_jsonl(status.path)
                record.events = payload
            else:
                payload = _load_json_object(status.path)
                if relative_path == "manifest.json":
                    record.manifest = payload
                elif relative_path == "task_config.json":
                    record.task_config = payload
                elif relative_path == "episode_result.json":
                    record.episode_result = payload
            status.parsed = True
        except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
            status.error = f"{type(exc).__name__}: {exc}"

    record.discovered_artifacts = _discover_artifacts(run_dir)
    record.referenced_artifacts = _collect_expected_artifacts(record.task_config)
    return record


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"expected JSON object on line {line_number} in {path}")
            records.append(payload)
    return records


def _discover_artifacts(run_dir: Path) -> list[str]:
    artifacts_dir = run_dir / "artifacts"
    if not artifacts_dir.is_dir():
        return []
    return sorted(path.relative_to(run_dir).as_posix() for path in artifacts_dir.rglob("*") if path.is_file())


def _collect_expected_artifacts(task_config: dict[str, Any] | None) -> list[str]:
    if not isinstance(task_config, dict):
        return []

    refs: set[str] = set()
    metadata = task_config.get("metadata")
    _collect_artifact_refs_from_payload(metadata, refs)

    if isinstance(metadata, dict) and "agent_runtime_v0" in metadata:
        refs.update(_AGENT_RUNTIME_ARTIFACTS)

    return sorted(refs)


def _collect_artifact_refs_from_payload(payload: Any, refs: set[str]) -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "artifacts" and isinstance(value, dict):
                for artifact_path in value.values():
                    normalized = _normalize_artifact_ref(artifact_path)
                    if normalized is not None:
                        refs.add(normalized)
            else:
                _collect_artifact_refs_from_payload(value, refs)
        return

    if isinstance(payload, list):
        for item in payload:
            _collect_artifact_refs_from_payload(item, refs)


def _normalize_artifact_ref(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return Path(normalized).as_posix()
