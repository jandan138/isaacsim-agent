#!/usr/bin/env python3
"""Run the minimal Isaac-backed or toy navigation baseline."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from isaacsim_agent.tasks.navigation import build_minimal_navigation_task_config
from isaacsim_agent.tasks.navigation import run_and_write_navigation_baseline
from isaacsim_agent.tools.navigation import Pose2D


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the minimal navigation baseline.")
    parser.add_argument("--run-id", default=None, help="Run identifier. Defaults to a UTC timestamp-based id.")
    parser.add_argument("--results-root", default="results", help="Root directory for contract-compliant outputs.")
    parser.add_argument(
        "--backend",
        choices=["isaac", "toy"],
        default="isaac",
        help="Execution backend. Use 'isaac' via scripts/isaac_python.sh for the M2.5 baseline, or 'toy' for fast testing.",
    )
    parser.add_argument(
        "--task-id",
        default=None,
        help="Task identifier. Defaults to a backend-specific minimal navigation task id.",
    )
    parser.add_argument(
        "--scene-id",
        default=None,
        help="Scene identifier. Defaults to a backend-specific minimal scene id.",
    )
    parser.add_argument(
        "--robot-id",
        default=None,
        help="Robot identifier. Defaults to a backend-specific minimal agent id.",
    )
    parser.add_argument("--seed", type=int, default=0, help="Deterministic seed recorded in task artifacts.")
    parser.add_argument("--max-steps", type=int, default=10, help="Maximum control steps before termination.")
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
        help="Deterministic straight-line motion applied on each control step.",
    )
    parser.add_argument(
        "--control-dt-sec",
        type=float,
        default=0.5,
        help="Simulated time increment recorded for each control step.",
    )
    return parser


def default_run_id() -> str:
    return "nav-baseline-" + datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    args = build_parser().parse_args()
    run_id = args.run_id or default_run_id()
    task_id = args.task_id or (
        "minimal_isaac_navigation" if args.backend == "isaac" else "minimal_deterministic_navigation"
    )
    robot_id = args.robot_id or ("isaac_stage_agent" if args.backend == "isaac" else "point_robot")

    config = build_minimal_navigation_task_config(
        task_id=task_id,
        scene_id=args.scene_id,
        robot_id=robot_id,
        seed=args.seed,
        max_steps=args.max_steps,
        max_time_sec=args.max_time_sec,
        start_pose=Pose2D(x=args.start_x, y=args.start_y, yaw=args.start_yaw),
        goal_pose=Pose2D(x=args.goal_x, y=args.goal_y, yaw=args.goal_yaw),
        success_radius_m=args.success_radius_m,
        step_size_m=args.step_size_m,
        control_dt_sec=args.control_dt_sec,
        backend=args.backend,
    )
    run_data, layout = run_and_write_navigation_baseline(
        config=config,
        run_id=run_id,
        results_root=args.results_root,
    )

    print("Run directory:", layout.run_dir)
    print("Task:", run_data.config.task_id)
    print("Backend:", run_data.config.metadata["navigation_baseline"]["backend"])
    print("Scene:", run_data.config.scene_id)
    print("Termination:", run_data.result.termination_reason.value)
    print("Steps:", run_data.result.step_count)
    print("Final goal distance (m):", run_data.result.metrics["navigation.final_goal_distance_m"])
    if "stage.usda" in run_data.text_artifacts:
        print("Stage artifact:", layout.artifacts_dir / "stage.usda")

    if run_data.result.success:
        print("NAV_BASELINE_OK")
        return 0

    print("NAV_BASELINE_FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
