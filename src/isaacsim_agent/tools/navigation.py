"""Minimal navigation geometry and deterministic scripted step helpers."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .registry import ToolSpec


@dataclass(frozen=True)
class Pose2D:
    """Simple planar pose used by the minimal navigation baseline."""

    x: float
    y: float
    yaw: float = 0.0

    @classmethod
    def from_dict(cls, payload: dict[str, float]) -> "Pose2D":
        return cls(
            x=float(payload["x"]),
            y=float(payload["y"]),
            yaw=float(payload.get("yaw", 0.0)),
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "x": round(self.x, 6),
            "y": round(self.y, 6),
            "yaw": round(self.yaw, 6),
        }


@dataclass(frozen=True)
class DirectNavigationAction:
    """One deterministic straight-line motion command toward the goal."""

    target_pose: Pose2D
    step_distance_m: float
    goal_distance_before_m: float
    heading_rad: float

    def to_dict(self) -> dict[str, float | dict[str, float]]:
        return {
            "target_pose": self.target_pose.to_dict(),
            "step_distance_m": round(self.step_distance_m, 6),
            "goal_distance_before_m": round(self.goal_distance_before_m, 6),
            "heading_rad": round(self.heading_rad, 6),
        }


SCRIPTED_NAVIGATE_TOOL = ToolSpec(
    name="scripted_navigate_step",
    description="Move one deterministic straight-line step toward the configured navigation goal.",
)


def distance_between_poses(start_pose: Pose2D, end_pose: Pose2D) -> float:
    """Return Euclidean distance between two planar poses."""

    return math.hypot(end_pose.x - start_pose.x, end_pose.y - start_pose.y)


def compute_path_length(poses: list[Pose2D]) -> float:
    """Return the cumulative path length of a pose sequence."""

    if len(poses) < 2:
        return 0.0

    return sum(distance_between_poses(poses[index - 1], poses[index]) for index in range(1, len(poses)))


def compute_direct_navigation_step(
    current_pose: Pose2D,
    goal_pose: Pose2D,
    step_size_m: float,
) -> DirectNavigationAction:
    """Return the next straight-line step toward the goal pose."""

    if step_size_m <= 0:
        raise ValueError("step_size_m must be positive for the scripted navigation baseline")

    dx = goal_pose.x - current_pose.x
    dy = goal_pose.y - current_pose.y
    goal_distance = math.hypot(dx, dy)

    if goal_distance == 0.0:
        return DirectNavigationAction(
            target_pose=Pose2D(x=goal_pose.x, y=goal_pose.y, yaw=goal_pose.yaw),
            step_distance_m=0.0,
            goal_distance_before_m=0.0,
            heading_rad=current_pose.yaw,
        )

    heading = math.atan2(dy, dx)
    travel_distance = min(step_size_m, goal_distance)
    ratio = travel_distance / goal_distance
    target_pose = Pose2D(
        x=current_pose.x + (dx * ratio),
        y=current_pose.y + (dy * ratio),
        yaw=heading,
    )
    return DirectNavigationAction(
        target_pose=target_pose,
        step_distance_m=travel_distance,
        goal_distance_before_m=goal_distance,
        heading_rad=heading,
    )
