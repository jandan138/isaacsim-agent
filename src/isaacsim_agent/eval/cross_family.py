"""Cross-family post-processing over existing processed block A summaries."""

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


_TASK_FAMILY_DISPLAY = {
    "navigation": "Navigation",
    "pick_place": "Manipulation",
}

_TASK_FAMILY_PIVOT_PREFIX = {
    "navigation": "navigation",
    "pick_place": "manipulation",
}

_CROSS_FAMILY_CSV_COLUMNS = [
    "task_family",
    "task_family_display",
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
    "termination_reasons",
]


@dataclass(frozen=True)
class ProcessedSummarySource:
    """One processed summary directory used as an input source."""

    input_dir: Path
    run_summary_jsonl_path: Path
    validation_json_path: Path
    run_count: int
    task_families: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_dir": str(self.input_dir.resolve()),
            "run_summary_jsonl_path": str(self.run_summary_jsonl_path.resolve()),
            "validation_json_path": str(self.validation_json_path.resolve()),
            "run_count": self.run_count,
            "task_families": list(self.task_families),
        }


@dataclass(frozen=True)
class CrossFamilySummaryResult:
    """Materialized cross-family summary outputs."""

    input_dirs: list[Path]
    output_dir: Path
    sources: list[ProcessedSummarySource]
    bundle: SummaryBundle
    summary: dict[str, Any]
    written_outputs: dict[str, Path]


def summarize_cross_family_processed_dirs(
    input_dirs: list[str | Path],
    output_dir: str | Path,
) -> CrossFamilySummaryResult:
    """Merge processed block A summaries and write combined cross-family outputs."""

    if len(input_dirs) < 2:
        raise ValueError("cross-family summary requires at least two processed input directories")

    output_dir = Path(output_dir)
    sources, summaries, validations = _load_processed_summary_dirs(input_dirs)
    _ensure_unique_run_ids(summaries)

    bundle = SummaryBundle(
        summaries=summaries,
        validations=validations,
        aggregate=aggregate_episode_summaries(summaries),
    )
    written_outputs = write_summary_outputs(bundle=bundle, output_dir=output_dir)

    summary = build_cross_family_summary(
        bundle=bundle,
        sources=sources,
        output_dir=output_dir,
    )

    summary_json_path = output_dir / "cross_family_summary.json"
    summary_json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    written_outputs["cross_family_summary_json"] = summary_json_path

    summary_csv_path = output_dir / "cross_family_summary.csv"
    _write_cross_family_csv(summary_csv_path, summary["group_by_task_family_prompt_runtime"])
    written_outputs["cross_family_summary_csv"] = summary_csv_path

    summary_md_path = output_dir / "block_a_cross_family_summary.md"
    summary_md_path.write_text(_render_cross_family_markdown(summary), encoding="utf-8")
    written_outputs["cross_family_summary_md"] = summary_md_path

    return CrossFamilySummaryResult(
        input_dirs=[Path(path) for path in input_dirs],
        output_dir=output_dir,
        sources=sources,
        bundle=bundle,
        summary=summary,
        written_outputs=written_outputs,
    )


def build_cross_family_summary(
    bundle: SummaryBundle,
    sources: list[ProcessedSummarySource],
    output_dir: str | Path,
) -> dict[str, Any]:
    """Build the structured cross-family summary payload."""

    grouped_rows = _aggregate_summary_rows(
        summaries=bundle.summaries,
        group_fields=("task_family", "prompt_variant", "runtime_variant"),
    )
    by_task_family = _aggregate_summary_rows(
        summaries=bundle.summaries,
        group_fields=("task_family",),
    )
    by_prompt_runtime = _aggregate_summary_rows(
        summaries=bundle.summaries,
        group_fields=("prompt_variant", "runtime_variant"),
    )

    return {
        "summary_title": "Block A Cross-Family Summary",
        "description": (
            "Combined navigation and manipulation block A results built from the existing processed "
            "run summaries without launching new experiments."
        ),
        "output_dir": str(Path(output_dir).resolve()),
        "sources": [source.to_dict() for source in sources],
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
        "group_by_task_family": by_task_family,
        "group_by_prompt_runtime": by_prompt_runtime,
        "group_by_task_family_prompt_runtime": grouped_rows,
        "tables": {
            "table_1_success_rate": _build_pivot_table_rows(
                grouped_rows,
                metric_columns=(
                    "run_count",
                    "success_rate",
                ),
            ),
            "table_2_invalid_action_frequency": _build_pivot_table_rows(
                grouped_rows,
                metric_columns=(
                    "average_invalid_actions",
                    "invalid_action_run_rate",
                ),
            ),
            "table_3_planner_tool_efficiency": _build_pivot_table_rows(
                grouped_rows,
                metric_columns=(
                    "average_planner_calls",
                    "average_tool_calls",
                    "average_retries",
                ),
            ),
        },
    }


def _load_processed_summary_dirs(
    input_dirs: list[str | Path],
) -> tuple[list[ProcessedSummarySource], list[EpisodeSummary], list[RunValidation]]:
    sources: list[ProcessedSummarySource] = []
    summaries: list[EpisodeSummary] = []
    validations: list[RunValidation] = []

    for input_dir_value in input_dirs:
        input_dir = Path(input_dir_value)
        summary_jsonl_path = input_dir / "run_summary.jsonl"
        validation_json_path = input_dir / "validation.json"
        if not summary_jsonl_path.is_file():
            raise FileNotFoundError(f"missing run_summary.jsonl in processed directory: {input_dir}")
        if not validation_json_path.is_file():
            raise FileNotFoundError(f"missing validation.json in processed directory: {input_dir}")

        source_summaries = _load_episode_summaries(summary_jsonl_path)
        source_validations = _load_validations(validation_json_path)

        sources.append(
            ProcessedSummarySource(
                input_dir=input_dir,
                run_summary_jsonl_path=summary_jsonl_path,
                validation_json_path=validation_json_path,
                run_count=len(source_summaries),
                task_families=sorted({summary.task_family or "unknown" for summary in source_summaries}),
            )
        )
        summaries.extend(source_summaries)
        validations.extend(source_validations)

    summaries.sort(key=_summary_sort_key)
    validations.sort(key=lambda item: item.run_id)
    return sources, summaries, validations


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


def _aggregate_summary_rows(
    summaries: list[EpisodeSummary],
    group_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[EpisodeSummary]] = {}
    for summary in summaries:
        key = tuple(_summary_field_value(summary, field_name) for field_name in group_fields)
        grouped.setdefault(key, []).append(summary)

    rows: list[dict[str, Any]] = []
    for key in sorted(grouped, key=_group_key_sort_key):
        group_summaries = grouped[key]
        row = {field_name: value for field_name, value in zip(group_fields, key)}
        if "task_family" in row:
            row["task_family_display"] = _task_family_display(row["task_family"])
        row.update(_build_group_metrics(group_summaries))
        rows.append(row)
    return rows


def _build_group_metrics(summaries: list[EpisodeSummary]) -> dict[str, Any]:
    run_count = len(summaries)
    successful_runs = sum(1 for summary in summaries if summary.success is True)
    invalid_action_run_count = sum(1 for summary in summaries if (summary.invalid_actions or 0) > 0)

    total_planner_calls = sum(summary.planner_calls or 0 for summary in summaries)
    total_tool_calls = sum(summary.tool_calls or 0 for summary in summaries)
    total_invalid_actions = sum(summary.invalid_actions or 0 for summary in summaries)
    total_retries = sum(summary.retries or 0 for summary in summaries)

    termination_reasons: dict[str, int] = {}
    for summary in summaries:
        if summary.termination_reason:
            termination_reasons[summary.termination_reason] = termination_reasons.get(summary.termination_reason, 0) + 1

    return {
        "run_count": run_count,
        "contract_complete_runs": sum(1 for summary in summaries if summary.contract_complete),
        "run_complete_runs": sum(1 for summary in summaries if summary.run_complete),
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
        "termination_reasons": termination_reasons,
        "run_ids": [summary.run_id for summary in summaries],
    }


def _build_pivot_table_rows(
    rows: list[dict[str, Any]],
    metric_columns: tuple[str, ...],
) -> list[dict[str, Any]]:
    pivoted: dict[tuple[str, str], dict[str, Any]] = {}

    for row in rows:
        prompt_variant = str(row.get("prompt_variant", "unknown"))
        runtime_variant = str(row.get("runtime_variant", "unknown"))
        pivot_key = (prompt_variant, runtime_variant)
        pivot_row = pivoted.setdefault(
            pivot_key,
            {
                "prompt_variant": prompt_variant,
                "runtime_variant": runtime_variant,
            },
        )

        task_family = str(row.get("task_family", "unknown"))
        prefix = _TASK_FAMILY_PIVOT_PREFIX.get(task_family, task_family)
        for metric_name in metric_columns:
            pivot_row[f"{prefix}_{metric_name}"] = row.get(metric_name)

    return [pivoted[key] for key in sorted(pivoted)]


def _write_cross_family_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_CROSS_FAMILY_CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            csv_row["termination_reasons"] = json.dumps(row.get("termination_reasons", {}), sort_keys=True)
            writer.writerow({column: csv_row.get(column) for column in _CROSS_FAMILY_CSV_COLUMNS})


def _render_cross_family_markdown(summary: dict[str, Any]) -> str:
    lines = [
        f"# {summary['summary_title']}",
        "",
        f"- Output dir: `{summary['output_dir']}`",
        f"- Source summaries: `{len(summary['sources'])}`",
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
            summary["sources"],
            columns=[
                "input_dir",
                "run_count",
                "task_families",
            ],
        ),
        "",
        "## Table 1: Success rate (Navigation vs Manipulation)",
        "",
        _render_markdown_table(
            summary["tables"]["table_1_success_rate"],
            columns=[
                "prompt_variant",
                "runtime_variant",
                "navigation_run_count",
                "navigation_success_rate",
                "manipulation_run_count",
                "manipulation_success_rate",
            ],
        ),
        "",
        "## Table 2: Invalid action frequency",
        "",
        _render_markdown_table(
            summary["tables"]["table_2_invalid_action_frequency"],
            columns=[
                "prompt_variant",
                "runtime_variant",
                "navigation_average_invalid_actions",
                "navigation_invalid_action_run_rate",
                "manipulation_average_invalid_actions",
                "manipulation_invalid_action_run_rate",
            ],
        ),
        "",
        "## Table 3: Planner / tool efficiency",
        "",
        _render_markdown_table(
            summary["tables"]["table_3_planner_tool_efficiency"],
            columns=[
                "prompt_variant",
                "runtime_variant",
                "navigation_average_planner_calls",
                "navigation_average_tool_calls",
                "navigation_average_retries",
                "manipulation_average_planner_calls",
                "manipulation_average_tool_calls",
                "manipulation_average_retries",
            ],
        ),
        "",
        "## Notes",
        "",
        "- `Manipulation` rows correspond to canonical `task_family=pick_place` in the merged run summaries.",
        "- `Navigation` rows aggregate both `toy` and `isaac` backend variants; `Manipulation` rows are currently `toy` only.",
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


def _summary_field_value(summary: EpisodeSummary, field_name: str) -> str:
    value = getattr(summary, field_name)
    if isinstance(value, str) and value:
        return value
    if value is None:
        return "unknown"
    return str(value)


def _summary_sort_key(summary: EpisodeSummary) -> tuple[str, str, str, str]:
    return (
        _task_family_display(summary.task_family or "unknown"),
        summary.prompt_variant or "unknown",
        summary.runtime_variant or "unknown",
        summary.run_id,
    )


def _group_key_sort_key(key: tuple[str, ...]) -> tuple[str, ...]:
    normalized = list(key)
    if normalized:
        normalized[0] = _task_family_display(normalized[0])
    return tuple(normalized)


def _task_family_display(task_family: str) -> str:
    return _TASK_FAMILY_DISPLAY.get(task_family, task_family.replace("_", " ").title())


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None
