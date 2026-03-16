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
    hover_offset_m: float | None = None
    grasp_tolerance_m: float | None = None
    place_tolerance_m: float | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
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
        if self.hover_offset_m is not None:
            payload["hover_offset_m"] = self.hover_offset_m
        if self.grasp_tolerance_m is not None:
            payload["grasp_tolerance_m"] = self.grasp_tolerance_m
        if self.place_tolerance_m is not None:
            payload["place_tolerance_m"] = self.place_tolerance_m
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
            "task_id": self.task.task_id,
            "scene_id": self.task.scene_id,
            "backend": self.task.backend,
            "robot_id": self.task.robot_id,
            "seed": self.task.seed,
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
    if task_family not in {"navigation", "manipulation"}:
        raise ValueError("pilot runner currently supports only task_family='navigation' or 'manipulation'")

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

    return {
        "experiment_name": config.experiment_name,
        "description": config.description,
        "config_path": str(config_path.resolve()),
        "summary_title": config.summary_title,
        "task_family": config.task_family,
        "execution_mode": config.execution_mode,
        "backend": config.backend,
        "planner_backend": config.planner_backend,
        "results_root": str(results_root.resolve()),
        "output_dir": str(output_dir.resolve()),
        "matrix": {
            "task_count": len(config.tasks),
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
            "total_retries": sum(summary.retries or 0 for summary in bundle.summaries),
        },
        "planned_run_ids": planned_run_ids,
        "missing_run_ids": sorted(planned_run_id_set - summarized_run_id_set),
        "unexpected_run_ids": sorted(summarized_run_id_set - planned_run_id_set),
        "by_prompt_runtime": _aggregate_summary_rows(
            bundle=bundle,
            group_fields=("prompt_variant", "runtime_variant"),
        ),
        "by_backend_prompt_runtime": _aggregate_summary_rows(
            bundle=bundle,
            group_fields=("backend_variant", "prompt_variant", "runtime_variant"),
        ),
        "by_task_variant": _aggregate_summary_rows(
            bundle=bundle,
            group_fields=("backend_variant", "task_id", "scene_id", "prompt_variant", "runtime_variant"),
        ),
        "incomplete_runs": incomplete_runs,
        "unsuccessful_runs": unsuccessful_runs,
    }


def _build_run_task_config(config: PilotExperimentConfig, run: PlannedRun):
    prompt_text = _render_prompt_text(run)
    if config.task_family == "manipulation":
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
    extra_options[f"{config.task_family}_backend"] = run.task.backend
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
        "task_family": config.task_family,
        "backend": run.task.backend,
    }

    agent_metadata = dict(metadata.get("agent_runtime_v0", {}))
    agent_metadata["prompt_variant"] = run.prompt_variant.variant_id
    agent_metadata["prompt_response_mode"] = run.prompt_variant.response_mode
    agent_metadata["prompt_self_check_required"] = run.prompt_variant.self_check_required
    agent_metadata["runtime_variant"] = run.runtime_variant.variant_id
    agent_metadata["runtime_policy"] = run.runtime_variant.runtime_policy
    agent_metadata["runtime_validate_actions"] = run.runtime_variant.validate_actions
    agent_metadata["runtime_max_retries_per_step"] = run.runtime_variant.max_retries_per_step
    agent_metadata[f"{config.task_family}_backend"] = run.task.backend
    agent_metadata["prompt_text"] = prompt_text
    metadata["agent_runtime_v0"] = agent_metadata
    task_config.metadata = metadata

    tags = list(task_config.tags)
    for tag in (
        "pilot",
        f"pilot_{config.task_family}",
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
        "hover_offset_m": run.task.hover_offset_m if run.task.hover_offset_m is not None else 0.0,
        "grasp_tolerance_m": (
            run.task.grasp_tolerance_m if run.task.grasp_tolerance_m is not None else 0.0
        ),
        "place_tolerance_m": (
            run.task.place_tolerance_m if run.task.place_tolerance_m is not None else 0.0
        ),
        "control_dt_sec": run.task.control_dt_sec if run.task.control_dt_sec is not None else 0.0,
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
    episode_times = [summary.episode_time_s for summary in summaries if summary.episode_time_s is not None]
    planner_latencies = [
        summary.planner_latency_s for summary in summaries if summary.planner_latency_s is not None
    ]
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
        "average_step_count": round(sum(step_counts) / len(step_counts), 6) if step_counts else None,
        "average_planner_calls": round(sum(planner_calls) / len(planner_calls), 6) if planner_calls else None,
        "average_tool_calls": round(sum(tool_calls) / len(tool_calls), 6) if tool_calls else None,
        "average_episode_time_s": round(sum(episode_times) / len(episode_times), 6) if episode_times else None,
        "average_planner_latency_s": round(sum(planner_latencies) / len(planner_latencies), 6)
        if planner_latencies
        else None,
        "total_invalid_actions": sum(summary.invalid_actions or 0 for summary in summaries),
        "total_retries": sum(summary.retries or 0 for summary in summaries),
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

    lines.extend(
        [
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
                    "total_invalid_actions",
                    "total_retries",
                    "average_episode_time_s",
                    "average_planner_latency_s",
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
                    "total_invalid_actions",
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
                    "backend_variant",
                    "task_id",
                    "scene_id",
                    "prompt_variant",
                    "runtime_variant",
                    "run_count",
                    "successful_runs",
                    "success_rate",
                    "average_step_count",
                    "total_invalid_actions",
                    "total_retries",
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
    shared = {
        "task_id": task_id,
        "scene_id": _required_string(payload, "scene_id"),
        "backend": _parse_backend(
            _optional_string(payload.get("backend")) or _optional_string(defaults.get("backend")) or suite_backend,
            field_name=f"tasks[{task_id}].backend",
            allow_mixed=False,
        ),
        "robot_id": _optional_string(payload.get("robot_id"))
        or _optional_string(defaults.get("robot_id"))
        or ("gripper_marker" if task_family == "manipulation" else "agent_point_robot"),
        "seed": _positive_or_zero_int(payload.get("seed", defaults.get("seed", 0)), "seed"),
        "max_steps": _positive_int(payload.get("max_steps", defaults.get("max_steps", 10)), "max_steps"),
        "max_time_sec": _positive_float(
            payload.get("max_time_sec", defaults.get("max_time_sec", 10.0)),
            "max_time_sec",
        ),
        "notes": _optional_string(payload.get("notes")) or "",
    }

    if task_family == "manipulation":
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
