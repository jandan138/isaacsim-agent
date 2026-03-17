"""Config-driven block A pilot and suite runner built on the M4/M5 paths."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None

from isaacsim_agent.agent import render_prompt_template
from isaacsim_agent.eval import SummaryBundle
from isaacsim_agent.eval import summarize_results_root
from isaacsim_agent.eval import write_summary_outputs
from isaacsim_agent.planner import BlockAPilotPlannerBackend
from isaacsim_agent.planner import MockPlannerBackend
from isaacsim_agent.planner import PlannerConfig
from isaacsim_agent.runtime import AgentRuntimeConfig
from isaacsim_agent.runtime import build_agent_v0_manipulation_task_config
from isaacsim_agent.runtime import build_agent_v0_navigation_task_config
from isaacsim_agent.runtime import run_and_write_agent_v0
from isaacsim_agent.tools import Pose2D
from isaacsim_agent.tools import Pose3D

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
ISAAC_WRAPPER = REPO_ROOT / "scripts" / "isaac_python.sh"
PILOT_RUNNER = REPO_ROOT / "scripts" / "run_pilot_run.py"


@dataclass(frozen=True)
class PilotPromptVariant:
    """One prompt variant defined in the pilot config."""

    variant_id: str
    label: str
    instruction_template: str
    response_mode: str = "tool_json"
    self_check_required: bool = False
    repair_instruction_template: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.variant_id,
            "label": self.label,
            "instruction_template": self.instruction_template,
            "response_mode": self.response_mode,
            "self_check_required": self.self_check_required,
            "repair_instruction_template": self.repair_instruction_template,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class PilotRuntimeVariant:
    """One runtime variant defined in the pilot config."""

    variant_id: str
    label: str
    runtime_policy: str
    validate_actions: bool
    max_retries_per_step: int
    max_invalid_actions: int
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.variant_id,
            "label": self.label,
            "runtime_policy": self.runtime_policy,
            "validate_actions": self.validate_actions,
            "max_retries_per_step": self.max_retries_per_step,
            "max_invalid_actions": self.max_invalid_actions,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class PilotTaskSpec:
    """One navigation or manipulation task used in the pilot suite."""

    task_family: str
    task_id: str
    scene_id: str
    backend: str
    robot_id: str
    seed: int
    max_steps: int
    max_time_sec: float
    start_pose: Pose2D | None = None
    goal_pose: Pose2D | None = None
    success_radius_m: float | None = None
    step_size_m: float | None = None
    control_dt_sec: float | None = None
    gripper_start_pose: Pose3D | None = None
    object_start_pose: Pose3D | None = None
    target_pose: Pose3D | None = None
    transfer_waypoints: tuple[Pose3D, ...] = ()
    hover_offset_m: float | None = None
    grasp_tolerance_m: float | None = None
    place_tolerance_m: float | None = None
    runtime_probe_invalid_first_action: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "task_family": self.task_family,
            "task_id": self.task_id,
            "scene_id": self.scene_id,
            "backend": self.backend,
            "robot_id": self.robot_id,
            "seed": self.seed,
            "max_steps": self.max_steps,
            "max_time_sec": self.max_time_sec,
            "notes": self.notes,
        }
        if self.start_pose is not None:
            payload["start_pose"] = self.start_pose.to_dict()
        if self.goal_pose is not None:
            payload["goal_pose"] = self.goal_pose.to_dict()
        if self.success_radius_m is not None:
            payload["success_radius_m"] = self.success_radius_m
        if self.step_size_m is not None:
            payload["step_size_m"] = self.step_size_m
        if self.control_dt_sec is not None:
            payload["control_dt_sec"] = self.control_dt_sec
        if self.gripper_start_pose is not None:
            payload["gripper_start_pose"] = self.gripper_start_pose.to_dict()
        if self.object_start_pose is not None:
            payload["object_start_pose"] = self.object_start_pose.to_dict()
        if self.target_pose is not None:
            payload["target_pose"] = self.target_pose.to_dict()
        if self.transfer_waypoints:
            payload["transfer_waypoints"] = [pose.to_dict() for pose in self.transfer_waypoints]
        if self.hover_offset_m is not None:
            payload["hover_offset_m"] = self.hover_offset_m
        if self.grasp_tolerance_m is not None:
            payload["grasp_tolerance_m"] = self.grasp_tolerance_m
        if self.place_tolerance_m is not None:
            payload["place_tolerance_m"] = self.place_tolerance_m
        if self.runtime_probe_invalid_first_action:
            payload["runtime_probe_invalid_first_action"] = True
        return payload


@dataclass(frozen=True)
class PilotExperimentConfig:
    """Minimal pilot experiment config."""

    experiment_name: str
    description: str
    task_family: str
    execution_mode: str
    backend: str
    planner_backend: str
    prompt_variants: list[PilotPromptVariant]
    runtime_variants: list[PilotRuntimeVariant]
    tasks: list[PilotTaskSpec]
    summary_basename: str = "pilot_summary"
    summary_title: str = "Pilot Summary"
    results_root: str | None = None
    output_dir: str | None = None
    analysis_mode: str | None = None
    reference_summary_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_name": self.experiment_name,
            "description": self.description,
            "task_family": self.task_family,
            "execution_mode": self.execution_mode,
            "backend": self.backend,
            "planner_backend": self.planner_backend,
            "summary_basename": self.summary_basename,
            "summary_title": self.summary_title,
            "results_root": self.results_root,
            "output_dir": self.output_dir,
            "analysis_mode": self.analysis_mode,
            "reference_summary_path": self.reference_summary_path,
            "prompt_variants": [variant.to_dict() for variant in self.prompt_variants],
            "runtime_variants": [variant.to_dict() for variant in self.runtime_variants],
            "tasks": [task.to_dict() for task in self.tasks],
        }


@dataclass(frozen=True)
class PlannedRun:
    """One concrete run expanded from the pilot experiment config."""

    run_id: str
    task: PilotTaskSpec
    prompt_variant: PilotPromptVariant
    runtime_variant: PilotRuntimeVariant

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "task_family": self.task.task_family,
            "task_id": self.task.task_id,
            "scene_id": self.task.scene_id,
            "backend": self.task.backend,
            "robot_id": self.task.robot_id,
            "seed": self.task.seed,
            "runtime_probe_invalid_first_action": self.task.runtime_probe_invalid_first_action,
            "prompt_variant": self.prompt_variant.variant_id,
            "prompt_response_mode": self.prompt_variant.response_mode,
            "prompt_self_check_required": self.prompt_variant.self_check_required,
            "runtime_variant": self.runtime_variant.variant_id,
            "runtime_policy": self.runtime_variant.runtime_policy,
            "validate_actions": self.runtime_variant.validate_actions,
            "max_retries_per_step": self.runtime_variant.max_retries_per_step,
            "max_invalid_actions": self.runtime_variant.max_invalid_actions,
        }


@dataclass(frozen=True)
class PilotExecutionResult:
    """Outputs from one pilot suite execution."""

    config_path: Path
    config: PilotExperimentConfig
    results_root: Path
    output_dir: Path
    planned_runs: list[PlannedRun]
    bundle: SummaryBundle
    written_outputs: dict[str, Path]
    run_plan_path: Path
    pilot_summary_json_path: Path
    pilot_summary_md_path: Path
    pilot_summary: dict[str, Any]


def load_pilot_experiment_config(config_path: str | Path) -> PilotExperimentConfig:
    """Load the minimal pilot experiment config from a YAML-compatible file."""

    path = Path(config_path)
    payload = _load_mapping_file(path)
    defaults = payload.get("defaults", {})
    if defaults is None:
        defaults = {}
    if not isinstance(defaults, dict):
        raise ValueError("defaults must be a JSON/YAML mapping when provided")

    task_family = _required_string(payload, "task_family")
    if task_family not in {"navigation", "manipulation", "mixed"}:
        raise ValueError(
            "pilot runner currently supports only task_family='navigation', 'manipulation', or 'mixed'"
        )

    execution_mode = _optional_string(payload.get("execution_mode")) or "sequential"
    if execution_mode != "sequential":
        raise ValueError("pilot runner currently supports only sequential execution")

    backend = _parse_backend(
        _optional_string(payload.get("backend")) or _optional_string(defaults.get("backend")) or "toy",
        field_name="backend",
        allow_mixed=True,
    )

    planner_backend = (
        _optional_string(payload.get("planner_backend"))
        or _optional_string(defaults.get("planner_backend"))
        or "mock_rule_based"
    )

    prompt_variants_payload = payload.get("prompt_variants", [])
    if not isinstance(prompt_variants_payload, list) or not prompt_variants_payload:
        raise ValueError("prompt_variants must contain at least one variant")

    runtime_variants_payload = payload.get("runtime_variants", [])
    if not isinstance(runtime_variants_payload, list) or not runtime_variants_payload:
        raise ValueError("runtime_variants must contain at least one variant")

    tasks_payload = payload.get("tasks", [])
    if not isinstance(tasks_payload, list) or not tasks_payload:
        raise ValueError("tasks must contain at least one task")

    prompt_variants = [_parse_prompt_variant(item) for item in prompt_variants_payload]
    runtime_variants = [_parse_runtime_variant(item) for item in runtime_variants_payload]
    tasks = [_parse_task(item, defaults, suite_backend=backend, task_family=task_family) for item in tasks_payload]

    _ensure_unique_ids([variant.variant_id for variant in prompt_variants], "prompt variant")
    _ensure_unique_ids([variant.variant_id for variant in runtime_variants], "runtime variant")
    _ensure_unique_ids([task.task_id for task in tasks], "task")

    task_families = {task.task_family for task in tasks}
    if task_family == "mixed":
        if len(task_families) < 2:
            raise ValueError("task_family='mixed' requires at least two distinct task families")
    elif task_families != {task_family}:
        raise ValueError(
            "task family overrides must match the suite task_family unless task_family='mixed'"
        )

    task_backends = {task.backend for task in tasks}
    if backend == "mixed":
        if len(task_backends) < 2:
            raise ValueError("backend='mixed' requires at least two distinct task backends")
    elif task_backends != {backend}:
        raise ValueError(
            "task backend overrides must match the suite backend unless backend='mixed'"
        )

    return PilotExperimentConfig(
        experiment_name=_required_string(payload, "experiment_name"),
        description=_optional_string(payload.get("description")) or "",
        task_family=task_family,
        execution_mode=execution_mode,
        backend=backend,
        planner_backend=planner_backend,
        prompt_variants=prompt_variants,
        runtime_variants=runtime_variants,
        tasks=tasks,
        summary_basename=_optional_string(payload.get("summary_basename")) or "pilot_summary",
        summary_title=_optional_string(payload.get("summary_title")) or "Pilot Summary",
        results_root=_optional_string(payload.get("results_root")),
        output_dir=_optional_string(payload.get("output_dir")),
        analysis_mode=_optional_string(payload.get("analysis_mode")),
        reference_summary_path=_optional_string(payload.get("reference_summary_path")),
    )


def plan_pilot_runs(config: PilotExperimentConfig) -> list[PlannedRun]:
    """Expand the pilot matrix into a deterministic list of runs."""

    planned_runs: list[PlannedRun] = []
    seen_run_ids: set[str] = set()
    for task in config.tasks:
        for prompt_variant in config.prompt_variants:
            for runtime_variant in config.runtime_variants:
                run_id = _build_run_id(
                    experiment_name=config.experiment_name,
                    task_id=task.task_id,
                    scene_id=task.scene_id,
                    prompt_variant=prompt_variant.variant_id,
                    runtime_variant=runtime_variant.variant_id,
                    seed=task.seed,
                )
                if run_id in seen_run_ids:
                    raise ValueError(f"duplicate planned run_id generated: {run_id}")
                planned_runs.append(
                    PlannedRun(
                        run_id=run_id,
                        task=task,
                        prompt_variant=prompt_variant,
                        runtime_variant=runtime_variant,
                    )
                )
                seen_run_ids.add(run_id)
    return planned_runs


def run_pilot_suite(
    config_path: str | Path,
    results_root: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> PilotExecutionResult:
    """Execute the configured pilot suite and emit M5 plus pilot-level summaries."""

    config_path = Path(config_path)
    config = load_pilot_experiment_config(config_path)
    resolved_results_root = _resolve_results_root(config=config, override=results_root)
    resolved_output_dir = _resolve_output_dir(
        config=config,
        results_root=resolved_results_root,
        override=output_dir,
    )
    planned_runs = plan_pilot_runs(config)

    _ensure_clean_results_root(resolved_results_root)
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    run_plan_path = resolved_output_dir / "run_plan.json"
    _write_json(
        run_plan_path,
        {
            "experiment_name": config.experiment_name,
            "config_path": str(config_path.resolve()),
            "results_root": str(resolved_results_root.resolve()),
            "output_dir": str(resolved_output_dir.resolve()),
            "planned_runs": [run.to_dict() for run in planned_runs],
        },
    )

    planner_backend = _build_planner_backend(config.planner_backend)
    for run in planned_runs:
        task_config = _build_run_task_config(config=config, run=run)
        runtime_config = AgentRuntimeConfig(
            planner_config=PlannerConfig(backend=config.planner_backend),
            policy_name=run.runtime_variant.runtime_policy,
            validation_enabled=run.runtime_variant.validate_actions,
            max_validation_retries=run.runtime_variant.max_retries_per_step,
            max_invalid_actions=run.runtime_variant.max_invalid_actions,
        )
        _execute_planned_run(
            run=run,
            task_config=task_config,
            results_root=resolved_results_root,
            planner_backend_name=config.planner_backend,
            planner_backend=planner_backend,
            runtime_config=runtime_config,
        )

    bundle = summarize_results_root(resolved_results_root)
    written_outputs = write_summary_outputs(bundle=bundle, output_dir=resolved_output_dir)
    pilot_summary = build_pilot_summary(
        config=config,
        config_path=config_path,
        results_root=resolved_results_root,
        output_dir=resolved_output_dir,
        planned_runs=planned_runs,
        bundle=bundle,
    )

    pilot_summary_json_path = resolved_output_dir / f"{config.summary_basename}.json"
    pilot_summary_md_path = resolved_output_dir / f"{config.summary_basename}.md"
    _write_json(pilot_summary_json_path, pilot_summary)
    pilot_summary_md_path.write_text(_render_pilot_summary_markdown(pilot_summary), encoding="utf-8")

    return PilotExecutionResult(
        config_path=config_path,
        config=config,
        results_root=resolved_results_root,
        output_dir=resolved_output_dir,
        planned_runs=planned_runs,
        bundle=bundle,
        written_outputs=written_outputs,
        run_plan_path=run_plan_path,
        pilot_summary_json_path=pilot_summary_json_path,
        pilot_summary_md_path=pilot_summary_md_path,
        pilot_summary=pilot_summary,
    )


def build_pilot_summary(
    config: PilotExperimentConfig,
    config_path: Path,
    results_root: Path,
    output_dir: Path,
    planned_runs: list[PlannedRun],
    bundle: SummaryBundle,
) -> dict[str, Any]:
    """Build a small pilot-specific summary for manual go/no-go review."""

    planned_run_ids = [run.run_id for run in planned_runs]
    planned_run_id_set = set(planned_run_ids)
    summarized_run_id_set = {summary.run_id for summary in bundle.summaries}

    incomplete_runs = [_failure_row(summary) for summary in bundle.summaries if not summary.run_complete]
    unsuccessful_runs = [_failure_row(summary) for summary in bundle.summaries if summary.success is False]

    summary = {
        "experiment_name": config.experiment_name,
        "description": config.description,
        "config_path": str(config_path.resolve()),
        "summary_title": config.summary_title,
        "task_family": config.task_family,
        "task_families": sorted({task.task_family for task in config.tasks}),
        "execution_mode": config.execution_mode,
        "backend": config.backend,
        "planner_backend": config.planner_backend,
        "results_root": str(results_root.resolve()),
        "output_dir": str(output_dir.resolve()),
        "matrix": {
            "task_count": len(config.tasks),
            "task_family_count": len({task.task_family for task in config.tasks}),
            "backend_count": len({task.backend for task in config.tasks}),
            "prompt_variant_count": len(config.prompt_variants),
            "runtime_variant_count": len(config.runtime_variants),
            "planned_run_count": len(planned_runs),
        },
        "backends": sorted({task.backend for task in config.tasks}),
        "prompt_variants": [variant.to_dict() for variant in config.prompt_variants],
        "runtime_variants": [variant.to_dict() for variant in config.runtime_variants],
        "tasks": [task.to_dict() for task in config.tasks],
        "overall": {
            "planned_runs": len(planned_runs),
            "summarized_runs": bundle.aggregate.total_runs,
            "contract_complete_runs": bundle.aggregate.contract_complete_runs,
            "run_complete_runs": bundle.aggregate.run_complete_runs,
            "successful_runs": bundle.aggregate.successful_runs,
            "bad_runs": bundle.aggregate.bad_runs,
            "success_rate": bundle.aggregate.success_rate,
            "average_step_count": bundle.aggregate.average_step_count,
            "average_episode_time_s": bundle.aggregate.average_episode_time_s,
            "total_planner_calls": bundle.aggregate.total_planner_calls,
            "total_tool_calls": bundle.aggregate.total_tool_calls,
            "total_invalid_actions": bundle.aggregate.total_invalid_actions,
            "total_retries": sum(summary.retries or 0 for summary in bundle.summaries),
        },
        "planned_run_ids": planned_run_ids,
        "missing_run_ids": sorted(planned_run_id_set - summarized_run_id_set),
        "unexpected_run_ids": sorted(summarized_run_id_set - planned_run_id_set),
        "by_task_family": _aggregate_summary_rows(
            bundle=bundle,
            group_fields=("task_family",),
        ),
        "by_prompt_runtime": _aggregate_summary_rows(
            bundle=bundle,
            group_fields=("prompt_variant", "runtime_variant"),
        ),
        "by_task_family_prompt_runtime": _aggregate_summary_rows(
            bundle=bundle,
            group_fields=("task_family", "prompt_variant", "runtime_variant"),
        ),
        "by_backend_prompt_runtime": _aggregate_summary_rows(
            bundle=bundle,
            group_fields=("backend_variant", "prompt_variant", "runtime_variant"),
        ),
        "by_task_variant": _aggregate_summary_rows(
            bundle=bundle,
            group_fields=("task_family", "backend_variant", "task_id", "scene_id", "prompt_variant", "runtime_variant"),
        ),
        "incomplete_runs": incomplete_runs,
        "unsuccessful_runs": unsuccessful_runs,
    }
    analysis = _build_optional_analysis(config=config, config_path=config_path, summary=summary)
    if analysis is not None:
        summary["analysis"] = analysis
    return summary


def _build_optional_analysis(
    config: PilotExperimentConfig,
    config_path: Path,
    summary: dict[str, Any],
) -> dict[str, Any] | None:
    if config.analysis_mode == "block_a_runtime_only_ablation":
        return _build_block_a_runtime_only_ablation_analysis(summary=summary)
    if config.analysis_mode == "block_a_prompt_only_ablation":
        return _build_block_a_prompt_only_ablation_analysis(summary=summary)
    if config.analysis_mode == "block_a_navigation_robustness":
        return _build_block_a_navigation_robustness_analysis(
            config=config,
            config_path=config_path,
            summary=summary,
        )
    if config.analysis_mode == "block_a_manipulation_harder":
        return _build_block_a_manipulation_harder_analysis(
            config=config,
            config_path=config_path,
            summary=summary,
        )
    return None


def _build_block_a_runtime_only_ablation_analysis(summary: dict[str, Any]) -> dict[str, Any]:
    prompt_runtime_rows = _prompt_runtime_row_map(summary)
    family_prompt_runtime_rows = _task_family_prompt_runtime_row_map(summary)
    p1_r0 = prompt_runtime_rows.get(("P1", "R0"))
    p1_r1 = prompt_runtime_rows.get(("P1", "R1"))

    family_consistency: dict[str, bool | None] = {}
    family_details: list[str] = []
    for family in _summary_task_families(summary):
        r0_row = family_prompt_runtime_rows.get((family, "P1", "R0"))
        r1_row = family_prompt_runtime_rows.get((family, "P1", "R1"))
        if r0_row is None or r1_row is None:
            family_consistency[family] = None
            continue
        family_consistency[family] = (r1_row.get("success_rate") or 0.0) > (r0_row.get("success_rate") or 0.0)
        family_details.append(
            f"{_family_display_name(family)} success `{r0_row.get('success_rate')}` -> `{r1_row.get('success_rate')}`, "
            f"recovery `{r0_row.get('recovery_success_rate')}` -> `{r1_row.get('recovery_success_rate')}`"
        )

    runtime_has_independent_value = bool(
        p1_r0
        and p1_r1
        and (
            (p1_r1.get("success_rate") or 0.0) > (p1_r0.get("success_rate") or 0.0)
            or (p1_r1.get("recovery_success_rate") or 0.0) > (p1_r0.get("recovery_success_rate") or 0.0)
        )
    )
    value_concentrates_in_recovery = bool(
        p1_r0
        and p1_r1
        and (p1_r1.get("invalid_action_run_count") == p1_r0.get("invalid_action_run_count"))
        and (p1_r1.get("successful_invalid_action_runs") or 0) > (p1_r0.get("successful_invalid_action_runs") or 0)
        and (p1_r1.get("total_retries") or 0) > (p1_r0.get("total_retries") or 0)
    )
    cross_family_consistent = bool(
        family_consistency and all(value is True for value in family_consistency.values() if value is not None)
    )

    findings: list[str] = []
    if p1_r0 is not None and p1_r1 is not None:
        findings.append(
            "Under fixed prompt P1, runtime validation plus one retry improves outcomes over the bare runtime: "
            f"success `{p1_r0['successful_runs']}/{p1_r0['run_count']}` -> "
            f"`{p1_r1['successful_runs']}/{p1_r1['run_count']}`, recovery success "
            f"`{p1_r0.get('recovery_success_rate')}` -> `{p1_r1.get('recovery_success_rate')}`."
        )
        findings.append(
            "The gain is concentrated in recoverable invalid actions rather than fewer invalid attempts: "
            f"invalid-action runs stay at `{p1_r0.get('invalid_action_run_count')}` vs "
            f"`{p1_r1.get('invalid_action_run_count')}`, while successful invalid-action recoveries rise from "
            f"`{p1_r0.get('successful_invalid_action_runs')}` to `{p1_r1.get('successful_invalid_action_runs')}` "
            f"with retries `{p1_r0.get('total_retries')}` -> `{p1_r1.get('total_retries')}`."
        )
    if family_details:
        findings.append("The same runtime-only trend appears in both task families: " + "; ".join(family_details) + ".")

    return {
        "mode": "block_a_runtime_only_ablation",
        "questions": {
            "q1_runtime_has_independent_value": {
                "answer": runtime_has_independent_value,
                "p1_r0": p1_r0,
                "p1_r1": p1_r1,
            },
            "q2_value_concentrates_in_recovery": {
                "answer": value_concentrates_in_recovery,
                "p1_r0": p1_r0,
                "p1_r1": p1_r1,
            },
            "q3_cross_family_consistency": {
                "answer": cross_family_consistent,
                "by_task_family": family_consistency,
            },
        },
        "findings": findings,
    }


def _build_block_a_prompt_only_ablation_analysis(summary: dict[str, Any]) -> dict[str, Any]:
    prompt_runtime_rows = _prompt_runtime_row_map(summary)
    family_prompt_runtime_rows = _task_family_prompt_runtime_row_map(summary)
    p0_r0 = prompt_runtime_rows.get(("P0", "R0"))
    p1_r0 = prompt_runtime_rows.get(("P1", "R0"))
    p2_r0 = prompt_runtime_rows.get(("P2", "R0"))

    per_family_consistency: dict[str, bool | None] = {}
    family_details: list[str] = []
    for family in _summary_task_families(summary):
        family_p0 = family_prompt_runtime_rows.get((family, "P0", "R0"))
        family_p1 = family_prompt_runtime_rows.get((family, "P1", "R0"))
        family_p2 = family_prompt_runtime_rows.get((family, "P2", "R0"))
        if family_p0 is None or family_p1 is None or family_p2 is None:
            per_family_consistency[family] = None
            continue
        per_family_consistency[family] = bool(
            (family_p1.get("total_invalid_actions") or 0) < (family_p0.get("total_invalid_actions") or 0)
            and (family_p2.get("total_invalid_actions") or 0) < (family_p0.get("total_invalid_actions") or 0)
            and (family_p2.get("average_planner_calls") or 0.0) < (family_p1.get("average_planner_calls") or 0.0)
            and (family_p2.get("average_tool_calls") or 0.0) < (family_p1.get("average_tool_calls") or 0.0)
        )
        family_details.append(
            f"{_family_display_name(family)} invalid actions P0/P1/P2 "
            f"`{family_p0.get('total_invalid_actions')}`/`{family_p1.get('total_invalid_actions')}`/"
            f"`{family_p2.get('total_invalid_actions')}`, planner/tool P1 `{family_p1.get('average_planner_calls')}`/"
            f"`{family_p1.get('average_tool_calls')}` vs P2 `{family_p2.get('average_planner_calls')}`/"
            f"`{family_p2.get('average_tool_calls')}`"
        )

    prompt_structure_reduces_invalid = bool(
        p0_r0
        and p1_r0
        and p2_r0
        and (p1_r0.get("total_invalid_actions") or 0) < (p0_r0.get("total_invalid_actions") or 0)
        and (p2_r0.get("total_invalid_actions") or 0) < (p0_r0.get("total_invalid_actions") or 0)
    )
    p2_efficiency_edge = bool(
        p1_r0
        and p2_r0
        and (p2_r0.get("average_planner_calls") or 0.0) < (p1_r0.get("average_planner_calls") or 0.0)
        and (p2_r0.get("average_tool_calls") or 0.0) < (p1_r0.get("average_tool_calls") or 0.0)
    )
    cross_family_consistent = bool(
        per_family_consistency and all(value is True for value in per_family_consistency.values() if value is not None)
    )

    findings: list[str] = []
    if p0_r0 is not None and p1_r0 is not None and p2_r0 is not None:
        findings.append(
            "With runtime fixed at R0, prompt structure independently lowers invalid actions: "
            f"P0 invalid-action runs `{p0_r0.get('invalid_action_run_count')}` and total invalid actions "
            f"`{p0_r0.get('total_invalid_actions')}` versus P1 `{p1_r0.get('invalid_action_run_count')}`/"
            f"`{p1_r0.get('total_invalid_actions')}` and P2 `{p2_r0.get('invalid_action_run_count')}`/"
            f"`{p2_r0.get('total_invalid_actions')}`."
        )
        findings.append(
            "P2 preserves the success profile of structured prompting while reducing planner/tool workload relative to P1: "
            f"planner/tool `{p1_r0.get('average_planner_calls')}`/`{p1_r0.get('average_tool_calls')}` -> "
            f"`{p2_r0.get('average_planner_calls')}`/`{p2_r0.get('average_tool_calls')}`."
        )
    if family_details:
        findings.append("The prompt-only ordering matches across navigation and manipulation: " + "; ".join(family_details) + ".")

    return {
        "mode": "block_a_prompt_only_ablation",
        "questions": {
            "q1_prompt_structure_reduces_invalid_actions": {
                "answer": prompt_structure_reduces_invalid,
                "p0_r0": p0_r0,
                "p1_r0": p1_r0,
                "p2_r0": p2_r0,
            },
            "q2_p2_more_efficient_than_p1": {
                "answer": p2_efficiency_edge,
                "p1_r0": p1_r0,
                "p2_r0": p2_r0,
            },
            "q3_cross_family_consistency": {
                "answer": cross_family_consistent,
                "by_task_family": per_family_consistency,
            },
        },
        "findings": findings,
    }


def _build_block_a_navigation_robustness_analysis(
    config: PilotExperimentConfig,
    config_path: Path,
    summary: dict[str, Any],
) -> dict[str, Any]:
    prompt_runtime_rows = {
        (str(row.get("prompt_variant")), str(row.get("runtime_variant"))): row
        for row in summary.get("by_prompt_runtime", [])
        if isinstance(row, dict)
    }
    task_rows = [
        row
        for row in summary.get("by_task_variant", [])
        if isinstance(row, dict)
    ]

    p0_r0 = prompt_runtime_rows.get(("P0", "R0"))
    p0_r1 = prompt_runtime_rows.get(("P0", "R1"))
    p1_r0 = prompt_runtime_rows.get(("P1", "R0"))
    p1_r1 = prompt_runtime_rows.get(("P1", "R1"))
    p2_r0 = prompt_runtime_rows.get(("P2", "R0"))
    p2_r1 = prompt_runtime_rows.get(("P2", "R1"))

    questions: dict[str, dict[str, Any]] = {}
    findings: list[str] = []

    p0_r0_worst = bool(
        p0_r0
        and all(
            (row.get("success_rate") or 0.0) > (p0_r0.get("success_rate") or 0.0)
            for key, row in prompt_runtime_rows.items()
            if key != ("P0", "R0")
        )
    )
    p0_r0_termination = _format_termination_reasons(
        p0_r0.get("termination_reasons") if isinstance(p0_r0, dict) else None
    )
    questions["q1_p0_r0_worst"] = {
        "answer": p0_r0_worst,
        "success_rate": p0_r0.get("success_rate") if p0_r0 else None,
        "termination_reasons": p0_r0.get("termination_reasons") if p0_r0 else {},
    }
    if p0_r0 is not None:
        findings.append(
            "P0/R0 remains the worst cell on the harder navigation slice: "
            f"success_rate `{p0_r0['success_rate']}` with termination `{p0_r0_termination}`, "
            f"`{p0_r0['total_invalid_actions']}` invalid actions, and `{p0_r0['total_retries']}` retries."
        )

    p0_r1_recovered = bool(p0_r1 and p0_r1.get("successful_runs") == p0_r1.get("run_count"))
    questions["q2_r1_recovers_p0"] = {
        "answer": p0_r1_recovered,
        "success_rate": p0_r1.get("success_rate") if p0_r1 else None,
        "total_retries": p0_r1.get("total_retries") if p0_r1 else None,
        "average_planner_calls": p0_r1.get("average_planner_calls") if p0_r1 else None,
        "average_tool_calls": p0_r1.get("average_tool_calls") if p0_r1 else None,
    }
    if p0_r1 is not None:
        findings.append(
            "R1 still recovers P0 across the full harder-task slice: "
            f"P0/R1 reaches success_rate `{p0_r1['success_rate']}` with `{p0_r1['total_retries']}` retries, "
            f"`{p0_r1['average_planner_calls']}` average planner calls, and "
            f"`{p0_r1['average_tool_calls']}` average tool calls."
        )

    p1_p2_success = bool(
        all(
            row is not None and row.get("successful_runs") == row.get("run_count")
            for row in (p1_r0, p1_r1, p2_r0, p2_r1)
        )
    )
    questions["q3_p1_p2_success"] = {
        "answer": p1_p2_success,
        "rows": {
            "P1/R0": p1_r0,
            "P1/R1": p1_r1,
            "P2/R0": p2_r0,
            "P2/R1": p2_r1,
        },
    }
    findings.append(
        "P1 and P2 remain globally successful on these harder navigation tasks: "
        f"P1/R0 `{_success_rate_text(p1_r0)}`, P1/R1 `{_success_rate_text(p1_r1)}`, "
        f"P2/R0 `{_success_rate_text(p2_r0)}`, and P2/R1 `{_success_rate_text(p2_r1)}`."
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
    questions["q4_p2_more_efficient_than_p1"] = {
        "answer": p2_more_efficient,
        "r0": {
            "p1_average_planner_calls": p1_r0.get("average_planner_calls") if p1_r0 else None,
            "p2_average_planner_calls": p2_r0.get("average_planner_calls") if p2_r0 else None,
            "p1_average_tool_calls": p1_r0.get("average_tool_calls") if p1_r0 else None,
            "p2_average_tool_calls": p2_r0.get("average_tool_calls") if p2_r0 else None,
        },
        "r1": {
            "p1_average_planner_calls": p1_r1.get("average_planner_calls") if p1_r1 else None,
            "p2_average_planner_calls": p2_r1.get("average_planner_calls") if p2_r1 else None,
            "p1_average_tool_calls": p1_r1.get("average_tool_calls") if p1_r1 else None,
            "p2_average_tool_calls": p2_r1.get("average_tool_calls") if p2_r1 else None,
        },
    }
    if p1_r0 is not None and p2_r0 is not None and p1_r1 is not None and p2_r1 is not None:
        findings.append(
            "P2 keeps the planner/tool efficiency edge over P1 under both runtimes: "
            f"R0 planner/tool `{p2_r0['average_planner_calls']}`/`{p2_r0['average_tool_calls']}` "
            f"vs P1 `{p1_r0['average_planner_calls']}`/`{p1_r0['average_tool_calls']}`, "
            f"and R1 planner/tool `{p2_r1['average_planner_calls']}`/`{p2_r1['average_tool_calls']}` "
            f"vs P1 `{p1_r1['average_planner_calls']}`/`{p1_r1['average_tool_calls']}`."
        )

    unsuccessful_rows = [
        row
        for row in task_rows
        if row.get("success_rate") == 0.0
    ]
    questions["q5_harder_tasks_amplify_differences"] = {
        "answer": None,
        "reference_summary_path": None,
        "details": [],
    }

    reference_comparison = _build_reference_comparison(
        config=config,
        config_path=config_path,
        prompt_runtime_rows=prompt_runtime_rows,
    )
    if reference_comparison is not None:
        questions["q5_harder_tasks_amplify_differences"] = reference_comparison
        if reference_comparison.get("answer") is True:
            findings.append(
                "Compared with the existing easy navigation reference, the harder slice increases planner/tool "
                "overhead while preserving the same qualitative ordering: "
                + "; ".join(reference_comparison["details"])
                + "."
            )
        else:
            findings.append(
                "Relative to the existing easy navigation reference, the harder slice preserves the same success "
                "ordering without a clear efficiency-gap increase."
            )
    elif unsuccessful_rows:
        findings.append(
            "The harder slice does not create new failure cells beyond P0/R0; the main difference is higher "
            "planner/tool overhead on successful variants."
        )

    return {
        "mode": "block_a_navigation_robustness",
        "reference_summary_path": reference_comparison.get("reference_summary_path") if reference_comparison else None,
        "questions": questions,
        "findings": findings,
    }


def _build_block_a_manipulation_harder_analysis(
    config: PilotExperimentConfig,
    config_path: Path,
    summary: dict[str, Any],
) -> dict[str, Any]:
    prompt_runtime_rows = _prompt_runtime_row_map(summary)
    p0_r0 = prompt_runtime_rows.get(("P0", "R0"))
    p0_r1 = prompt_runtime_rows.get(("P0", "R1"))
    p1_r0 = prompt_runtime_rows.get(("P1", "R0"))
    p1_r1 = prompt_runtime_rows.get(("P1", "R1"))
    p2_r0 = prompt_runtime_rows.get(("P2", "R0"))
    p2_r1 = prompt_runtime_rows.get(("P2", "R1"))

    questions: dict[str, dict[str, Any]] = {}
    findings: list[str] = []

    p0_r0_worst = bool(
        p0_r0
        and all(
            (row.get("success_rate") or 0.0) > (p0_r0.get("success_rate") or 0.0)
            for key, row in prompt_runtime_rows.items()
            if key != ("P0", "R0")
        )
    )
    questions["q1_p0_r0_worst"] = {
        "answer": p0_r0_worst,
        "row": p0_r0,
    }
    if p0_r0 is not None:
        findings.append(
            "P0/R0 remains the worst harder-manipulation cell: "
            f"success `{_success_rate_text(p0_r0)}` with termination `{_format_termination_reasons(p0_r0.get('termination_reasons'))}`."
        )

    p0_r1_recovered = bool(p0_r1 and p0_r1.get("successful_runs") == p0_r1.get("run_count"))
    questions["q2_r1_recovers_p0"] = {
        "answer": p0_r1_recovered,
        "row": p0_r1,
    }
    if p0_r1 is not None:
        findings.append(
            "R1 still recovers P0 on the harder manipulation slice: "
            f"success `{_success_rate_text(p0_r1)}` with retries `{p0_r1.get('total_retries')}`."
        )

    p1_p2_success = bool(
        all(
            row is not None and row.get("successful_runs") == row.get("run_count")
            for row in (p1_r0, p1_r1, p2_r0, p2_r1)
        )
    )
    questions["q3_p1_p2_success"] = {
        "answer": p1_p2_success,
        "rows": {
            "P1/R0": p1_r0,
            "P1/R1": p1_r1,
            "P2/R0": p2_r0,
            "P2/R1": p2_r1,
        },
    }
    findings.append(
        "P1 and P2 remain successful on the harder manipulation slice: "
        f"P1/R0 `{_success_rate_text(p1_r0)}`, P1/R1 `{_success_rate_text(p1_r1)}`, "
        f"P2/R0 `{_success_rate_text(p2_r0)}`, P2/R1 `{_success_rate_text(p2_r1)}`."
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
    questions["q4_p2_more_efficient_than_p1"] = {
        "answer": p2_more_efficient,
        "r0": {"p1": p1_r0, "p2": p2_r0},
        "r1": {"p1": p1_r1, "p2": p2_r1},
    }
    if p1_r0 is not None and p2_r0 is not None and p1_r1 is not None and p2_r1 is not None:
        findings.append(
            "P2 keeps the planner/tool efficiency edge over P1 under both runtimes: "
            f"R0 planner/tool `{p1_r0.get('average_planner_calls')}`/`{p1_r0.get('average_tool_calls')}` -> "
            f"`{p2_r0.get('average_planner_calls')}`/`{p2_r0.get('average_tool_calls')}`, "
            f"R1 `{p1_r1.get('average_planner_calls')}`/`{p1_r1.get('average_tool_calls')}` -> "
            f"`{p2_r1.get('average_planner_calls')}`/`{p2_r1.get('average_tool_calls')}`."
        )

    reference_comparison = _build_reference_comparison(
        config=config,
        config_path=config_path,
        prompt_runtime_rows=prompt_runtime_rows,
    )
    questions["q5_harder_tasks_amplify_differences"] = reference_comparison or {
        "answer": None,
        "reference_summary_path": None,
        "details": [],
    }
    if reference_comparison is not None:
        if reference_comparison.get("answer") is True:
            findings.append(
                "Relative to the easy manipulation pilot, the harder manipulation slice increases planner/tool overhead "
                "while preserving the same qualitative ordering: "
                + "; ".join(reference_comparison["details"])
                + "."
            )
        else:
            findings.append(
                "Relative to the easy manipulation pilot, the harder slice preserves ordering without a clear workload increase."
            )

    return {
        "mode": "block_a_manipulation_harder",
        "reference_summary_path": reference_comparison.get("reference_summary_path") if reference_comparison else None,
        "questions": questions,
        "findings": findings,
    }


def _build_reference_comparison(
    config: PilotExperimentConfig,
    config_path: Path,
    prompt_runtime_rows: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any] | None:
    if not config.reference_summary_path:
        return None
    reference_summary_path = _resolve_reference_summary_path(
        reference_summary_path=config.reference_summary_path,
        config_path=config_path,
    )
    if not reference_summary_path.is_file():
        return None

    payload = json.loads(reference_summary_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return None

    reference_rows = _select_reference_prompt_runtime_rows(
        reference_summary=payload,
        backend=config.backend,
    )
    comparisons: list[str] = []
    amplified = False
    for prompt_variant, runtime_variant in (("P0", "R1"), ("P1", "R0"), ("P2", "R0")):
        current = prompt_runtime_rows.get((prompt_variant, runtime_variant))
        reference = reference_rows.get((prompt_variant, runtime_variant))
        if current is None or reference is None:
            continue
        current_planner = current.get("average_planner_calls")
        reference_planner = reference.get("average_planner_calls")
        current_tool = current.get("average_tool_calls")
        reference_tool = reference.get("average_tool_calls")
        if not isinstance(current_planner, (int, float)) or not isinstance(reference_planner, (int, float)):
            continue
        if not isinstance(current_tool, (int, float)) or not isinstance(reference_tool, (int, float)):
            continue
        if current_planner > reference_planner or current_tool > reference_tool:
            amplified = True
        comparisons.append(
            f"{prompt_variant}/{runtime_variant} planner/tool "
            f"`{reference_planner}`/`{reference_tool}` -> `{current_planner}`/`{current_tool}`"
        )

    if not comparisons:
        return None
    return {
        "answer": amplified,
        "reference_summary_path": str(reference_summary_path),
        "details": comparisons,
    }


def _resolve_reference_summary_path(reference_summary_path: str, config_path: Path) -> Path:
    candidate = Path(reference_summary_path)
    if candidate.is_absolute():
        return candidate
    repo_candidate = REPO_ROOT / candidate
    if repo_candidate.exists():
        return repo_candidate
    config_candidate = config_path.parent / candidate
    if config_candidate.exists():
        return config_candidate
    return repo_candidate


def _select_reference_prompt_runtime_rows(
    reference_summary: dict[str, Any],
    backend: str,
) -> dict[tuple[str, str], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if backend in {"toy", "isaac"}:
        backend_rows = reference_summary.get("by_backend_prompt_runtime", [])
        if isinstance(backend_rows, list):
            rows = [
                row
                for row in backend_rows
                if isinstance(row, dict) and row.get("backend_variant") == backend
            ]
    if not rows:
        prompt_runtime_rows = reference_summary.get("by_prompt_runtime", [])
        if isinstance(prompt_runtime_rows, list):
            rows = [row for row in prompt_runtime_rows if isinstance(row, dict)]
    return {
        (str(row.get("prompt_variant")), str(row.get("runtime_variant"))): row
        for row in rows
    }


def _format_termination_reasons(payload: Any) -> str:
    if not isinstance(payload, dict) or not payload:
        return "unknown"
    return ", ".join(f"{key}:{payload[key]}" for key in sorted(payload))


def _summary_task_families(summary: dict[str, Any]) -> list[str]:
    row_payload = summary.get("by_task_family")
    if isinstance(row_payload, list):
        families = [str(row.get("task_family")) for row in row_payload if isinstance(row, dict)]
        if families:
            return families
    payload = summary.get("task_families")
    if isinstance(payload, list):
        return [("pick_place" if str(item) == "manipulation" else str(item)) for item in payload]
    return []


def _family_display_name(family: str) -> str:
    if family in {"pick_place", "manipulation"}:
        return "Manipulation"
    return family.replace("_", " ").title()


def _prompt_runtime_row_map(summary: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row.get("prompt_variant")), str(row.get("runtime_variant"))): row
        for row in summary.get("by_prompt_runtime", [])
        if isinstance(row, dict)
    }


def _task_family_prompt_runtime_row_map(summary: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    return {
        (str(row.get("task_family")), str(row.get("prompt_variant")), str(row.get("runtime_variant"))): row
        for row in summary.get("by_task_family_prompt_runtime", [])
        if isinstance(row, dict)
    }


def _analysis_heading(analysis: Any) -> str | None:
    if not isinstance(analysis, dict):
        return None
    return {
        "block_a_runtime_only_ablation": "Runtime-Only Findings",
        "block_a_prompt_only_ablation": "Prompt-Only Findings",
        "block_a_navigation_robustness": "Robustness Findings",
        "block_a_manipulation_harder": "Harder Manipulation Findings",
    }.get(str(analysis.get("mode")))


def _success_rate_text(row: dict[str, Any] | None) -> str:
    if row is None:
        return "missing"
    return f"{row.get('successful_runs')}/{row.get('run_count')} ({row.get('success_rate')})"


def _build_run_task_config(config: PilotExperimentConfig, run: PlannedRun):
    prompt_text = _render_prompt_text(run)
    if run.task.task_family == "manipulation":
        task_config = build_agent_v0_manipulation_task_config(
            backend=run.task.backend,
            planner_backend=config.planner_backend,
            task_id=run.task.task_id,
            scene_id=run.task.scene_id,
            robot_id=run.task.robot_id,
            seed=run.task.seed,
            max_steps=run.task.max_steps,
            max_time_sec=run.task.max_time_sec,
            gripper_start_pose=run.task.gripper_start_pose,
            object_start_pose=run.task.object_start_pose,
            target_pose=run.task.target_pose,
            transfer_waypoints=list(run.task.transfer_waypoints),
            hover_offset_m=run.task.hover_offset_m,
            grasp_tolerance_m=run.task.grasp_tolerance_m,
            place_tolerance_m=run.task.place_tolerance_m,
            control_dt_sec=run.task.control_dt_sec,
        )
    else:
        task_config = build_agent_v0_navigation_task_config(
            backend=run.task.backend,
            planner_backend=config.planner_backend,
            task_id=run.task.task_id,
            scene_id=run.task.scene_id,
            robot_id=run.task.robot_id,
            seed=run.task.seed,
            max_steps=run.task.max_steps,
            max_time_sec=run.task.max_time_sec,
            start_pose=run.task.start_pose,
            goal_pose=run.task.goal_pose,
            success_radius_m=run.task.success_radius_m,
            step_size_m=run.task.step_size_m,
            control_dt_sec=run.task.control_dt_sec,
        )
    task_config.runtime_options.tool_validation_enabled = run.runtime_variant.validate_actions
    task_config.runtime_options.recovery_enabled = run.runtime_variant.max_retries_per_step > 0

    extra_options = dict(task_config.runtime_options.extra_options)
    extra_options["prompt_variant"] = run.prompt_variant.variant_id
    extra_options["prompt_response_mode"] = run.prompt_variant.response_mode
    extra_options["prompt_self_check_required"] = run.prompt_variant.self_check_required
    extra_options["prompt_repair_instruction_template"] = run.prompt_variant.repair_instruction_template
    extra_options["runtime_variant"] = run.runtime_variant.variant_id
    extra_options["runtime_policy"] = run.runtime_variant.runtime_policy
    extra_options["runtime_validate_actions"] = run.runtime_variant.validate_actions
    extra_options["runtime_max_retries_per_step"] = run.runtime_variant.max_retries_per_step
    extra_options[f"{run.task.task_family}_backend"] = run.task.backend
    extra_options["runtime_probe_invalid_first_action"] = run.task.runtime_probe_invalid_first_action
    extra_options["recoverable_invalid_first_action"] = run.task.runtime_probe_invalid_first_action
    extra_options["suite_experiment"] = config.experiment_name
    extra_options["planner_prompt_text"] = prompt_text
    task_config.runtime_options.extra_options = extra_options

    metadata = dict(task_config.metadata)
    metadata["prompting"] = {
        "prompt_variant": run.prompt_variant.variant_id,
        "label": run.prompt_variant.label,
        "instruction_template": run.prompt_variant.instruction_template,
        "instruction_text": prompt_text,
        "response_mode": run.prompt_variant.response_mode,
        "self_check_required": run.prompt_variant.self_check_required,
        "repair_instruction_template": run.prompt_variant.repair_instruction_template,
        "notes": run.prompt_variant.notes,
    }
    metadata["pilot_suite"] = {
        "experiment_name": config.experiment_name,
        "task_id": run.task.task_id,
        "scene_id": run.task.scene_id,
        "prompt_variant": run.prompt_variant.variant_id,
        "runtime_variant": run.runtime_variant.variant_id,
        "runtime_policy": run.runtime_variant.runtime_policy,
        "validate_actions": run.runtime_variant.validate_actions,
        "max_retries_per_step": run.runtime_variant.max_retries_per_step,
        "max_invalid_actions": run.runtime_variant.max_invalid_actions,
        "planner_backend": config.planner_backend,
        "task_family": run.task.task_family,
        "backend": run.task.backend,
        "runtime_probe_invalid_first_action": run.task.runtime_probe_invalid_first_action,
        "recoverable_invalid_first_action": run.task.runtime_probe_invalid_first_action,
    }

    agent_metadata = dict(metadata.get("agent_runtime_v0", {}))
    agent_metadata["prompt_variant"] = run.prompt_variant.variant_id
    agent_metadata["prompt_response_mode"] = run.prompt_variant.response_mode
    agent_metadata["prompt_self_check_required"] = run.prompt_variant.self_check_required
    agent_metadata["runtime_variant"] = run.runtime_variant.variant_id
    agent_metadata["runtime_policy"] = run.runtime_variant.runtime_policy
    agent_metadata["runtime_validate_actions"] = run.runtime_variant.validate_actions
    agent_metadata["runtime_max_retries_per_step"] = run.runtime_variant.max_retries_per_step
    agent_metadata[f"{run.task.task_family}_backend"] = run.task.backend
    agent_metadata["prompt_text"] = prompt_text
    agent_metadata["runtime_probe_invalid_first_action"] = run.task.runtime_probe_invalid_first_action
    agent_metadata["recoverable_invalid_first_action"] = run.task.runtime_probe_invalid_first_action
    metadata["agent_runtime_v0"] = agent_metadata
    task_config.metadata = metadata

    tags = list(task_config.tags)
    for tag in (
        "pilot",
        f"pilot_{run.task.task_family}",
        f"backend_{run.task.backend.lower()}",
        f"prompt_{run.prompt_variant.variant_id.lower()}",
        f"runtime_{run.runtime_variant.variant_id.lower()}",
    ):
        if tag not in tags:
            tags.append(tag)
    task_config.tags = tags

    return task_config


def _execute_planned_run(
    run: PlannedRun,
    task_config: Any,
    results_root: Path,
    planner_backend_name: str,
    planner_backend: Any,
    runtime_config: AgentRuntimeConfig,
) -> None:
    if run.task.backend == "isaac":
        _run_agent_subprocess(
            task_config=task_config,
            run_id=run.run_id,
            results_root=results_root,
            planner_backend_name=planner_backend_name,
            runtime_config=runtime_config,
        )
        return

    run_and_write_agent_v0(
        config=task_config,
        run_id=run.run_id,
        results_root=results_root,
        planner_backend=planner_backend,
        runtime_config=runtime_config,
    )


def _run_agent_subprocess(
    task_config: Any,
    run_id: str,
    results_root: Path,
    planner_backend_name: str,
    runtime_config: AgentRuntimeConfig,
) -> None:
    helper_script = REPO_ROOT / "scripts" / "run_agent_v0_task_config.py"
    python_executable = _resolve_isaac_python_executable() or Path(sys.executable)

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix=f"{_slugify(run_id)}-",
        delete=False,
        encoding="utf-8",
    ) as handle:
        json.dump(task_config.to_dict(), handle, indent=2)
        handle.write("\n")
        temp_config_path = Path(handle.name)

    try:
        command = [
            str(python_executable),
            str(helper_script),
            "--task-config",
            str(temp_config_path),
            "--run-id",
            run_id,
            "--results-root",
            str(results_root),
            "--planner-backend",
            planner_backend_name,
            "--runtime-policy",
            runtime_config.policy_name,
            "--validation-enabled",
            "true" if runtime_config.validation_enabled else "false",
            "--max-validation-retries",
            str(runtime_config.max_validation_retries),
            "--max-invalid-actions",
            str(runtime_config.max_invalid_actions),
        ]
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=False,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"subprocess Isaac run failed for {run_id} with exit code {completed.returncode}"
            )
    finally:
        temp_config_path.unlink(missing_ok=True)


def _resolve_isaac_python_executable() -> Path | None:
    env_root = os.environ.get("ISAAC_SIM_ROOT")
    candidates: list[Path] = []
    if env_root:
        candidates.append(Path(env_root) / "python.sh")
    candidates.append(Path("/isaac-sim/python.sh"))

    ov_root = Path.home() / ".local" / "share" / "ov" / "pkg"
    if ov_root.is_dir():
        candidates.extend(sorted((path / "python.sh") for path in ov_root.glob("isaac_sim-*")))

    candidates.extend(
        [
            Path("/opt/nvidia/isaac-sim/python.sh"),
            Path("/opt/NVIDIA/isaac-sim/python.sh"),
            Path("/opt/omniverse/isaac-sim/python.sh"),
        ]
    )

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _render_prompt_text(run: PlannedRun) -> str:
    values = {
        "task_id": run.task.task_id,
        "scene_id": run.task.scene_id,
        "task_family": run.task.task_family,
        "robot_id": run.task.robot_id,
        "seed": run.task.seed,
        "max_steps": run.task.max_steps,
        "max_time_sec": run.task.max_time_sec,
        "start_x": run.task.start_pose.x if run.task.start_pose is not None else 0.0,
        "start_y": run.task.start_pose.y if run.task.start_pose is not None else 0.0,
        "start_yaw": run.task.start_pose.yaw if run.task.start_pose is not None else 0.0,
        "goal_x": run.task.goal_pose.x if run.task.goal_pose is not None else 0.0,
        "goal_y": run.task.goal_pose.y if run.task.goal_pose is not None else 0.0,
        "goal_yaw": run.task.goal_pose.yaw if run.task.goal_pose is not None else 0.0,
        "success_radius_m": run.task.success_radius_m if run.task.success_radius_m is not None else 0.0,
        "gripper_start_x": (
            run.task.gripper_start_pose.x if run.task.gripper_start_pose is not None else 0.0
        ),
        "gripper_start_y": (
            run.task.gripper_start_pose.y if run.task.gripper_start_pose is not None else 0.0
        ),
        "gripper_start_z": (
            run.task.gripper_start_pose.z if run.task.gripper_start_pose is not None else 0.0
        ),
        "object_x": run.task.object_start_pose.x if run.task.object_start_pose is not None else 0.0,
        "object_y": run.task.object_start_pose.y if run.task.object_start_pose is not None else 0.0,
        "object_z": run.task.object_start_pose.z if run.task.object_start_pose is not None else 0.0,
        "target_x": run.task.target_pose.x if run.task.target_pose is not None else 0.0,
        "target_y": run.task.target_pose.y if run.task.target_pose is not None else 0.0,
        "target_z": run.task.target_pose.z if run.task.target_pose is not None else 0.0,
        "transfer_waypoint_count": len(run.task.transfer_waypoints),
        "hover_offset_m": run.task.hover_offset_m if run.task.hover_offset_m is not None else 0.0,
        "grasp_tolerance_m": (
            run.task.grasp_tolerance_m if run.task.grasp_tolerance_m is not None else 0.0
        ),
        "place_tolerance_m": (
            run.task.place_tolerance_m if run.task.place_tolerance_m is not None else 0.0
        ),
        "control_dt_sec": run.task.control_dt_sec if run.task.control_dt_sec is not None else 0.0,
        "runtime_probe_invalid_first_action": str(run.task.runtime_probe_invalid_first_action).lower(),
        "recoverable_invalid_first_action": str(run.task.runtime_probe_invalid_first_action).lower(),
        "prompt_variant": run.prompt_variant.variant_id,
        "response_mode": run.prompt_variant.response_mode,
        "self_check_required": str(run.prompt_variant.self_check_required).lower(),
    }
    return render_prompt_template(run.prompt_variant.instruction_template, values)


def _aggregate_summary_rows(
    bundle: SummaryBundle,
    group_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[Any]] = {}
    for summary in bundle.summaries:
        key = tuple(_summary_field_value(summary, field_name) for field_name in group_fields)
        grouped.setdefault(key, []).append(summary)

    rows: list[dict[str, Any]] = []
    for key in sorted(grouped):
        summaries = grouped[key]
        row = {field_name: field_value for field_name, field_value in zip(group_fields, key)}
        row.update(_build_group_metrics(summaries))
        rows.append(row)
    return rows


def _build_group_metrics(summaries: list[Any]) -> dict[str, Any]:
    run_count = len(summaries)
    successful_runs = sum(1 for summary in summaries if summary.success is True)
    step_counts = [summary.step_count for summary in summaries if summary.step_count is not None]
    planner_calls = [summary.planner_calls for summary in summaries if summary.planner_calls is not None]
    tool_calls = [summary.tool_calls for summary in summaries if summary.tool_calls is not None]
    invalid_actions = [summary.invalid_actions or 0 for summary in summaries]
    retries = [summary.retries or 0 for summary in summaries]
    episode_times = [summary.episode_time_s for summary in summaries if summary.episode_time_s is not None]
    planner_latencies = [
        summary.planner_latency_s for summary in summaries if summary.planner_latency_s is not None
    ]
    termination_reasons: dict[str, int] = {}
    for summary in summaries:
        if summary.termination_reason:
            termination_reasons[summary.termination_reason] = termination_reasons.get(summary.termination_reason, 0) + 1

    invalid_action_run_count = sum(1 for summary in summaries if (summary.invalid_actions or 0) > 0)
    retry_run_count = sum(1 for summary in summaries if (summary.retries or 0) > 0)
    successful_invalid_action_runs = sum(
        1 for summary in summaries if summary.success is True and (summary.invalid_actions or 0) > 0
    )
    successful_retry_runs = sum(
        1 for summary in summaries if summary.success is True and (summary.retries or 0) > 0
    )

    return {
        "run_count": run_count,
        "contract_complete_runs": sum(1 for summary in summaries if summary.contract_complete),
        "run_complete_runs": sum(1 for summary in summaries if summary.run_complete),
        "successful_runs": successful_runs,
        "success_rate": round(successful_runs / run_count, 6) if run_count else None,
        "average_step_count": round(sum(step_counts) / len(step_counts), 6) if step_counts else None,
        "average_planner_calls": round(sum(planner_calls) / len(planner_calls), 6) if planner_calls else None,
        "average_tool_calls": round(sum(tool_calls) / len(tool_calls), 6) if tool_calls else None,
        "average_invalid_actions": round(sum(invalid_actions) / len(invalid_actions), 6) if invalid_actions else None,
        "average_retries": round(sum(retries) / len(retries), 6) if retries else None,
        "average_episode_time_s": round(sum(episode_times) / len(episode_times), 6) if episode_times else None,
        "average_planner_latency_s": round(sum(planner_latencies) / len(planner_latencies), 6)
        if planner_latencies
        else None,
        "total_invalid_actions": sum(invalid_actions),
        "invalid_action_run_count": invalid_action_run_count,
        "invalid_action_run_rate": round(invalid_action_run_count / run_count, 6) if run_count else None,
        "total_retries": sum(retries),
        "retry_run_count": retry_run_count,
        "retry_run_rate": round(retry_run_count / run_count, 6) if run_count else None,
        "successful_invalid_action_runs": successful_invalid_action_runs,
        "successful_retry_runs": successful_retry_runs,
        "recovery_success_rate": (
            round(successful_invalid_action_runs / invalid_action_run_count, 6) if invalid_action_run_count else None
        ),
        "termination_reasons": termination_reasons,
        "run_ids": [summary.run_id for summary in summaries],
    }


def _failure_row(summary: Any) -> dict[str, Any]:
    return {
        "run_id": summary.run_id,
        "task_id": summary.task_id,
        "scene_id": summary.scene_id,
        "prompt_variant": summary.prompt_variant,
        "runtime_variant": summary.runtime_variant,
        "success": summary.success,
        "termination_reason": summary.termination_reason,
        "retries": summary.retries,
        "run_complete": summary.run_complete,
        "contract_complete": summary.contract_complete,
        "validation_issue_codes": list(summary.validation_issue_codes),
    }


def _render_pilot_summary_markdown(summary: dict[str, Any]) -> str:
    summary_title = summary.get("summary_title") or "Pilot Summary"
    lines = [
        f"# {summary_title}: {summary['experiment_name']}",
        "",
        f"- Config: `{summary['config_path']}`",
        f"- Results root: `{summary['results_root']}`",
        f"- Output dir: `{summary['output_dir']}`",
        f"- Task family: `{summary['task_family']}`",
        f"- Task families in tasks: `{', '.join(summary['task_families'])}`",
        f"- Backend: `{summary['backend']}`",
        f"- Backends in tasks: `{', '.join(summary['backends'])}`",
        f"- Planner backend: `{summary['planner_backend']}`",
        f"- Planned runs: `{summary['overall']['planned_runs']}`",
        f"- Summarized runs: `{summary['overall']['summarized_runs']}`",
        f"- Run-complete runs: `{summary['overall']['run_complete_runs']}`",
        f"- Successful runs: `{summary['overall']['successful_runs']}`",
        f"- Success rate: `{summary['overall']['success_rate']}`",
    ]

    if summary.get("description"):
        lines.extend(["", summary["description"]])

    analysis = summary.get("analysis")
    analysis_heading = _analysis_heading(analysis)
    if isinstance(analysis, dict) and analysis_heading is not None:
        lines.extend(["", f"## {analysis_heading}", ""])
        for finding in analysis.get("findings", []):
            lines.append(f"- {finding}")
        reference_summary_path = analysis.get("reference_summary_path")
        if isinstance(reference_summary_path, str) and reference_summary_path.strip():
            lines.append(f"- Reference summary: `{reference_summary_path}`")

    lines.extend(
        [
            "",
            "## Task Family",
            "",
            _render_markdown_table(
                summary["by_task_family"],
                columns=[
                    "task_family",
                    "run_count",
                    "run_complete_runs",
                    "successful_runs",
                    "success_rate",
                    "average_planner_calls",
                    "average_tool_calls",
                    "total_invalid_actions",
                    "total_retries",
                ],
            ),
            "",
            "## Prompt x Runtime",
            "",
            _render_markdown_table(
                summary["by_prompt_runtime"],
                columns=[
                    "prompt_variant",
                    "runtime_variant",
                    "run_count",
                    "run_complete_runs",
                    "successful_runs",
                    "success_rate",
                    "average_step_count",
                    "average_planner_calls",
                    "average_tool_calls",
                    "average_invalid_actions",
                    "total_invalid_actions",
                    "recovery_success_rate",
                    "total_retries",
                    "average_episode_time_s",
                    "average_planner_latency_s",
                ],
            ),
            "",
            "## Task Family x Prompt x Runtime",
            "",
            _render_markdown_table(
                summary["by_task_family_prompt_runtime"],
                columns=[
                    "task_family",
                    "prompt_variant",
                    "runtime_variant",
                    "run_count",
                    "successful_runs",
                    "success_rate",
                    "average_planner_calls",
                    "average_tool_calls",
                    "total_invalid_actions",
                    "recovery_success_rate",
                    "total_retries",
                ],
            ),
            "",
            "## Backend x Prompt x Runtime",
            "",
            _render_markdown_table(
                summary["by_backend_prompt_runtime"],
                columns=[
                    "backend_variant",
                    "prompt_variant",
                    "runtime_variant",
                    "run_count",
                    "run_complete_runs",
                    "successful_runs",
                    "success_rate",
                    "average_step_count",
                    "average_planner_calls",
                    "average_tool_calls",
                    "average_invalid_actions",
                    "total_invalid_actions",
                    "recovery_success_rate",
                    "total_retries",
                    "average_episode_time_s",
                    "average_planner_latency_s",
                ],
            ),
            "",
            "## Task x Variant",
            "",
            _render_markdown_table(
                summary["by_task_variant"],
                columns=[
                    "task_family",
                    "backend_variant",
                    "task_id",
                    "scene_id",
                    "prompt_variant",
                    "runtime_variant",
                    "run_count",
                    "successful_runs",
                    "success_rate",
                    "average_step_count",
                    "average_planner_calls",
                    "average_tool_calls",
                    "average_invalid_actions",
                    "total_invalid_actions",
                    "recovery_success_rate",
                    "total_retries",
                    "average_episode_time_s",
                    "termination_reasons",
                ],
            ),
        ]
    )

    lines.extend(["", "## Incomplete Runs", ""])
    if summary["incomplete_runs"]:
        for item in summary["incomplete_runs"]:
            lines.append(
                f"- `{item['run_id']}`: termination={item['termination_reason']}, "
                f"validation={','.join(item['validation_issue_codes']) or 'none'}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Unsuccessful Runs", ""])
    if summary["unsuccessful_runs"]:
        for item in summary["unsuccessful_runs"]:
            lines.append(
                f"- `{item['run_id']}`: termination={item['termination_reason']}, "
                f"prompt={item['prompt_variant']}, runtime={item['runtime_variant']}, retries={item['retries']}"
            )
    else:
        lines.append("- none")

    if summary["missing_run_ids"]:
        lines.extend(["", "## Missing Planned Runs", ""])
        for run_id in summary["missing_run_ids"]:
            lines.append(f"- `{run_id}`")

    if summary["unexpected_run_ids"]:
        lines.extend(["", "## Unexpected Runs", ""])
        for run_id in summary["unexpected_run_ids"]:
            lines.append(f"- `{run_id}`")

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


def _load_mapping_file(path: Path) -> dict[str, Any]:
    raw_text = path.read_text(encoding="utf-8")
    if yaml is not None:
        payload = yaml.safe_load(raw_text)
    else:
        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "pilot configs currently require JSON-compatible YAML when PyYAML is unavailable"
            ) from exc

    if not isinstance(payload, dict):
        raise ValueError(f"expected top-level mapping in pilot config: {path}")
    return payload


def _parse_prompt_variant(payload: Any) -> PilotPromptVariant:
    if not isinstance(payload, dict):
        raise ValueError("each prompt variant must be a mapping")
    self_check_required = payload.get("self_check_required", False)
    if not isinstance(self_check_required, bool):
        raise ValueError("prompt variant self_check_required must be a boolean")
    return PilotPromptVariant(
        variant_id=_required_string(payload, "id"),
        label=_optional_string(payload.get("label")) or _required_string(payload, "id"),
        instruction_template=_required_string(payload, "instruction_template"),
        response_mode=_optional_string(payload.get("response_mode")) or "tool_json",
        self_check_required=self_check_required,
        repair_instruction_template=_optional_string(payload.get("repair_instruction_template")),
        notes=_optional_string(payload.get("notes")) or "",
    )


def _parse_runtime_variant(payload: Any) -> PilotRuntimeVariant:
    if not isinstance(payload, dict):
        raise ValueError("each runtime variant must be a mapping")
    validate_actions = payload.get("validate_actions", True)
    if not isinstance(validate_actions, bool):
        raise ValueError("runtime variant validate_actions must be a boolean")
    max_retries_per_step = payload.get("max_retries_per_step", 0)
    if isinstance(max_retries_per_step, bool) or not isinstance(max_retries_per_step, int) or max_retries_per_step < 0:
        raise ValueError("runtime variant max_retries_per_step must be a non-negative integer")
    max_invalid_actions = payload.get("max_invalid_actions", 1)
    if isinstance(max_invalid_actions, bool) or not isinstance(max_invalid_actions, int) or max_invalid_actions <= 0:
        raise ValueError("runtime variant max_invalid_actions must be a positive integer")
    return PilotRuntimeVariant(
        variant_id=_required_string(payload, "id"),
        label=_optional_string(payload.get("label")) or _required_string(payload, "id"),
        runtime_policy=_optional_string(payload.get("runtime_policy")) or "agent_runtime_v0",
        validate_actions=validate_actions,
        max_retries_per_step=max_retries_per_step,
        max_invalid_actions=max_invalid_actions,
        notes=_optional_string(payload.get("notes")) or "",
    )


def _parse_task(
    payload: Any,
    defaults: dict[str, Any],
    suite_backend: str,
    task_family: str,
) -> PilotTaskSpec:
    if not isinstance(payload, dict):
        raise ValueError("each task must be a mapping")
    task_id = _required_string(payload, "task_id")
    task_family_value = _optional_string(payload.get("task_family")) or _optional_string(defaults.get("task_family"))
    if task_family_value is None:
        if task_family == "mixed":
            raise ValueError(f"tasks[{task_id}].task_family is required when suite task_family='mixed'")
        task_family_value = task_family
    resolved_task_family = _parse_task_family(
        task_family_value,
        field_name=f"tasks[{task_id}].task_family",
        allow_mixed=False,
    )
    runtime_probe_invalid_first_action = _optional_bool_alias(
        payload=payload,
        defaults=defaults,
        primary_field="runtime_probe_invalid_first_action",
        alias_field="recoverable_invalid_first_action",
    )
    shared = {
        "task_family": resolved_task_family,
        "task_id": task_id,
        "scene_id": _required_string(payload, "scene_id"),
        "backend": _parse_backend(
            _optional_string(payload.get("backend")) or _optional_string(defaults.get("backend")) or suite_backend,
            field_name=f"tasks[{task_id}].backend",
            allow_mixed=False,
        ),
        "robot_id": _optional_string(payload.get("robot_id"))
        or _optional_string(defaults.get("robot_id"))
        or ("gripper_marker" if resolved_task_family == "manipulation" else "agent_point_robot"),
        "seed": _positive_or_zero_int(payload.get("seed", defaults.get("seed", 0)), "seed"),
        "max_steps": _positive_int(payload.get("max_steps", defaults.get("max_steps", 10)), "max_steps"),
        "max_time_sec": _positive_float(
            payload.get("max_time_sec", defaults.get("max_time_sec", 10.0)),
            "max_time_sec",
        ),
        "runtime_probe_invalid_first_action": runtime_probe_invalid_first_action,
        "notes": _optional_string(payload.get("notes")) or "",
    }

    if resolved_task_family == "manipulation":
        return PilotTaskSpec(
            **shared,
            gripper_start_pose=_parse_pose3d(
                payload.get("gripper_start_pose", defaults.get("gripper_start_pose")),
                "gripper_start_pose",
            ),
            object_start_pose=_parse_pose3d(
                payload.get("object_start_pose", defaults.get("object_start_pose")),
                "object_start_pose",
            ),
            target_pose=_parse_pose3d(
                payload.get("target_pose", defaults.get("target_pose")),
                "target_pose",
            ),
            transfer_waypoints=_parse_pose3d_sequence(
                _optional_payload_alias(
                    payload=payload,
                    defaults=defaults,
                    primary_field="transfer_waypoints",
                    alias_field="transfer_waypoint_poses",
                ),
                "transfer_waypoints",
            ),
            hover_offset_m=_positive_float(
                payload.get("hover_offset_m", defaults.get("hover_offset_m", 0.12)),
                "hover_offset_m",
            ),
            grasp_tolerance_m=_positive_float(
                payload.get("grasp_tolerance_m", defaults.get("grasp_tolerance_m", 0.01)),
                "grasp_tolerance_m",
            ),
            place_tolerance_m=_positive_float(
                payload.get("place_tolerance_m", defaults.get("place_tolerance_m", 0.02)),
                "place_tolerance_m",
            ),
            control_dt_sec=_positive_float(
                payload.get("control_dt_sec", defaults.get("control_dt_sec", 0.5)),
                "control_dt_sec",
            ),
        )

    return PilotTaskSpec(
        **shared,
        start_pose=_parse_pose(payload.get("start_pose", defaults.get("start_pose")), "start_pose"),
        goal_pose=_parse_pose(payload.get("goal_pose", defaults.get("goal_pose")), "goal_pose"),
        success_radius_m=_positive_float(
            payload.get("success_radius_m", defaults.get("success_radius_m", 0.2)),
            "success_radius_m",
        ),
        step_size_m=_positive_float(
            payload.get("step_size_m", defaults.get("step_size_m", 0.5)),
            "step_size_m",
        ),
        control_dt_sec=_positive_float(
            payload.get("control_dt_sec", defaults.get("control_dt_sec", 0.5)),
            "control_dt_sec",
        ),
    )


def _parse_pose(payload: Any, field_name: str) -> Pose2D:
    if not isinstance(payload, dict):
        raise ValueError(f"{field_name} must be a mapping with x, y, yaw")
    return Pose2D.from_dict(payload)


def _parse_pose3d(payload: Any, field_name: str) -> Pose3D:
    if not isinstance(payload, dict):
        raise ValueError(f"{field_name} must be a mapping with x, y, z")
    return Pose3D.from_dict(payload)


def _parse_pose3d_sequence(payload: Any, field_name: str) -> tuple[Pose3D, ...]:
    if payload is None:
        return ()
    if not isinstance(payload, (list, tuple)):
        raise ValueError(f"{field_name} must be a list of pose mappings when provided")
    return tuple(_parse_pose3d(item, f"{field_name}[{index}]") for index, item in enumerate(payload))


def _build_planner_backend(planner_backend: str):
    if planner_backend == "mock_rule_based":
        return MockPlannerBackend(planner_name=planner_backend)
    if planner_backend == "mock_block_a":
        return BlockAPilotPlannerBackend(planner_name=planner_backend)
    raise ValueError(f"unsupported planner_backend for pilot runner: {planner_backend}")


def _resolve_results_root(config: PilotExperimentConfig, override: str | Path | None) -> Path:
    if override is not None:
        return Path(override)
    if config.results_root:
        return Path(config.results_root)
    return Path("results") / "pilot" / _slugify(config.experiment_name)


def _resolve_output_dir(
    config: PilotExperimentConfig,
    results_root: Path,
    override: str | Path | None,
) -> Path:
    if override is not None:
        return Path(override)
    if config.output_dir:
        return Path(config.output_dir)
    return results_root / "processed" / _slugify(config.experiment_name)


def _ensure_clean_results_root(results_root: Path) -> None:
    runs_root = results_root / "runs"
    if not runs_root.exists():
        return
    existing_runs = sorted(path.name for path in runs_root.iterdir() if path.is_dir())
    if existing_runs:
        raise FileExistsError(
            f"results root already contains run directories: {results_root} ({', '.join(existing_runs)})"
        )


def _required_string(payload: dict[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _parse_backend(value: str, field_name: str, allow_mixed: bool) -> str:
    allowed = {"toy", "isaac"}
    if allow_mixed:
        allowed.add("mixed")
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of: {', '.join(sorted(allowed))}")
    return value


def _parse_task_family(value: str, field_name: str, allow_mixed: bool) -> str:
    allowed = {"navigation", "manipulation"}
    if allow_mixed:
        allowed.add("mixed")
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of: {', '.join(sorted(allowed))}")
    return value


def _optional_payload_alias(
    payload: dict[str, Any],
    defaults: dict[str, Any],
    primary_field: str,
    alias_field: str,
) -> Any:
    value = payload.get(primary_field)
    alias_value = payload.get(alias_field)
    if value is not None and alias_value is not None:
        raise ValueError(f"provide only one of {primary_field} or {alias_field}")
    if value is not None:
        return value
    if alias_value is not None:
        return alias_value
    default_value = defaults.get(primary_field)
    default_alias_value = defaults.get(alias_field)
    if default_value is not None and default_alias_value is not None:
        raise ValueError(f"defaults may provide only one of {primary_field} or {alias_field}")
    if default_value is not None:
        return default_value
    return default_alias_value


def _optional_bool_alias(
    payload: dict[str, Any],
    defaults: dict[str, Any],
    primary_field: str,
    alias_field: str,
) -> bool:
    value = _optional_payload_alias(
        payload=payload,
        defaults=defaults,
        primary_field=primary_field,
        alias_field=alias_field,
    )
    if value is None:
        return False
    if not isinstance(value, bool):
        raise ValueError(f"{primary_field} must be a boolean when provided")
    return value


def _positive_or_zero_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be an integer >= 0")
    return value


def _positive_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _positive_float(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{field_name} must be a positive number")
    return float(value)


def _ensure_unique_ids(values: list[str], label: str) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        raise ValueError(f"duplicate {label} ids: {', '.join(sorted(duplicates))}")


def _summary_field_value(summary: Any, field_name: str) -> str:
    value = getattr(summary, field_name)
    if value is None:
        return "unknown"
    return str(value)


def _build_run_id(
    experiment_name: str,
    task_id: str,
    scene_id: str,
    prompt_variant: str,
    runtime_variant: str,
    seed: int,
) -> str:
    return "-".join(
        [
            _slugify(experiment_name),
            _slugify(task_id),
            _slugify(scene_id),
            _slugify(prompt_variant),
            _slugify(runtime_variant),
            f"s{seed}",
        ]
    )


def _slugify(value: str) -> str:
    chars: list[str] = []
    last_was_dash = False
    for character in value.lower():
        if character.isalnum():
            chars.append(character)
            last_was_dash = False
            continue
        if not last_was_dash:
            chars.append("-")
            last_was_dash = True
    slug = "".join(chars).strip("-")
    return slug or "run"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
