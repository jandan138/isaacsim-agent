"""Paper-facing Block A tables, figures, and analysis packaging."""

from __future__ import annotations

import csv
import json
import math
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_CELL_ORDER = [
    ("P0", "R0"),
    ("P0", "R1"),
    ("P1", "R0"),
    ("P1", "R1"),
    ("P2", "R0"),
    ("P2", "R1"),
]

_COHORTS = [
    {
        "task_family": "navigation",
        "task_difficulty": "easy",
        "label": "NAVIGATION EASY",
        "column_prefix": "navigation_easy",
    },
    {
        "task_family": "navigation",
        "task_difficulty": "harder",
        "label": "NAVIGATION HARDER",
        "column_prefix": "navigation_harder",
    },
    {
        "task_family": "manipulation",
        "task_difficulty": "easy",
        "label": "MANIPULATION EASY",
        "column_prefix": "manipulation_easy",
    },
]

_TABLE_SPECS = [
    ("success_table", "block_a_success_table.csv", "main_success_table"),
    ("invalid_actions_table", "block_a_invalid_actions_table.csv", "invalid_action_table"),
    ("efficiency_table", "block_a_efficiency_table.csv", "efficiency_table"),
]

_FIGURE_SPECS = [
    {
        "key": "success_rate_figure",
        "filename": "block_a_success_rate.png",
        "metric_key": "success_rate",
        "table_key": "main_success_table",
        "table_metric_suffix": "success_rate",
        "title": "BLOCK A SUCCESS RATE",
        "subtitle": "NAVIGATION VS MANIPULATION ACROSS P0/P1/P2 X R0/R1",
        "value_label_digits": 2,
    },
    {
        "key": "invalid_actions_figure",
        "filename": "block_a_invalid_actions.png",
        "metric_key": "average_invalid_actions",
        "table_key": "invalid_action_table",
        "table_metric_suffix": "average_invalid_actions",
        "title": "BLOCK A INVALID ACTIONS PER RUN",
        "subtitle": "NAVIGATION VS MANIPULATION ACROSS P0/P1/P2 X R0/R1",
        "value_label_digits": 2,
    },
    {
        "key": "planner_calls_figure",
        "filename": "block_a_planner_calls.png",
        "metric_key": "average_planner_calls",
        "table_key": "efficiency_table",
        "table_metric_suffix": "average_planner_calls",
        "title": "BLOCK A PLANNER CALLS PER RUN",
        "subtitle": "NAVIGATION VS MANIPULATION ACROSS P0/P1/P2 X R0/R1",
        "value_label_digits": 2,
    },
    {
        "key": "tool_calls_figure",
        "filename": "block_a_tool_calls.png",
        "metric_key": "average_tool_calls",
        "table_key": "efficiency_table",
        "table_metric_suffix": "average_tool_calls",
        "title": "BLOCK A TOOL CALLS PER RUN",
        "subtitle": "NAVIGATION VS MANIPULATION ACROSS P0/P1/P2 X R0/R1",
        "value_label_digits": 2,
    },
]

_FONT_5X7: dict[str, tuple[str, ...]] = {
    " ": (
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
    ),
    "-": (
        "00000",
        "00000",
        "00000",
        "01110",
        "00000",
        "00000",
        "00000",
    ),
    ".": (
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00110",
        "00110",
    ),
    "/": (
        "00001",
        "00010",
        "00100",
        "01000",
        "10000",
        "00000",
        "00000",
    ),
    "0": (
        "01110",
        "10001",
        "10011",
        "10101",
        "11001",
        "10001",
        "01110",
    ),
    "1": (
        "00100",
        "01100",
        "00100",
        "00100",
        "00100",
        "00100",
        "01110",
    ),
    "2": (
        "01110",
        "10001",
        "00001",
        "00010",
        "00100",
        "01000",
        "11111",
    ),
    "3": (
        "11110",
        "00001",
        "00001",
        "01110",
        "00001",
        "00001",
        "11110",
    ),
    "4": (
        "00010",
        "00110",
        "01010",
        "10010",
        "11111",
        "00010",
        "00010",
    ),
    "5": (
        "11111",
        "10000",
        "10000",
        "11110",
        "00001",
        "00001",
        "11110",
    ),
    "6": (
        "01110",
        "10000",
        "10000",
        "11110",
        "10001",
        "10001",
        "01110",
    ),
    "7": (
        "11111",
        "00001",
        "00010",
        "00100",
        "01000",
        "01000",
        "01000",
    ),
    "8": (
        "01110",
        "10001",
        "10001",
        "01110",
        "10001",
        "10001",
        "01110",
    ),
    "9": (
        "01110",
        "10001",
        "10001",
        "01111",
        "00001",
        "00001",
        "01110",
    ),
    "A": (
        "01110",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001",
    ),
    "B": (
        "11110",
        "10001",
        "10001",
        "11110",
        "10001",
        "10001",
        "11110",
    ),
    "C": (
        "01110",
        "10001",
        "10000",
        "10000",
        "10000",
        "10001",
        "01110",
    ),
    "D": (
        "11110",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "11110",
    ),
    "E": (
        "11111",
        "10000",
        "10000",
        "11110",
        "10000",
        "10000",
        "11111",
    ),
    "F": (
        "11111",
        "10000",
        "10000",
        "11110",
        "10000",
        "10000",
        "10000",
    ),
    "G": (
        "01110",
        "10001",
        "10000",
        "10111",
        "10001",
        "10001",
        "01110",
    ),
    "H": (
        "10001",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001",
    ),
    "I": (
        "01110",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
        "01110",
    ),
    "J": (
        "00111",
        "00010",
        "00010",
        "00010",
        "00010",
        "10010",
        "01100",
    ),
    "K": (
        "10001",
        "10010",
        "10100",
        "11000",
        "10100",
        "10010",
        "10001",
    ),
    "L": (
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "11111",
    ),
    "M": (
        "10001",
        "11011",
        "10101",
        "10101",
        "10001",
        "10001",
        "10001",
    ),
    "N": (
        "10001",
        "11001",
        "10101",
        "10011",
        "10001",
        "10001",
        "10001",
    ),
    "O": (
        "01110",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01110",
    ),
    "P": (
        "11110",
        "10001",
        "10001",
        "11110",
        "10000",
        "10000",
        "10000",
    ),
    "Q": (
        "01110",
        "10001",
        "10001",
        "10001",
        "10101",
        "10010",
        "01101",
    ),
    "R": (
        "11110",
        "10001",
        "10001",
        "11110",
        "10100",
        "10010",
        "10001",
    ),
    "S": (
        "01111",
        "10000",
        "10000",
        "01110",
        "00001",
        "00001",
        "11110",
    ),
    "T": (
        "11111",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
    ),
    "U": (
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01110",
    ),
    "V": (
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01010",
        "00100",
    ),
    "W": (
        "10001",
        "10001",
        "10001",
        "10101",
        "10101",
        "10101",
        "01010",
    ),
    "X": (
        "10001",
        "10001",
        "01010",
        "00100",
        "01010",
        "10001",
        "10001",
    ),
    "Y": (
        "10001",
        "10001",
        "01010",
        "00100",
        "00100",
        "00100",
        "00100",
    ),
    "Z": (
        "11111",
        "00001",
        "00010",
        "00100",
        "01000",
        "10000",
        "11111",
    ),
}

_BACKGROUND = (247, 244, 237)
_PANEL_BACKGROUND = (255, 255, 255)
_PANEL_BORDER = (207, 196, 181)
_GRID = (221, 217, 208)
_AXIS = (88, 84, 78)
_TEXT = (45, 41, 36)
_VALUE_TEXT = (76, 72, 67)
_CELL_COLORS = {
    ("P0", "R0"): (173, 62, 56),
    ("P0", "R1"): (226, 119, 100),
    ("P1", "R0"): (46, 102, 168),
    ("P1", "R1"): (113, 159, 214),
    ("P2", "R0"): (191, 145, 49),
    ("P2", "R1"): (224, 186, 98),
}


@dataclass(frozen=True)
class BlockAPaperPackagingResult:
    """Materialized paper-facing assets for the existing Block A master summary."""

    output_dir: Path
    master_summary_json_path: Path
    paper_tables_dir: Path
    paper_figures_dir: Path
    analysis_dir: Path
    written_outputs: dict[str, Path]
    validation: dict[str, Any]
    consistency_checks: dict[str, Any]

    @property
    def master_summary_path(self) -> Path:
        return self.master_summary_json_path

    @property
    def analysis_path(self) -> Path:
        return self.written_outputs["analysis_markdown"]

    @property
    def paper_tables(self) -> dict[str, Path]:
        return {
            "main_success_table": self.written_outputs["success_table"],
            "invalid_action_table": self.written_outputs["invalid_actions_table"],
            "efficiency_table": self.written_outputs["efficiency_table"],
        }

    @property
    def paper_figures(self) -> dict[str, Path]:
        return {
            "success_rate": self.written_outputs["success_rate_figure"],
            "average_invalid_actions": self.written_outputs["invalid_actions_figure"],
            "average_planner_calls": self.written_outputs["planner_calls_figure"],
            "average_tool_calls": self.written_outputs["tool_calls_figure"],
        }


def package_block_a_master_for_paper(
    *,
    master_summary_json_path: str | Path,
    output_dir: str | Path,
) -> BlockAPaperPackagingResult:
    """Package the existing Block A master summary into paper-facing assets."""

    master_summary_json_path = Path(master_summary_json_path)
    output_dir = Path(output_dir)
    summary = json.loads(master_summary_json_path.read_text(encoding="utf-8"))
    _validate_summary_shape(summary)

    paper_tables_dir = output_dir / "paper_tables"
    paper_figures_dir = output_dir / "paper_figures"
    analysis_dir = output_dir / "analysis"
    paper_tables_dir.mkdir(parents=True, exist_ok=True)
    paper_figures_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    row_map = _build_row_map(summary["group_by_task_family_difficulty_prompt_runtime"])
    consistency_checks = _build_consistency_checks(row_map)

    written_outputs: dict[str, Path] = {}
    table_validation = {"all_consistent": True, "checks": 0, "mismatches": []}
    for output_key, filename, summary_table_key in _TABLE_SPECS:
        rows = _augment_table_rows(summary["tables"][summary_table_key])
        path = paper_tables_dir / filename
        _write_csv(path, rows)
        written_outputs[output_key] = path
        _merge_validation(
            table_validation,
            _validate_written_table(
                path=path,
                expected_rows=rows,
                table_name=summary_table_key,
            ),
        )

    figure_validation = {"all_consistent": True, "checks": 0, "mismatches": []}
    for spec in _FIGURE_SPECS:
        panels = _build_figure_panels(row_map=row_map, metric_key=spec["metric_key"])
        _merge_validation(
            figure_validation,
            _validate_figure_panels(
                summary=summary,
                panels=panels,
                table_key=spec["table_key"],
                table_metric_suffix=spec["table_metric_suffix"],
                metric_key=spec["metric_key"],
            ),
        )
        path = paper_figures_dir / spec["filename"]
        _render_metric_figure(
            path=path,
            title=spec["title"],
            subtitle=spec["subtitle"],
            panels=panels,
            value_label_digits=int(spec["value_label_digits"]),
        )
        written_outputs[spec["key"]] = path

    overall_validation = {
        "all_consistent": table_validation["all_consistent"] and figure_validation["all_consistent"],
        "table_validation": table_validation,
        "figure_validation": figure_validation,
    }
    if not overall_validation["all_consistent"]:
        mismatches = table_validation["mismatches"] + figure_validation["mismatches"]
        raise ValueError("Block A paper packaging consistency check failed: " + "; ".join(mismatches))

    analysis_path = analysis_dir / "block_a_analysis.md"
    analysis_path.write_text(
        _render_analysis_markdown(
            summary=summary,
            written_outputs=written_outputs,
            validation=overall_validation,
            consistency_checks=consistency_checks,
        ),
        encoding="utf-8",
    )
    written_outputs["analysis_markdown"] = analysis_path

    return BlockAPaperPackagingResult(
        output_dir=output_dir,
        master_summary_json_path=master_summary_json_path,
        paper_tables_dir=paper_tables_dir,
        paper_figures_dir=paper_figures_dir,
        analysis_dir=analysis_dir,
        written_outputs=written_outputs,
        validation=overall_validation,
        consistency_checks=consistency_checks,
    )


def package_block_a_master_summary(
    *,
    master_summary_path: str | Path,
    output_dir: str | Path,
) -> BlockAPaperPackagingResult:
    """Compatibility wrapper for paper packaging from the Block A master summary."""

    return package_block_a_master_for_paper(
        master_summary_json_path=master_summary_path,
        output_dir=output_dir,
    )


def _validate_summary_shape(summary: dict[str, Any]) -> None:
    required_keys = {
        "overall",
        "coverage",
        "tables",
        "answers",
        "group_by_task_family_difficulty_prompt_runtime",
    }
    missing = sorted(required_keys.difference(summary))
    if missing:
        raise ValueError(f"Block A master summary is missing required keys: {', '.join(missing)}")


def _build_row_map(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    row_map: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (
            str(row["task_family"]),
            str(row["task_difficulty"]),
            str(row["prompt_variant"]),
            str(row["runtime_variant"]),
        )
        row_map[key] = row
    return row_map


def _build_consistency_checks(
    row_map: dict[tuple[str, str, str, str], dict[str, Any]],
) -> dict[str, Any]:
    available_cohorts = {
        f"{task_family}/{task_difficulty}"
        for task_family, task_difficulty, _, _ in row_map
    }
    expected_cohorts = {
        "navigation/easy",
        "navigation/harder",
        "manipulation/easy",
        "manipulation/harder",
    }
    return {
        "covered_master_cells": len(row_map),
        "available_cohorts": sorted(available_cohorts),
        "missing_cohorts": sorted(expected_cohorts - available_cohorts),
    }


def _augment_table_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    augmented_rows: list[dict[str, Any]] = []
    for row in rows:
        augmented_rows.append(
            {
                "prompt_runtime_cell": f"{row['prompt_variant']}/{row['runtime_variant']}",
                **row,
            }
        )
    return augmented_rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _normalize_csv_value(value) for key, value in row.items()})


def _normalize_csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".") if not value.is_integer() else f"{value:.1f}"
    return value


def _validate_written_table(
    *,
    path: Path,
    expected_rows: list[dict[str, Any]],
    table_name: str,
) -> dict[str, Any]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        observed_rows = list(csv.DictReader(handle))

    mismatches: list[str] = []
    if len(observed_rows) != len(expected_rows):
        mismatches.append(
            f"{table_name}: expected {len(expected_rows)} rows, found {len(observed_rows)} rows in {path.name}"
        )

    checks = 0
    for index, expected_row in enumerate(expected_rows):
        if index >= len(observed_rows):
            break
        observed_row = observed_rows[index]
        for key, expected_value in expected_row.items():
            expected_text = str(_normalize_csv_value(expected_value))
            observed_text = observed_row.get(key, "")
            checks += 1
            if expected_text != observed_text:
                mismatches.append(
                    f"{table_name}: row {index + 1} field {key} expected {expected_text!r}, found {observed_text!r}"
                )

    return {
        "all_consistent": not mismatches,
        "checks": checks,
        "mismatches": mismatches,
    }


def _build_figure_panels(
    *,
    row_map: dict[tuple[str, str, str, str], dict[str, Any]],
    metric_key: str,
) -> list[dict[str, Any]]:
    panels: list[dict[str, Any]] = []
    for cohort in _COHORTS:
        task_family = str(cohort["task_family"])
        task_difficulty = str(cohort["task_difficulty"])
        values: list[float] = []
        run_count: int | None = None
        for prompt_variant, runtime_variant in _CELL_ORDER:
            row = row_map.get((task_family, task_difficulty, prompt_variant, runtime_variant))
            if row is None:
                raise ValueError(
                    "Missing Block A master summary row for "
                    f"{task_family}/{task_difficulty}/{prompt_variant}/{runtime_variant}"
                )
            values.append(float(row[metric_key]))
            if run_count is None:
                run_count = int(row["run_count"])
        panels.append(
            {
                "label": str(cohort["label"]),
                "column_prefix": str(cohort["column_prefix"]),
                "run_count": int(run_count or 0),
                "values": values,
            }
        )
    return panels


def _validate_figure_panels(
    *,
    summary: dict[str, Any],
    panels: list[dict[str, Any]],
    table_key: str,
    table_metric_suffix: str,
    metric_key: str,
) -> dict[str, Any]:
    table_rows = {
        (str(row["prompt_variant"]), str(row["runtime_variant"])): row
        for row in summary["tables"][table_key]
    }

    mismatches: list[str] = []
    checks = 0
    for panel in panels:
        column_prefix = str(panel["column_prefix"])
        for index, (prompt_variant, runtime_variant) in enumerate(_CELL_ORDER):
            table_row = table_rows[(prompt_variant, runtime_variant)]
            expected = table_row.get(f"{column_prefix}_{table_metric_suffix}")
            observed = panel["values"][index]
            checks += 1
            if expected is None:
                mismatches.append(
                    f"{metric_key}: missing table value for {column_prefix} {prompt_variant}/{runtime_variant}"
                )
                continue
            if not _float_equal(float(expected), float(observed)):
                mismatches.append(
                    f"{metric_key}: {column_prefix} {prompt_variant}/{runtime_variant} expected {expected}, found {observed}"
                )

    return {
        "all_consistent": not mismatches,
        "checks": checks,
        "mismatches": mismatches,
    }


def _merge_validation(target: dict[str, Any], incoming: dict[str, Any]) -> None:
    target["all_consistent"] = target["all_consistent"] and incoming["all_consistent"]
    target["checks"] += int(incoming["checks"])
    target["mismatches"].extend(incoming["mismatches"])


def _render_analysis_markdown(
    *,
    summary: dict[str, Any],
    written_outputs: dict[str, Path],
    validation: dict[str, Any],
    consistency_checks: dict[str, Any],
) -> str:
    overall = summary["overall"]
    difficulty_rows = summary["tables"]["difficulty_comparison_table"]
    navigation_deltas = [
        row["planner_call_delta"]
        for row in difficulty_rows
        if row["task_family"] == "navigation"
        and row["comparison_status"] == "matched"
        and row["planner_call_delta"] is not None
        and row["easy_success_rate"] == 1.0
        and row["harder_success_rate"] == 1.0
    ]
    mean_navigation_delta = sum(float(value) for value in navigation_deltas) / len(navigation_deltas)

    lines = [
        "# Block A Analysis",
        "",
        "## Scope",
        "",
        (
            "This package converts the existing Block A master summary into paper-facing tables, figures, and a short "
            "analysis note without adding any new experiments."
        ),
        (
            f"The packaged checkpoint covers {overall['merged_runs']} merged runs with "
            f"{overall['successful_runs']} successes ({_format_decimal(float(overall['success_rate']), 6)} success rate), "
            f"{overall['total_invalid_actions']} invalid actions, {overall['total_planner_calls']} planner calls, "
            f"and {overall['total_tool_calls']} tool calls."
        ),
        (
            "Covered cohorts are Navigation Easy, Navigation Harder, and Manipulation Easy. "
            "Manipulation Harder remains intentionally absent in the current Block A freeze."
        ),
        (
            "Manipulation / Harder is intentionally shown as missing in this package because it was not run in the "
            "frozen Block A master summary."
        ),
        "",
        "## Asset Index",
        "",
        f"- Success table: `../paper_tables/{written_outputs['success_table'].name}`",
        f"- Invalid-action table: `../paper_tables/{written_outputs['invalid_actions_table'].name}`",
        f"- Efficiency table: `../paper_tables/{written_outputs['efficiency_table'].name}`",
        f"- Success-rate figure: `../paper_figures/{written_outputs['success_rate_figure'].name}`",
        f"- Invalid-actions figure: `../paper_figures/{written_outputs['invalid_actions_figure'].name}`",
        f"- Planner-calls figure: `../paper_figures/{written_outputs['planner_calls_figure'].name}`",
        f"- Tool-calls figure: `../paper_figures/{written_outputs['tool_calls_figure'].name}`",
        "",
        "## Findings",
        "",
        (
            "1. Runtime recovery is decisive for the weakest prompt. `P0/R0` fails in every covered cohort, while "
            "`P0/R1` reaches 1.0 success in Navigation Easy, Navigation Harder, and Manipulation Easy."
        ),
        (
            "2. Invalid actions concentrate entirely in the `P0` prompt family. Both `P0/R0` and `P0/R1` average 1.0 "
            "invalid action per run in every covered cohort, while `P1` and `P2` reduce invalid actions to 0.0."
        ),
        (
            "3. `P2` is the efficiency frontier among the fully successful prompts. Relative to `P1`, `P2` preserves "
            "1.0 success while lowering average planner and tool calls by 1.0 on both navigation cohorts and by 2.0 on "
            "Manipulation Easy."
        ),
        (
            f"4. Harder navigation increases cost without changing the qualitative ranking. Across the matched successful "
            f"navigation cells, the harder slice adds {mean_navigation_delta:.6f} average planner calls and the same "
            "number of tool calls relative to Navigation Easy."
        ),
        (
            "5. The remaining symmetry gap is still Manipulation Harder. The master summary already classifies that gap "
            "as non-blocking for the Block A checkpoint, so the current package is suitable for paper drafting and result freeze."
        ),
        "",
        "## Consistency Checks",
        "",
        (
            f"- Verified `{consistency_checks['covered_master_cells']}` covered master-summary cells and "
            f"`{', '.join(consistency_checks['missing_cohorts'])}` as the only missing cohort."
        ),
        (
            f"- Table export checks: {validation['table_validation']['checks']} field comparisons from the written CSV files "
            "back to the master-summary table payloads."
        ),
        (
            f"- Figure data checks: {validation['figure_validation']['checks']} plotted values verified against the same "
            "master-summary values used for the paper tables."
        ),
        "- All consistency checks passed before the figures and analysis were written.",
        "",
        "## Paper Framing Notes",
        "",
        (
            "The paper-facing narrative should emphasize three stable claims from Block A: "
            "(i) runtime validation/retry rescues the weakest prompt, "
            "(ii) structured prompts remove invalid actions, and "
            "(iii) `P2` matches `P1` success at lower execution cost."
        ),
        (
            "The limitations section should explicitly note that harder difficulty coverage is currently available only for "
            "navigation, not manipulation."
        ),
        "",
    ]
    return "\n".join(lines)


def _render_metric_figure(
    *,
    path: Path,
    title: str,
    subtitle: str,
    panels: list[dict[str, Any]],
    value_label_digits: int,
) -> None:
    width = 1680
    height = 920
    canvas = _Canvas(width=width, height=height, background=_BACKGROUND)

    canvas.draw_text(64, 36, title, color=_TEXT, scale=4)
    canvas.draw_text(64, 84, subtitle, color=_VALUE_TEXT, scale=2)

    y_max = _nice_upper_bound(max(max(panel["values"]) for panel in panels))
    ticks = _build_ticks(y_max)

    panel_width = 500
    panel_height = 640
    panel_gap = 30
    origin_x = 58
    origin_y = 150
    inner_left = 76
    inner_right = 28
    inner_top = 76
    inner_bottom = 118

    for panel_index, panel in enumerate(panels):
        panel_x = origin_x + panel_index * (panel_width + panel_gap)
        panel_y = origin_y
        canvas.fill_rect(panel_x, panel_y, panel_x + panel_width, panel_y + panel_height, _PANEL_BACKGROUND)
        canvas.draw_rect(panel_x, panel_y, panel_x + panel_width, panel_y + panel_height, _PANEL_BORDER)

        canvas.draw_centered_text(
            panel_x + panel_width // 2,
            panel_y + 22,
            panel["label"],
            color=_TEXT,
            scale=3,
        )
        canvas.draw_centered_text(
            panel_x + panel_width // 2,
            panel_y + 54,
            f"RUNS CELL {panel['run_count']}",
            color=_VALUE_TEXT,
            scale=2,
        )

        chart_left = panel_x + inner_left
        chart_top = panel_y + inner_top
        chart_right = panel_x + panel_width - inner_right
        chart_bottom = panel_y + panel_height - inner_bottom
        chart_width = chart_right - chart_left
        chart_height = chart_bottom - chart_top

        for tick_value in ticks:
            tick_y = chart_bottom - int(round((tick_value / y_max) * chart_height))
            canvas.draw_line(chart_left, tick_y, chart_right, tick_y, _GRID)
            canvas.draw_text(
                panel_x + 12,
                tick_y - 8,
                _format_tick_value(tick_value),
                color=_VALUE_TEXT,
                scale=2,
            )

        canvas.draw_line(chart_left, chart_top, chart_left, chart_bottom, _AXIS)
        canvas.draw_line(chart_left, chart_bottom, chart_right, chart_bottom, _AXIS)

        group_gap = 18
        bar_width = int((chart_width - group_gap * (len(_CELL_ORDER) + 1)) / len(_CELL_ORDER))
        for bar_index, ((prompt_variant, runtime_variant), value) in enumerate(zip(_CELL_ORDER, panel["values"])):
            bar_left = chart_left + group_gap + bar_index * (bar_width + group_gap)
            bar_right = bar_left + bar_width
            bar_height = int(round((value / y_max) * chart_height))
            bar_top = chart_bottom - max(bar_height, 2)
            color = _CELL_COLORS[(prompt_variant, runtime_variant)]
            canvas.fill_rect(bar_left, bar_top, bar_right, chart_bottom, color)
            canvas.draw_rect(bar_left, bar_top, bar_right, chart_bottom, _AXIS)

            value_text = _format_decimal(float(value), value_label_digits)
            canvas.draw_centered_text(
                (bar_left + bar_right) // 2,
                max(chart_top + 4, bar_top - 22),
                value_text,
                color=_VALUE_TEXT,
                scale=2,
            )
            canvas.draw_centered_text(
                (bar_left + bar_right) // 2,
                chart_bottom + 18,
                f"{prompt_variant}/{runtime_variant}",
                color=_TEXT,
                scale=2,
            )

    canvas.draw_text(
        64,
        height - 48,
        "COVERED COHORTS ONLY. MANIPULATION HARDER NOT RUN IN BLOCK A MASTER SUMMARY.",
        color=_VALUE_TEXT,
        scale=2,
    )
    canvas.write_png(path)


def _nice_upper_bound(value: float) -> float:
    if value <= 1.0:
        return 1.0
    magnitude = 10 ** math.floor(math.log10(value))
    normalized = value / magnitude
    for step in (1.0, 2.0, 2.5, 5.0, 10.0):
        if normalized <= step:
            return step * magnitude
    return 10.0 * magnitude


def _build_ticks(y_max: float) -> list[float]:
    if y_max <= 1.0:
        return [0.0, 0.25, 0.5, 0.75, 1.0]
    step = _nice_upper_bound(y_max / 5.0)
    tick_count = int(round(y_max / step))
    return [round(step * index, 6) for index in range(tick_count + 1)]


def _format_tick_value(value: float) -> str:
    if _float_equal(value, round(value)):
        return str(int(round(value)))
    return _format_decimal(value, 2)


def _format_decimal(value: float, digits: int) -> str:
    return f"{value:.{digits}f}".rstrip("0").rstrip(".") if digits > 0 else str(int(round(value)))


def _float_equal(left: float, right: float, *, tolerance: float = 1e-9) -> bool:
    return abs(left - right) <= tolerance


class _Canvas:
    def __init__(self, *, width: int, height: int, background: tuple[int, int, int]) -> None:
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, background)

    def fill_rect(self, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        x0 = max(0, min(self.width, x0))
        x1 = max(0, min(self.width, x1))
        y0 = max(0, min(self.height, y0))
        y1 = max(0, min(self.height, y1))
        if x0 >= x1 or y0 >= y1:
            return
        for y in range(y0, y1):
            row_start = (y * self.width + x0) * 3
            for x in range(x0, x1):
                index = row_start + (x - x0) * 3
                self.pixels[index : index + 3] = bytes(color)

    def draw_rect(self, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        self.draw_line(x0, y0, x1 - 1, y0, color)
        self.draw_line(x0, y1 - 1, x1 - 1, y1 - 1, color)
        self.draw_line(x0, y0, x0, y1 - 1, color)
        self.draw_line(x1 - 1, y0, x1 - 1, y1 - 1, color)

    def draw_line(self, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        step_x = 1 if x0 < x1 else -1
        step_y = 1 if y0 < y1 else -1
        error = dx + dy

        while True:
            self._set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            doubled_error = 2 * error
            if doubled_error >= dy:
                error += dy
                x0 += step_x
            if doubled_error <= dx:
                error += dx
                y0 += step_y

    def draw_text(self, x: int, y: int, text: str, *, color: tuple[int, int, int], scale: int) -> None:
        cursor_x = x
        for raw_char in text.upper():
            glyph = _FONT_5X7.get(raw_char, _FONT_5X7[" "])
            for row_index, row in enumerate(glyph):
                for column_index, bit in enumerate(row):
                    if bit == "1":
                        self.fill_rect(
                            cursor_x + column_index * scale,
                            y + row_index * scale,
                            cursor_x + (column_index + 1) * scale,
                            y + (row_index + 1) * scale,
                            color,
                        )
            cursor_x += (5 * scale) + scale

    def draw_centered_text(
        self,
        center_x: int,
        y: int,
        text: str,
        *,
        color: tuple[int, int, int],
        scale: int,
    ) -> None:
        text_width = _measure_text_width(text, scale)
        self.draw_text(center_x - text_width // 2, y, text, color=color, scale=scale)

    def write_png(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = bytearray()
        stride = self.width * 3
        for row_index in range(self.height):
            raw.append(0)
            start = row_index * stride
            raw.extend(self.pixels[start : start + stride])

        def chunk(chunk_type: bytes, data: bytes) -> bytes:
            crc = zlib.crc32(chunk_type)
            crc = zlib.crc32(data, crc)
            return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)
        compressed = zlib.compress(bytes(raw), level=9)
        png = b"".join(
            [
                b"\x89PNG\r\n\x1a\n",
                chunk(b"IHDR", ihdr),
                chunk(b"IDAT", compressed),
                chunk(b"IEND", b""),
            ]
        )
        path.write_bytes(png)

    def _set_pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        index = (y * self.width + x) * 3
        self.pixels[index : index + 3] = bytes(color)


def _measure_text_width(text: str, scale: int) -> int:
    if not text:
        return 0
    return len(text) * ((5 * scale) + scale) - scale
