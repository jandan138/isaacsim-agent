"""Unified Block A final-closure summary over the master checkpoint and final closure slices."""

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


_FINAL_CSV_COLUMNS = [
    "question_id",
    "question",
    "answer",
    "answer_label",
    "evidence_sources",
    "explanation",
]


@dataclass(frozen=True)
class BlockAFinalClosureProcessedSource:
    """One processed directory loaded into the unified closure aggregate."""

    source_name: str
    input_dir: Path
    run_summary_jsonl_path: Path
    validation_json_path: Path
    run_count: int
    successful_runs: int
    success_rate: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_kind": "processed_runs",
            "source_name": self.source_name,
            "input_dir": str(self.input_dir.resolve()),
            "run_summary_jsonl_path": str(self.run_summary_jsonl_path.resolve()),
            "validation_json_path": str(self.validation_json_path.resolve()),
            "run_count": self.run_count,
            "successful_runs": self.successful_runs,
            "success_rate": self.success_rate,
        }


@dataclass(frozen=True)
class BlockAFinalClosureReferenceSummary:
    """One summary JSON used as structured evidence for the closure answers."""

    source_name: str
    input_dir: Path
    summary_json_path: Path

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_kind": "reference_summary",
            "source_name": self.source_name,
            "input_dir": str(self.input_dir.resolve()),
            "summary_json_path": str(self.summary_json_path.resolve()),
        }


@dataclass(frozen=True)
class BlockAFinalClosureSummaryResult:
    """Materialized outputs for the Block A final closure summary."""

    output_dir: Path
    processed_sources: list[BlockAFinalClosureProcessedSource]
    reference_summaries: list[BlockAFinalClosureReferenceSummary]
    bundle: SummaryBundle
    summary: dict[str, Any]
    written_outputs: dict[str, Path]


def summarize_block_a_final_closure_processed_dirs(
    *,
    master_summary_dir: str | Path,
    runtime_only_dir: str | Path,
    prompt_only_dir: str | Path,
    manipulation_harder_dir: str | Path,
    output_dir: str | Path,
) -> BlockAFinalClosureSummaryResult:
    """Build the unified Block A final closure summary from processed Block A outputs."""

    output_dir = Path(output_dir)
    processed_specs = [
        ("master_summary", Path(master_summary_dir)),
        ("runtime_only_ablation", Path(runtime_only_dir)),
        ("prompt_only_ablation", Path(prompt_only_dir)),
        ("manipulation_harder", Path(manipulation_harder_dir)),
    ]
    summary_specs = [
        ("master_summary", Path(master_summary_dir), "block_a_master_summary.json"),
        ("runtime_only_ablation", Path(runtime_only_dir), "block_a_runtime_only_summary.json"),
        ("prompt_only_ablation", Path(prompt_only_dir), "block_a_prompt_only_summary.json"),
        ("manipulation_harder", Path(manipulation_harder_dir), "block_a_manipulation_harder_summary.json"),
    ]

    processed_sources, summaries, validations = _load_processed_sources(processed_specs)
    _ensure_unique_run_ids(summaries)
    reference_summaries, reference_payloads = _load_reference_summaries(summary_specs)

    bundle = SummaryBundle(
        summaries=summaries,
        validations=validations,
        aggregate=aggregate_episode_summaries(summaries),
    )
    written_outputs = write_summary_outputs(bundle=bundle, output_dir=output_dir)

    summary = build_block_a_final_closure_summary(
        bundle=bundle,
        processed_sources=processed_sources,
        reference_summaries=reference_summaries,
        reference_payloads=reference_payloads,
        output_dir=output_dir,
    )

    summary_json_path = output_dir / "block_a_final_closure_summary.json"
    summary_json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    written_outputs["final_closure_summary_json"] = summary_json_path

    summary_csv_path = output_dir / "block_a_final_closure_summary.csv"
    _write_final_csv(summary_csv_path, summary["questions"])
    written_outputs["final_closure_summary_csv"] = summary_csv_path

    summary_md_path = output_dir / "block_a_final_closure_summary.md"
    summary_md_path.write_text(_render_final_markdown(summary), encoding="utf-8")
    written_outputs["final_closure_summary_md"] = summary_md_path

    return BlockAFinalClosureSummaryResult(
        output_dir=output_dir,
        processed_sources=processed_sources,
        reference_summaries=reference_summaries,
        bundle=bundle,
        summary=summary,
        written_outputs=written_outputs,
    )


def build_block_a_final_closure_summary(
    *,
    bundle: SummaryBundle,
    processed_sources: list[BlockAFinalClosureProcessedSource],
    reference_summaries: list[BlockAFinalClosureReferenceSummary],
    reference_payloads: dict[str, dict[str, Any]],
    output_dir: str | Path,
) -> dict[str, Any]:
    """Build the structured Block A final closure payload."""

    master_summary = reference_payloads["master_summary"]
    runtime_only = reference_payloads["runtime_only_ablation"]
    prompt_only = reference_payloads["prompt_only_ablation"]
    manipulation_harder = reference_payloads["manipulation_harder"]

    master_main_effect = _find_master_question(master_summary, "主效应")
    master_cross_family = _find_master_question(master_summary, "跨 task families")
    master_harder_navigation = _find_master_question(master_summary, "harder navigation")

    runtime_analysis = _required_mapping(runtime_only, "analysis", "runtime_only_ablation")
    runtime_questions = _required_mapping(runtime_analysis, "questions", "runtime_only_ablation.analysis")
    prompt_analysis = _required_mapping(prompt_only, "analysis", "prompt_only_ablation")
    prompt_questions = _required_mapping(prompt_analysis, "questions", "prompt_only_ablation.analysis")
    manipulation_analysis = _required_mapping(manipulation_harder, "analysis", "manipulation_harder")
    manipulation_questions = _required_mapping(manipulation_analysis, "questions", "manipulation_harder.analysis")

    q1_answer = bool(
        _question_answer(master_main_effect)
        and _question_answer(manipulation_questions.get("q1_p0_r0_worst"))
        and _question_answer(manipulation_questions.get("q2_r1_recovers_p0"))
        and _question_answer(manipulation_questions.get("q3_p1_p2_success"))
        and _question_answer(manipulation_questions.get("q4_p2_more_efficient_than_p1"))
    )
    q2_answer = bool(_question_answer(runtime_questions.get("q1_runtime_has_independent_value")))
    q3_answer = bool(
        _question_answer(prompt_questions.get("q1_prompt_structure_reduces_invalid_actions"))
        and _question_answer(prompt_questions.get("q2_p2_more_efficient_than_p1"))
    )
    q4_answer = bool(
        _question_answer(master_cross_family)
        and _question_answer(runtime_questions.get("q3_cross_family_consistency"))
        and _question_answer(prompt_questions.get("q3_cross_family_consistency"))
    )
    q5_answer = bool(
        _question_answer(master_harder_navigation)
        and _question_answer(manipulation_questions.get("q5_harder_tasks_amplify_differences"))
    )
    q6_answer = bool(q1_answer and q2_answer and q3_answer and q4_answer and q5_answer)

    runtime_p1_r0 = _prompt_runtime_row(runtime_only, "P1", "R0")
    runtime_p1_r1 = _prompt_runtime_row(runtime_only, "P1", "R1")
    prompt_p0_r0 = _prompt_runtime_row(prompt_only, "P0", "R0")
    prompt_p1_r0 = _prompt_runtime_row(prompt_only, "P1", "R0")
    prompt_p2_r0 = _prompt_runtime_row(prompt_only, "P2", "R0")

    questions = [
        {
            "question_id": "q1_main_effect_stable",
            "question": "Prompt × Runtime 的主效应是否已经稳定成立？",
            "answer": q1_answer,
            "answer_label": _yes_no(q1_answer),
            "evidence_sources": ["master_summary", "manipulation_harder"],
            "explanation": (
                "是。既有 master summary 已在 navigation easy、manipulation easy、navigation harder 上确认同一排序，"
                "而新的 manipulation harder slice 也继续满足 P0/R0 最差、P0/R1 可恢复、P1/P2 全成功且 P2 更省 planner/tool calls。"
                if q1_answer
                else "否。至少有一个关键 closure slice 未能保持既有 Prompt × Runtime 排序。"
            ),
            "supporting_metrics": {
                "master_main_effect": master_main_effect,
                "manipulation_harder": {
                    "p0_r0": manipulation_questions.get("q1_p0_r0_worst"),
                    "p0_r1": manipulation_questions.get("q2_r1_recovers_p0"),
                    "p1_p2_success": manipulation_questions.get("q3_p1_p2_success"),
                    "p2_efficiency": manipulation_questions.get("q4_p2_more_efficient_than_p1"),
                },
            },
        },
        {
            "question_id": "q2_runtime_independent_value",
            "question": "runtime 是否有独立价值？",
            "answer": q2_answer,
            "answer_label": _yes_no(q2_answer),
            "evidence_sources": ["runtime_only_ablation"],
            "explanation": (
                "是。固定 P1 后，runtime-only ablation 中 P1/R0 的成功率从 "
                f"`{runtime_p1_r0.get('success_rate')}` 提升到 P1/R1 的 `{runtime_p1_r1.get('success_rate')}`，"
                "recoverable invalid-action runs 被 R1 转化为成功恢复。"
                if q2_answer and runtime_p1_r0 and runtime_p1_r1
                else "否。固定 P1 后没有观察到来自 runtime validation + retry 的独立收益。"
            ),
            "supporting_metrics": {
                "p1_r0": runtime_p1_r0,
                "p1_r1": runtime_p1_r1,
            },
        },
        {
            "question_id": "q3_prompt_independent_value",
            "question": "prompt structure 是否有独立价值？",
            "answer": q3_answer,
            "answer_label": _yes_no(q3_answer),
            "evidence_sources": ["prompt_only_ablation"],
            "explanation": (
                "是。固定 R0 后，P0/R0 仍产生最高 invalid actions，P1/P2 将 invalid actions 压到 0，"
                "并且 P2 在保持成功率的同时继续低于 P1 的 planner/tool calls。"
                if q3_answer
                else "否。固定 R0 后 prompt structure 没有带来稳定的 invalid-action 或效率收益。"
            ),
            "supporting_metrics": {
                "p0_r0": prompt_p0_r0,
                "p1_r0": prompt_p1_r0,
                "p2_r0": prompt_p2_r0,
            },
        },
        {
            "question_id": "q4_cross_family_consistency",
            "question": "这些趋势是否跨 navigation / manipulation 成立？",
            "answer": q4_answer,
            "answer_label": _yes_no(q4_answer),
            "evidence_sources": ["master_summary", "runtime_only_ablation", "prompt_only_ablation"],
            "explanation": (
                "是。master summary 已经给出共享 easy slice 的 family-level 一致性，新加入的 runtime-only 和 prompt-only cross-family ablations 也都同时在 navigation 与 manipulation 上复现了同方向结论。"
                if q4_answer
                else "否。至少有一个 cross-family ablation 没能在 navigation 与 manipulation 上同时复现既有趋势。"
            ),
            "supporting_metrics": {
                "master_cross_family": master_cross_family,
                "runtime_only_cross_family": runtime_questions.get("q3_cross_family_consistency"),
                "prompt_only_cross_family": prompt_questions.get("q3_cross_family_consistency"),
            },
        },
        {
            "question_id": "q5_harder_cost_not_ordering",
            "question": "harder navigation 与 harder manipulation 是否只增加成本、不改变排序？",
            "answer": q5_answer,
            "answer_label": _yes_no(q5_answer),
            "evidence_sources": ["master_summary", "manipulation_harder"],
            "explanation": (
                "是。master summary 已确认 harder navigation 只放大 planner/tool 成本而不改变排序，"
                "新的 manipulation harder summary 也显示相对 easy manipulation 需要更多 planner/tool calls，"
                "但排序仍保持不变。"
                if q5_answer
                else "否。至少有一个 harder slice 改变了原有排序，或没有显示清晰的成本放大。"
            ),
            "supporting_metrics": {
                "harder_navigation": master_harder_navigation,
                "harder_manipulation": manipulation_questions.get("q5_harder_tasks_amplify_differences"),
            },
        },
        {
            "question_id": "q6_block_a_closed_for_paper",
            "question": "Block A 是否已实验封闭到足以单独支撑一整篇系统设计论文？",
            "answer": q6_answer,
            "answer_label": _yes_no(q6_answer),
            "evidence_sources": [
                "master_summary",
                "runtime_only_ablation",
                "prompt_only_ablation",
                "manipulation_harder",
            ],
            "explanation": (
                "是。在当前受控系统设计论文 framing 下，Block A 已同时覆盖主效应、runtime 单因子、prompt 单因子、"
                "以及 navigation / manipulation 的 harder cost amplification，因此 reviewer 最直接的封闭性质疑已经被最小补齐。"
                if q6_answer
                else "否。当前 closure 证据仍不足以把 Block A 作为单独完整论文主线。"
            ),
            "supporting_metrics": {
                "merged_runs": bundle.aggregate.total_runs,
                "merged_success_rate": bundle.aggregate.success_rate,
            },
        },
    ]

    supporting_findings = (
        ["Master summary: " + _question_explanation(master_main_effect)]
        + ["Runtime-only: " + finding for finding in _analysis_findings(runtime_analysis)]
        + ["Prompt-only: " + finding for finding in _analysis_findings(prompt_analysis)]
        + ["Manipulation harder: " + finding for finding in _analysis_findings(manipulation_analysis)]
    )

    return {
        "summary_title": "Block A Final Closure Summary",
        "description": (
            "Unified Block A closure over the existing master checkpoint plus the runtime-only ablation, "
            "prompt-only ablation, and harder manipulation slice."
        ),
        "output_dir": str(Path(output_dir).resolve()),
        "processed_sources": [source.to_dict() for source in processed_sources],
        "reference_summaries": [source.to_dict() for source in reference_summaries],
        "overall": {
            "merged_runs": bundle.aggregate.total_runs,
            "contract_complete_runs": bundle.aggregate.contract_complete_runs,
            "run_complete_runs": bundle.aggregate.run_complete_runs,
            "successful_runs": bundle.aggregate.successful_runs,
            "success_rate": bundle.aggregate.success_rate,
            "total_planner_calls": bundle.aggregate.total_planner_calls,
            "total_tool_calls": bundle.aggregate.total_tool_calls,
            "total_invalid_actions": bundle.aggregate.total_invalid_actions,
            "total_retries": bundle.aggregate.total_retries,
            "average_step_count": bundle.aggregate.average_step_count,
            "average_episode_time_s": bundle.aggregate.average_episode_time_s,
            "by_task_family": bundle.aggregate.by_task_family,
        },
        "source_overview": [source.to_dict() for source in processed_sources],
        "questions": questions,
        "supporting_findings": supporting_findings,
        "closure_verdict": {
            "answer": q6_answer,
            "answer_label": _yes_no(q6_answer),
            "recommended_next_step": "freeze_block_a_and_write_paper" if q6_answer else "investigate_remaining_gap",
        },
    }


def _load_processed_sources(
    specs: list[tuple[str, Path]],
) -> tuple[list[BlockAFinalClosureProcessedSource], list[EpisodeSummary], list[RunValidation]]:
    sources: list[BlockAFinalClosureProcessedSource] = []
    summaries: list[EpisodeSummary] = []
    validations: list[RunValidation] = []

    for source_name, input_dir in specs:
        run_summary_jsonl_path = input_dir / "run_summary.jsonl"
        validation_json_path = input_dir / "validation.json"
        if not run_summary_jsonl_path.is_file():
            raise FileNotFoundError(f"missing run_summary.jsonl in processed directory: {input_dir}")
        if not validation_json_path.is_file():
            raise FileNotFoundError(f"missing validation.json in processed directory: {input_dir}")

        source_summaries = _load_episode_summaries(run_summary_jsonl_path)
        source_validations = _load_validations(validation_json_path)
        successful_runs = sum(1 for summary in source_summaries if summary.success is True)
        success_rate = round(successful_runs / len(source_summaries), 6) if source_summaries else None

        sources.append(
            BlockAFinalClosureProcessedSource(
                source_name=source_name,
                input_dir=input_dir,
                run_summary_jsonl_path=run_summary_jsonl_path,
                validation_json_path=validation_json_path,
                run_count=len(source_summaries),
                successful_runs=successful_runs,
                success_rate=success_rate,
            )
        )
        summaries.extend(source_summaries)
        validations.extend(source_validations)

    summaries.sort(key=lambda item: item.run_id)
    validations.sort(key=lambda item: item.run_id)
    return sources, summaries, validations


def _load_reference_summaries(
    specs: list[tuple[str, Path, str]],
) -> tuple[list[BlockAFinalClosureReferenceSummary], dict[str, dict[str, Any]]]:
    sources: list[BlockAFinalClosureReferenceSummary] = []
    payloads: dict[str, dict[str, Any]] = {}

    for source_name, input_dir, filename in specs:
        summary_json_path = input_dir / filename
        if not summary_json_path.is_file():
            raise FileNotFoundError(f"missing summary JSON for {source_name}: {summary_json_path}")
        payload = json.loads(summary_json_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"expected summary JSON mapping for {source_name}: {summary_json_path}")
        sources.append(
            BlockAFinalClosureReferenceSummary(
                source_name=source_name,
                input_dir=input_dir,
                summary_json_path=summary_json_path,
            )
        )
        payloads[source_name] = payload
    return sources, payloads


def _load_episode_summaries(path: Path) -> list[EpisodeSummary]:
    rows: list[EpisodeSummary] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(EpisodeSummary(**json.loads(line)))
    return rows


def _load_validations(path: Path) -> list[RunValidation]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"expected validation JSON list: {path}")

    rows: list[RunValidation] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError(f"expected validation row mapping: {path}")
        issues = [
            ValidationIssue(
                code=str(issue["code"]),
                message=str(issue["message"]),
                severity=str(issue.get("severity", "error")),
                relative_path=(
                    str(issue.get("relative_path")) if issue.get("relative_path") is not None else None
                ),
            )
            for issue in item.get("issues", [])
            if isinstance(issue, dict)
        ]
        rows.append(
            RunValidation(
                run_id=str(item["run_id"]),
                run_dir=Path(str(item["run_dir"])),
                required_files_present=bool(item.get("required_files_present", False)),
                parsed_files_ok=bool(item.get("parsed_files_ok", False)),
                event_count=int(item.get("event_count", 0)),
                has_episode_end=bool(item.get("has_episode_end", False)),
                expected_artifact_count=int(item.get("expected_artifact_count", 0)),
                missing_artifacts=[str(value) for value in item.get("missing_artifacts", [])],
                contract_complete=bool(item.get("contract_complete", False)),
                run_complete=bool(item.get("run_complete", False)),
                issues=issues,
            )
        )
    return rows


def _ensure_unique_run_ids(summaries: list[EpisodeSummary]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for summary in summaries:
        if summary.run_id in seen:
            duplicates.add(summary.run_id)
        seen.add(summary.run_id)
    if duplicates:
        raise ValueError(f"duplicate run_ids detected in final closure inputs: {', '.join(sorted(duplicates))}")


def _required_mapping(payload: dict[str, Any], field_name: str, label: str) -> dict[str, Any]:
    value = payload.get(field_name)
    if not isinstance(value, dict):
        raise ValueError(f"{label} is missing required mapping '{field_name}'")
    return value


def _find_master_question(payload: dict[str, Any], fragment: str) -> dict[str, Any] | None:
    for field_name in ("answers", "questions"):
        rows = payload.get(field_name, [])
        if isinstance(rows, dict):
            iterable = rows.values()
        elif isinstance(rows, list):
            iterable = rows
        else:
            continue
        for row in iterable:
            if isinstance(row, dict) and fragment in str(row.get("question", "")):
                return row
    return None


def _question_answer(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    answer = payload.get("answer")
    return answer is True


def _question_explanation(payload: Any) -> str:
    if not isinstance(payload, dict):
        return "missing"
    explanation = payload.get("explanation")
    if isinstance(explanation, str) and explanation.strip():
        return explanation.strip()
    return str(payload.get("answer"))


def _analysis_findings(payload: dict[str, Any]) -> list[str]:
    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        return []
    return [str(item) for item in findings]


def _prompt_runtime_row(payload: dict[str, Any], prompt_variant: str, runtime_variant: str) -> dict[str, Any] | None:
    rows = payload.get("by_prompt_runtime", [])
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("prompt_variant") == prompt_variant and row.get("runtime_variant") == runtime_variant:
            return row
    return None


def _write_final_csv(path: Path, questions: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_FINAL_CSV_COLUMNS)
        writer.writeheader()
        for question in questions:
            writer.writerow(
                {
                    "question_id": question["question_id"],
                    "question": question["question"],
                    "answer": str(question["answer"]).lower(),
                    "answer_label": question["answer_label"],
                    "evidence_sources": ";".join(question["evidence_sources"]),
                    "explanation": question["explanation"],
                }
            )


def _render_final_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Block A Final Closure Summary",
        "",
        f"- Output dir: `{summary['output_dir']}`",
        f"- Merged runs: `{summary['overall']['merged_runs']}`",
        f"- Successful runs: `{summary['overall']['successful_runs']}`",
        f"- Success rate: `{summary['overall']['success_rate']}`",
        "",
        "## Closure Answers",
        "",
    ]

    for index, question in enumerate(summary["questions"], start=1):
        lines.append(f"{index}. {question['question']}")
        lines.append(f"Answer: `{question['answer_label']}`")
        lines.append(question["explanation"])
        lines.append("")

    lines.extend(["## Supporting Findings", ""])
    for finding in summary.get("supporting_findings", []):
        lines.append(f"- {finding}")

    lines.extend(["", "## Verdict", ""])
    verdict = summary["closure_verdict"]
    lines.append(
        "Block A can stand as a self-contained system-design paper core: "
        f"`{verdict['answer_label']}` with next step `{verdict['recommended_next_step']}`."
    )
    return "\n".join(lines) + "\n"


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"
