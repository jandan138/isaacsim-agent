#!/usr/bin/env python3
"""Run the minimal Isaac-backed or toy pick-and-place baseline."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from isaacsim_agent.tasks.manipulation import build_minimal_pickplace_task_config
from isaacsim_agent.tasks.manipulation import run_and_write_pickplace_baseline
from isaacsim_agent.tools.manipulation import Pose3D


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the minimal pick-and-place baseline.")
    parser.add_argument("--run-id", default=None, help="Run identifier. Defaults to a UTC timestamp-based id.")
    parser.add_argument("--results-root", default="results", help="Root directory for contract-compliant outputs.")
    parser.add_argument(
        "--backend",
        choices=["isaac", "toy"],
        default="isaac",
        help=(
            "Execution backend. Use 'isaac' via scripts/isaac_python.sh for the M3 baseline, "
            "or 'toy' for fast validation of the same scripted sequence."
        ),
    )
    parser.add_argument(
        "--task-id",
        default=None,
        help="Task identifier. Defaults to a backend-specific minimal pick-and-place task id.",
    )
    parser.add_argument(
        "--scene-id",
        default=None,
        help="Scene identifier. Defaults to a backend-specific minimal scene id.",
    )
    parser.add_argument(
        "--robot-id",
        default=None,
        help="Robot identifier. Defaults to a backend-specific minimal gripper marker id.",
    )
    parser.add_argument("--seed", type=int, default=0, help="Deterministic seed recorded in task artifacts.")
    parser.add_argument("--max-steps", type=int, default=12, help="Maximum scripted phases before termination.")
    parser.add_argument("--max-time-sec", type=float, default=12.0, help="Maximum simulated time before timeout.")
    parser.add_argument("--gripper-start-x", type=float, default=-0.2, help="Start x position of the gripper.")
    parser.add_argument("--gripper-start-y", type=float, default=-0.25, help="Start y position of the gripper.")
    parser.add_argument("--gripper-start-z", type=float, default=0.18, help="Start z position of the gripper.")
    parser.add_argument("--object-x", type=float, default=0.0, help="Initial object x position.")
    parser.add_argument("--object-y", type=float, default=0.0, help="Initial object y position.")
    parser.add_argument("--object-z", type=float, default=0.03, help="Initial object z position.")
    parser.add_argument("--target-x", type=float, default=0.35, help="Target object x position.")
    parser.add_argument("--target-y", type=float, default=0.0, help="Target object y position.")
    parser.add_argument("--target-z", type=float, default=0.03, help="Target object z position.")
    parser.add_argument(
        "--hover-offset-m",
        type=float,
        default=0.12,
        help="Vertical clearance added above source and target poses during transfer phases.",
    )
    parser.add_argument(
        "--grasp-tolerance-m",
        type=float,
        default=0.01,
        help="Maximum gripper-to-object distance allowed for the scripted grasp phase to succeed.",
    )
    parser.add_argument(
        "--place-tolerance-m",
        type=float,
        default=0.02,
        help="Maximum object-to-target distance allowed for a successful place.",
    )
    parser.add_argument(
        "--control-dt-sec",
        type=float,
        default=0.5,
        help="Simulated time increment recorded for each scripted phase.",
    )
    return parser


def default_run_id() -> str:
    return "pickplace-baseline-" + datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    args = build_parser().parse_args()
    run_id = args.run_id or default_run_id()
    task_id = args.task_id or (
        "minimal_isaac_pick_place" if args.backend == "isaac" else "minimal_reference_pick_place"
    )
    robot_id = args.robot_id or ("isaac_gripper_marker" if args.backend == "isaac" else "gripper_marker")

    config = build_minimal_pickplace_task_config(
        task_id=task_id,
        scene_id=args.scene_id,
        robot_id=robot_id,
        seed=args.seed,
        max_steps=args.max_steps,
        max_time_sec=args.max_time_sec,
        gripper_start_pose=Pose3D(
            x=args.gripper_start_x,
            y=args.gripper_start_y,
            z=args.gripper_start_z,
        ),
        object_start_pose=Pose3D(
            x=args.object_x,
            y=args.object_y,
            z=args.object_z,
        ),
        target_pose=Pose3D(
            x=args.target_x,
            y=args.target_y,
            z=args.target_z,
        ),
        hover_offset_m=args.hover_offset_m,
        grasp_tolerance_m=args.grasp_tolerance_m,
        place_tolerance_m=args.place_tolerance_m,
        control_dt_sec=args.control_dt_sec,
        backend=args.backend,
    )
    run_data, layout = run_and_write_pickplace_baseline(
        config=config,
        run_id=run_id,
        results_root=args.results_root,
    )

    print("Run directory:", layout.run_dir)
    print("Task:", run_data.config.task_id)
    print("Backend:", run_data.config.metadata["manipulation_baseline"]["backend"])
    print("Scene:", run_data.config.scene_id)
    print("Termination:", run_data.result.termination_reason.value)
    print("Steps:", run_data.result.step_count)
    print(
        "Final object-to-target distance (m):",
        run_data.result.metrics["manipulation.final_object_to_target_distance_m"],
    )
    if "stage.usda" in run_data.text_artifacts:
        print("Stage artifact:", layout.artifacts_dir / "stage.usda")

    if run_data.result.success:
        print("PICKPLACE_BASELINE_OK")
        return 0

    print("PICKPLACE_BASELINE_FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
