#!/usr/bin/env python3
"""Minimal end-to-end contract validation and dummy artifact writer."""

from __future__ import annotations

import argparse
from pathlib import Path

from isaacsim_agent.contracts import DifficultyLevel
from isaacsim_agent.contracts import EpisodeResult
from isaacsim_agent.contracts import EventRecord
from isaacsim_agent.contracts import EventType
from isaacsim_agent.contracts import NavigationSpec
from isaacsim_agent.contracts import RunArtifactsLayout
from isaacsim_agent.contracts import RunManifest
from isaacsim_agent.contracts import RuntimeOptions
from isaacsim_agent.contracts import TaskConfig
from isaacsim_agent.contracts import TaskType
from isaacsim_agent.contracts import TerminationReason
from isaacsim_agent.contracts import TokenUsage
from isaacsim_agent.contracts import read_task_config
from isaacsim_agent.contracts import write_episode_result
from isaacsim_agent.contracts import write_event_log
from isaacsim_agent.contracts import write_run_manifest
from isaacsim_agent.contracts import write_task_config


def build_dummy_contracts(run_id: str) -> tuple[TaskConfig, EpisodeResult, list[EventRecord], RunManifest]:
    config = TaskConfig(
        task_type=TaskType.NAVIGATION,
        task_id="dummy_nav_contract",
        scene_id="dummy_scene",
        robot_id="dummy_robot",
        seed=7,
        max_steps=50,
        max_time_sec=30.0,
        headless=True,
        render=False,
        difficulty=DifficultyLevel.EASY,
        runtime_options=RuntimeOptions(
            planner_enabled=False,
            memory_enabled=False,
            tool_validation_enabled=True,
            recovery_enabled=True,
        ),
        description="Dummy contract validation run.",
        tags=["contracts", "dummy"],
        navigation=NavigationSpec(goal_ref="goal_marker_A", waypoint_refs=["wp1", "wp2"], success_radius_m=0.4),
    )

    result = EpisodeResult(
        run_id=run_id,
        task_type=config.task_type,
        task_id=config.task_id,
        scene_id=config.scene_id,
        robot_id=config.robot_id,
        seed=config.seed,
        success=True,
        termination_reason=TerminationReason.SUCCESS,
        step_count=3,
        elapsed_time_sec=1.25,
        sim_time_sec=0.75,
        invalid_action_count=0,
        collision_count=0,
        recovery_count=0,
        tool_call_count=1,
        planner_call_count=0,
        token_usage=TokenUsage(),
        planner_latency_sec=0.0,
        notes=["Dummy validation result for contract serialization."],
        metrics={
            "navigation.goal_reached": True,
            "navigation.final_goal_distance_m": 0.12,
            "navigation.waypoints_completed": 2,
        },
    )

    events = [
        EventRecord(
            run_id=run_id,
            event_index=0,
            event_type=EventType.EPISODE_START,
            step_index=0,
            task_type=config.task_type,
            task_id=config.task_id,
            scene_id=config.scene_id,
            robot_id=config.robot_id,
            seed=config.seed,
            payload={"headless": config.headless, "render": config.render},
        ),
        EventRecord(
            run_id=run_id,
            event_index=1,
            event_type=EventType.TOOL_CALL,
            step_index=1,
            task_type=config.task_type,
            task_id=config.task_id,
            scene_id=config.scene_id,
            robot_id=config.robot_id,
            seed=config.seed,
            tool_name="navigate_to",
            success=True,
            payload={"goal_ref": "goal_marker_A"},
            metrics={"navigation.final_goal_distance_m": 0.12},
        ),
        EventRecord(
            run_id=run_id,
            event_index=2,
            event_type=EventType.EPISODE_END,
            step_index=result.step_count,
            task_type=config.task_type,
            task_id=config.task_id,
            scene_id=config.scene_id,
            robot_id=config.robot_id,
            seed=config.seed,
            sim_time_sec=result.sim_time_sec,
            success=result.success,
            payload={"termination_reason": result.termination_reason.value},
        ),
    ]

    manifest = RunManifest(
        run_id=run_id,
        task_type=config.task_type,
        task_id=config.task_id,
        scene_id=config.scene_id,
        robot_id=config.robot_id,
        seed=config.seed,
    )
    return config, result, events, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate shared task/result/event contracts.")
    parser.add_argument("--run-id", default="dummy-contract-run", help="Run identifier for the dummy artifact set.")
    parser.add_argument(
        "--results-root",
        default="results",
        help="Root directory where the canonical results/runs/<run_id>/ layout will be created.",
    )
    args = parser.parse_args()

    config, result, events, manifest = build_dummy_contracts(args.run_id)
    layout = RunArtifactsLayout(run_id=args.run_id, results_root=args.results_root)
    layout.ensure()

    write_run_manifest(layout.manifest_path, manifest)
    write_task_config(layout.task_config_path, config)
    write_episode_result(layout.episode_result_path, result)
    write_event_log(layout.event_log_path, events)

    loaded = read_task_config(layout.task_config_path)
    artifact_note = layout.artifacts_dir / "README.txt"
    artifact_note.write_text(
        "Reserved for optional run-level artifacts such as screenshots, traces, or debug dumps.\n",
        encoding="utf-8",
    )

    print("Run directory:", layout.run_dir)
    print("Manifest:", layout.manifest_path)
    print("Task config:", layout.task_config_path)
    print("Episode result:", layout.episode_result_path)
    print("Event log:", layout.event_log_path)
    print("Round-trip task type:", loaded.task_type.value)
    print("CONTRACT_VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
