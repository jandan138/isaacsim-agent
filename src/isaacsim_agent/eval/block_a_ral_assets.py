"""Regenerate RA-L paper assets from the frozen Block A summaries."""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .block_a_paper import _AXIS
from .block_a_paper import _BACKGROUND
from .block_a_paper import _CELL_COLORS
from .block_a_paper import _Canvas
from .block_a_paper import _GRID
from .block_a_paper import _PANEL_BACKGROUND
from .block_a_paper import _PANEL_BORDER
from .block_a_paper import _TEXT
from .block_a_paper import _VALUE_TEXT


_CELL_ORDER = [
    ("P0", "R0"),
    ("P0", "R1"),
    ("P1", "R0"),
    ("P1", "R1"),
    ("P2", "R0"),
    ("P2", "R1"),
]

_PANEL_GRID = {
    1: (1, 1),
    2: (1, 2),
    3: (2, 2),
    4: (2, 2),
}


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
    """Write regenerated RA-L figures, table CSVs, and an asset manifest."""

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
    main_figure_path = figures_dir / "main_condition_ordering.png"
    _render_bar_grid_figure(
        path=main_figure_path,
        title="MAIN CONTRACT X RUNTIME ORDERING",
        subtitle="SUCCESS RATE ACROSS NAVIGATION / MANIPULATION AND EASY / HARDER SLICES",
        panels=main_panels,
        y_max=1.0,
        footer="Frozen sources: block_a_master_summary plus block_a_manipulation_harder_summary.",
        value_digits=2,
    )
    written_outputs["main_condition_ordering_figure"] = main_figure_path
    main_figure_csv = figures_dir / "main_condition_ordering.csv"
    _write_panel_csv(main_figure_csv, main_panels)
    written_outputs["main_condition_ordering_csv"] = main_figure_csv
    main_figure_tex = figures_dir / "main_condition_ordering.tex"
    _write_text(
        main_figure_tex,
        _figure_wrapper(
            image_filename="main_condition_ordering.png",
            caption=(
                "Success rate for the retained contract and runtime conditions across both task families and both "
                "difficulty slices. The under-specified direct-action contract \\texttt{P0/R0} is the weakest cell, "
                "\\texttt{P0/R1} recovers, and the typed tool-call contracts remain successful in the covered easy and "
                "harder slices."
            ),
            label="fig:main-condition-ordering",
        ),
    )
    written_outputs["main_condition_ordering_tex"] = main_figure_tex

    invalid_recovery_panels = _build_invalid_recovery_panels(prompt_rows, runtime_rows)
    invalid_recovery_path = figures_dir / "invalid_actions_recovery.png"
    _render_bar_grid_figure(
        path=invalid_recovery_path,
        title="INVALID ACTIONS AND RUNTIME-ASSISTED RECOVERY",
        subtitle="TOP: FIXED-R0 ACTION-INTERFACE ABLATION. BOTTOM: FIXED-P1 RUNTIME-ONLY ABLATION.",
        panels=invalid_recovery_panels,
        y_max=1.0,
        footer="Runtime-only success rises from 0.5 to 1.0 in both families while retries appear only under R1.",
        value_digits=2,
    )
    written_outputs["invalid_actions_recovery_figure"] = invalid_recovery_path
    invalid_recovery_csv = figures_dir / "invalid_actions_recovery.csv"
    _write_panel_csv(invalid_recovery_csv, invalid_recovery_panels)
    written_outputs["invalid_actions_recovery_csv"] = invalid_recovery_csv
    invalid_recovery_tex = figures_dir / "invalid_actions_recovery.tex"
    _write_text(
        invalid_recovery_tex,
        _figure_wrapper(
            image_filename="invalid_actions_recovery.png",
            caption=(
                "Top: under fixed bare dispatch \\texttt{R0}, typed tool-call contracts drive invalid actions to zero "
                "in both families. Bottom: under fixed \\texttt{P1}, validate-and-retry \\texttt{R1} adds retries only "
                "for the recoverable invalid-first-action probes and is accompanied by a 0.5 to 1.0 success change in "
                "both families."
            ),
            label="fig:invalid-actions-recovery",
        ),
    )
    written_outputs["invalid_actions_recovery_tex"] = invalid_recovery_tex

    overhead_panels = _build_overhead_panels(prompt_rows, manipulation_harder_rows)
    overhead_path = figures_dir / "planner_tool_overhead.png"
    _render_bar_grid_figure(
        path=overhead_path,
        title="PLANNER / TOOL OVERHEAD WITHIN TYPED CONTRACTS",
        subtitle="EASY ACTION-INTERFACE ABLATION AND HARDER MANIPULATION COMPARISONS",
        panels=overhead_panels,
        y_max=12.0,
        footer="Descriptive workload comparison only: the retained slices show P2 below P1 without a new success regime.",
        value_digits=2,
    )
    written_outputs["planner_tool_overhead_figure"] = overhead_path
    overhead_csv = figures_dir / "planner_tool_overhead.csv"
    _write_panel_csv(overhead_csv, overhead_panels)
    written_outputs["planner_tool_overhead_csv"] = overhead_csv
    overhead_tex = figures_dir / "planner_tool_overhead.tex"
    _write_text(
        overhead_tex,
        _figure_wrapper(
            image_filename="planner_tool_overhead.png",
            caption=(
                "Planner and tool calls in the retained \\texttt{P1} versus \\texttt{P2} comparisons. In the easy "
                "fixed-\\texttt{R0} action-interface ablation and in the harder manipulation slice under both runtimes, "
                "\\texttt{P2} keeps the same success profile as \\texttt{P1} while using fewer planner/tool calls. The "
                "figure is descriptive rather than a broader statistical claim."
            ),
            label="fig:planner-tool-overhead",
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

    final_closure_rows = _build_final_closure_summary_rows(main_rows)
    final_closure_csv = tables_dir / "final_closure_result_summary.csv"
    _write_csv(final_closure_csv, final_closure_rows)
    written_outputs["final_closure_result_summary_csv"] = final_closure_csv
    final_closure_tex = tables_dir / "final_closure_result_summary.tex"
    _write_text(final_closure_tex, _final_closure_table_tex(final_closure_rows))
    written_outputs["final_closure_result_summary_tex"] = final_closure_tex

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
            master_summary_path=Path(master_summary_path),
            prompt_only_summary_path=Path(prompt_only_summary_path),
            runtime_only_summary_path=Path(runtime_only_summary_path),
            manipulation_harder_summary_path=Path(manipulation_harder_summary_path),
            cross_family_summary_path=Path(cross_family_summary_path),
            written_outputs=written_outputs,
        ),
    )
    written_outputs["asset_manifest"] = manifest_path

    validation = {
        "final_closure_merged_runs": int(final_closure["overall"]["merged_runs"]),
        "final_closure_successful_runs": int(final_closure["overall"]["successful_runs"]),
        "main_result_cells": len(main_panels) * len(_CELL_ORDER),
        "prompt_only_family_rows": len(prompt_rows),
        "runtime_only_family_rows": len(runtime_rows),
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


def _normalize_task_family(value: str) -> str:
    return "manipulation" if value == "pick_place" else value


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
    for task_family, difficulty, label in [
        ("navigation", "easy", "NAVIGATION EASY"),
        ("manipulation", "easy", "MANIPULATION EASY"),
        ("navigation", "harder", "NAVIGATION HARDER"),
        ("manipulation", "harder", "MANIPULATION HARDER"),
    ]:
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
                    "color": _CELL_COLORS[(prompt_variant, runtime_variant)],
                }
            )
        panels.append(
            {
                "label": label,
                "note": f"{run_count} runs per cell",
                "bars": bars,
            }
        )
    return panels


def _build_invalid_recovery_panels(
    prompt_rows: dict[tuple[str, str, str], dict[str, Any]],
    runtime_rows: dict[tuple[str, str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    panels: list[dict[str, Any]] = []
    for family, label in [("navigation", "NAVIGATION INVALID ACTIONS"), ("manipulation", "MANIPULATION INVALID ACTIONS")]:
        bars = []
        for prompt_variant in ("P0", "P1", "P2"):
            row = prompt_rows[(family, prompt_variant, "R0")]
            bars.append(
                {
                    "label": prompt_variant,
                    "value": float(row["average_invalid_actions"]),
                    "color": _CELL_COLORS[(prompt_variant, "R0")],
                }
            )
        panels.append(
            {
                "label": label,
                "note": "Fixed R0 action-interface ablation",
                "bars": bars,
            }
        )

    for family, label in [("navigation", "NAVIGATION RETRIES"), ("manipulation", "MANIPULATION RETRIES")]:
        bars = []
        for runtime_variant in ("R0", "R1"):
            row = runtime_rows[(family, "P1", runtime_variant)]
            bars.append(
                {
                    "label": runtime_variant,
                    "value": float(row["average_retries"]),
                    "color": _CELL_COLORS[("P1", runtime_variant)],
                }
            )
        panels.append(
            {
                "label": label,
                "note": "Fixed P1 runtime-only ablation",
                "bars": bars,
            }
        )
    return panels


def _build_overhead_panels(
    prompt_rows: dict[tuple[str, str, str], dict[str, Any]],
    manipulation_harder_rows: dict[tuple[str, str, str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    panels: list[dict[str, Any]] = []
    for family, label in [("navigation", "NAVIGATION EASY"), ("manipulation", "MANIPULATION EASY")]:
        p1 = prompt_rows[(family, "P1", "R0")]
        p2 = prompt_rows[(family, "P2", "R0")]
        panels.append(
            {
                "label": label,
                "note": "Fixed R0 action-interface ablation",
                "bars": [
                    {"label": "P1-P", "value": float(p1["average_planner_calls"]), "color": _CELL_COLORS[("P1", "R0")]},
                    {"label": "P1-T", "value": float(p1["average_tool_calls"]), "color": _CELL_COLORS[("P1", "R0")]},
                    {"label": "P2-P", "value": float(p2["average_planner_calls"]), "color": _CELL_COLORS[("P2", "R0")]},
                    {"label": "P2-T", "value": float(p2["average_tool_calls"]), "color": _CELL_COLORS[("P2", "R0")]},
                ],
            }
        )

    for runtime_variant in ("R0", "R1"):
        p1 = manipulation_harder_rows[("manipulation", "harder", "P1", runtime_variant)]
        p2 = manipulation_harder_rows[("manipulation", "harder", "P2", runtime_variant)]
        panels.append(
            {
                "label": f"MANIPULATION HARDER {runtime_variant}",
                "note": "Harder manipulation summary",
                "bars": [
                    {"label": "P1-P", "value": float(p1["average_planner_calls"]), "color": _CELL_COLORS[("P1", runtime_variant)]},
                    {"label": "P1-T", "value": float(p1["average_tool_calls"]), "color": _CELL_COLORS[("P1", runtime_variant)]},
                    {"label": "P2-P", "value": float(p2["average_planner_calls"]), "color": _CELL_COLORS[("P2", runtime_variant)]},
                    {"label": "P2-T", "value": float(p2["average_tool_calls"]), "color": _CELL_COLORS[("P2", runtime_variant)]},
                ],
            }
        )
    return panels


def _build_experimental_design_rows(
    *,
    master_summary: dict[str, Any],
    prompt_only: dict[str, Any],
    runtime_only: dict[str, Any],
    manipulation_harder: dict[str, Any],
) -> list[dict[str, Any]]:
    coverage_rows = {(_normalize_task_family(str(row["task_family"])), str(row["task_difficulty"])): row for row in master_summary["coverage"]}
    manipulation_harder_run_count = int(manipulation_harder["analysis"]["questions"]["q1_p0_r0_worst"]["row"]["run_count"])
    manipulation_harder_task_count = int(manipulation_harder["matrix"]["task_count"])
    return [
        {
            "comparison_block": "main factorial",
            "task_family": "navigation",
            "slice": "easy",
            "varying_axes": "P0/P1/P2 x R0/R1",
            "runs_per_cell": coverage_rows[("navigation", "easy")]["run_count"] // 6,
            "total_runs": coverage_rows[("navigation", "easy")]["run_count"],
            "task_count": coverage_rows[("navigation", "easy")]["task_count"],
            "paper_role": "main contract x runtime ordering",
        },
        {
            "comparison_block": "main factorial",
            "task_family": "manipulation",
            "slice": "easy",
            "varying_axes": "P0/P1/P2 x R0/R1",
            "runs_per_cell": coverage_rows[("manipulation", "easy")]["run_count"] // 6,
            "total_runs": coverage_rows[("manipulation", "easy")]["run_count"],
            "task_count": coverage_rows[("manipulation", "easy")]["task_count"],
            "paper_role": "main contract x runtime ordering",
        },
        {
            "comparison_block": "main factorial",
            "task_family": "navigation",
            "slice": "harder",
            "varying_axes": "P0/P1/P2 x R0/R1",
            "runs_per_cell": coverage_rows[("navigation", "harder")]["run_count"] // 6,
            "total_runs": coverage_rows[("navigation", "harder")]["run_count"],
            "task_count": coverage_rows[("navigation", "harder")]["task_count"],
            "paper_role": "harder-task robustness",
        },
        {
            "comparison_block": "main factorial",
            "task_family": "manipulation",
            "slice": "harder",
            "varying_axes": "P0/P1/P2 x R0/R1",
            "runs_per_cell": manipulation_harder_run_count,
            "total_runs": manipulation_harder["overall"]["summarized_runs"],
            "task_count": manipulation_harder_task_count,
            "paper_role": "harder-task robustness",
        },
        {
            "comparison_block": "action-interface ablation",
            "task_family": "navigation + manipulation",
            "slice": "easy shared subset",
            "varying_axes": "P0/P1/P2 at fixed R0",
            "runs_per_cell": prompt_only["overall"]["summarized_runs"] // 3,
            "total_runs": prompt_only["overall"]["summarized_runs"],
            "task_count": prompt_only["matrix"]["task_count"],
            "paper_role": "invalid actions and P2 overhead",
        },
        {
            "comparison_block": "runtime-only ablation",
            "task_family": "navigation + manipulation",
            "slice": "recoverable easy probes",
            "varying_axes": "R0/R1 at fixed P1",
            "runs_per_cell": runtime_only["overall"]["summarized_runs"] // 2,
            "total_runs": runtime_only["overall"]["summarized_runs"],
            "task_count": runtime_only["matrix"]["task_count"],
            "paper_role": "recovery and retry value",
        },
    ]


def _build_final_closure_summary_rows(
    main_rows: dict[tuple[str, str, str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for prompt_variant, runtime_variant in _CELL_ORDER:
        rows.append(
            {
                "cell": f"{prompt_variant}/{runtime_variant}",
                "navigation_easy": _format_main_summary_cell(main_rows[("navigation", "easy", prompt_variant, runtime_variant)]),
                "manipulation_easy": _format_main_summary_cell(main_rows[("manipulation", "easy", prompt_variant, runtime_variant)]),
                "navigation_harder": _format_main_summary_cell(main_rows[("navigation", "harder", prompt_variant, runtime_variant)]),
                "manipulation_harder": _format_main_summary_cell(main_rows[("manipulation", "harder", prompt_variant, runtime_variant)]),
            }
        )
    return rows


def _build_focused_ablation_rows(
    *,
    prompt_only: dict[str, Any],
    runtime_only: dict[str, Any],
) -> list[dict[str, Any]]:
    prompt_questions = prompt_only["analysis"]["questions"]
    runtime_questions = runtime_only["analysis"]["questions"]
    prompt_rows = [
        ("action-interface ablation", "P0/R0", prompt_questions["q1_prompt_structure_reduces_invalid_actions"]["p0_r0"]),
        ("action-interface ablation", "P1/R0", prompt_questions["q1_prompt_structure_reduces_invalid_actions"]["p1_r0"]),
        ("action-interface ablation", "P2/R0", prompt_questions["q1_prompt_structure_reduces_invalid_actions"]["p2_r0"]),
        ("runtime-only ablation", "P1/R0", runtime_questions["q1_runtime_has_independent_value"]["p1_r0"]),
        ("runtime-only ablation", "P1/R1", runtime_questions["q1_runtime_has_independent_value"]["p1_r1"]),
    ]
    rows: list[dict[str, Any]] = []
    for comparison, cell, row in prompt_rows:
        rows.append(
            {
                "comparison": comparison,
                "cell": cell,
                "run_count": row["run_count"],
                "success": f"{row['successful_runs']}/{row['run_count']} ({_fmt(row['success_rate'])})",
                "invalid_action_runs": row["invalid_action_run_count"],
                "successful_recoveries": row["successful_invalid_action_runs"],
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
                    "task_family": family,
                    "cell": f"{prompt_variant}/{runtime_variant}",
                    "easy_success": f"{easy_row['successful_runs']}/{easy_row['run_count']} ({_fmt(easy_row['success_rate'])})",
                    "harder_success": f"{harder_row['successful_runs']}/{harder_row['run_count']} ({_fmt(harder_row['success_rate'])})",
                    "easy_planner_tool": f"{_fmt(easy_row['average_planner_calls'])}/{_fmt(easy_row['average_tool_calls'])}",
                    "harder_planner_tool": f"{_fmt(harder_row['average_planner_calls'])}/{_fmt(harder_row['average_tool_calls'])}",
                    "planner_delta": _fmt(float(harder_row["average_planner_calls"]) - float(easy_row["average_planner_calls"])),
                    "tool_delta": _fmt(float(harder_row["average_tool_calls"]) - float(easy_row["average_tool_calls"])),
                }
            )
    return rows


def _format_main_summary_cell(row: dict[str, Any]) -> str:
    return (
        f"S {row['successful_runs']}/{row['run_count']} ({_fmt(row['success_rate'])}); "
        f"I { _fmt(row['average_invalid_actions'])}; "
        f"Rt {_fmt(row['average_retries'])}; "
        f"P/T {_fmt(row['average_planner_calls'])}/{_fmt(row['average_tool_calls'])}"
    )


def _render_bar_grid_figure(
    *,
    path: Path,
    title: str,
    subtitle: str,
    panels: list[dict[str, Any]],
    y_max: float,
    footer: str,
    value_digits: int,
) -> None:
    panel_count = len(panels)
    rows, cols = _PANEL_GRID.get(panel_count, (math.ceil(panel_count / 2), 2))
    width = 1760
    height = 220 + rows * 410 + max(0, rows - 1) * 28 + 90
    canvas = _Canvas(width=width, height=height, background=_BACKGROUND)

    canvas.draw_text(64, 36, title, color=_TEXT, scale=4)
    canvas.draw_text(64, 84, subtitle, color=_VALUE_TEXT, scale=2)

    ticks = _build_ticks(y_max)
    panel_width = 800
    panel_height = 410
    origin_x = 60
    origin_y = 150
    panel_gap_x = 34
    panel_gap_y = 28
    inner_left = 80
    inner_right = 26
    inner_top = 90
    inner_bottom = 108

    for panel_index, panel in enumerate(panels):
        grid_row = panel_index // cols
        grid_col = panel_index % cols
        panel_x = origin_x + grid_col * (panel_width + panel_gap_x)
        panel_y = origin_y + grid_row * (panel_height + panel_gap_y)

        canvas.fill_rect(panel_x, panel_y, panel_x + panel_width, panel_y + panel_height, _PANEL_BACKGROUND)
        canvas.draw_rect(panel_x, panel_y, panel_x + panel_width, panel_y + panel_height, _PANEL_BORDER)
        canvas.draw_centered_text(panel_x + panel_width // 2, panel_y + 18, str(panel["label"]), color=_TEXT, scale=3)
        canvas.draw_centered_text(panel_x + panel_width // 2, panel_y + 50, str(panel["note"]), color=_VALUE_TEXT, scale=2)

        chart_left = panel_x + inner_left
        chart_right = panel_x + panel_width - inner_right
        chart_top = panel_y + inner_top
        chart_bottom = panel_y + panel_height - inner_bottom
        chart_width = chart_right - chart_left
        chart_height = chart_bottom - chart_top

        for tick in ticks:
            tick_y = chart_bottom - int(round((tick / y_max) * chart_height))
            canvas.draw_line(chart_left, tick_y, chart_right, tick_y, _GRID)
            canvas.draw_text(panel_x + 14, tick_y - 8, _fmt(tick), color=_VALUE_TEXT, scale=2)

        canvas.draw_line(chart_left, chart_top, chart_left, chart_bottom, _AXIS)
        canvas.draw_line(chart_left, chart_bottom, chart_right, chart_bottom, _AXIS)

        bars = panel["bars"]
        group_gap = 20
        available_width = chart_width - group_gap * (len(bars) + 1)
        bar_width = max(18, int(available_width / max(len(bars), 1)))
        for bar_index, bar in enumerate(bars):
            bar_left = chart_left + group_gap + bar_index * (bar_width + group_gap)
            bar_right = bar_left + bar_width
            bar_height = int(round((float(bar["value"]) / y_max) * chart_height))
            bar_top = chart_bottom - max(bar_height, 2)
            canvas.fill_rect(bar_left, bar_top, bar_right, chart_bottom, tuple(bar["color"]))
            canvas.draw_rect(bar_left, bar_top, bar_right, chart_bottom, _AXIS)
            canvas.draw_centered_text(
                (bar_left + bar_right) // 2,
                max(chart_top + 4, bar_top - 22),
                _fmt(float(bar["value"]), digits=value_digits),
                color=_VALUE_TEXT,
                scale=2,
            )
            canvas.draw_centered_text(
                (bar_left + bar_right) // 2,
                chart_bottom + 18,
                str(bar["label"]),
                color=_TEXT,
                scale=2,
            )

    canvas.draw_text(64, height - 48, footer, color=_VALUE_TEXT, scale=2)
    canvas.write_png(path)


def _build_ticks(y_max: float) -> list[float]:
    if y_max <= 1.0:
        return [0.0, 0.25, 0.5, 0.75, 1.0]
    step = y_max / 4.0
    return [round(step * index, 2) for index in range(5)]


def _write_panel_csv(path: Path, panels: list[dict[str, Any]]) -> None:
    rows: list[dict[str, Any]] = []
    for panel in panels:
        for bar in panel["bars"]:
            rows.append(
                {
                    "panel_label": panel["label"],
                    "panel_note": panel["note"],
                    "bar_label": bar["label"],
                    "value": _fmt(float(bar["value"]), digits=6),
                }
            )
    _write_csv(path, rows)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _experimental_design_table_tex(rows: list[dict[str, Any]]) -> str:
    body_rows = [
        " & ".join(
            [
                str(row["comparison_block"]).title(),
                _display_family(str(row["task_family"])),
                _display_slice(str(row["slice"])),
                str(row["varying_axes"]),
                str(row["runs_per_cell"]),
                str(row["total_runs"]),
                str(row["paper_role"]).title(),
            ]
        )
        + r" \\"
        for row in rows
    ]
    return "\n".join(
        [
            r"\begin{table}[t]",
            r"\centering",
            r"\caption{Experimental design summary. The main factorial comparison covers a shared easy slice plus one harder slice per task family. Two compact ablations isolate action-interface and runtime-validation effects without adding new experiment axes.}",
            r"\label{tab:experimental-design-summary}",
            r"\footnotesize",
            r"\resizebox{\columnwidth}{!}{%",
            r"\begin{tabular}{llllrrl}",
            r"\hline",
            r"Block & Family & Slice & Varying axes & Runs/cell & Runs & Role \\",
            r"\hline",
            *body_rows,
            r"\hline",
            r"\end{tabular}%",
            r"}",
            r"\end{table}",
            "",
        ]
    )


def _final_closure_table_tex(rows: list[dict[str, Any]]) -> str:
    body_rows = [
        " & ".join(
            [
                str(row["cell"]),
                _summary_stack(str(row["navigation_easy"])),
                _summary_stack(str(row["manipulation_easy"])),
                _summary_stack(str(row["navigation_harder"])),
                _summary_stack(str(row["manipulation_harder"])),
            ]
        )
        + r" \\"
        for row in rows
    ]
    return "\n".join(
        [
            r"\begin{table*}[t]",
            r"\centering",
            r"\caption{Final closure result summary across the four retained cohorts. Each cell reports success, invalid actions per run, retries per run, and planner/tool calls per run.}",
            r"\label{tab:final-closure-result-summary}",
            r"\footnotesize",
            r"\resizebox{\textwidth}{!}{%",
            r"\begin{tabular}{lcccc}",
            r"\hline",
            r"Cell & Navigation Easy & Manipulation Easy & Navigation Harder & Manipulation Harder \\",
            r"\hline",
            *body_rows,
            r"\hline",
            r"\end{tabular}%",
            r"}",
            r"\end{table*}",
            "",
        ]
    )


def _focused_ablation_table_tex(rows: list[dict[str, Any]]) -> str:
    body_rows = [
        " & ".join(
            [
                str(row["comparison"]).title(),
                str(row["cell"]),
                str(row["run_count"]),
                str(row["success"]),
                str(row["invalid_action_runs"]),
                str(row["successful_recoveries"]),
                str(row["avg_retries"]),
                str(row["planner_tool"]),
            ]
        )
        + r" \\"
        for row in rows
    ]
    return "\n".join(
        [
            r"\begin{table}[t]",
            r"\centering",
            r"\caption{Focused ablation summary. This compact table remains the first manuscript table to drop if page pressure requires it.}",
            r"\label{tab:focused-ablation-summary}",
            r"\footnotesize",
            r"\resizebox{\columnwidth}{!}{%",
            r"\begin{tabular}{llrlllll}",
            r"\hline",
            r"Comparison & Cell & Runs & Success & Invalid runs & Recoveries & Avg retries & Planner/Tool \\",
            r"\hline",
            *body_rows,
            r"\hline",
            r"\end{tabular}%",
            r"}",
            r"\end{table}",
            "",
        ]
    )


def _harder_task_table_tex(rows: list[dict[str, Any]]) -> str:
    body_rows = [
        " & ".join(
            [
                _display_family(str(row["task_family"])),
                str(row["cell"]),
                str(row["easy_success"]),
                str(row["harder_success"]),
                str(row["easy_planner_tool"]),
                str(row["harder_planner_tool"]),
                str(row["planner_delta"]),
                str(row["tool_delta"]),
            ]
        )
        + r" \\"
        for row in rows
    ]
    return "\n".join(
        [
            r"\begin{table}[t]",
            r"\centering",
            r"\caption{Optional harder-task support table. It is not bound to a dedicated placeholder in the current draft, but it records the retained easy-to-harder comparison that supports the cost-amplification interpretation.}",
            r"\label{tab:harder-task-summary}",
            r"\footnotesize",
            r"\resizebox{\columnwidth}{!}{%",
            r"\begin{tabular}{llcccccc}",
            r"\hline",
            r"Family & Cell & Easy success & Harder success & Easy P/T & Harder P/T & Delta P & Delta T \\",
            r"\hline",
            *body_rows,
            r"\hline",
            r"\end{tabular}%",
            r"}",
            r"\end{table}",
            "",
        ]
    )


def _summary_stack(text: str) -> str:
    return r"\shortstack[c]{" + text.replace("; ", r"\\") + "}"


def _display_family(value: str) -> str:
    if value == "navigation + manipulation":
        return "Mixed"
    return value.title()


def _display_slice(value: str) -> str:
    return value.replace("_", " ").title()


def _figure_wrapper(*, image_filename: str, caption: str, label: str) -> str:
    return "\n".join(
        [
            "\\begin{figure*}[t]",
            "  \\centering",
            f"  \\includegraphics[width=\\textwidth]{{figures/{image_filename}}}",
            f"  \\caption{{{caption}}}",
            f"  \\label{{{label}}}",
            "\\end{figure*}",
            "",
        ]
    )


def _asset_manifest(
    *,
    final_closure: dict[str, Any],
    master_summary_path: Path,
    prompt_only_summary_path: Path,
    runtime_only_summary_path: Path,
    manipulation_harder_summary_path: Path,
    cross_family_summary_path: Path,
    written_outputs: dict[str, Path],
) -> str:
    lines = [
        "# RA-L Asset Manifest",
        "",
        "## Canonical frozen evidence",
        "",
        f"- Final closure summary: `{Path(final_closure['output_dir']) / 'block_a_final_closure_summary.json'}`",
        f"- Master summary: `{master_summary_path.resolve()}`",
        f"- Prompt-only ablation: `{prompt_only_summary_path.resolve()}`",
        f"- Runtime-only ablation: `{runtime_only_summary_path.resolve()}`",
        f"- Manipulation harder: `{manipulation_harder_summary_path.resolve()}`",
        f"- Cross-family summary: `{cross_family_summary_path.resolve()}`",
        "",
        "## Frozen closure headline",
        "",
        f"- Merged runs: `{final_closure['overall']['merged_runs']}`",
        f"- Successful runs: `{final_closure['overall']['successful_runs']}`",
        f"- Success rate: `{_fmt(final_closure['overall']['success_rate'], digits=6)}`",
        "",
        "## Written outputs",
        "",
    ]
    for key in sorted(written_outputs):
        lines.append(f"- {key}: `{written_outputs[key].resolve()}`")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Legacy paper packaging under `results/processed/block_a_master_summary/paper_figures/` and `paper_tables/` was used only as a layout reference.",
            "- The regenerated RA-L figure PNGs and table CSVs are written under `paper/versions/ral/` and do not modify immutable processed-result directories.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fmt(value: Any, *, digits: int = 2) -> str:
    numeric = float(value)
    if abs(numeric - round(numeric)) <= 1e-9 and digits <= 2:
        return f"{numeric:.1f}"
    return f"{numeric:.{digits}f}".rstrip("0").rstrip(".")
