"""Episode-level summaries and export helpers for the minimal M5 eval harness."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .loader import RunRecord
from .loader import scan_results_root
from .validate import RunValidation
from .validate import validate_run_record


@dataclass(frozen=True)
class EpisodeSummary:
    """Script-friendly episode summary row."""

    run_id: str
    run_dir: str
    task_family: str | None
    task_id: str | None
    scene_id: str | None
    robot_id: str | None
    seed: int | None
    success: bool | None
    termination_reason: str | None
    failure_reason: str | None
    step_count: int | None
    planner_calls: int | None
    tool_calls: int | None
    invalid_actions: int | None
    episode_time_s: float | None
    planner_latency_s: float | None
    backend_variant: str | None
    model_variant: str | None
    runtime_variant: str | None
    planner_backend: str | None
    tool_variant: str | None
    contract_complete: bool
    run_complete: bool
    validation_issue_count: int
    validation_issue_codes: list[str]
    validation_issue_messages: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "task_family": self.task_family,
            "task_id": self.task_id,
            "scene_id": self.scene_id,
            "robot_id": self.robot_id,
            "seed": self.seed,
            "success": self.success,
            "termination_reason": self.termination_reason,
            "failure_reason": self.failure_reason,
            "step_count": self.step_count,
            "planner_calls": self.planner_calls,
            "tool_calls": self.tool_calls,
            "invalid_actions": self.invalid_actions,
            "episode_time_s": self.episode_time_s,
            "planner_latency_s": self.planner_latency_s,
            "backend_variant": self.backend_variant,
            "model_variant": self.model_variant,
            "runtime_variant": self.runtime_variant,
            "planner_backend": self.planner_backend,
            "tool_variant": self.tool_variant,
            "contract_complete": self.contract_complete,
            "run_complete": self.run_complete,
            "validation_issue_count": self.validation_issue_count,
            "validation_issue_codes": list(self.validation_issue_codes),
            "validation_issue_messages": list(self.validation_issue_messages),
        }

    def to_csv_row(self) -> dict[str, Any]:
        row = self.to_dict()
        row["validation_issue_codes"] = ";".join(self.validation_issue_codes)
        row["validation_issue_messages"] = " | ".join(self.validation_issue_messages)
        return row


@dataclass(frozen=True)
class SummaryAggregate:
    """Minimal aggregate statistics over episode summaries."""

    total_runs: int
    contract_complete_runs: int
    run_complete_runs: int
    bad_runs: int
    successful_runs: int
    success_rate: float | None
    total_step_count: int
    average_step_count: float | None
    total_planner_calls: int
    total_tool_calls: int
    total_invalid_actions: int
    average_episode_time_s: float | None
    by_task_family: dict[str, dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_runs": self.total_runs,
            "contract_complete_runs": self.contract_complete_runs,
            "run_complete_runs": self.run_complete_runs,
            "bad_runs": self.bad_runs,
            "successful_runs": self.successful_runs,
            "success_rate": self.success_rate,
            "total_step_count": self.total_step_count,
            "average_step_count": self.average_step_count,
            "total_planner_calls": self.total_planner_calls,
            "total_tool_calls": self.total_tool_calls,
            "total_invalid_actions": self.total_invalid_actions,
            "average_episode_time_s": self.average_episode_time_s,
            "by_task_family": self.by_task_family,
        }


@dataclass(frozen=True)
class SummaryBundle:
    """All summary artifacts produced from one results root."""

    summaries: list[EpisodeSummary]
    validations: list[RunValidation]
    aggregate: SummaryAggregate


def summarize_results_root(results_root: str | Path) -> SummaryBundle:
    """Load, validate, summarize, and aggregate one results root."""

    records = scan_results_root(results_root)
    validations = [validate_run_record(record) for record in records]
    summaries = [build_episode_summary(record, validation) for record, validation in zip(records, validations)]
    aggregate = aggregate_episode_summaries(summaries)
    return SummaryBundle(summaries=summaries, validations=validations, aggregate=aggregate)


def build_episode_summary(record: RunRecord, validation: RunValidation) -> EpisodeSummary:
    """Construct one summary row from a loaded run and its validation state."""

    manifest = record.manifest or {}
    task_config = record.task_config or {}
    episode_result = record.episode_result or {}
    runtime_options = task_config.get("runtime_options", {})
    metadata = task_config.get("metadata", {})
    extra_options = runtime_options.get("extra_options", {}) if isinstance(runtime_options, dict) else {}
    metrics = episode_result.get("metrics", {}) if isinstance(episode_result.get("metrics"), dict) else {}

    task_family = _first_string(
        episode_result.get("task_type"),
        task_config.get("task_type"),
        manifest.get("task_type"),
    )
    termination_reason = _first_string(episode_result.get("termination_reason"))
    success = episode_result.get("success") if isinstance(episode_result.get("success"), bool) else None

    return EpisodeSummary(
        run_id=record.run_id,
        run_dir=str(record.run_dir),
        task_family=task_family,
        task_id=_first_string(episode_result.get("task_id"), task_config.get("task_id"), manifest.get("task_id")),
        scene_id=_first_string(
            episode_result.get("scene_id"),
            task_config.get("scene_id"),
            manifest.get("scene_id"),
        ),
        robot_id=_first_string(
            episode_result.get("robot_id"),
            task_config.get("robot_id"),
            manifest.get("robot_id"),
        ),
        seed=_first_int(episode_result.get("seed"), task_config.get("seed"), manifest.get("seed")),
        success=success,
        termination_reason=termination_reason,
        failure_reason=_extract_failure_reason(episode_result, validation),
        step_count=_first_int(episode_result.get("step_count")),
        planner_calls=_first_int(episode_result.get("planner_call_count")),
        tool_calls=_first_int(episode_result.get("tool_call_count")),
        invalid_actions=_first_int(episode_result.get("invalid_action_count")),
        episode_time_s=_first_float(episode_result.get("elapsed_time_sec")),
        planner_latency_s=_first_float(episode_result.get("planner_latency_sec")),
        backend_variant=_extract_backend_variant(metadata, metrics),
        model_variant=_first_string(
            extra_options.get("model_variant"),
            metadata.get("model_variant") if isinstance(metadata, dict) else None,
            metrics.get("model_variant") if isinstance(metrics, dict) else None,
        ),
        runtime_variant=_extract_runtime_variant(metadata, extra_options),
        planner_backend=_extract_planner_backend(metadata, extra_options, metrics),
        tool_variant=_extract_tool_variant(metadata),
        contract_complete=validation.contract_complete,
        run_complete=validation.run_complete,
        validation_issue_count=len(validation.issues),
        validation_issue_codes=validation.issue_codes,
        validation_issue_messages=[issue.message for issue in validation.issues],
    )


def aggregate_episode_summaries(summaries: list[EpisodeSummary]) -> SummaryAggregate:
    """Compute a minimal aggregate view over episode summary rows."""

    total_runs = len(summaries)
    contract_complete_runs = sum(1 for summary in summaries if summary.contract_complete)
    run_complete_runs = sum(1 for summary in summaries if summary.run_complete)
    bad_runs = total_runs - run_complete_runs
    successful_runs = sum(1 for summary in summaries if summary.success is True)

    step_counts = [summary.step_count for summary in summaries if summary.step_count is not None]
    episode_times = [summary.episode_time_s for summary in summaries if summary.episode_time_s is not None]

    by_task_family: dict[str, dict[str, Any]] = {}
    for summary in summaries:
        family = summary.task_family or "unknown"
        entry = by_task_family.setdefault(
            family,
            {
                "run_count": 0,
                "contract_complete_runs": 0,
                "run_complete_runs": 0,
                "successful_runs": 0,
                "total_planner_calls": 0,
                "total_tool_calls": 0,
                "total_invalid_actions": 0,
            },
        )
        entry["run_count"] += 1
        entry["contract_complete_runs"] += int(summary.contract_complete)
        entry["run_complete_runs"] += int(summary.run_complete)
        entry["successful_runs"] += int(summary.success is True)
        entry["total_planner_calls"] += summary.planner_calls or 0
        entry["total_tool_calls"] += summary.tool_calls or 0
        entry["total_invalid_actions"] += summary.invalid_actions or 0

    for entry in by_task_family.values():
        run_count = entry["run_count"]
        entry["success_rate"] = round(entry["successful_runs"] / run_count, 6) if run_count else None

    return SummaryAggregate(
        total_runs=total_runs,
        contract_complete_runs=contract_complete_runs,
        run_complete_runs=run_complete_runs,
        bad_runs=bad_runs,
        successful_runs=successful_runs,
        success_rate=round(successful_runs / total_runs, 6) if total_runs else None,
        total_step_count=sum(step_counts),
        average_step_count=round(sum(step_counts) / len(step_counts), 6) if step_counts else None,
        total_planner_calls=sum(summary.planner_calls or 0 for summary in summaries),
        total_tool_calls=sum(summary.tool_calls or 0 for summary in summaries),
        total_invalid_actions=sum(summary.invalid_actions or 0 for summary in summaries),
        average_episode_time_s=round(sum(episode_times) / len(episode_times), 6) if episode_times else None,
        by_task_family=by_task_family,
    )


def write_summary_outputs(
    bundle: SummaryBundle,
    output_dir: str | Path,
    write_jsonl: bool = True,
    write_csv: bool = True,
) -> dict[str, Path]:
    """Write script-friendly summary outputs and validation artifacts."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    written: dict[str, Path] = {}
    if write_jsonl:
        summary_jsonl_path = output_dir / "run_summary.jsonl"
        _write_jsonl(summary_jsonl_path, [summary.to_dict() for summary in bundle.summaries])
        written["summary_jsonl"] = summary_jsonl_path

    if write_csv:
        summary_csv_path = output_dir / "run_summary.csv"
        _write_csv(summary_csv_path, bundle.summaries)
        written["summary_csv"] = summary_csv_path

    aggregate_path = output_dir / "aggregate.json"
    aggregate_path.write_text(json.dumps(bundle.aggregate.to_dict(), indent=2) + "\n", encoding="utf-8")
    written["aggregate_json"] = aggregate_path

    validation_path = output_dir / "validation.json"
    validation_payload = [validation.to_dict() for validation in bundle.validations]
    validation_path.write_text(json.dumps(validation_payload, indent=2) + "\n", encoding="utf-8")
    written["validation_json"] = validation_path

    return written


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _write_csv(path: Path, summaries: list[EpisodeSummary]) -> None:
    fieldnames = list(EpisodeSummary.__dataclass_fields__.keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for summary in summaries:
            writer.writerow(summary.to_csv_row())


def _extract_failure_reason(
    episode_result: dict[str, Any],
    validation: RunValidation,
) -> str | None:
    success = episode_result.get("success")
    if success is True:
        return None

    notes = episode_result.get("notes")
    if isinstance(notes, list):
        for note in reversed(notes):
            if isinstance(note, str) and note.strip():
                return note.strip()

    termination_reason = episode_result.get("termination_reason")
    if isinstance(termination_reason, str) and termination_reason:
        return termination_reason

    if validation.issues:
        return validation.issues[0].message
    return None


def _extract_backend_variant(metadata: Any, metrics: Any) -> str | None:
    if isinstance(metrics, dict):
        for key in ("navigation.backend", "manipulation.backend", "instruction_following.backend"):
            value = metrics.get(key)
            if isinstance(value, str) and value:
                return value

    if isinstance(metadata, dict):
        for key in ("navigation_baseline", "manipulation_baseline"):
            payload = metadata.get(key)
            if isinstance(payload, dict):
                backend = payload.get("backend")
                if isinstance(backend, str) and backend:
                    return backend
    return None


def _extract_runtime_variant(metadata: Any, extra_options: Any) -> str | None:
    if isinstance(extra_options, dict):
        runtime_policy = extra_options.get("runtime_policy")
        if isinstance(runtime_policy, str) and runtime_policy:
            return runtime_policy

    if isinstance(metadata, dict):
        if "agent_runtime_v0" in metadata:
            return "agent_runtime_v0"
        if "navigation_baseline" in metadata:
            return "navigation_baseline"
        if "manipulation_baseline" in metadata:
            return "manipulation_baseline"
    return None


def _extract_planner_backend(metadata: Any, extra_options: Any, metrics: Any) -> str | None:
    candidates = []
    if isinstance(extra_options, dict):
        candidates.append(extra_options.get("planner_backend"))
    if isinstance(metadata, dict):
        agent_runtime = metadata.get("agent_runtime_v0")
        if isinstance(agent_runtime, dict):
            candidates.append(agent_runtime.get("planner_backend"))
    if isinstance(metrics, dict):
        candidates.extend(
            [
                metrics.get("navigation.planner_backend"),
                metrics.get("manipulation.planner_backend"),
            ]
        )
    return _first_string(*candidates)


def _extract_tool_variant(metadata: Any) -> str | None:
    if not isinstance(metadata, dict):
        return None

    agent_runtime = metadata.get("agent_runtime_v0")
    if isinstance(agent_runtime, dict):
        available_tools = agent_runtime.get("available_tools")
        if isinstance(available_tools, list):
            tool_names = [tool_name for tool_name in available_tools if isinstance(tool_name, str) and tool_name]
            if tool_names:
                return "|".join(tool_names)

    for key in ("navigation_baseline", "manipulation_baseline"):
        payload = metadata.get(key)
        if isinstance(payload, dict):
            controller = payload.get("controller")
            if isinstance(controller, dict):
                tool_name = controller.get("type")
                if isinstance(tool_name, str) and tool_name:
                    return tool_name
    return None


def _first_string(*values: Any) -> str | None:
    for value in values:
        if isinstance(value, str) and value:
            return value
    return None


def _first_int(*values: Any) -> int | None:
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
    return None


def _first_float(*values: Any) -> float | None:
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
    return None
