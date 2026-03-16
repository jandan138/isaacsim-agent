#!/usr/bin/env python3
"""Run the minimal M4 agent runtime v0 on the deterministic navigation task."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from isaacsim_agent.runtime import build_agent_v0_navigation_task_config
from isaacsim_agent.runtime import run_and_write_agent_v0
from isaacsim_agent.tools import Pose2D


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the minimal M4 agent runtime v0.")
    parser.add_argument("--run-id", default=None, help="Run identifier. Defaults to a UTC timestamp-based id.")
    parser.add_argument("--results-root", default="results", help="Root directory for contract-compliant outputs.")
    parser.add_argument(
        "--task-type",
        choices=["navigation"],
        default="navigation",
        help="M4 runtime v0 currently supports only the minimal navigation task.",
    )
    parser.add_argument(
        "--backend",
        choices=["isaac", "toy"],
        default="toy",
        help="Execution backend. Use 'toy' for lightweight validation or 'isaac' via scripts/isaac_python.sh.",
    )
    parser.add_argument(
        "--planner-backend",
        choices=["mock"],
        default="mock",
        help="Planner backend. M4 defaults to the deterministic mock structured-output planner.",
    )
    parser.add_argument("--task-id", default="minimal_agent_runtime_navigation", help="Task identifier.")
    parser.add_argument("--scene-id", default=None, help="Scene identifier override.")
    parser.add_argument("--robot-id", default="agent_point_robot", help="Robot identifier.")
    parser.add_argument("--seed", type=int, default=0, help="Deterministic seed recorded in task artifacts.")
    parser.add_argument("--max-steps", type=int, default=10, help="Maximum runtime steps before termination.")
    parser.add_argument("--max-time-sec", type=float, default=10.0, help="Maximum simulated time before timeout.")
    parser.add_argument("--start-x", type=float, default=0.0, help="Start x position in meters.")
    parser.add_argument("--start-y", type=float, default=0.0, help="Start y position in meters.")
    parser.add_argument("--start-yaw", type=float, default=0.0, help="Start yaw in radians.")
    parser.add_argument("--goal-x", type=float, default=2.0, help="Goal x position in meters.")
    parser.add_argument("--goal-y", type=float, default=0.0, help="Goal y position in meters.")
    parser.add_argument("--goal-yaw", type=float, default=0.0, help="Goal yaw in radians.")
    parser.add_argument(
        "--success-radius-m",
        type=float,
        default=0.2,
        help="Goal-distance threshold required for success.",
    )
    parser.add_argument(
        "--step-size-m",
        type=float,
        default=0.5,
        help="Deterministic straight-line motion applied on each navigate_to tool call.",
    )
    parser.add_argument(
        "--control-dt-sec",
        type=float,
        default=0.5,
        help="Simulated time increment recorded for each navigation action.",
    )
    return parser


def default_run_id() -> str:
    return "agent-runtime-v0-" + datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    args = build_parser().parse_args()
    run_id = args.run_id or default_run_id()

    if args.task_type != "navigation":
        raise ValueError("M4 agent runtime v0 currently supports only navigation")

    config = build_agent_v0_navigation_task_config(
        backend=args.backend,
        planner_backend="mock_rule_based",
        task_id=args.task_id,
        scene_id=args.scene_id,
        robot_id=args.robot_id,
        seed=args.seed,
        max_steps=args.max_steps,
        max_time_sec=args.max_time_sec,
        start_pose=Pose2D(x=args.start_x, y=args.start_y, yaw=args.start_yaw),
        goal_pose=Pose2D(x=args.goal_x, y=args.goal_y, yaw=args.goal_yaw),
        success_radius_m=args.success_radius_m,
        step_size_m=args.step_size_m,
        control_dt_sec=args.control_dt_sec,
    )
    run_data, layout = run_and_write_agent_v0(
        config=config,
        run_id=run_id,
        results_root=args.results_root,
    )

    print("Run directory:", layout.run_dir)
    print("Task:", run_data.config.task_id)
    print("Backend:", run_data.result.metrics["navigation.backend"])
    print("Planner backend:", run_data.result.metrics["navigation.planner_backend"])
    print("Termination:", run_data.result.termination_reason.value)
    print("Steps:", run_data.result.step_count)
    print("Planner calls:", run_data.result.planner_call_count)
    print("Tool calls:", run_data.result.tool_call_count)
    print("Invalid actions:", run_data.result.invalid_action_count)
    print("Final goal distance (m):", run_data.result.metrics["navigation.final_goal_distance_m"])
    print("Planner trace:", layout.artifacts_dir / "planner_trace.json")
    print("Tool trace:", layout.artifacts_dir / "tool_trace.json")
    if "stage.usda" in run_data.text_artifacts:
        print("Stage artifact:", layout.artifacts_dir / "stage.usda")

    if run_data.result.success:
        print("AGENT_RUNTIME_V0_OK")
        return 0

    print("AGENT_RUNTIME_V0_FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
