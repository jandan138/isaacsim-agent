"""Master Block A checkpoint summary over existing processed summaries."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .summarize import EpisodeSummary
from .summarize import SummaryBundle
from .summarize import aggregate_episode_summaries
from .summarize import write_summary_outputs
from .validate import RunValidation
from .validate import ValidationIssue


_TASK_FAMILY_NORMALIZATION = {
    "navigation": "navigation",
    "pick_place": "manipulation",
}

_TASK_FAMILY_DISPLAY = {
    "navigation": "Navigation",
    "manipulation": "Manipulation",
}

_TASK_DIFFICULTY_DISPLAY = {
    "easy": "Easy",
    "harder": "Harder",
}

_SOURCE_SLICE_DISPLAY = {
    "navigation_easy_pilot": "Navigation Easy Pilot",
    "navigation_expanded": "Navigation Expanded",
    "manipulation_pilot": "Manipulation Pilot",
    "navigation_robustness": "Navigation Robustness",
}

_SOURCE_SLICE_ORDER = [
    "navigation_easy_pilot",
    "navigation_expanded",
    "manipulation_pilot",
    "navigation_robustness",
]

_COHORT_ORDER = [
    ("navigation", "easy"),
    ("navigation", "harder"),
    ("manipulation", "easy"),
    ("manipulation", "harder"),
]

_MASTER_CSV_COLUMNS = [
    "task_family",
    "task_family_display",
    "task_difficulty",
    "task_difficulty_display",
    "prompt_variant",
    "runtime_variant",
    "run_count",
    "contract_complete_runs",
    "run_complete_runs",
    "successful_runs",
    "success_rate",
    "total_invalid_actions",
    "average_invalid_actions",
    "invalid_action_run_count",
    "invalid_action_run_rate",
    "total_planner_calls",
    "average_planner_calls",
    "total_tool_calls",
    "average_tool_calls",
    "total_retries",
    "average_retries",
    "retry_run_count",
    "retry_run_rate",
    "successful_retry_runs",
    "successful_invalid_action_runs",
    "recovery_success_rate",
    "episode_time_run_count",
    "average_episode_time_s",
    "termination_reasons",
]


@dataclass(frozen=True)
class BlockAMasterProcessedSource:
    """One processed run-summary directory used in the merged checkpoint."""

    source_slice: str
    input_dir: Path
    run_summary_jsonl_path: Path
    validation_json_path: Path
    task_difficulty: str
    run_count: int
    task_families: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_kind": "processed_runs",
            "source_slice": self.source_slice,
            "source_slice_display": _source_slice_display(self.source_slice),
            "input_dir": str(self.input_dir.resolve()),
            "run_summary_jsonl_path": str(self.run_summary_jsonl_path.resolve()),
            "validation_json_path": str(self.validation_json_path.resolve()),
            "task_difficulty": self.task_difficulty,
            "task_difficulty_display": _task_difficulty_display(self.task_difficulty),
            "run_count": self.run_count,
            "task_families": list(self.task_families),
        }


@dataclass(frozen=True)
class BlockAMasterReferenceSummary:
    """One reference-only summary used for consistency checks."""

    source_name: str
    input_dir: Path
    summary_json_path: Path
    task_families: list[str]
    prompt_runtime_cell_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_kind": "reference_summary",
            "source_name": self.source_name,
            "input_dir": str(self.input_dir.resolve()),
            "summary_json_path": str(self.summary_json_path.resolve()),
            "task_families": list(self.task_families),
            "prompt_runtime_cell_count": self.prompt_runtime_cell_count,
        }


@dataclass(frozen=True)
class BlockAMasterSummaryResult:
    """Materialized outputs for the Block A master checkpoint."""

    output_dir: Path
    processed_sources: list[BlockAMasterProcessedSource]
    reference_summaries: list[BlockAMasterReferenceSummary]
    bundle: SummaryBundle
    summary: dict[str, Any]
    written_outputs: dict[str, Path]


def summarize_block_a_master_processed_dirs(
    *,
    navigation_pilot_dir: str | Path,
    navigation_expanded_dir: str | Path,
    manipulation_pilot_dir: str | Path,
    cross_family_dir: str | Path,
    navigation_robustness_dir: str | Path,
    output_dir: str | Path,
) -> BlockAMasterSummaryResult:
    """Build the unified Block A checkpoint package from processed summaries."""

    output_dir = Path(output_dir)
    processed_specs = [
        ("navigation_easy_pilot", Path(navigation_pilot_dir), "easy"),
        ("navigation_expanded", Path(navigation_expanded_dir), "easy"),
        ("manipulation_pilot", Path(manipulation_pilot_dir), "easy"),
        ("navigation_robustness", Path(navigation_robustness_dir), "harder"),
    ]

    processed_sources, summaries, validations, run_annotations = _load_processed_sources(processed_specs)
    _ensure_unique_run_ids(summaries)

    bundle = SummaryBundle(
        summaries=summaries,
        validations=validations,
        aggregate=aggregate_episode_summaries(summaries),
    )
    written_outputs = write_summary_outputs(bundle=bundle, output_dir=output_dir)

    reference_summary, reference_payload = _load_cross_family_reference_summary(cross_family_dir)
    summary = build_block_a_master_summary(
        bundle=bundle,
        processed_sources=processed_sources,
        reference_summaries=[reference_summary],
        reference_payload=reference_payload,
        run_annotations=run_annotations,
        output_dir=output_dir,
    )

    summary_json_path = output_dir / "block_a_master_summary.json"
    summary_json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    written_outputs["master_summary_json"] = summary_json_path

    summary_csv_path = output_dir / "block_a_master_summary.csv"
    _write_master_csv(summary_csv_path, summary["group_by_task_family_difficulty_prompt_runtime"])
    written_outputs["master_summary_csv"] = summary_csv_path

    summary_md_path = output_dir / "block_a_master_summary.md"
    summary_md_path.write_text(_render_master_markdown(summary), encoding="utf-8")
    written_outputs["master_summary_md"] = summary_md_path

    return BlockAMasterSummaryResult(
        output_dir=output_dir,
        processed_sources=processed_sources,
        reference_summaries=[reference_summary],
        bundle=bundle,
        summary=summary,
        written_outputs=written_outputs,
    )


def build_block_a_master_summary(
    *,
    bundle: SummaryBundle,
    processed_sources: list[BlockAMasterProcessedSource],
    reference_summaries: list[BlockAMasterReferenceSummary],
    reference_payload: dict[str, Any],
    run_annotations: dict[str, dict[str, str]],
    output_dir: str | Path,
) -> dict[str, Any]:
    """Build the structured Block A checkpoint payload."""

    rows = _build_enriched_rows(bundle.summaries, run_annotations)
    grouped_source_rows = _aggregate_row_groups(rows, ("source_slice", "prompt_variant", "runtime_variant"))
    grouped_family_rows = _aggregate_row_groups(rows, ("task_family",))
    grouped_difficulty_rows = _aggregate_row_groups(rows, ("task_difficulty",))
    grouped_family_difficulty_rows = _aggregate_row_groups(rows, ("task_family", "task_difficulty"))
    grouped_family_difficulty_prompt_runtime_rows = _aggregate_row_groups(
        rows,
        ("task_family", "task_difficulty", "prompt_variant", "runtime_variant"),
    )
    grouped_prompt_runtime_rows = _aggregate_row_groups(rows, ("prompt_variant", "runtime_variant"))

    coverage_rows = _build_coverage_rows(rows)
    source_slice_assessments = _build_source_slice_assessments(grouped_source_rows)
    cross_family_reference = _evaluate_cross_family_reference(reference_payload)
    navigation_difficulty = _evaluate_navigation_difficulty(grouped_family_difficulty_prompt_runtime_rows)
    answers = _build_checkpoint_answers(
        source_slice_assessments=source_slice_assessments,
        cross_family_reference=cross_family_reference,
        navigation_difficulty=navigation_difficulty,
        coverage_rows=coverage_rows,
    )

    return {
        "summary_title": "Block A Master Summary",
        "description": (
            "Unified Block A checkpoint over the existing easy navigation pilot, navigation expanded, "
            "manipulation pilot, cross-family summary, and navigation robustness slice without adding "
            "new experiment axes."
        ),
        "output_dir": str(Path(output_dir).resolve()),
        "processed_sources": [source.to_dict() for source in processed_sources],
        "reference_summaries": [source.to_dict() for source in reference_summaries],
        "overall": {
            "merged_runs": bundle.aggregate.total_runs,
            "contract_complete_runs": bundle.aggregate.contract_complete_runs,
            "run_complete_runs": bundle.aggregate.run_complete_runs,
            "bad_runs": bundle.aggregate.bad_runs,
            "successful_runs": bundle.aggregate.successful_runs,
            "success_rate": bundle.aggregate.success_rate,
            "total_planner_calls": bundle.aggregate.total_planner_calls,
            "total_tool_calls": bundle.aggregate.total_tool_calls,
            "total_invalid_actions": bundle.aggregate.total_invalid_actions,
            "total_retries": bundle.aggregate.total_retries,
            "average_step_count": bundle.aggregate.average_step_count,
            "average_episode_time_s": bundle.aggregate.average_episode_time_s,
        },
        "coverage": coverage_rows,
        "group_by_source_slice_prompt_runtime": grouped_source_rows,
        "group_by_task_family": grouped_family_rows,
        "group_by_task_difficulty": grouped_difficulty_rows,
        "group_by_task_family_difficulty": grouped_family_difficulty_rows,
        "group_by_prompt_runtime": grouped_prompt_runtime_rows,
        "group_by_task_family_difficulty_prompt_runtime": grouped_family_difficulty_prompt_runtime_rows,
        "source_slice_assessments": source_slice_assessments,
        "reference_checks": {
            "cross_family_summary": cross_family_reference,
        },
        "answers": answers,
        "tables": {
            "main_success_table": _build_family_difficulty_pivot(
                grouped_family_difficulty_prompt_runtime_rows,
                metric_columns=("run_count", "success_rate"),
            ),
            "invalid_action_table": _build_family_difficulty_pivot(
                grouped_family_difficulty_prompt_runtime_rows,
                metric_columns=("average_invalid_actions", "invalid_action_run_rate"),
            ),
            "efficiency_table": _build_family_difficulty_pivot(
                grouped_family_difficulty_prompt_runtime_rows,
                metric_columns=("average_planner_calls", "average_tool_calls", "average_episode_time_s"),
            ),
            "recovery_table": _build_family_difficulty_pivot(
                grouped_family_difficulty_prompt_runtime_rows,
                metric_columns=(
                    "invalid_action_run_count",
                    "successful_invalid_action_runs",
                    "recovery_success_rate",
                    "average_retries",
                ),
            ),
            "difficulty_comparison_table": _build_difficulty_comparison_table(
                grouped_family_difficulty_prompt_runtime_rows
            ),
        },
    }


def _load_processed_sources(
    processed_specs: list[tuple[str, Path, str]],
) -> tuple[
    list[BlockAMasterProcessedSource],
    list[EpisodeSummary],
    list[RunValidation],
    dict[str, dict[str, str]],
]:
    processed_sources: list[BlockAMasterProcessedSource] = []
    summaries: list[EpisodeSummary] = []
    validations: list[RunValidation] = []
    run_annotations: dict[str, dict[str, str]] = {}

    for source_slice, input_dir, task_difficulty in processed_specs:
        summary_jsonl_path = input_dir / "run_summary.jsonl"
        validation_json_path = input_dir / "validation.json"
        if not summary_jsonl_path.is_file():
            raise FileNotFoundError(f"missing run_summary.jsonl in processed directory: {input_dir}")
        if not validation_json_path.is_file():
            raise FileNotFoundError(f"missing validation.json in processed directory: {input_dir}")

        source_summaries = _load_episode_summaries(summary_jsonl_path)
        source_validations = _load_validations(validation_json_path)

        processed_sources.append(
            BlockAMasterProcessedSource(
                source_slice=source_slice,
                input_dir=input_dir,
                run_summary_jsonl_path=summary_jsonl_path,
                validation_json_path=validation_json_path,
                task_difficulty=task_difficulty,
                run_count=len(source_summaries),
                task_families=sorted(
                    {
                        _normalize_task_family(summary.task_family or "unknown")
                        for summary in source_summaries
                    }
                ),
            )
        )

        for summary in source_summaries:
            run_annotations[summary.run_id] = {
                "source_slice": source_slice,
                "task_difficulty": task_difficulty,
            }

        summaries.extend(source_summaries)
        validations.extend(source_validations)

    summaries.sort(key=_summary_sort_key)
    validations.sort(key=lambda item: item.run_id)
    return processed_sources, summaries, validations, run_annotations


def _load_cross_family_reference_summary(
    cross_family_dir: str | Path,
) -> tuple[BlockAMasterReferenceSummary, dict[str, Any]]:
    input_dir = Path(cross_family_dir)
    summary_json_path = input_dir / "cross_family_summary.json"
    if not summary_json_path.is_file():
        raise FileNotFoundError(f"missing cross_family_summary.json in processed directory: {input_dir}")

    payload = json.loads(summary_json_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload["_summary_json_path"] = str(summary_json_path.resolve())
    task_families = []
    for row in payload.get("group_by_task_family", []):
        if isinstance(row, dict):
            task_families.append(_normalize_task_family(str(row.get("task_family", "unknown"))))

    return (
        BlockAMasterReferenceSummary(
            source_name="cross_family_summary",
            input_dir=input_dir,
            summary_json_path=summary_json_path,
            task_families=sorted(set(task_families)),
            prompt_runtime_cell_count=len(payload.get("group_by_task_family_prompt_runtime", [])),
        ),
        payload,
    )


def _load_episode_summaries(path: Path) -> list[EpisodeSummary]:
    summaries: list[EpisodeSummary] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        summaries.append(EpisodeSummary(**payload))
    return summaries


def _load_validations(path: Path) -> list[RunValidation]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"expected validation.json to contain a list: {path}")

    validations: list[RunValidation] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError(f"expected validation row to be a mapping: {path}")

        issues_payload = item.get("issues", [])
        if not isinstance(issues_payload, list):
            raise ValueError(f"expected validation issues to be a list: {path}")

        issues = [
            ValidationIssue(
                code=str(issue.get("code", "")),
                message=str(issue.get("message", "")),
                severity=str(issue.get("severity", "error")),
                relative_path=_optional_string(issue.get("relative_path")),
            )
            for issue in issues_payload
            if isinstance(issue, dict)
        ]

        validations.append(
            RunValidation(
                run_id=str(item.get("run_id", "")),
                run_dir=Path(str(item.get("run_dir", ""))),
                required_files_present=bool(item.get("required_files_present", False)),
                parsed_files_ok=bool(item.get("parsed_files_ok", False)),
                event_count=int(item.get("event_count", 0)),
                has_episode_end=bool(item.get("has_episode_end", False)),
                expected_artifact_count=int(item.get("expected_artifact_count", 0)),
                missing_artifacts=[
                    str(artifact)
                    for artifact in item.get("missing_artifacts", [])
                    if isinstance(artifact, str)
                ],
                contract_complete=bool(item.get("contract_complete", False)),
                run_complete=bool(item.get("run_complete", False)),
                issues=issues,
            )
        )
    return validations


def _build_enriched_rows(
    summaries: list[EpisodeSummary],
    run_annotations: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for summary in summaries:
        annotations = run_annotations.get(summary.run_id, {})
        task_family = _normalize_task_family(summary.task_family or "unknown")
        task_difficulty = annotations.get("task_difficulty", "unknown")
        source_slice = annotations.get("source_slice", "unknown")
        row = summary.to_dict()
        row["task_family"] = task_family
        row["task_family_display"] = _task_family_display(task_family)
        row["task_difficulty"] = task_difficulty
        row["task_difficulty_display"] = _task_difficulty_display(task_difficulty)
        row["source_slice"] = source_slice
        row["source_slice_display"] = _source_slice_display(source_slice)
        rows.append(row)
    return rows


def _aggregate_row_groups(
    rows: list[dict[str, Any]],
    group_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in rows:
        key = tuple(_row_field_value(row, field_name) for field_name in group_fields)
        grouped.setdefault(key, []).append(row)

    aggregated_rows: list[dict[str, Any]] = []
    for key in sorted(grouped, key=lambda item: _group_key_sort_key(group_fields, item)):
        group_rows = grouped[key]
        aggregated_row = {field_name: value for field_name, value in zip(group_fields, key)}
        if "task_family" in aggregated_row:
            aggregated_row["task_family_display"] = _task_family_display(aggregated_row["task_family"])
        if "task_difficulty" in aggregated_row:
            aggregated_row["task_difficulty_display"] = _task_difficulty_display(
                aggregated_row["task_difficulty"]
            )
        if "source_slice" in aggregated_row:
            aggregated_row["source_slice_display"] = _source_slice_display(aggregated_row["source_slice"])
        aggregated_row.update(_build_group_metrics(group_rows))
        aggregated_rows.append(aggregated_row)
    return aggregated_rows


def _build_group_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    run_count = len(rows)
    successful_runs = sum(1 for row in rows if row.get("success") is True)
    invalid_action_run_count = sum(1 for row in rows if (row.get("invalid_actions") or 0) > 0)
    retry_run_count = sum(1 for row in rows if (row.get("retries") or 0) > 0)
    successful_retry_runs = sum(
        1 for row in rows if row.get("success") is True and (row.get("retries") or 0) > 0
    )
    successful_invalid_action_runs = sum(
        1 for row in rows if row.get("success") is True and (row.get("invalid_actions") or 0) > 0
    )

    total_planner_calls = sum(int(row.get("planner_calls") or 0) for row in rows)
    total_tool_calls = sum(int(row.get("tool_calls") or 0) for row in rows)
    total_invalid_actions = sum(int(row.get("invalid_actions") or 0) for row in rows)
    total_retries = sum(int(row.get("retries") or 0) for row in rows)
    episode_times = [
        float(value)
        for value in (row.get("episode_time_s") for row in rows)
        if isinstance(value, (int, float))
    ]

    termination_reasons: dict[str, int] = {}
    for row in rows:
        termination_reason = row.get("termination_reason")
        if isinstance(termination_reason, str) and termination_reason:
            termination_reasons[termination_reason] = termination_reasons.get(termination_reason, 0) + 1

    return {
        "run_count": run_count,
        "contract_complete_runs": sum(1 for row in rows if row.get("contract_complete") is True),
        "run_complete_runs": sum(1 for row in rows if row.get("run_complete") is True),
        "successful_runs": successful_runs,
        "success_rate": round(successful_runs / run_count, 6) if run_count else None,
        "total_invalid_actions": total_invalid_actions,
        "average_invalid_actions": round(total_invalid_actions / run_count, 6) if run_count else None,
        "invalid_action_run_count": invalid_action_run_count,
        "invalid_action_run_rate": round(invalid_action_run_count / run_count, 6) if run_count else None,
        "total_planner_calls": total_planner_calls,
        "average_planner_calls": round(total_planner_calls / run_count, 6) if run_count else None,
        "total_tool_calls": total_tool_calls,
        "average_tool_calls": round(total_tool_calls / run_count, 6) if run_count else None,
        "total_retries": total_retries,
        "average_retries": round(total_retries / run_count, 6) if run_count else None,
        "retry_run_count": retry_run_count,
        "retry_run_rate": round(retry_run_count / run_count, 6) if run_count else None,
        "successful_retry_runs": successful_retry_runs,
        "successful_invalid_action_runs": successful_invalid_action_runs,
        "recovery_success_rate": round(successful_invalid_action_runs / invalid_action_run_count, 6)
        if invalid_action_run_count
        else None,
        "episode_time_run_count": len(episode_times),
        "average_episode_time_s": round(sum(episode_times) / len(episode_times), 6)
        if episode_times
        else None,
        "termination_reasons": termination_reasons,
        "run_ids": [str(row.get("run_id", "")) for row in rows],
    }


def _build_coverage_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    meta: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row.get("task_family", "unknown")), str(row.get("task_difficulty", "unknown")))
        entry = meta.setdefault(
            key,
            {
                "task_ids": set(),
                "source_slices": set(),
                "prompt_runtime_cells": set(),
            },
        )
        entry["task_ids"].add(str(row.get("task_id", "unknown")))
        entry["source_slices"].add(str(row.get("source_slice", "unknown")))
        entry["prompt_runtime_cells"].add(
            (str(row.get("prompt_variant", "unknown")), str(row.get("runtime_variant", "unknown")))
        )

    aggregated_rows = _aggregate_row_groups(rows, ("task_family", "task_difficulty"))
    for row in aggregated_rows:
        key = (str(row.get("task_family", "unknown")), str(row.get("task_difficulty", "unknown")))
        metadata = meta.get(key, {})
        row["task_count"] = len(metadata.get("task_ids", set()))
        row["source_slices"] = sorted(metadata.get("source_slices", set()))
        row["prompt_runtime_cell_count"] = len(metadata.get("prompt_runtime_cells", set()))
    return aggregated_rows


def _build_source_slice_assessments(
    grouped_source_rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    by_source_slice: dict[str, list[dict[str, Any]]] = {}
    for row in grouped_source_rows:
        by_source_slice.setdefault(str(row.get("source_slice", "unknown")), []).append(row)

    assessments: dict[str, dict[str, Any]] = {}
    for source_slice, rows in by_source_slice.items():
        assessments[source_slice] = _evaluate_prompt_runtime_pattern(rows)
        assessments[source_slice]["source_slice_display"] = _source_slice_display(source_slice)
    return assessments


def _evaluate_cross_family_reference(reference_payload: dict[str, Any]) -> dict[str, Any]:
    family_rows: dict[str, list[dict[str, Any]]] = {}
    for row in reference_payload.get("group_by_task_family_prompt_runtime", []):
        if not isinstance(row, dict):
            continue
        family = _normalize_task_family(str(row.get("task_family", "unknown")))
        family_rows.setdefault(family, []).append(row)

    by_task_family = {
        family: _evaluate_prompt_runtime_pattern(rows)
        for family, rows in sorted(family_rows.items())
    }
    return {
        "summary_path": str(reference_payload.get("_summary_json_path", "")),
        "by_task_family": by_task_family,
        "consistent_across_families": all(
            assessment.get("pattern_stable") is True for assessment in by_task_family.values()
        ),
    }


def _evaluate_navigation_difficulty(
    grouped_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    easy_rows = [
        row
        for row in grouped_rows
        if row.get("task_family") == "navigation" and row.get("task_difficulty") == "easy"
    ]
    harder_rows = [
        row
        for row in grouped_rows
        if row.get("task_family") == "navigation" and row.get("task_difficulty") == "harder"
    ]

    easy_assessment = _evaluate_prompt_runtime_pattern(easy_rows)
    harder_assessment = _evaluate_prompt_runtime_pattern(harder_rows)

    easy_map = {
        (str(row.get("prompt_variant")), str(row.get("runtime_variant"))): row
        for row in easy_rows
    }
    harder_map = {
        (str(row.get("prompt_variant")), str(row.get("runtime_variant"))): row
        for row in harder_rows
    }

    deltas: list[dict[str, Any]] = []
    shared_pairs = sorted(set(easy_map) & set(harder_map))
    for prompt_variant, runtime_variant in shared_pairs:
        easy_row = easy_map[(prompt_variant, runtime_variant)]
        harder_row = harder_map[(prompt_variant, runtime_variant)]
        deltas.append(
            {
                "prompt_variant": prompt_variant,
                "runtime_variant": runtime_variant,
                "easy_success_rate": easy_row.get("success_rate"),
                "harder_success_rate": harder_row.get("success_rate"),
                "success_rate_delta": _float_delta(
                    easy_row.get("success_rate"),
                    harder_row.get("success_rate"),
                ),
                "easy_average_planner_calls": easy_row.get("average_planner_calls"),
                "harder_average_planner_calls": harder_row.get("average_planner_calls"),
                "planner_call_delta": _float_delta(
                    easy_row.get("average_planner_calls"),
                    harder_row.get("average_planner_calls"),
                ),
                "easy_average_tool_calls": easy_row.get("average_tool_calls"),
                "harder_average_tool_calls": harder_row.get("average_tool_calls"),
                "tool_call_delta": _float_delta(
                    easy_row.get("average_tool_calls"),
                    harder_row.get("average_tool_calls"),
                ),
            }
        )

    successful_shared_deltas = [
        row
        for row in deltas
        if row.get("easy_success_rate") == 1.0 and row.get("harder_success_rate") == 1.0
    ]
    cost_only_increase = bool(
        easy_assessment.get("pattern_stable") is True
        and harder_assessment.get("pattern_stable") is True
        and successful_shared_deltas
        and all(
            isinstance(row.get("planner_call_delta"), (int, float))
            and isinstance(row.get("tool_call_delta"), (int, float))
            and row["planner_call_delta"] > 0
            and row["tool_call_delta"] > 0
            for row in successful_shared_deltas
        )
    )

    return {
        "easy_assessment": easy_assessment,
        "harder_assessment": harder_assessment,
        "shared_prompt_runtime_deltas": deltas,
        "cost_only_increase": cost_only_increase,
    }


def _evaluate_prompt_runtime_pattern(rows: list[dict[str, Any]]) -> dict[str, Any]:
    row_map = {
        (str(row.get("prompt_variant", "unknown")), str(row.get("runtime_variant", "unknown"))): row
        for row in rows
    }
    p0_r0 = row_map.get(("P0", "R0"))
    p0_r1 = row_map.get(("P0", "R1"))
    p1_r0 = row_map.get(("P1", "R0"))
    p1_r1 = row_map.get(("P1", "R1"))
    p2_r0 = row_map.get(("P2", "R0"))
    p2_r1 = row_map.get(("P2", "R1"))

    p0_r0_worst = bool(
        p0_r0
        and all(
            (row.get("success_rate") or 0.0) > (p0_r0.get("success_rate") or 0.0)
            for key, row in row_map.items()
            if key != ("P0", "R0")
        )
    )
    p0_r1_recovers = bool(p0_r1 and p0_r1.get("successful_runs") == p0_r1.get("run_count"))
    p1_p2_succeed = bool(
        all(
            row is not None and row.get("successful_runs") == row.get("run_count")
            for row in (p1_r0, p1_r1, p2_r0, p2_r1)
        )
    )
    p2_more_efficient = bool(
        p1_r0
        and p2_r0
        and p1_r1
        and p2_r1
        and (p2_r0.get("average_planner_calls") or 0.0) < (p1_r0.get("average_planner_calls") or 0.0)
        and (p2_r0.get("average_tool_calls") or 0.0) < (p1_r0.get("average_tool_calls") or 0.0)
        and (p2_r1.get("average_planner_calls") or 0.0) < (p1_r1.get("average_planner_calls") or 0.0)
        and (p2_r1.get("average_tool_calls") or 0.0) < (p1_r1.get("average_tool_calls") or 0.0)
    )
    return {
        "available_prompt_runtime_cells": sorted(
            f"{prompt_variant}/{runtime_variant}" for prompt_variant, runtime_variant in row_map
        ),
        "p0_r0_worst": p0_r0_worst,
        "p0_r1_recovers": p0_r1_recovers,
        "p1_p2_succeed": p1_p2_succeed,
        "p2_more_efficient": p2_more_efficient,
        "pattern_stable": bool(p0_r0_worst and p0_r1_recovers and p1_p2_succeed and p2_more_efficient),
    }


def _build_checkpoint_answers(
    *,
    source_slice_assessments: dict[str, dict[str, Any]],
    cross_family_reference: dict[str, Any],
    navigation_difficulty: dict[str, Any],
    coverage_rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    direct_slices_stable = bool(
        source_slice_assessments
        and all(assessment.get("pattern_stable") is True for assessment in source_slice_assessments.values())
    )
    cross_family_stable = bool(
        cross_family_reference.get("consistent_across_families") is True
        and source_slice_assessments.get("navigation_expanded", {}).get("pattern_stable") is True
        and source_slice_assessments.get("manipulation_pilot", {}).get("pattern_stable") is True
    )
    harder_navigation_cost_only = navigation_difficulty.get("cost_only_increase") is True

    manipulation_harder_present = any(
        row.get("task_family") == "manipulation" and row.get("task_difficulty") == "harder"
        for row in coverage_rows
    )
    manipulation_harder_necessary = bool(
        not manipulation_harder_present
        and not (direct_slices_stable and cross_family_stable and harder_navigation_cost_only)
    )
    next_step = (
        "paper_block_a_cleanup"
        if not manipulation_harder_necessary
        else "minimal_manipulation_harder_slice"
    )

    return {
        "q1_main_effect_stable": {
            "question": "Block A 的主效应是否已经稳定成立？",
            "answer": direct_slices_stable,
            "short_answer": "是" if direct_slices_stable else "否",
            "explanation": (
                "四个直接运行的 Block A slices 都满足相同排序：P0/R0 最差，P0/R1 能恢复，P1/P2 全成功，且 P2 比 P1 更省 planner/tool calls。"
                if direct_slices_stable
                else "至少有一个直接运行的 Block A slice 没有保持当前主效应排序。"
            ),
            "supporting_source_slices": sorted(source_slice_assessments),
        },
        "q2_cross_family_trends": {
            "question": "这些趋势是否跨 task families 成立？",
            "answer": cross_family_stable,
            "short_answer": "是" if cross_family_stable else "否",
            "explanation": (
                "是，在当前共享的 easy slice 上，navigation 和 manipulation 都保持相同趋势；现有 cross-family summary 也与这一结论一致。"
                if cross_family_stable
                else "当前跨 family 证据还不足以说明这些趋势稳定成立。"
            ),
            "scope_note": "harder 难度目前只有 navigation，有效的跨-family 对齐范围是 easy slice。",
        },
        "q3_harder_navigation_changes_conclusion": {
            "question": "harder navigation 是否改变了结论还是只增加了成本？",
            "answer": harder_navigation_cost_only,
            "short_answer": "只增加了成本，没有改变结论" if harder_navigation_cost_only else "结论存在变化或证据不足",
            "explanation": (
                "harder navigation 仍保持相同成功排序，但在共享成功单元上 planner/tool calls 系统性上升。"
                if harder_navigation_cost_only
                else "harder navigation 与 easy navigation 之间还没有形成“只增成本、不改排序”的稳定证据。"
            ),
            "shared_prompt_runtime_deltas": navigation_difficulty.get("shared_prompt_runtime_deltas", []),
        },
        "q4_manipulation_harder_slice_necessary": {
            "question": "manipulation harder slice 是否是当前必要缺口？",
            "answer": manipulation_harder_necessary,
            "short_answer": "是" if manipulation_harder_necessary else "否",
            "explanation": (
                "不是当前必要缺口。它是唯一尚未对称覆盖的 harder family，但现有 easy cross-family 结果和 navigation harder slice 已足以完成 Block A checkpoint。"
                if not manipulation_harder_necessary
                else "是当前必要缺口，因为缺少 manipulation harder slice 会直接影响 Block A checkpoint 的稳定判断。"
            ),
        },
        "q5_next_step": {
            "question": "下一步更合理的是：补 manipulation harder，还是进入 M7 / 论文整理？",
            "answer": next_step,
            "short_answer": (
                "先做 Block A 论文整理/结果固化，不优先补 manipulation harder。"
                if next_step == "paper_block_a_cleanup"
                else "先补最小 manipulation harder slice，再决定是否进入后续阶段。"
            ),
            "explanation": (
                "当前更合理的是先把 Block A 结果整理成稳定论文包，而不是继续扩实验；如果后续必须要 harder 难度的 family 对称性，再补一个最小 manipulation harder slice。"
                if next_step == "paper_block_a_cleanup"
                else "当前证据还不足以直接冻结 Block A，因此先补最小 manipulation harder slice 更稳妥。"
            ),
        },
    }


def _build_family_difficulty_pivot(
    rows: list[dict[str, Any]],
    *,
    metric_columns: tuple[str, ...],
) -> list[dict[str, Any]]:
    pivoted: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        prompt_variant = str(row.get("prompt_variant", "unknown"))
        runtime_variant = str(row.get("runtime_variant", "unknown"))
        task_family = str(row.get("task_family", "unknown"))
        task_difficulty = str(row.get("task_difficulty", "unknown"))
        cohort = _cohort_prefix(task_family, task_difficulty)
        pivot_row = pivoted.setdefault(
            (prompt_variant, runtime_variant),
            {
                "prompt_variant": prompt_variant,
                "runtime_variant": runtime_variant,
            },
        )
        for metric_name in metric_columns:
            pivot_row[f"{cohort}_{metric_name}"] = row.get(metric_name)
    return [pivoted[key] for key in sorted(pivoted)]


def _build_difficulty_comparison_table(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    row_map = {
        (
            str(row.get("task_family", "unknown")),
            str(row.get("task_difficulty", "unknown")),
            str(row.get("prompt_variant", "unknown")),
            str(row.get("runtime_variant", "unknown")),
        ): row
        for row in rows
    }

    prompt_runtime_pairs = sorted(
        {
            (str(row.get("prompt_variant", "unknown")), str(row.get("runtime_variant", "unknown")))
            for row in rows
        }
    )
    comparison_rows: list[dict[str, Any]] = []
    for task_family in ("navigation", "manipulation"):
        for prompt_variant, runtime_variant in prompt_runtime_pairs:
            easy_row = row_map.get((task_family, "easy", prompt_variant, runtime_variant))
            harder_row = row_map.get((task_family, "harder", prompt_variant, runtime_variant))
            comparison_rows.append(
                {
                    "task_family": task_family,
                    "task_family_display": _task_family_display(task_family),
                    "prompt_variant": prompt_variant,
                    "runtime_variant": runtime_variant,
                    "easy_run_count": easy_row.get("run_count") if easy_row else 0,
                    "harder_run_count": harder_row.get("run_count") if harder_row else 0,
                    "easy_success_rate": easy_row.get("success_rate") if easy_row else None,
                    "harder_success_rate": harder_row.get("success_rate") if harder_row else None,
                    "success_rate_delta": _float_delta(
                        easy_row.get("success_rate") if easy_row else None,
                        harder_row.get("success_rate") if harder_row else None,
                    ),
                    "easy_average_planner_calls": easy_row.get("average_planner_calls") if easy_row else None,
                    "harder_average_planner_calls": (
                        harder_row.get("average_planner_calls") if harder_row else None
                    ),
                    "planner_call_delta": _float_delta(
                        easy_row.get("average_planner_calls") if easy_row else None,
                        harder_row.get("average_planner_calls") if harder_row else None,
                    ),
                    "easy_average_tool_calls": easy_row.get("average_tool_calls") if easy_row else None,
                    "harder_average_tool_calls": harder_row.get("average_tool_calls") if harder_row else None,
                    "tool_call_delta": _float_delta(
                        easy_row.get("average_tool_calls") if easy_row else None,
                        harder_row.get("average_tool_calls") if harder_row else None,
                    ),
                    "easy_average_episode_time_s": easy_row.get("average_episode_time_s") if easy_row else None,
                    "harder_average_episode_time_s": (
                        harder_row.get("average_episode_time_s") if harder_row else None
                    ),
                    "episode_time_delta": _float_delta(
                        easy_row.get("average_episode_time_s") if easy_row else None,
                        harder_row.get("average_episode_time_s") if harder_row else None,
                    ),
                    "comparison_status": _comparison_status(easy_row, harder_row),
                }
            )
    return comparison_rows


def _write_master_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_MASTER_CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            csv_row["termination_reasons"] = json.dumps(row.get("termination_reasons", {}), sort_keys=True)
            writer.writerow({column: csv_row.get(column) for column in _MASTER_CSV_COLUMNS})


def _render_master_markdown(summary: dict[str, Any]) -> str:
    answers = summary["answers"]
    lines = [
        f"# {summary['summary_title']}",
        "",
        f"- Output dir: `{summary['output_dir']}`",
        f"- Direct processed sources: `{len(summary['processed_sources'])}`",
        f"- Reference summaries: `{len(summary['reference_summaries'])}`",
        f"- Merged runs: `{summary['overall']['merged_runs']}`",
        f"- Run-complete runs: `{summary['overall']['run_complete_runs']}`",
        f"- Successful runs: `{summary['overall']['successful_runs']}`",
        f"- Success rate: `{summary['overall']['success_rate']}`",
        f"- Total invalid actions: `{summary['overall']['total_invalid_actions']}`",
        f"- Total retries: `{summary['overall']['total_retries']}`",
        "",
        summary["description"],
        "",
        "## Source Inputs",
        "",
        _render_markdown_table(
            summary["processed_sources"],
            columns=[
                "source_slice_display",
                "task_difficulty_display",
                "run_count",
                "task_families",
                "input_dir",
            ],
        ),
        "",
        "## Reference Summaries",
        "",
        _render_markdown_table(
            summary["reference_summaries"],
            columns=[
                "source_name",
                "task_families",
                "prompt_runtime_cell_count",
                "summary_json_path",
            ],
        ),
        "",
        "## Coverage",
        "",
        _render_markdown_table(
            summary["coverage"],
            columns=[
                "task_family_display",
                "task_difficulty_display",
                "run_count",
                "task_count",
                "prompt_runtime_cell_count",
                "source_slices",
            ],
        ),
        "",
        "## Checkpoint Answers",
        "",
        f"1. {answers['q1_main_effect_stable']['question']}",
        f"   {answers['q1_main_effect_stable']['short_answer']}。{answers['q1_main_effect_stable']['explanation']}",
        f"2. {answers['q2_cross_family_trends']['question']}",
        f"   {answers['q2_cross_family_trends']['short_answer']}。{answers['q2_cross_family_trends']['explanation']} {answers['q2_cross_family_trends']['scope_note']}",
        f"3. {answers['q3_harder_navigation_changes_conclusion']['question']}",
        f"   {answers['q3_harder_navigation_changes_conclusion']['short_answer']}。{answers['q3_harder_navigation_changes_conclusion']['explanation']}",
        f"4. {answers['q4_manipulation_harder_slice_necessary']['question']}",
        f"   {answers['q4_manipulation_harder_slice_necessary']['short_answer']}。{answers['q4_manipulation_harder_slice_necessary']['explanation']}",
        f"5. {answers['q5_next_step']['question']}",
        f"   {answers['q5_next_step']['short_answer']} {answers['q5_next_step']['explanation']}",
        "",
        "## Table 1: Main Success",
        "",
        _render_markdown_table(
            summary["tables"]["main_success_table"],
            columns=[
                "prompt_variant",
                "runtime_variant",
                "navigation_easy_run_count",
                "navigation_easy_success_rate",
                "navigation_harder_run_count",
                "navigation_harder_success_rate",
                "manipulation_easy_run_count",
                "manipulation_easy_success_rate",
            ],
        ),
        "",
        "## Table 2: Invalid Actions",
        "",
        _render_markdown_table(
            summary["tables"]["invalid_action_table"],
            columns=[
                "prompt_variant",
                "runtime_variant",
                "navigation_easy_average_invalid_actions",
                "navigation_easy_invalid_action_run_rate",
                "navigation_harder_average_invalid_actions",
                "navigation_harder_invalid_action_run_rate",
                "manipulation_easy_average_invalid_actions",
                "manipulation_easy_invalid_action_run_rate",
            ],
        ),
        "",
        "## Table 3: Efficiency",
        "",
        _render_markdown_table(
            summary["tables"]["efficiency_table"],
            columns=[
                "prompt_variant",
                "runtime_variant",
                "navigation_easy_average_planner_calls",
                "navigation_easy_average_tool_calls",
                "navigation_harder_average_planner_calls",
                "navigation_harder_average_tool_calls",
                "manipulation_easy_average_planner_calls",
                "manipulation_easy_average_tool_calls",
            ],
        ),
        "",
        "## Table 4: Recovery",
        "",
        _render_markdown_table(
            summary["tables"]["recovery_table"],
            columns=[
                "prompt_variant",
                "runtime_variant",
                "navigation_easy_invalid_action_run_count",
                "navigation_easy_successful_invalid_action_runs",
                "navigation_easy_recovery_success_rate",
                "navigation_harder_invalid_action_run_count",
                "navigation_harder_successful_invalid_action_runs",
                "navigation_harder_recovery_success_rate",
                "manipulation_easy_invalid_action_run_count",
                "manipulation_easy_successful_invalid_action_runs",
                "manipulation_easy_recovery_success_rate",
            ],
        ),
        "",
        "## Table 5: Difficulty Comparison",
        "",
        _render_markdown_table(
            summary["tables"]["difficulty_comparison_table"],
            columns=[
                "task_family_display",
                "prompt_variant",
                "runtime_variant",
                "easy_success_rate",
                "harder_success_rate",
                "planner_call_delta",
                "tool_call_delta",
                "comparison_status",
            ],
        ),
        "",
        "## Notes",
        "",
        "- `easy` currently aggregates the navigation easy pilot, navigation expanded slice, and manipulation pilot.",
        "- `harder` currently aggregates only the navigation robustness slice.",
        "- `Manipulation` rows normalize the canonical run-level `task_family=pick_place` values into a paper-facing label.",
        "- The existing cross-family summary is used as a reference consistency check and is not counted as extra runs in the merged totals.",
    ]
    return "\n".join(lines) + "\n"


def _render_markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_None_"
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join(_format_markdown_cell(row.get(column)) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, divider, *body])


def _format_markdown_cell(value: Any) -> str:
    if isinstance(value, dict):
        return ", ".join(f"{key}:{value[key]}" for key in sorted(value)) or "none"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or "none"
    if value is None:
        return ""
    return str(value)


def _ensure_unique_run_ids(summaries: list[EpisodeSummary]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for summary in summaries:
        if summary.run_id in seen:
            duplicates.add(summary.run_id)
        seen.add(summary.run_id)
    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        raise ValueError(f"duplicate run_id values found while merging summaries: {duplicate_list}")


def _summary_sort_key(summary: EpisodeSummary) -> tuple[tuple[int, str], tuple[int, str], str, str]:
    return (
        _field_sort_value("task_family", _normalize_task_family(summary.task_family or "unknown")),
        _field_sort_value("prompt_variant", summary.prompt_variant or "unknown"),
        _field_sort_value("runtime_variant", summary.runtime_variant or "unknown"),
        summary.run_id,
    )


def _group_key_sort_key(group_fields: tuple[str, ...], key: tuple[str, ...]) -> tuple[tuple[int, str], ...]:
    return tuple(_field_sort_value(field_name, field_value) for field_name, field_value in zip(group_fields, key))


def _row_field_value(row: dict[str, Any], field_name: str) -> str:
    value = row.get(field_name)
    if isinstance(value, str) and value:
        return value
    if value is None:
        return "unknown"
    return str(value)


def _field_sort_value(field_name: str, value: str) -> tuple[int, str]:
    if field_name == "task_family":
        order = {"navigation": 0, "manipulation": 1}.get(value, 99)
        return (order, _task_family_display(value))
    if field_name == "task_difficulty":
        order = {"easy": 0, "harder": 1}.get(value, 99)
        return (order, _task_difficulty_display(value))
    if field_name == "source_slice":
        try:
            return (_SOURCE_SLICE_ORDER.index(value), _source_slice_display(value))
        except ValueError:
            return (99, _source_slice_display(value))
    return (0, value)


def _normalize_task_family(task_family: str) -> str:
    return _TASK_FAMILY_NORMALIZATION.get(task_family, task_family)


def _task_family_display(task_family: str) -> str:
    return _TASK_FAMILY_DISPLAY.get(task_family, task_family.replace("_", " ").title())


def _task_difficulty_display(task_difficulty: str) -> str:
    return _TASK_DIFFICULTY_DISPLAY.get(task_difficulty, task_difficulty.replace("_", " ").title())


def _source_slice_display(source_slice: str) -> str:
    return _SOURCE_SLICE_DISPLAY.get(source_slice, source_slice.replace("_", " ").title())


def _cohort_prefix(task_family: str, task_difficulty: str) -> str:
    return f"{task_family}_{task_difficulty}"


def _comparison_status(easy_row: dict[str, Any] | None, harder_row: dict[str, Any] | None) -> str:
    if easy_row and harder_row:
        return "matched"
    if easy_row and not harder_row:
        return "missing_harder_slice"
    if harder_row and not easy_row:
        return "missing_easy_reference"
    return "missing_both"


def _float_delta(
    easy_value: Any,
    harder_value: Any,
) -> float | None:
    if not isinstance(easy_value, (int, float)) or not isinstance(harder_value, (int, float)):
        return None
    return round(float(harder_value) - float(easy_value), 6)


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None
