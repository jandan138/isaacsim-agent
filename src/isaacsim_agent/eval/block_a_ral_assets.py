"""Regenerate RA-L paper assets from the frozen Block A summaries."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]

_CELL_ORDER = [
    ("P0", "R0"),
    ("P0", "R1"),
    ("P1", "R0"),
    ("P1", "R1"),
    ("P2", "R0"),
    ("P2", "R1"),
]

_CELL_COLOR_NAMES = {
    ("P0", "R0"): "ralP0R0",
    ("P0", "R1"): "ralP0R1",
    ("P1", "R0"): "ralP1R0",
    ("P1", "R1"): "ralP1R1",
    ("P2", "R0"): "ralP2R0",
    ("P2", "R1"): "ralP2R1",
}

_MAIN_COHORTS = [
    ("navigation", "easy", "Navigation Easy"),
    ("manipulation", "easy", "Manipulation Easy"),
    ("navigation", "harder", "Navigation Harder"),
    ("manipulation", "harder", "Manipulation Harder"),
]


@dataclass(frozen=True)
class BlockARalAssetPackagingResult:
    """Materialized RA-L-facing assets and lightweight validation metadata."""

    output_dir: Path
    figures_dir: Path
    tables_dir: Path
    written_outputs: dict[str, Path]
    validation: dict[str, Any]


def package_block_a_ral_assets(
    *,
    final_closure_summary_path: str | Path,
    master_summary_path: str | Path,
    prompt_only_summary_path: str | Path,
    runtime_only_summary_path: str | Path,
    manipulation_harder_summary_path: str | Path,
    cross_family_summary_path: str | Path,
    output_dir: str | Path,
) -> BlockARalAssetPackagingResult:
    """Write reviewer-facing RA-L figures, tables, and a manifest."""

    output_dir = Path(output_dir)
    figures_dir = output_dir / "figures"
    tables_dir = output_dir / "tables"
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    final_closure = _load_json(final_closure_summary_path)
    master_summary = _load_json(master_summary_path)
    prompt_only = _load_json(prompt_only_summary_path)
    runtime_only = _load_json(runtime_only_summary_path)
    manipulation_harder = _load_json(manipulation_harder_summary_path)
    cross_family = _load_json(cross_family_summary_path)

    master_rows = _load_master_rows(master_summary)
    manipulation_harder_rows = _load_manipulation_harder_rows(manipulation_harder)
    main_rows = {**master_rows, **manipulation_harder_rows}
    prompt_rows = _load_family_prompt_runtime_rows(prompt_only)
    runtime_rows = _load_family_prompt_runtime_rows(runtime_only)

    written_outputs: dict[str, Path] = {}

    main_panels = _build_main_condition_panels(main_rows)
    main_figure_csv = figures_dir / "main_condition_ordering.csv"
    _write_csv(main_figure_csv, _panel_csv_rows(main_panels))
    written_outputs["main_condition_ordering_csv"] = main_figure_csv
    main_figure_tex = figures_dir / "main_condition_ordering.tex"
    _write_text(
        main_figure_tex,
        _bar_group_figure_tex(
            panels=main_panels,
            y_max=1.0,
            y_label="Success rate",
            float_env="figure*",
            axis_width=r"0.43\textwidth",
            axis_height=r"0.25\textwidth",
            label="fig:main-condition-ordering",
            caption=(
                "Success rate across the retained navigation and manipulation cohorts for all six "
                "contract/runtime cells. \\texttt{P0/R0} is consistently weakest, \\texttt{P0/R1} recovers, "
                "and the typed contracts remain successful in the covered slices."
            ),
        ),
    )
    written_outputs["main_condition_ordering_tex"] = main_figure_tex

    invalid_recovery_panels = _build_invalid_recovery_panels(prompt_rows, runtime_rows)
    invalid_recovery_csv = figures_dir / "invalid_actions_recovery.csv"
    _write_csv(invalid_recovery_csv, _panel_csv_rows(invalid_recovery_panels))
    written_outputs["invalid_actions_recovery_csv"] = invalid_recovery_csv
    invalid_recovery_tex = figures_dir / "invalid_actions_recovery.tex"
    _write_text(
        invalid_recovery_tex,
        _bar_group_figure_tex(
            panels=invalid_recovery_panels,
            y_max=1.0,
            y_label="Average per run",
            float_env="figure",
            axis_width=r"0.39\columnwidth",
            axis_height=r"0.32\columnwidth",
            label="fig:invalid-actions-recovery",
            caption=(
                "Invalid actions in the fixed-\\texttt{R0} contract comparison (top row) and retries in the "
                "fixed-\\texttt{P1} runtime comparison (bottom row). Typed contracts eliminate the invalid-action "
                "mode in the shared ablation slice, while \\texttt{R1} adds retry work only on recoverable "
                "invalid-first-action probes."
            ),
        ),
    )
    written_outputs["invalid_actions_recovery_tex"] = invalid_recovery_tex

    overhead_panels = _build_overhead_panels(prompt_rows, manipulation_harder_rows)
    overhead_csv = figures_dir / "planner_tool_overhead.csv"
    _write_csv(overhead_csv, _panel_csv_rows(overhead_panels))
    written_outputs["planner_tool_overhead_csv"] = overhead_csv
    overhead_tex = figures_dir / "planner_tool_overhead.tex"
    _write_text(
        overhead_tex,
        _bar_group_figure_tex(
            panels=overhead_panels,
            y_max=12.0,
            y_label="Calls per run",
            float_env="figure",
            axis_width=r"0.39\columnwidth",
            axis_height=r"0.32\columnwidth",
            label="fig:planner-tool-overhead",
            caption=(
                "Planner and tool calls in the retained \\texttt{P1} versus \\texttt{P2} comparisons across the "
                "fixed-\\texttt{R0} contract ablation and the harder manipulation slice. The figure is descriptive: "
                "in the covered slices, \\texttt{P2} matches the success profile of \\texttt{P1} while using fewer "
                "planner/tool calls."
            ),
        ),
    )
    written_outputs["planner_tool_overhead_tex"] = overhead_tex

    experimental_design_rows = _build_experimental_design_rows(
        master_summary=master_summary,
        prompt_only=prompt_only,
        runtime_only=runtime_only,
        manipulation_harder=manipulation_harder,
    )
    experimental_design_csv = tables_dir / "experimental_design_summary.csv"
    _write_csv(experimental_design_csv, experimental_design_rows)
    written_outputs["experimental_design_summary_csv"] = experimental_design_csv
    experimental_design_tex = tables_dir / "experimental_design_summary.tex"
    _write_text(experimental_design_tex, _experimental_design_table_tex(experimental_design_rows))
    written_outputs["experimental_design_summary_tex"] = experimental_design_tex

    main_outcome_rows = _build_main_outcome_rows(main_rows)
    main_outcome_csv = tables_dir / "main_outcome_summary.csv"
    _write_csv(main_outcome_csv, main_outcome_rows)
    written_outputs["main_outcome_summary_csv"] = main_outcome_csv
    main_outcome_tex = tables_dir / "main_outcome_summary.tex"
    _write_text(main_outcome_tex, _main_outcome_table_tex(main_outcome_rows))
    written_outputs["main_outcome_summary_tex"] = main_outcome_tex
    legacy_outcome_csv = tables_dir / "final_closure_result_summary.csv"
    _write_csv(legacy_outcome_csv, main_outcome_rows)
    written_outputs["final_closure_result_summary_csv"] = legacy_outcome_csv
    legacy_outcome_tex = tables_dir / "final_closure_result_summary.tex"
    _write_text(legacy_outcome_tex, _legacy_outcome_alias_tex())
    written_outputs["final_closure_result_summary_tex"] = legacy_outcome_tex

    planner_overhead_rows = _build_planner_overhead_rows(main_rows)
    planner_overhead_csv = tables_dir / "planner_tool_overhead_summary.csv"
    _write_csv(planner_overhead_csv, planner_overhead_rows)
    written_outputs["planner_tool_overhead_summary_csv"] = planner_overhead_csv
    planner_overhead_tex = tables_dir / "planner_tool_overhead_summary.tex"
    _write_text(planner_overhead_tex, _planner_overhead_table_tex(planner_overhead_rows))
    written_outputs["planner_tool_overhead_summary_tex"] = planner_overhead_tex

    focused_ablation_rows = _build_focused_ablation_rows(prompt_only=prompt_only, runtime_only=runtime_only)
    focused_ablation_csv = tables_dir / "focused_ablation_summary.csv"
    _write_csv(focused_ablation_csv, focused_ablation_rows)
    written_outputs["focused_ablation_summary_csv"] = focused_ablation_csv
    focused_ablation_tex = tables_dir / "focused_ablation_summary.tex"
    _write_text(focused_ablation_tex, _focused_ablation_table_tex(focused_ablation_rows))
    written_outputs["focused_ablation_summary_tex"] = focused_ablation_tex

    harder_task_rows = _build_harder_task_rows(main_rows)
    harder_task_csv = tables_dir / "harder_task_summary.csv"
    _write_csv(harder_task_csv, harder_task_rows)
    written_outputs["harder_task_summary_csv"] = harder_task_csv
    harder_task_tex = tables_dir / "harder_task_summary.tex"
    _write_text(harder_task_tex, _harder_task_table_tex(harder_task_rows))
    written_outputs["harder_task_summary_tex"] = harder_task_tex

    manifest_path = output_dir / "asset_manifest.md"
    _write_text(
        manifest_path,
        _asset_manifest(
            final_closure=final_closure,
            cross_family=cross_family,
            written_outputs=written_outputs,
        ),
    )
    written_outputs["asset_manifest"] = manifest_path

    validation = {
        "final_closure_merged_runs": int(final_closure["overall"]["merged_runs"]),
        "final_closure_successful_runs": int(final_closure["overall"]["successful_runs"]),
        "main_result_cells": len(main_rows),
        "cross_family_rows": len(cross_family["group_by_task_family_prompt_runtime"]),
        "written_output_count": len(written_outputs),
    }

    return BlockARalAssetPackagingResult(
        output_dir=output_dir,
        figures_dir=figures_dir,
        tables_dir=tables_dir,
        written_outputs=written_outputs,
        validation=validation,
    )


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _normalize_task_family(value: str) -> str:
    return "manipulation" if value == "pick_place" else value


def _fmt(value: float | int) -> str:
    numeric = float(value)
    if abs(numeric - round(numeric)) < 1e-9:
        return f"{numeric:.1f}"
    if abs(numeric * 10 - round(numeric * 10)) < 1e-9:
        return f"{numeric:.1f}"
    return f"{numeric:.2f}"


def _escape_latex(text: str) -> str:
    replacements = {
        "\\": "\\textbackslash{}",
        "_": "\\_",
        "&": "\\&",
        "%": "\\%",
        "#": "\\#",
        "{": "\\{",
        "}": "\\}",
    }
    return "".join(replacements.get(char, char) for char in text)


def _load_master_rows(summary: dict[str, Any]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    rows: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in summary["group_by_task_family_difficulty_prompt_runtime"]:
        key = (
            _normalize_task_family(str(row["task_family"])),
            str(row["task_difficulty"]),
            str(row["prompt_variant"]),
            str(row["runtime_variant"]),
        )
        rows[key] = row
    return rows


def _load_manipulation_harder_rows(summary: dict[str, Any]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    questions = summary["analysis"]["questions"]
    rows: dict[tuple[str, str, str, str], dict[str, Any]] = {
        ("manipulation", "harder", "P0", "R0"): questions["q1_p0_r0_worst"]["row"],
        ("manipulation", "harder", "P0", "R1"): questions["q2_r1_recovers_p0"]["row"],
    }
    for row in questions["q3_p1_p2_success"]["rows"].values():
        rows[("manipulation", "harder", str(row["prompt_variant"]), str(row["runtime_variant"]))] = row
    for runtime_variant in ("R0", "R1"):
        runtime_key = runtime_variant.lower()
        for prompt_variant in ("P1", "P2"):
            row = questions["q4_p2_more_efficient_than_p1"][runtime_key][prompt_variant.lower()]
            rows[("manipulation", "harder", prompt_variant, runtime_variant)] = row
    return rows


def _load_family_prompt_runtime_rows(summary: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    rows: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in summary["by_task_family_prompt_runtime"]:
        key = (
            _normalize_task_family(str(row["task_family"])),
            str(row["prompt_variant"]),
            str(row["runtime_variant"]),
        )
        rows[key] = row
    return rows


def _build_main_condition_panels(
    main_rows: dict[tuple[str, str, str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    panels: list[dict[str, Any]] = []
    for task_family, difficulty, label in _MAIN_COHORTS:
        bars = []
        run_count = None
        for prompt_variant, runtime_variant in _CELL_ORDER:
            row = main_rows[(task_family, difficulty, prompt_variant, runtime_variant)]
            if run_count is None:
                run_count = int(row["run_count"])
            bars.append(
                {
                    "label": f"{prompt_variant}/{runtime_variant}",
                    "value": float(row["success_rate"]),
                    "color": _CELL_COLOR_NAMES[(prompt_variant, runtime_variant)],
                }
            )
        panels.append({"label": label, "note": f"{run_count} runs/cell", "bars": bars})
    return panels


def _build_invalid_recovery_panels(
    prompt_rows: dict[tuple[str, str, str], dict[str, Any]],
    runtime_rows: dict[tuple[str, str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    panels: list[dict[str, Any]] = []
    for family, label in [("navigation", "Navigation Invalid"), ("manipulation", "Manipulation Invalid")]:
        bars = []
        for prompt_variant in ("P0", "P1", "P2"):
            row = prompt_rows[(family, prompt_variant, "R0")]
            bars.append(
                {
                    "label": prompt_variant,
                    "value": float(row["average_invalid_actions"]),
                    "color": _CELL_COLOR_NAMES[(prompt_variant, "R0")],
                }
            )
        panels.append({"label": label, "note": "Fixed R0 contract ablation", "bars": bars})

    for family, label in [("navigation", "Navigation Retries"), ("manipulation", "Manipulation Retries")]:
        bars = []
        for runtime_variant in ("R0", "R1"):
            row = runtime_rows[(family, "P1", runtime_variant)]
            bars.append(
                {
                    "label": runtime_variant,
                    "value": float(row["average_retries"]),
                    "color": _CELL_COLOR_NAMES[("P1", runtime_variant)],
                }
            )
        panels.append({"label": label, "note": "Fixed P1 runtime ablation", "bars": bars})
    return panels


def _build_overhead_panels(
    prompt_rows: dict[tuple[str, str, str], dict[str, Any]],
    manipulation_harder_rows: dict[tuple[str, str, str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    panels: list[dict[str, Any]] = []
    for family, label in [("navigation", "Navigation Easy"), ("manipulation", "Manipulation Easy")]:
        p1 = prompt_rows[(family, "P1", "R0")]
        p2 = prompt_rows[(family, "P2", "R0")]
        panels.append(
            {
                "label": label,
                "note": "Fixed R0 contract ablation",
                "bars": [
                    {"label": "P1-P", "value": float(p1["average_planner_calls"]), "color": _CELL_COLOR_NAMES[("P1", "R0")]},
                    {"label": "P1-T", "value": float(p1["average_tool_calls"]), "color": _CELL_COLOR_NAMES[("P1", "R0")]},
                    {"label": "P2-P", "value": float(p2["average_planner_calls"]), "color": _CELL_COLOR_NAMES[("P2", "R0")]},
                    {"label": "P2-T", "value": float(p2["average_tool_calls"]), "color": _CELL_COLOR_NAMES[("P2", "R0")]},
                ],
            }
        )

    for runtime_variant in ("R0", "R1"):
        p1 = manipulation_harder_rows[("manipulation", "harder", "P1", runtime_variant)]
        p2 = manipulation_harder_rows[("manipulation", "harder", "P2", runtime_variant)]
        panels.append(
            {
                "label": f"Manipulation Harder {runtime_variant}",
                "note": "Harder manipulation slice",
                "bars": [
                    {"label": "P1-P", "value": float(p1["average_planner_calls"]), "color": _CELL_COLOR_NAMES[("P1", runtime_variant)]},
                    {"label": "P1-T", "value": float(p1["average_tool_calls"]), "color": _CELL_COLOR_NAMES[("P1", runtime_variant)]},
                    {"label": "P2-P", "value": float(p2["average_planner_calls"]), "color": _CELL_COLOR_NAMES[("P2", runtime_variant)]},
                    {"label": "P2-T", "value": float(p2["average_tool_calls"]), "color": _CELL_COLOR_NAMES[("P2", runtime_variant)]},
                ],
            }
        )
    return panels


def _panel_csv_rows(panels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for panel in panels:
        for bar in panel["bars"]:
            rows.append(
                {
                    "panel": panel["label"],
                    "note": panel["note"],
                    "bar_label": bar["label"],
                    "value": _fmt(bar["value"]),
                    "color": bar["color"],
                }
            )
    return rows


def _build_experimental_design_rows(
    *,
    master_summary: dict[str, Any],
    prompt_only: dict[str, Any],
    runtime_only: dict[str, Any],
    manipulation_harder: dict[str, Any],
) -> list[dict[str, Any]]:
    coverage_rows = {
        (_normalize_task_family(str(row["task_family"])), str(row["task_difficulty"])): row
        for row in master_summary["coverage"]
    }
    manipulation_harder_run_count = int(manipulation_harder["analysis"]["questions"]["q1_p0_r0_worst"]["row"]["run_count"])
    manipulation_harder_task_count = int(manipulation_harder["matrix"]["task_count"])
    return [
        {
            "block": "Main factorial",
            "family": "Navigation",
            "slice": "Easy",
            "axes": "P0/P1/P2 x R0/R1",
            "tasks": coverage_rows[("navigation", "easy")]["task_count"],
            "runs_per_cell": coverage_rows[("navigation", "easy")]["run_count"] // 6,
            "total_runs": coverage_rows[("navigation", "easy")]["run_count"],
            "role": "Main contract/runtime ordering",
        },
        {
            "block": "Main factorial",
            "family": "Manipulation",
            "slice": "Easy",
            "axes": "P0/P1/P2 x R0/R1",
            "tasks": coverage_rows[("manipulation", "easy")]["task_count"],
            "runs_per_cell": coverage_rows[("manipulation", "easy")]["run_count"] // 6,
            "total_runs": coverage_rows[("manipulation", "easy")]["run_count"],
            "role": "Main contract/runtime ordering",
        },
        {
            "block": "Main factorial",
            "family": "Navigation",
            "slice": "Harder",
            "axes": "P0/P1/P2 x R0/R1",
            "tasks": coverage_rows[("navigation", "harder")]["task_count"],
            "runs_per_cell": coverage_rows[("navigation", "harder")]["run_count"] // 6,
            "total_runs": coverage_rows[("navigation", "harder")]["run_count"],
            "role": "Harder-task robustness",
        },
        {
            "block": "Main factorial",
            "family": "Manipulation",
            "slice": "Harder",
            "axes": "P0/P1/P2 x R0/R1",
            "tasks": manipulation_harder_task_count,
            "runs_per_cell": manipulation_harder_run_count,
            "total_runs": manipulation_harder["overall"]["summarized_runs"],
            "role": "Harder-task robustness",
        },
        {
            "block": "Action-interface ablation",
            "family": "Mixed",
            "slice": "Easy shared subset",
            "axes": "P0/P1/P2 at fixed R0",
            "tasks": prompt_only["matrix"]["task_count"],
            "runs_per_cell": prompt_only["overall"]["summarized_runs"] // 3,
            "total_runs": prompt_only["overall"]["summarized_runs"],
            "role": "Invalid-action mechanism check",
        },
        {
            "block": "Runtime-only ablation",
            "family": "Mixed",
            "slice": "Recoverable probes",
            "axes": "R0/R1 at fixed P1",
            "tasks": runtime_only["matrix"]["task_count"],
            "runs_per_cell": runtime_only["overall"]["summarized_runs"] // 2,
            "total_runs": runtime_only["overall"]["summarized_runs"],
            "role": "Validation/retry mechanism check",
        },
    ]


def _build_main_outcome_rows(
    main_rows: dict[tuple[str, str, str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for prompt_variant, runtime_variant in _CELL_ORDER:
        row = {"cell": f"{prompt_variant}/{runtime_variant}"}
        for family, difficulty, label in _MAIN_COHORTS:
            cohort_row = main_rows[(family, difficulty, prompt_variant, runtime_variant)]
            row[_cohort_key(label)] = (
                f"{cohort_row['successful_runs']}/{cohort_row['run_count']}; "
                f"{_fmt(cohort_row['average_invalid_actions'])}; "
                f"{_fmt(cohort_row['average_retries'])}"
            )
        rows.append(row)
    return rows


def _build_planner_overhead_rows(
    main_rows: dict[tuple[str, str, str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for prompt_variant, runtime_variant in _CELL_ORDER:
        row = {"cell": f"{prompt_variant}/{runtime_variant}"}
        for family, difficulty, label in _MAIN_COHORTS:
            cohort_row = main_rows[(family, difficulty, prompt_variant, runtime_variant)]
            row[_cohort_key(label)] = (
                f"{_fmt(cohort_row['average_planner_calls'])}/"
                f"{_fmt(cohort_row['average_tool_calls'])}"
            )
        rows.append(row)
    return rows


def _build_focused_ablation_rows(
    *,
    prompt_only: dict[str, Any],
    runtime_only: dict[str, Any],
) -> list[dict[str, Any]]:
    prompt_questions = prompt_only["analysis"]["questions"]
    runtime_questions = runtime_only["analysis"]["questions"]
    prompt_rows = [
        ("Action-interface", "P0/R0", prompt_questions["q1_prompt_structure_reduces_invalid_actions"]["p0_r0"]),
        ("Action-interface", "P1/R0", prompt_questions["q1_prompt_structure_reduces_invalid_actions"]["p1_r0"]),
        ("Action-interface", "P2/R0", prompt_questions["q1_prompt_structure_reduces_invalid_actions"]["p2_r0"]),
        ("Runtime-only", "P1/R0", runtime_questions["q1_runtime_has_independent_value"]["p1_r0"]),
        ("Runtime-only", "P1/R1", runtime_questions["q1_runtime_has_independent_value"]["p1_r1"]),
    ]
    rows: list[dict[str, Any]] = []
    for comparison, cell, row in prompt_rows:
        rows.append(
            {
                "comparison": comparison,
                "cell": cell,
                "runs": row["run_count"],
                "success": f"{row['successful_runs']}/{row['run_count']} ({_fmt(row['success_rate'])})",
                "invalid_runs": row["invalid_action_run_count"],
                "recoveries": row["successful_invalid_action_runs"],
                "avg_retries": _fmt(row["average_retries"]),
                "planner_tool": f"{_fmt(row['average_planner_calls'])}/{_fmt(row['average_tool_calls'])}",
            }
        )
    return rows


def _build_harder_task_rows(
    main_rows: dict[tuple[str, str, str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family in ("navigation", "manipulation"):
        for prompt_variant, runtime_variant in _CELL_ORDER:
            easy_row = main_rows[(family, "easy", prompt_variant, runtime_variant)]
            harder_row = main_rows[(family, "harder", prompt_variant, runtime_variant)]
            rows.append(
                {
                    "family": family.title(),
                    "cell": f"{prompt_variant}/{runtime_variant}",
                    "easy_success": f"{easy_row['successful_runs']}/{easy_row['run_count']} ({_fmt(easy_row['success_rate'])})",
                    "harder_success": f"{harder_row['successful_runs']}/{harder_row['run_count']} ({_fmt(harder_row['success_rate'])})",
                    "easy_planner_tool": f"{_fmt(easy_row['average_planner_calls'])}/{_fmt(easy_row['average_tool_calls'])}",
                    "harder_planner_tool": f"{_fmt(harder_row['average_planner_calls'])}/{_fmt(harder_row['average_tool_calls'])}",
                    "delta_planner": _fmt(float(harder_row["average_planner_calls"]) - float(easy_row["average_planner_calls"])),
                    "delta_tool": _fmt(float(harder_row["average_tool_calls"]) - float(easy_row["average_tool_calls"])),
                }
            )
    return rows


def _cohort_key(label: str) -> str:
    return label.lower().replace(" ", "_")


def _bar_group_figure_tex(
    *,
    panels: list[dict[str, Any]],
    y_max: float,
    y_label: str,
    float_env: str,
    axis_width: str,
    axis_height: str,
    label: str,
    caption: str,
) -> str:
    lines = [
        f"\\begin{{{float_env}}}[!t]",
        "  \\centering",
        "  \\begin{tikzpicture}",
        "    \\begin{groupplot}[",
        "      group style={group size=2 by 2, horizontal sep=1.15cm, vertical sep=0.95cm},",
        f"      width={axis_width},",
        f"      height={axis_height},",
        "      ybar,",
        f"      ymin=0, ymax={y_max:.2f},",
        f"      ylabel={{{y_label}}},",
        "      symbolic x coords={P0/R0,P0/R1,P1/R0,P1/R1,P2/R0,P2/R1,P0,P1,P2,R0,R1,P1-P,P1-T,P2-P,P2-T},",
        "      xtick=data,",
        "      xticklabel style={font=\\scriptsize, rotate=35, anchor=east},",
        "      ymajorgrids=true,",
        "      grid style={draw=ralGrid},",
        "      axis line style={draw=ralBorder},",
        "      tick style={draw=ralBorder},",
        "      title style={font=\\small\\bfseries, text=ralSlate},",
        "      label style={font=\\footnotesize, text=ralSlate},",
        "      tick label style={font=\\scriptsize, text=ralMuted},",
        "      every axis plot/.append style={draw opacity=1, fill opacity=1},",
        "    ]",
    ]
    for panel in panels:
        lines.append(f"      \\nextgroupplot[title={{{panel['label']}}}]")
        for bar in panel["bars"]:
            lines.append(
                "      "
                + _bar_coordinate_tex(
                    bar["label"],
                    float(bar["value"]),
                    str(bar["color"]),
                )
            )
        lines.append(
            "      "
            + f"\\node[anchor=north east,font=\\scriptsize,text=ralMuted] at (rel axis cs:0.98,0.98) {{{panel['note']}}};"
        )
    lines.extend(
        [
            "    \\end{groupplot}",
            "  \\end{tikzpicture}",
            f"  \\caption{{{caption}}}",
            f"  \\label{{{label}}}",
            f"\\end{{{float_env}}}",
        ]
    )
    return "\n".join(lines)


def _bar_coordinate_tex(label: str, value: float, color: str) -> str:
    return (
        f"\\addplot+[ybar, fill={color}, draw={color}, area legend] "
        f"coordinates {{({label},{value:.6f})}};"
    )


def _experimental_design_table_tex(rows: list[dict[str, Any]]) -> str:
    body = []
    for row in rows:
        body.append(
            "    "
            + " & ".join(
                [
                    row["block"],
                    row["family"],
                    row["slice"],
                    row["axes"],
                    str(row["tasks"]),
                    str(row["runs_per_cell"]),
                    str(row["total_runs"]),
                    row["role"],
                ]
            )
            + " \\\\"
        )
    return "\n".join(
        [
            "\\begin{table*}[!t]",
            "  \\centering",
            "  \\caption{Evaluation matrix used by the manuscript. The main factorial sweep remains frozen, while the two compact ablations isolate contract and runtime effects without adding new experiments.}",
            "  \\label{tab:experimental-design-summary}",
            "  \\footnotesize",
            "  \\setlength{\\tabcolsep}{4pt}",
            "  \\rowcolors{2}{ralPanel}{white}",
            "  \\begin{tabularx}{\\textwidth}{L{2.2cm} L{1.5cm} L{1.9cm} L{2.6cm} >{\\centering\\arraybackslash}p{0.9cm} >{\\centering\\arraybackslash}p{1.2cm} >{\\centering\\arraybackslash}p{1.1cm} Y}",
            "    \\toprule",
            "    Block & Family & Slice & Varying axes & Tasks & Runs/cell & Runs & Role \\\\",
            "    \\midrule",
            *body,
            "    \\bottomrule",
            "  \\end{tabularx}",
            "\\end{table*}",
        ]
    )


def _main_outcome_table_tex(rows: list[dict[str, Any]]) -> str:
    return _cohort_summary_table_tex(
        rows=rows,
        caption=(
            "Outcome summary across the retained cohorts. Each cohort entry reports success, invalid actions per run, "
            "and retries per run in that order."
        ),
        label="tab:main-outcome-summary",
        note="Cell entries are \\emph{success; invalid/run; retries/run}.",
    )


def _legacy_outcome_alias_tex() -> str:
    return "\n".join(
        [
            "% Legacy compatibility wrapper.",
            "% Use tables/main_outcome_summary.tex in the current reviewer-facing manuscript.",
            "\\input{tables/main_outcome_summary.tex}",
        ]
    )


def _planner_overhead_table_tex(rows: list[dict[str, Any]]) -> str:
    return _cohort_summary_table_tex(
        rows=rows,
        caption=(
            "Planner/tool workload across the retained cohorts. The table stays descriptive and is separated from the "
            "outcome table so the main text does not hide workload inside outcome cells."
        ),
        label="tab:planner-tool-overhead-summary",
        note="Cell entries are \\emph{planner calls/tool calls per run}.",
    )


def _cohort_summary_table_tex(
    *,
    rows: list[dict[str, Any]],
    caption: str,
    label: str,
    note: str,
) -> str:
    body = []
    for row in rows:
        body.append(
            "    "
            + " & ".join(
                [
                    row["cell"],
                    row["navigation_easy"],
                    row["manipulation_easy"],
                    row["navigation_harder"],
                    row["manipulation_harder"],
                ]
            )
            + " \\\\"
        )
    return "\n".join(
        [
            "\\begin{table*}[!t]",
            "  \\centering",
            f"  \\caption{{{caption}}}",
            f"  \\label{{{label}}}",
            "  \\footnotesize",
            "  \\setlength{\\tabcolsep}{5pt}",
            "  \\rowcolors{2}{ralPanel}{white}",
            "  \\begin{tabularx}{\\textwidth}{L{1.1cm} Y Y Y Y}",
            "    \\toprule",
            "    Cell & \\thead{Navigation\\\\Easy} & \\thead{Manipulation\\\\Easy} & \\thead{Navigation\\\\Harder} & \\thead{Manipulation\\\\Harder} \\\\",
            "    \\midrule",
            *body,
            "    \\bottomrule",
            "  \\end{tabularx}",
            "  \\\\[1pt]",
            f"  {{\\raggedright\\scriptsize {note}\\par}}",
            "\\end{table*}",
        ]
    )


def _focused_ablation_table_tex(rows: list[dict[str, Any]]) -> str:
    body = []
    for row in rows:
        body.append(
            "    "
            + " & ".join(
                [
                    row["comparison"],
                    row["cell"],
                    str(row["runs"]),
                    row["success"],
                    str(row["invalid_runs"]),
                    str(row["recoveries"]),
                    row["avg_retries"],
                    row["planner_tool"],
                ]
            )
            + " \\\\"
        )
    return "\n".join(
        [
            "\\begin{table}[!t]",
            "  \\centering",
            "  \\caption{Support-only summary of the targeted contract and runtime ablations.}",
            "  \\label{tab:focused-ablation-summary}",
            "  \\scriptsize",
            "  \\setlength{\\tabcolsep}{3.5pt}",
            "  \\begin{tabularx}{\\columnwidth}{L{1.55cm} L{0.8cm} >{\\centering\\arraybackslash}p{0.55cm} Y >{\\centering\\arraybackslash}p{0.55cm} >{\\centering\\arraybackslash}p{0.55cm} >{\\centering\\arraybackslash}p{0.7cm} Y}",
            "    \\toprule",
            "    Comparison & Cell & Runs & Success & Invalid & Recov. & Retry & Planner/tool \\\\",
            "    \\midrule",
            *body,
            "    \\bottomrule",
            "  \\end{tabularx}",
            "\\end{table}",
        ]
    )


def _harder_task_table_tex(rows: list[dict[str, Any]]) -> str:
    body = []
    for row in rows:
        body.append(
            "    "
            + " & ".join(
                [
                    row["family"],
                    row["cell"],
                    row["easy_success"],
                    row["harder_success"],
                    row["easy_planner_tool"],
                    row["harder_planner_tool"],
                    row["delta_planner"],
                    row["delta_tool"],
                ]
            )
            + " \\\\"
        )
    return "\n".join(
        [
            "\\begin{table}[!t]",
            "  \\centering",
            "  \\caption{Support-only easy-to-harder comparison for the retained cohorts.}",
            "  \\label{tab:harder-task-summary}",
            "  \\scriptsize",
            "  \\setlength{\\tabcolsep}{3pt}",
            "  \\begin{tabularx}{\\columnwidth}{L{0.95cm} L{0.8cm} Y Y Y Y >{\\centering\\arraybackslash}p{0.6cm} >{\\centering\\arraybackslash}p{0.6cm}}",
            "    \\toprule",
            "    Family & Cell & Easy success & Harder success & Easy P/T & Harder P/T & $\\Delta P$ & $\\Delta T$ \\\\",
            "    \\midrule",
            *body,
            "    \\bottomrule",
            "  \\end{tabularx}",
            "\\end{table}",
        ]
    )


def _load_system_overview_assets(runtime_only: dict[str, Any]) -> dict[str, Any]:
    runtime_rows = _load_family_prompt_runtime_rows(runtime_only)
    nav_row = runtime_rows[("navigation", "P1", "R1")]
    manip_row = runtime_rows[("manipulation", "P1", "R1")]
    nav_run_id = _select_probe_run_id(nav_row["run_ids"])
    manip_run_id = _select_probe_run_id(manip_row["run_ids"])
    nav_run_dir = _find_run_dir(nav_run_id)
    manip_run_dir = _find_run_dir(manip_run_id)
    nav_task_config = _load_json(nav_run_dir / "task_config.json")
    manip_task_config = _load_json(manip_run_dir / "task_config.json")
    nav_trajectory = _load_json(nav_run_dir / "artifacts" / "trajectory.json")
    manip_trajectory = _load_json(manip_run_dir / "artifacts" / "trajectory.json")
    nav_planner_trace = _load_json(nav_run_dir / "artifacts" / "planner_trace.json")
    manip_planner_trace = _load_json(manip_run_dir / "artifacts" / "planner_trace.json")

    nav_points = [
        (float(entry["pose"]["x"]), float(entry["pose"]["y"]))
        for entry in nav_trajectory["poses"]
    ]
    manip_gripper_points = [
        (float(entry["gripper_pose"]["x"]), float(entry["gripper_pose"]["y"]))
        for entry in manip_trajectory["states"]
    ]
    manip_object_points = [
        (float(entry["object_pose"]["x"]), float(entry["object_pose"]["y"]))
        for entry in manip_trajectory["states"]
    ]

    return {
        "navigation": {
            "start": nav_points[0],
            "goal": (
                float(nav_task_config["navigation"]["goal_pose"]["x"]),
                float(nav_task_config["navigation"]["goal_pose"]["y"]),
            ),
            "path": nav_points,
            "trace": _failure_trace_sequence(nav_planner_trace),
        },
        "manipulation": {
            "gripper_start": manip_gripper_points[0],
            "object_start": manip_object_points[0],
            "target": (
                float(manip_task_config["pick_place"]["target_pose"]["x"]),
                float(manip_task_config["pick_place"]["target_pose"]["y"]),
            ),
            "gripper_path": manip_gripper_points,
            "object_path": manip_object_points,
            "trace": _failure_trace_sequence(manip_planner_trace),
        },
    }


def _select_probe_run_id(run_ids: list[str]) -> str:
    for run_id in run_ids:
        if "probe" in run_id:
            return run_id
    return run_ids[0]


def _find_run_dir(run_id: str) -> Path:
    matches = list((REPO_ROOT / "results").glob(f"**/runs/{run_id}"))
    if not matches:
        raise FileNotFoundError(f"could not locate run directory for {run_id}")
    return matches[0]


def _failure_trace_sequence(planner_trace: list[dict[str, Any]]) -> list[str]:
    sequence: list[str] = []
    if planner_trace:
        invalid_tool = str(planner_trace[0]["parsed_action"]["tool_name"])
        sequence.append(invalid_tool)
    sequence.extend(["non-dispatchable", "R1 retry"])
    terminal_tool = ""
    fallback_tool = ""
    for row in planner_trace[1:]:
        tool_name = str(row["parsed_action"]["tool_name"])
        if not fallback_tool:
            fallback_tool = tool_name
        if tool_name in {"navigate_to", "scripted_pick_place_step"}:
            terminal_tool = tool_name
            break
    sequence.append(terminal_tool or fallback_tool)
    return sequence


def _system_overview_csv_rows(system_overview: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family in ("navigation", "manipulation"):
        trace = system_overview[family]["trace"]
        for index, value in enumerate(trace):
            rows.append({"panel": family, "kind": "trace", "index": index, "value": value})
    return rows


def _system_overview_figure_tex(system_overview: dict[str, Any]) -> str:
    nav = system_overview["navigation"]
    manip = system_overview["manipulation"]
    lines = [
        "\\begin{figure*}[!t]",
        "  \\centering",
        "  \\resizebox{\\textwidth}{!}{%",
        "  \\begin{tikzpicture}[x=1cm,y=1cm,>=Latex]",
        "    \\tikzstyle{stagebox}=[draw=ralBorder, rounded corners=2pt, fill=ralPanel, minimum height=1.3cm, align=center, font=\\small\\bfseries, text=ralSlate]",
        "    \\tikzstyle{smallnote}=[font=\\scriptsize, text=ralMuted, align=center]",
        "    \\tikzstyle{tracegood}=[draw=ralRepair, fill=ralRepair!12, rounded corners=1.5pt, minimum width=1.05cm, minimum height=0.45cm, align=center, font=\\ttfamily\\tiny, text=ralInk]",
        "    \\tikzstyle{tracewarn}=[draw=ralWarn, fill=ralWarn!12, rounded corners=1.5pt, minimum width=1.1cm, minimum height=0.45cm, align=center, font=\\ttfamily\\tiny, text=ralInk]",
        "    \\tikzstyle{traceinfo}=[draw=ralWarm, fill=ralWarm!12, rounded corners=1.5pt, minimum width=1.05cm, minimum height=0.45cm, align=center, font=\\scriptsize, text=ralInk]",
        "    \\node[stagebox, minimum width=2.15cm, font=\\small\\bfseries] (task) at (1.2,6.25) {\\shortstack{Task\\\\navigation or tabletop}};",
        "    \\node[stagebox, minimum width=2.25cm, font=\\small\\bfseries] (planner) at (4.1,6.25) {\\shortstack{Planner\\\\local \\texttt{mock\\_block\\_a}}};",
        "    \\node[stagebox, minimum width=3.2cm, font=\\small\\bfseries] (contract) at (7.75,6.25) {\\shortstack{Contract variant\\\\P0: direct action\\\\P1: typed tool call\\\\P2: typed tool call + self-check}};",
        "    \\node[stagebox, minimum width=2.55cm, font=\\small\\bfseries] (runtime) at (11.4,6.25) {\\shortstack{Runtime policy\\\\R0: bare dispatch\\\\R1: validate + 1 retry}};",
        "    \\node[stagebox, minimum width=2.6cm, font=\\small\\bfseries] (executor) at (14.7,6.25) {\\shortstack{Isaac Sim executor\\\\task-scoped tool namespace}};",
        "    \\node[stagebox, minimum width=2.4cm, font=\\small\\bfseries] (metrics) at (18.0,6.25) {\\shortstack{Metrics / outcomes\\\\success, invalid, retry, P/T calls}};",
        "    \\draw[thick, draw=ralMuted, ->] (task) -- (planner);",
        "    \\draw[thick, draw=ralMuted, ->] (planner) -- (contract);",
        "    \\draw[thick, draw=ralMuted, ->] (contract) -- (runtime);",
        "    \\draw[thick, draw=ralMuted, ->] (runtime) -- (executor);",
        "    \\draw[thick, draw=ralMuted, ->] (executor) -- (metrics);",
        "    \\node[smallnote] at (9.6,5.25) {The study manipulates the planner-to-executor contract and the runtime validation boundary while keeping the task families fixed.};",
        "    \\begin{scope}[shift={(0.2,0.05)}]",
        "      \\draw[draw=ralBorder, fill=white, rounded corners=2pt] (0,0) rectangle (9.1,4.45);",
        "      \\node[anchor=north west, font=\\small\\bfseries, text=ralSlate] at (0.18,4.22) {Navigation environment inset};",
        "      \\node[anchor=north west, font=\\scriptsize, text=ralMuted] at (0.18,3.92) {Representative frozen run: recoverable \\texttt{move\\_to\\_goal} handoff under \\texttt{P1/R1}.};",
        "      \\fill[ralPanel] (0.22,1.55) rectangle (4.55,3.55);",
        "      \\draw[draw=ralBorder] (0.22,1.55) rectangle (4.55,3.55);",
        *["      " + line for line in _navigation_scene_tex(nav)],
        "      \\node[anchor=west, font=\\scriptsize, text=ralMuted] at (0.22,1.16) {Failure-repair trace};",
        *["      " + line for line in _trace_chain_tex(nav["trace"], start_x=0.35, y=0.48, prefix="nav")],
        "    \\end{scope}",
        "    \\begin{scope}[shift={(9.6,0.05)}]",
        "      \\draw[draw=ralBorder, fill=white, rounded corners=2pt] (0,0) rectangle (9.1,4.45);",
        "      \\node[anchor=north west, font=\\small\\bfseries, text=ralSlate] at (0.18,4.22) {Tabletop environment inset};",
        "      \\node[anchor=north west, font=\\scriptsize, text=ralMuted] at (0.18,3.92) {Representative frozen run: recoverable \\texttt{move\\_object} handoff under \\texttt{P1/R1}.};",
        "      \\fill[ralPanel] (0.22,1.55) rectangle (4.55,3.55);",
        "      \\draw[draw=ralBorder] (0.22,1.55) rectangle (4.55,3.55);",
        *["      " + line for line in _manipulation_scene_tex(manip)],
        "      \\node[anchor=west, font=\\scriptsize, text=ralMuted] at (0.22,1.16) {Failure-repair trace};",
        *["      " + line for line in _trace_chain_tex(manip["trace"], start_x=0.35, y=0.48, prefix="manip")],
        "    \\end{scope}",
        "  \\end{tikzpicture}",
        "  }",
        "  \\caption{System overview of the evaluated planner-to-executor boundary. A task is mapped by the planner into one of three contract variants, then passed through bare dispatch \\texttt{R0} or validate-and-retry \\texttt{R1} before the Isaac Sim executor. Insets show representative navigation and tabletop task scenes together with compact failure-repair traces in which non-dispatchable verbs are rejected and corrected into executor-visible tools.}",
        "  \\label{fig:system-overview}",
        "\\end{figure*}",
    ]
    return "\n".join(lines)


def _navigation_scene_tex(nav: dict[str, Any]) -> list[str]:
    start = nav["start"]
    goal = nav["goal"]
    path = nav["path"]
    scaled = _scale_points(path, x_min=0.45, x_max=4.35, y_min=1.78, y_max=3.32)
    start_scaled = scaled[0]
    goal_scaled = _scale_points([goal], x_min=0.45, x_max=4.35, y_min=1.78, y_max=3.32, bounds=_point_bounds(path))[0]
    coords = " -- ".join(f"({x:.3f},{y:.3f})" for x, y in scaled)
    lines = [
        "\\draw[draw=ralGrid, step=0.48] (0.45,1.78) grid (4.35,3.32);",
        f"\\draw[very thick, draw=ralP1R0] {coords};",
        f"\\filldraw[fill=ralP0R0, draw=ralP0R0] ({start_scaled[0]:.3f},{start_scaled[1]:.3f}) circle (0.08);",
        f"\\filldraw[fill=ralP2R0, draw=ralP2R0] ({goal_scaled[0]:.3f},{goal_scaled[1]:.3f}) rectangle ++(0.16,0.16);",
        f"\\node[anchor=south west, font=\\scriptsize, text=ralSlate] at ({start_scaled[0]+0.06:.3f},{start_scaled[1]+0.06:.3f}) {{start}};",
        f"\\node[anchor=south east, font=\\scriptsize, text=ralSlate] at ({goal_scaled[0]-0.02:.3f},{goal_scaled[1]+0.18:.3f}) {{goal}};",
        "\\node[anchor=south east, font=\\scriptsize, text=ralMuted] at (4.35,1.58) {path from frozen trajectory};",
    ]
    return lines


def _manipulation_scene_tex(manip: dict[str, Any]) -> list[str]:
    gripper_points = manip["gripper_path"]
    object_points = manip["object_path"]
    bounds = _point_bounds(gripper_points + object_points + [manip["target"]])
    scaled_gripper = _scale_points(gripper_points, x_min=0.45, x_max=4.35, y_min=1.78, y_max=3.32, bounds=bounds)
    scaled_object = _scale_points(object_points, x_min=0.45, x_max=4.35, y_min=1.78, y_max=3.32, bounds=bounds)
    target = _scale_points([manip["target"]], x_min=0.45, x_max=4.35, y_min=1.78, y_max=3.32, bounds=bounds)[0]
    lines = [
        "\\fill[ralGrid!35] (0.72,2.00) rectangle (4.10,3.10);",
        "\\draw[draw=ralBorder] (0.72,2.00) rectangle (4.10,3.10);",
        f"\\draw[thick, draw=ralSlate] {' -- '.join(f'({x:.3f},{y:.3f})' for x, y in scaled_gripper)};",
        f"\\draw[thick, draw=ralWarm, dashed] {' -- '.join(f'({x:.3f},{y:.3f})' for x, y in scaled_object)};",
        f"\\filldraw[fill=ralP0R0, draw=ralP0R0] ({scaled_object[0][0]:.3f},{scaled_object[0][1]:.3f}) rectangle ++(0.14,0.14);",
        f"\\draw[draw=ralP2R0, line width=0.8pt, dashed] ({target[0]-0.12:.3f},{target[1]-0.12:.3f}) rectangle ({target[0]+0.12:.3f},{target[1]+0.12:.3f});",
        f"\\filldraw[fill=ralP1R0, draw=ralP1R0] ({scaled_gripper[0][0]:.3f},{scaled_gripper[0][1]:.3f}) circle (0.07);",
        f"\\node[anchor=north west, font=\\scriptsize, text=ralSlate] at ({scaled_object[0][0]+0.16:.3f},{scaled_object[0][1]+0.05:.3f}) {{object}};",
        f"\\node[anchor=south east, font=\\scriptsize, text=ralSlate] at ({target[0]-0.02:.3f},{target[1]+0.16:.3f}) {{target}};",
        "\\node[anchor=south east, font=\\scriptsize, text=ralMuted] at (4.35,1.58) {solid: gripper, dashed: object};",
    ]
    return lines


def _trace_chain_tex(sequence: list[str], *, start_x: float, y: float, prefix: str) -> list[str]:
    lines: list[str] = []
    step = 1.38
    names = []
    for index, item in enumerate(sequence):
        node_name = f"trace{prefix}{index}"
        names.append(node_name)
        style = "tracegood"
        if index == 0:
            style = "tracewarn"
        elif "non-dispatchable" in item or "retry" in item:
            style = "traceinfo"
        text = item if item in {"non-dispatchable", "R1 retry"} else _escape_latex(item)
        if item == "non-dispatchable":
            text = "non-\\\\dispatchable"
        lines.append(
            f"\\node[{style}] ({node_name}) at ({start_x + index * step:.2f},{y:.2f}) {{{text}}};"
        )
    for left, right in zip(names, names[1:]):
        lines.append(f"\\draw[draw=ralMuted, ->, thick] ({left}) -- ({right});")
    return lines


def _point_bounds(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    if abs(max_x - min_x) < 1e-9:
        max_x += 1.0
        min_x -= 1.0
    if abs(max_y - min_y) < 1e-9:
        max_y += 1.0
        min_y -= 1.0
    pad_x = max((max_x - min_x) * 0.15, 0.1)
    pad_y = max((max_y - min_y) * 0.15, 0.1)
    return min_x - pad_x, max_x + pad_x, min_y - pad_y, max_y + pad_y


def _scale_points(
    points: list[tuple[float, float]],
    *,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    bounds: tuple[float, float, float, float] | None = None,
) -> list[tuple[float, float]]:
    if bounds is None:
        bounds = _point_bounds(points)
    min_x, max_x, min_y, max_y = bounds
    x_range = max_x - min_x
    y_range = max_y - min_y
    scaled = []
    for x_value, y_value in points:
        x_scaled = x_min + ((x_value - min_x) / x_range) * (x_max - x_min)
        y_scaled = y_min + ((y_value - min_y) / y_range) * (y_max - y_min)
        scaled.append((x_scaled, y_scaled))
    return scaled


def _asset_manifest(
    *,
    final_closure: dict[str, Any],
    cross_family: dict[str, Any],
    written_outputs: dict[str, Path],
) -> str:
    lines = [
        "# RA-L Asset Manifest",
        "",
        "- Evidence base: frozen Block A final closure plus retained slice summaries.",
        f"- Final closure merged runs: `{final_closure['overall']['merged_runs']}`",
        f"- Final closure successful runs: `{final_closure['overall']['successful_runs']}`",
        f"- Cross-family prompt/runtime rows: `{len(cross_family['group_by_task_family_prompt_runtime'])}`",
        "- Figure style: manuscript figures are emitted as PGF/TikZ-backed `.tex` assets for vector-first compilation.",
        "- Figure 1 is a frozen manually selected asset and is intentionally out of scope for this generator.",
        "- Main reviewer-facing figures:",
        "  - `figures/fig1_system_overview_frozen.png`",
        "  - `figures/fig1_system_overview_frozen.pdf` (optional when present)",
        "  - `figures/main_condition_ordering.tex`",
        "  - `figures/invalid_actions_recovery.tex`",
        "  - `figures/planner_tool_overhead.tex`",
        "- Main reviewer-facing tables:",
        "  - `tables/experimental_design_summary.tex`",
        "  - `tables/main_outcome_summary.tex`",
        "  - `tables/planner_tool_overhead_summary.tex`",
        "- Support-only tables:",
        "  - `tables/focused_ablation_summary.tex`",
        "  - `tables/harder_task_summary.tex`",
        "",
        "## Written outputs",
        "",
    ]
    for key in sorted(written_outputs):
        lines.append(f"- `{key}`: `{written_outputs[key]}`")
    return "\n".join(lines)
