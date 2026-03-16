"""Minimal manipulation geometry and scripted pick-and-place action helpers."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .registry import ToolSpec


@dataclass(frozen=True)
class Pose3D:
    """Simple Cartesian pose used by the minimal manipulation baseline."""

    x: float
    y: float
    z: float
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0

    @classmethod
    def from_dict(cls, payload: dict[str, float]) -> "Pose3D":
        return cls(
            x=float(payload["x"]),
            y=float(payload["y"]),
            z=float(payload["z"]),
            roll=float(payload.get("roll", 0.0)),
            pitch=float(payload.get("pitch", 0.0)),
            yaw=float(payload.get("yaw", 0.0)),
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "x": round(self.x, 6),
            "y": round(self.y, 6),
            "z": round(self.z, 6),
            "roll": round(self.roll, 6),
            "pitch": round(self.pitch, 6),
            "yaw": round(self.yaw, 6),
        }


@dataclass(frozen=True)
class ScriptedPickPlaceAction:
    """One deterministic scripted pick-and-place action."""

    phase_name: str
    target_gripper_pose: Pose3D
    gripper_command: str = "hold"
    attach_object: bool = False
    release_object: bool = False

    def to_dict(self) -> dict[str, str | bool | dict[str, float]]:
        return {
            "phase_name": self.phase_name,
            "target_gripper_pose": self.target_gripper_pose.to_dict(),
            "gripper_command": self.gripper_command,
            "attach_object": self.attach_object,
            "release_object": self.release_object,
        }


SCRIPTED_PICKPLACE_TOOL = ToolSpec(
    name="scripted_pick_place_step",
    description="Apply one deterministic step from the fixed minimal pick-and-place sequence.",
)


def distance_between_poses(start_pose: Pose3D, end_pose: Pose3D) -> float:
    """Return Euclidean distance between two 3D positions."""

    return math.sqrt(
        ((end_pose.x - start_pose.x) ** 2)
        + ((end_pose.y - start_pose.y) ** 2)
        + ((end_pose.z - start_pose.z) ** 2)
    )


def compute_pose_path_length(poses: list[Pose3D]) -> float:
    """Return the cumulative Cartesian path length for a pose sequence."""

    if len(poses) < 2:
        return 0.0

    return sum(distance_between_poses(poses[index - 1], poses[index]) for index in range(1, len(poses)))
