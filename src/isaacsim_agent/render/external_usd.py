"""Helpers for rendering external USD assets with the shared render session."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .session import RenderSession
from .types import CameraViewSpec


DEFAULT_EXTERNAL_USD_VIEWS = ("front", "three_quarter", "top", "side")


def load_external_usd_stage(session: RenderSession, usd_path: str | Path):
    """Open an external USD asset into the shared Isaac render context."""

    backend = session._require_backend()
    resolved_path = Path(usd_path).expanduser().resolve()
    if not resolved_path.is_file():
        raise FileNotFoundError(f"USD asset was not found: {resolved_path}")

    if not backend.Usd.Stage.IsSupportedFile(str(resolved_path)):
        raise ValueError(f"Only USD-compatible files can be loaded: {resolved_path}")

    context = backend.omni_usd.get_context()
    disable_recent = getattr(context, "disable_save_to_recent_files", None)
    if callable(disable_recent):
        disable_recent()
    try:
        if not context.open_stage(str(resolved_path)):
            raise RuntimeError(f"omni.usd.get_context().open_stage() returned False for {resolved_path}")
    finally:
        enable_recent = getattr(context, "enable_save_to_recent_files", None)
        if callable(enable_recent):
            enable_recent()

    loading_status = getattr(context, "get_stage_loading_status", None)
    if callable(loading_status):
        for _ in range(300):
            _, _, loading = loading_status()
            if loading <= 0:
                break
            session.update(1)

    session.update(session.config.warmup_updates)
    stage = context.get_stage()
    if stage is None:
        raise RuntimeError(f"Isaac Sim returned no active USD stage after opening {resolved_path}")
    return stage


def _iter_bbox_root_prims(stage) -> list[object]:
    default_prim = stage.GetDefaultPrim()
    if default_prim and default_prim.IsValid() and default_prim.IsDefined() and default_prim.IsActive():
        return [default_prim]

    roots = [prim for prim in stage.GetPseudoRoot().GetChildren() if prim.IsDefined() and prim.IsActive()]
    if roots:
        return roots
    return [stage.GetPseudoRoot()]


def _compute_combined_bounds(stage, backend):
    purposes = [backend.UsdGeom.Tokens.default_]
    for token_name in ("render", "proxy"):
        token_value = getattr(backend.UsdGeom.Tokens, token_name, None)
        if token_value is not None:
            purposes.append(token_value)

    bbox_cache = backend.UsdGeom.BBoxCache(backend.Usd.TimeCode.Default(), purposes, True)

    total_bounds = backend.Gf.BBox3d()
    for root_prim in _iter_bbox_root_prims(stage):
        world_bound = bbox_cache.ComputeWorldBound(root_prim)
        total_bounds = backend.Gf.BBox3d.Combine(
            total_bounds,
            backend.Gf.BBox3d(world_bound.ComputeAlignedRange()),
        )

    aligned_range = total_bounds.GetRange()
    if aligned_range.IsEmpty():
        raise ValueError("External USD stage did not produce a non-empty world-space bounding box")
    return aligned_range


def build_bbox_camera_views(
    stage,
    width: int,
    height: int,
    selected_views: Sequence[str] | None = None,
) -> list[CameraViewSpec]:
    """Build default camera views around an external USD stage using world bounds."""

    if width <= 0 or height <= 0:
        raise ValueError("Camera resolution must be positive")

    try:
        from pxr import Gf  # type: ignore
        from pxr import Usd  # type: ignore
        from pxr import UsdGeom  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("BBox camera helpers require USD bindings at runtime") from exc

    backend = type(
        "_BackendProxy",
        (),
        {
            "Gf": Gf,
            "Usd": Usd,
            "UsdGeom": UsdGeom,
        },
    )()
    aligned_range = _compute_combined_bounds(stage, backend)

    minimum = aligned_range.GetMin()
    maximum = aligned_range.GetMax()
    size = aligned_range.GetSize()
    center_x = (minimum[0] + maximum[0]) / 2.0
    center_y = (minimum[1] + maximum[1]) / 2.0
    center_z = (minimum[2] + maximum[2]) / 2.0
    look_at = (center_x, center_y, center_z)

    footprint = max(float(size[0]), float(size[1]), 0.25)
    height_extent = max(float(size[2]), 0.1)
    diagonal = max((float(size[0]) ** 2 + float(size[1]) ** 2 + float(size[2]) ** 2) ** 0.5, 0.5)
    orbit_distance = max(footprint * 2.4, diagonal * 1.5, 1.25)
    elevation = max(height_extent * 0.9, diagonal * 0.35, 0.35)
    top_height = max(height_extent + diagonal * 1.6, 1.0)
    far_clip = max(1000.0, orbit_distance * 8.0)

    available = {
        "front": CameraViewSpec(
            name="front",
            position=(center_x, center_y - orbit_distance, center_z + elevation),
            look_at=look_at,
            resolution=(width, height),
            clipping_range=(0.01, far_clip),
        ),
        "three_quarter": CameraViewSpec(
            name="three_quarter",
            position=(
                center_x - (orbit_distance * 0.7),
                center_y - (orbit_distance * 0.7),
                center_z + (elevation * 1.15),
            ),
            look_at=look_at,
            resolution=(width, height),
            clipping_range=(0.01, far_clip),
        ),
        "top": CameraViewSpec(
            name="top",
            position=(center_x, center_y, center_z + top_height),
            look_at=look_at,
            resolution=(width, height),
            clipping_range=(0.01, far_clip),
        ),
        "side": CameraViewSpec(
            name="side",
            position=(center_x + orbit_distance, center_y, center_z + elevation),
            look_at=look_at,
            resolution=(width, height),
            clipping_range=(0.01, far_clip),
        ),
    }

    requested_views = tuple(selected_views or DEFAULT_EXTERNAL_USD_VIEWS)
    unknown_views = [name for name in requested_views if name not in available]
    if unknown_views:
        raise ValueError(f"Unknown external USD view name(s): {', '.join(unknown_views)}")
    return [available[name] for name in requested_views]
