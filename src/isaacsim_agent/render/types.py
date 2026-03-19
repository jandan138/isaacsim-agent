"""Shared types for the Isaac render package."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

ColorRGB = tuple[float, float, float]
Vec2i = tuple[int, int]
Vec3f = tuple[float, float, float]


def _default_palette() -> dict[str, ColorRGB]:
    return {
        "agent": (0.1, 0.4, 0.9),
        "goal": (0.1, 0.75, 0.2),
        "object": (0.95, 0.45, 0.1),
        "source_zone": (0.15, 0.65, 0.2),
        "target_zone": (0.8, 0.2, 0.2),
        "trajectory": (0.95, 0.85, 0.2),
    }


@dataclass(frozen=True)
class VisualizationConfig:
    """Optional stage-visualization toggles shared across render entrypoints."""

    show_trajectory: bool = False
    show_goal_region: bool = False
    show_labels: bool = False
    palette: dict[str, ColorRGB] = field(default_factory=_default_palette)


@dataclass(frozen=True)
class CameraViewSpec:
    """One camera view to be rendered to disk."""

    name: str
    position: Vec3f
    look_at: Vec3f
    resolution: Vec2i = (1280, 720)
    camera_prim_path: str | None = None
    up_axis: Vec3f = (0.0, 0.0, 1.0)
    clipping_range: tuple[float, float] = (0.01, 1000.0)
    focal_length: float | None = None
    horizontal_aperture: float | None = None
    vertical_aperture: float | None = None


@dataclass(frozen=True)
class RenderSessionConfig:
    """Lifecycle and renderer settings for a headless render session."""

    headless: bool = True
    sync_loads: bool = True
    renderer: str = "PathTracing"
    pathtracing_spp: int = 64
    pathtracing_total_spp: int | None = None
    enable_denoiser: bool = False
    rt_subframes: int = 4
    warmup_updates: int = 2
    capture_on_play: bool = False


@dataclass(frozen=True)
class RenderCaptureArtifact:
    """One PNG written by the render session."""

    view_name: str
    camera_prim_path: str
    image_path: Path
