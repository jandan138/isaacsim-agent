#!/usr/bin/env python3
"""Render project demo scenes once the phase-one render interfaces are available."""

from __future__ import annotations

import argparse
import inspect
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


BLOCKED_EXIT = 2
DEFAULT_VIEWS = ("front", "three_quarter", "top", "side")


class RenderEntrypointBlocked(RuntimeError):
    """Raised when the phase-one render interfaces are not yet available."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render phase-one project demo views.")
    parser.add_argument(
        "--task-type",
        choices=["navigation", "pick_place"],
        required=True,
        help="Project demo task family to render.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where rendered PNG files should be written.",
    )
    parser.add_argument(
        "--scene-id",
        default=None,
        help="Optional scene identifier recorded by downstream render integrations.",
    )
    parser.add_argument(
        "--view",
        action="append",
        dest="views",
        default=None,
        help="View name to render. Repeat the flag to request multiple views.",
    )
    parser.add_argument("--width", type=int, default=1280, help="Requested output width in pixels.")
    parser.add_argument("--height", type=int, default=720, help="Requested output height in pixels.")
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Launch the render session headless. Use --no-headless for local debugging.",
    )
    parser.add_argument("--save-stage", action="store_true", help="Request stage export alongside PNG output.")
    parser.add_argument("--show-trajectory", action="store_true", help="Request trajectory overlay where supported.")
    parser.add_argument("--show-goal-region", action="store_true", help="Request goal-region overlay where supported.")
    parser.add_argument("--show-labels", action="store_true", help="Request text labels where supported.")
    parser.add_argument("--palette", default="default", help="Visualization palette identifier passed downstream.")
    parser.add_argument("--start-x", type=float, default=0.0, help="Navigation demo start x position.")
    parser.add_argument("--start-y", type=float, default=0.0, help="Navigation demo start y position.")
    parser.add_argument("--start-yaw", type=float, default=0.0, help="Navigation demo start yaw in radians.")
    parser.add_argument("--goal-x", type=float, default=2.0, help="Navigation demo goal x position.")
    parser.add_argument("--goal-y", type=float, default=0.0, help="Navigation demo goal y position.")
    parser.add_argument("--goal-yaw", type=float, default=0.0, help="Navigation demo goal yaw in radians.")
    parser.add_argument("--success-radius-m", type=float, default=0.2, help="Navigation goal success radius.")
    parser.add_argument("--step-size-m", type=float, default=0.5, help="Navigation step size.")
    parser.add_argument("--control-dt-sec", type=float, default=0.5, help="Navigation control delta time.")
    parser.add_argument("--max-steps", type=int, default=10, help="Maximum deterministic control steps.")
    parser.add_argument("--max-time-sec", type=float, default=10.0, help="Maximum simulated time.")
    parser.add_argument("--gripper-start-x", type=float, default=0.0, help="Pick-place gripper start x position.")
    parser.add_argument("--gripper-start-y", type=float, default=0.0, help="Pick-place gripper start y position.")
    parser.add_argument("--gripper-start-z", type=float, default=0.18, help="Pick-place gripper start z position.")
    parser.add_argument("--object-start-x", type=float, default=0.0, help="Pick-place object start x position.")
    parser.add_argument("--object-start-y", type=float, default=0.0, help="Pick-place object start y position.")
    parser.add_argument("--object-start-z", type=float, default=0.02, help="Pick-place object start z position.")
    parser.add_argument("--target-x", type=float, default=0.25, help="Pick-place target x position.")
    parser.add_argument("--target-y", type=float, default=0.0, help="Pick-place target y position.")
    parser.add_argument("--target-z", type=float, default=0.02, help="Pick-place target z position.")
    parser.add_argument("--hover-offset-m", type=float, default=0.08, help="Pick-place hover offset.")
    parser.add_argument("--grasp-tolerance-m", type=float, default=0.03, help="Pick-place grasp tolerance.")
    parser.add_argument("--place-tolerance-m", type=float, default=0.04, help="Pick-place place tolerance.")
    return parser


def _instantiate_config(config_cls, payload: dict[str, object]) -> object:
    try:
        return config_cls(**payload)
    except TypeError:
        signature = inspect.signature(config_cls)
        filtered = {name: value for name, value in payload.items() if name in signature.parameters}
        return config_cls(**filtered)


def _resolve_render_hooks():
    try:
        from isaacsim_agent.render import CameraViewSpec  # type: ignore
        from isaacsim_agent.render import RenderBackendUnavailableError  # type: ignore
        from isaacsim_agent.render import RenderSessionConfig  # type: ignore
        from isaacsim_agent.render import VisualizationConfig  # type: ignore
        from isaacsim_agent.render import render_rgb_views  # type: ignore
        from isaacsim_agent.render import start_render_app  # type: ignore
    except ModuleNotFoundError as exc:
        raise RenderEntrypointBlocked(
            "isaacsim_agent.render is not importable yet. Worker 2 integration is still required."
        ) from exc
    except ImportError as exc:
        raise RenderEntrypointBlocked(
            "RenderSession/start_render_app/render_rgb_views exports are not available from isaacsim_agent.render."
        ) from exc

    return (
        CameraViewSpec,
        RenderBackendUnavailableError,
        RenderSessionConfig,
        VisualizationConfig,
        start_render_app,
        render_rgb_views,
    )


def _build_visualization_config(config_cls, args: argparse.Namespace) -> object:
    payload: dict[str, object] = {
        "show_trajectory": args.show_trajectory,
        "show_goal_region": args.show_goal_region,
        "show_labels": args.show_labels,
    }
    if args.palette != "default":
        raise ValueError(
            "Phase-one render_demo_views.py currently supports only --palette default."
        )
    return _instantiate_config(config_cls, payload)


def _build_navigation_payload(args: argparse.Namespace):
    from isaacsim_agent.tasks.navigation.baseline import NavigationTaskDefinition
    from isaacsim_agent.tasks.navigation.isaac_world import IsaacNavigationWorldConfig
    from isaacsim_agent.tasks.navigation.isaac_world import populate_navigation_stage
    from isaacsim_agent.tools.navigation import Pose2D

    definition = NavigationTaskDefinition(
        start_pose=Pose2D(x=args.start_x, y=args.start_y, yaw=args.start_yaw),
        goal_pose=Pose2D(x=args.goal_x, y=args.goal_y, yaw=args.goal_yaw),
        success_radius_m=args.success_radius_m,
        step_size_m=args.step_size_m,
        control_dt_sec=args.control_dt_sec,
        max_steps=args.max_steps,
        max_time_sec=args.max_time_sec,
        max_stuck_steps=3,
        stuck_distance_epsilon_m=1e-6,
    )
    return populate_navigation_stage, definition, IsaacNavigationWorldConfig()


def _build_pickplace_payload(args: argparse.Namespace):
    from isaacsim_agent.tasks.manipulation.baseline import PickPlaceTaskDefinition
    from isaacsim_agent.tasks.manipulation.isaac_world import IsaacPickPlaceWorldConfig
    from isaacsim_agent.tasks.manipulation.isaac_world import populate_pickplace_stage
    from isaacsim_agent.tools.manipulation import Pose3D

    definition = PickPlaceTaskDefinition(
        gripper_start_pose=Pose3D(x=args.gripper_start_x, y=args.gripper_start_y, z=args.gripper_start_z),
        object_start_pose=Pose3D(x=args.object_start_x, y=args.object_start_y, z=args.object_start_z),
        target_pose=Pose3D(x=args.target_x, y=args.target_y, z=args.target_z),
        hover_offset_m=args.hover_offset_m,
        grasp_tolerance_m=args.grasp_tolerance_m,
        place_tolerance_m=args.place_tolerance_m,
        control_dt_sec=args.control_dt_sec,
        max_steps=args.max_steps,
        max_time_sec=args.max_time_sec,
    )
    return populate_pickplace_stage, definition, IsaacPickPlaceWorldConfig()


def _build_navigation_views(camera_view_spec_cls, definition, args: argparse.Namespace) -> list[object]:
    center_x = (definition.start_pose.x + definition.goal_pose.x) / 2.0
    center_y = (definition.start_pose.y + definition.goal_pose.y) / 2.0
    span = max(
        abs(definition.goal_pose.x - definition.start_pose.x),
        abs(definition.goal_pose.y - definition.start_pose.y),
        definition.success_radius_m * 4.0,
        1.0,
    )
    distance = max(2.0, span * 2.5)
    height = max(1.0, span * 1.5)
    top_height = max(2.5, span * 3.0)
    look_at = (center_x, center_y, 0.0)
    available = {
        "front": camera_view_spec_cls(
            name="front",
            position=(center_x, center_y - distance, height),
            look_at=look_at,
            resolution=(args.width, args.height),
        ),
        "three_quarter": camera_view_spec_cls(
            name="three_quarter",
            position=(center_x - (distance * 0.7), center_y - (distance * 0.7), height * 1.1),
            look_at=look_at,
            resolution=(args.width, args.height),
        ),
        "top": camera_view_spec_cls(
            name="top",
            position=(center_x, center_y, top_height),
            look_at=look_at,
            resolution=(args.width, args.height),
        ),
        "side": camera_view_spec_cls(
            name="side",
            position=(center_x + distance, center_y, height),
            look_at=look_at,
            resolution=(args.width, args.height),
        ),
    }
    requested_views = tuple(args.views or DEFAULT_VIEWS)
    unknown_views = [name for name in requested_views if name not in available]
    if unknown_views:
        raise ValueError(f"Unknown view name(s): {', '.join(unknown_views)}")
    return [available[name] for name in requested_views]


def _build_pickplace_views(camera_view_spec_cls, definition, args: argparse.Namespace) -> list[object]:
    xs = [definition.gripper_start_pose.x, definition.object_start_pose.x, definition.target_pose.x]
    ys = [definition.gripper_start_pose.y, definition.object_start_pose.y, definition.target_pose.y]
    zs = [definition.gripper_start_pose.z, definition.object_start_pose.z, definition.target_pose.z]
    center_x = sum(xs) / len(xs)
    center_y = sum(ys) / len(ys)
    look_at_z = max(sum(zs) / len(zs), 0.02)
    span = max(max(xs) - min(xs), max(ys) - min(ys), 0.25)
    distance = max(0.5, span * 3.0)
    height = max(0.3, span * 2.0)
    top_height = max(0.8, span * 4.0)
    look_at = (center_x, center_y, look_at_z)
    available = {
        "front": camera_view_spec_cls(
            name="front",
            position=(center_x, center_y - distance, height),
            look_at=look_at,
            resolution=(args.width, args.height),
        ),
        "three_quarter": camera_view_spec_cls(
            name="three_quarter",
            position=(center_x - (distance * 0.7), center_y - (distance * 0.7), height * 1.2),
            look_at=look_at,
            resolution=(args.width, args.height),
        ),
        "top": camera_view_spec_cls(
            name="top",
            position=(center_x, center_y, top_height),
            look_at=look_at,
            resolution=(args.width, args.height),
        ),
        "side": camera_view_spec_cls(
            name="side",
            position=(center_x + distance, center_y, height),
            look_at=look_at,
            resolution=(args.width, args.height),
        ),
    }
    requested_views = tuple(args.views or DEFAULT_VIEWS)
    unknown_views = [name for name in requested_views if name not in available]
    if unknown_views:
        raise ValueError(f"Unknown view name(s): {', '.join(unknown_views)}")
    return [available[name] for name in requested_views]


def _export_stage(stage, output_dir: Path) -> Path:
    stage_path = output_dir / "stage.usda"
    stage.Export(str(stage_path))
    return stage_path


def _render_payload(args: argparse.Namespace) -> dict[str, Any]:
    (
        CameraViewSpec,
        RenderBackendUnavailableError,
        RenderSessionConfig,
        VisualizationConfig,
        start_render_app,
        render_rgb_views,
    ) = _resolve_render_hooks()
    if args.task_type == "navigation":
        populate_fn, definition, world_config = _build_navigation_payload(args)
        views = _build_navigation_views(CameraViewSpec, definition, args)
    else:
        populate_fn, definition, world_config = _build_pickplace_payload(args)
        views = _build_pickplace_views(CameraViewSpec, definition, args)

    visualization_config = _build_visualization_config(VisualizationConfig, args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session_config = RenderSessionConfig(headless=args.headless)
    try:
        session = start_render_app(config=session_config)
    except RenderBackendUnavailableError as exc:
        raise RenderEntrypointBlocked(str(exc)) from exc

    stage = session.new_stage()
    stage_handles = populate_fn(
        stage=stage,
        definition=definition,
        world_config=world_config,
        visualization_config=visualization_config,
    )
    render_result = render_rgb_views(session=session, views=views, output_dir=output_dir)
    stage_path = _export_stage(stage, output_dir) if args.save_stage else None

    return {
        "output_dir": output_dir,
        "render_result": render_result,
        "scene_id": args.scene_id,
        "stage_path": stage_path,
        "stage_metadata": getattr(stage_handles, "metadata", {}),
        "session": session,
    }


def main() -> int:
    args = build_parser().parse_args()
    payload: dict[str, Any] | None = None
    try:
        payload = _render_payload(args)
    except RenderEntrypointBlocked as exc:
        print(f"RENDER_DEMO_VIEWS_BLOCKED: {exc}", file=sys.stderr)
        return BLOCKED_EXIT
    except Exception as exc:
        print(f"RENDER_DEMO_VIEWS_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    try:
        print("Output directory:", payload["output_dir"])
        if payload["scene_id"] is not None:
            print("Scene id:", payload["scene_id"])
        for artifact in payload["render_result"] or []:
            print("Rendered:", artifact.image_path)
        if payload["stage_path"] is not None:
            print("Stage export:", payload["stage_path"])
        print("RENDER_DEMO_VIEWS_OK")
        return 0
    finally:
        session = payload.get("session")
        close_fn = getattr(session, "close", None)
        if callable(close_fn):
            close_fn()


if __name__ == "__main__":
    raise SystemExit(main())
