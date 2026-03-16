"""Validate loaded run artifacts for completeness and contract conformance."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from isaacsim_agent.contracts import EventType

from .loader import REQUIRED_RUN_FILES
from .loader import RunRecord
from .loader import scan_results_root


_CONTRACT_BLOCKING_CODES = {
    "missing_file",
    "json_parse_error",
    "schema_field_missing",
    "schema_type_error",
    "field_mismatch",
}

_COMPLETENESS_BLOCKING_CODES = _CONTRACT_BLOCKING_CODES | {
    "partial_run",
    "missing_artifact",
}

_MANIFEST_REQUIRED_FIELDS = (
    "run_id",
    "task_type",
    "task_id",
    "scene_id",
    "robot_id",
    "seed",
)

_TASK_CONFIG_REQUIRED_FIELDS = (
    "task_type",
    "task_id",
    "scene_id",
    "robot_id",
    "seed",
    "max_steps",
    "max_time_sec",
    "runtime_options",
    "metadata",
)

_EPISODE_RESULT_REQUIRED_FIELDS = (
    "run_id",
    "task_type",
    "task_id",
    "scene_id",
    "robot_id",
    "seed",
    "success",
    "termination_reason",
    "step_count",
    "elapsed_time_sec",
    "sim_time_sec",
    "invalid_action_count",
    "tool_call_count",
    "planner_call_count",
    "metrics",
)

_EVENT_REQUIRED_FIELDS = (
    "run_id",
    "event_index",
    "event_type",
    "step_index",
)


@dataclass(frozen=True)
class ValidationIssue:
    """One explicit validation failure or warning."""

    code: str
    message: str
    severity: str = "error"
    relative_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "relative_path": self.relative_path,
        }


@dataclass(frozen=True)
class RunValidation:
    """Computed validation status for one run."""

    run_id: str
    run_dir: Path
    required_files_present: bool
    parsed_files_ok: bool
    event_count: int
    has_episode_end: bool
    expected_artifact_count: int
    missing_artifacts: list[str]
    contract_complete: bool
    run_complete: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def issue_codes(self) -> list[str]:
        return [issue.code for issue in self.issues]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "run_dir": str(self.run_dir),
            "required_files_present": self.required_files_present,
            "parsed_files_ok": self.parsed_files_ok,
            "event_count": self.event_count,
            "has_episode_end": self.has_episode_end,
            "expected_artifact_count": self.expected_artifact_count,
            "missing_artifacts": list(self.missing_artifacts),
            "contract_complete": self.contract_complete,
            "run_complete": self.run_complete,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def validate_results_root(results_root: str | Path) -> list[RunValidation]:
    """Load and validate every run under a results root."""

    return [validate_run_record(record) for record in scan_results_root(results_root)]


def validate_run_record(record: RunRecord) -> RunValidation:
    """Validate one loaded run record."""

    issues: list[ValidationIssue] = []

    required_files_present = True
    parsed_files_ok = True
    for relative_path in REQUIRED_RUN_FILES:
        status = record.files[relative_path]
        if not status.exists:
            required_files_present = False
            issues.append(
                ValidationIssue(
                    code="missing_file",
                    message=f"required file is missing: {relative_path}",
                    relative_path=relative_path,
                )
            )
            continue
        if not status.parsed:
            parsed_files_ok = False
            issues.append(
                ValidationIssue(
                    code="json_parse_error",
                    message=status.error or f"failed to parse {relative_path}",
                    relative_path=relative_path,
                )
            )

    issues.extend(_validate_payload_fields(record.manifest, _MANIFEST_REQUIRED_FIELDS, "manifest.json"))
    issues.extend(_validate_payload_fields(record.task_config, _TASK_CONFIG_REQUIRED_FIELDS, "task_config.json"))
    issues.extend(
        _validate_payload_fields(
            record.episode_result,
            _EPISODE_RESULT_REQUIRED_FIELDS,
            "episode_result.json",
        )
    )
    issues.extend(_validate_core_types(record.task_config, record.episode_result))
    issues.extend(_validate_identity_consistency(record))

    event_count = len(record.events or [])
    has_episode_end = False
    if record.events is not None:
        for index, event in enumerate(record.events, start=1):
            issues.extend(
                _validate_event_payload(
                    event=event,
                    line_number=index,
                    run_id=record.run_id,
                )
            )
            if event.get("event_type") == EventType.EPISODE_END.value:
                has_episode_end = True
        if event_count == 0:
            issues.append(
                ValidationIssue(
                    code="partial_run",
                    message="events.jsonl parsed successfully but contains no events",
                    relative_path="events.jsonl",
                )
            )
        elif not has_episode_end:
            issues.append(
                ValidationIssue(
                    code="partial_run",
                    message="events.jsonl does not contain an episode_end event",
                    relative_path="events.jsonl",
                )
            )

    missing_artifacts = []
    for artifact_ref in record.referenced_artifacts:
        artifact_path = record.run_dir / artifact_ref
        if not artifact_path.is_file():
            missing_artifacts.append(artifact_ref)
            issues.append(
                ValidationIssue(
                    code="missing_artifact",
                    message=f"expected artifact is missing: {artifact_ref}",
                    relative_path=artifact_ref,
                )
            )

    contract_complete = not any(issue.code in _CONTRACT_BLOCKING_CODES for issue in issues)
    run_complete = contract_complete and not any(issue.code in _COMPLETENESS_BLOCKING_CODES for issue in issues)

    return RunValidation(
        run_id=record.run_id,
        run_dir=record.run_dir,
        required_files_present=required_files_present,
        parsed_files_ok=parsed_files_ok,
        event_count=event_count,
        has_episode_end=has_episode_end,
        expected_artifact_count=len(record.referenced_artifacts),
        missing_artifacts=missing_artifacts,
        contract_complete=contract_complete,
        run_complete=run_complete,
        issues=issues,
    )


def _validate_payload_fields(
    payload: dict[str, Any] | None,
    required_fields: tuple[str, ...],
    relative_path: str,
) -> list[ValidationIssue]:
    if payload is None:
        return []
    issues: list[ValidationIssue] = []
    for field_name in required_fields:
        if field_name not in payload:
            issues.append(
                ValidationIssue(
                    code="schema_field_missing",
                    message=f"missing field '{field_name}' in {relative_path}",
                    relative_path=relative_path,
                )
            )
    return issues


def _validate_core_types(
    task_config: dict[str, Any] | None,
    episode_result: dict[str, Any] | None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if isinstance(task_config, dict):
        runtime_options = task_config.get("runtime_options")
        if runtime_options is not None and not isinstance(runtime_options, dict):
            issues.append(
                ValidationIssue(
                    code="schema_type_error",
                    message="task_config.runtime_options must be a JSON object",
                    relative_path="task_config.json",
                )
            )
        metadata = task_config.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            issues.append(
                ValidationIssue(
                    code="schema_type_error",
                    message="task_config.metadata must be a JSON object",
                    relative_path="task_config.json",
                )
            )

    if isinstance(episode_result, dict):
        if "success" in episode_result and not isinstance(episode_result["success"], bool):
            issues.append(
                ValidationIssue(
                    code="schema_type_error",
                    message="episode_result.success must be a boolean",
                    relative_path="episode_result.json",
                )
            )
        metrics = episode_result.get("metrics")
        if metrics is not None and not isinstance(metrics, dict):
            issues.append(
                ValidationIssue(
                    code="schema_type_error",
                    message="episode_result.metrics must be a JSON object",
                    relative_path="episode_result.json",
                )
            )

    return issues


def _validate_identity_consistency(record: RunRecord) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    sources = {
        "run_dir": {"run_id": record.run_id},
        "manifest.json": record.manifest,
        "task_config.json": record.task_config,
        "episode_result.json": record.episode_result,
    }
    identity_fields = ("run_id", "task_type", "task_id", "scene_id", "robot_id", "seed")

    for field_name in identity_fields:
        observed: dict[str, Any] = {}
        for source_name, payload in sources.items():
            if isinstance(payload, dict) and field_name in payload:
                observed[source_name] = payload[field_name]
        if len(set(observed.values())) > 1:
            rendered = ", ".join(f"{source}={value!r}" for source, value in sorted(observed.items()))
            issues.append(
                ValidationIssue(
                    code="field_mismatch",
                    message=f"inconsistent {field_name} across run artifacts: {rendered}",
                )
            )

    return issues


def _validate_event_payload(
    event: dict[str, Any],
    line_number: int,
    run_id: str,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for field_name in _EVENT_REQUIRED_FIELDS:
        if field_name not in event:
            issues.append(
                ValidationIssue(
                    code="schema_field_missing",
                    message=f"missing field '{field_name}' in events.jsonl line {line_number}",
                    relative_path="events.jsonl",
                )
            )

    if event.get("run_id") not in {None, run_id}:
        issues.append(
            ValidationIssue(
                code="field_mismatch",
                message=(
                    f"events.jsonl line {line_number} has run_id={event.get('run_id')!r}, "
                    f"expected {run_id!r}"
                ),
                relative_path="events.jsonl",
            )
        )

    return issues
