"""Helpers for rendering external USD assets with the shared render session."""

from __future__ import annotations

from pathlib import Path
from typing import Any
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

    if ensure_external_usd_lighting(
        stage,
        Gf_module=backend.Gf,
        UsdGeom_module=backend.UsdGeom,
        UsdLux_module=backend.UsdLux,
    ):
        session.update(session.config.warmup_updates)
    return stage


def _resolve_usd_lighting_modules():
    try:
        from pxr import Gf  # type: ignore
        from pxr import UsdGeom  # type: ignore
        from pxr import UsdLux  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("External USD lighting helpers require USD Lux bindings at runtime") from exc
    return Gf, UsdGeom, UsdLux


def _resolve_usd_lux_module():
    try:
        from pxr import UsdLux  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("External USD light detection requires USD Lux bindings at runtime") from exc
    return UsdLux


def stage_has_lights(stage, usd_lux_module: Any | None = None) -> bool:
    """Return True when the opened external USD stage already provides lights."""

    if usd_lux_module is None:
        usd_lux_module = _resolve_usd_lux_module()

    light_api = getattr(usd_lux_module, "LightAPI", None)
    boundable_light_base = getattr(usd_lux_module, "BoundableLightBase", None)
    nonboundable_light_base = getattr(usd_lux_module, "NonboundableLightBase", None)

    for prim in stage.Traverse():
        if not prim.IsValid() or not prim.IsDefined() or not prim.IsActive():
            continue
        if light_api is not None and prim.HasAPI(light_api):
            return True
        if boundable_light_base is not None and prim.IsA(boundable_light_base):
            return True
        if nonboundable_light_base is not None and prim.IsA(nonboundable_light_base):
            return True
    return False


def _ensure_rotate_xyz_attr(prim, xformable):
    attr_name = "xformOp:rotateXYZ"
    if not prim.HasAttribute(attr_name):
        xformable.AddRotateXYZOp()
    return prim.GetAttribute(attr_name)


def ensure_external_usd_lighting(
    stage,
    *,
    Gf_module: Any | None = None,
    UsdGeom_module: Any | None = None,
    UsdLux_module: Any | None = None,
) -> bool:
    """Inject a conservative default light rig when the external USD stage has none."""

    if Gf_module is None or UsdGeom_module is None or UsdLux_module is None:
        Gf_module, UsdGeom_module, UsdLux_module = _resolve_usd_lighting_modules()

    if stage_has_lights(stage, usd_lux_module=UsdLux_module):
        return False

    UsdGeom_module.Xform.Define(stage, "/World")
    light_root_path = "/World/ExternalUsdFallbackLights"
    UsdGeom_module.Xform.Define(stage, light_root_path)

    dome = UsdLux_module.DomeLight.Define(stage, f"{light_root_path}/Dome")
    dome.CreateIntensityAttr().Set(150.0)
    dome.CreateColorAttr().Set(Gf_module.Vec3f(1.0, 1.0, 1.0))
    exposure_attr = getattr(dome, "CreateExposureAttr", None)
    if callable(exposure_attr):
        exposure_attr().Set(0.0)

    key = UsdLux_module.DistantLight.Define(stage, f"{light_root_path}/Key")
    key.CreateIntensityAttr().Set(550.0)
    key.CreateColorAttr().Set(Gf_module.Vec3f(1.0, 0.97, 0.92))
    key_angle_attr = getattr(key, "CreateAngleAttr", None)
    if callable(key_angle_attr):
        key_angle_attr().Set(0.53)
    key_prim = key.GetPrim()
    key_xformable = UsdGeom_module.Xformable(key_prim)
    _ensure_rotate_xyz_attr(key_prim, key_xformable).Set(Gf_module.Vec3f(-40.0, 35.0, 0.0))

    fill = UsdLux_module.DistantLight.Define(stage, f"{light_root_path}/Fill")
    fill.CreateIntensityAttr().Set(120.0)
    fill.CreateColorAttr().Set(Gf_module.Vec3f(0.84, 0.9, 1.0))
    fill_angle_attr = getattr(fill, "CreateAngleAttr", None)
    if callable(fill_angle_attr):
        fill_angle_attr().Set(0.53)
    fill_prim = fill.GetPrim()
    fill_xformable = UsdGeom_module.Xformable(fill_prim)
    _ensure_rotate_xyz_attr(fill_prim, fill_xformable).Set(Gf_module.Vec3f(-15.0, -130.0, 0.0))

    return True


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
