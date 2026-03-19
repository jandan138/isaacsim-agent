"""Single-app Isaac Sim render lifecycle helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Sequence

from .errors import RenderBackendUnavailableError
from .types import CameraViewSpec
from .types import RenderCaptureArtifact
from .types import RenderSessionConfig


@dataclass
class _RenderBackend:
    carb: Any
    omni_kit_app: Any
    omni_usd: Any
    rep: Any
    Gf: Any
    Usd: Any
    UsdGeom: Any
    UsdLux: Any


def _sanitize_prim_name(name: str) -> str:
    candidate = re.sub(r"[^A-Za-z0-9_]+", "_", name).strip("_")
    return candidate or "View"


def _ensure_runtime_cache_dirs() -> None:
    """Pre-create cache directories that Isaac/Replicator expect at startup."""

    cache_root = Path.home() / ".cache"
    for relative_path in ("warp", "ov/texturecache"):
        (cache_root / relative_path).mkdir(parents=True, exist_ok=True)


class RenderSession:
    """Manage one headless Isaac Sim app and capture RGB views from a USD stage."""

    def __init__(self, config: RenderSessionConfig | None = None) -> None:
        self.config = config or RenderSessionConfig()
        self._simulation_app = None
        self._backend: _RenderBackend | None = None
        self._settings_snapshot: dict[str, object | None] = {}

    @classmethod
    def start(cls, config: RenderSessionConfig | None = None) -> "RenderSession":
        session = cls(config=config)
        session._start()
        return session

    def _start(self) -> None:
        _ensure_runtime_cache_dirs()
        try:
            from isaacsim import SimulationApp  # type: ignore
        except ModuleNotFoundError as exc:
            raise RenderBackendUnavailableError(
                "Isaac-backed rendering requires launching via ./scripts/isaac_python.sh."
            ) from exc

        launch_config = {
            "headless": self.config.headless,
            "sync_loads": self.config.sync_loads,
            "renderer": self.config.renderer,
        }
        self._simulation_app = SimulationApp(launch_config)

        try:
            import carb.settings  # type: ignore
            import omni.kit.app  # type: ignore
            import omni.replicator.core as rep  # type: ignore
            import omni.usd  # type: ignore
            from pxr import Gf  # type: ignore
            from pxr import Usd  # type: ignore
            from pxr import UsdGeom  # type: ignore
            from pxr import UsdLux  # type: ignore
        except ModuleNotFoundError as exc:
            self.close()
            raise RenderBackendUnavailableError(
                "Isaac Sim render modules were not importable after starting SimulationApp."
            ) from exc

        self._backend = _RenderBackend(
            carb=carb,
            omni_kit_app=omni.kit.app,
            omni_usd=omni.usd,
            rep=rep,
            Gf=Gf,
            Usd=Usd,
            UsdGeom=UsdGeom,
            UsdLux=UsdLux,
        )
        self._apply_render_settings()
        self.update(self.config.warmup_updates)

    def _require_backend(self) -> _RenderBackend:
        if self._backend is None or self._simulation_app is None:
            raise RuntimeError("RenderSession has not been started")
        return self._backend

    def _apply_render_settings(self) -> None:
        backend = self._require_backend()
        settings = backend.carb.settings.get_settings()
        tracked_settings = {
            "/omni/replicator/captureOnPlay": self.config.capture_on_play,
            "/rtx/rendermode": self.config.renderer,
            "/rtx/pathtracing/spp": self.config.pathtracing_spp,
            "/rtx/pathtracing/totalSpp": self.config.pathtracing_total_spp or self.config.pathtracing_spp,
            "/rtx/pathtracing/optixDenoiser/enabled": int(self.config.enable_denoiser),
        }
        self._settings_snapshot = {key: settings.get(key) for key in tracked_settings}
        for key, value in tracked_settings.items():
            settings.set(key, value)

    def update(self, num_updates: int = 1) -> None:
        if self._simulation_app is None:
            raise RuntimeError("RenderSession has not been started")
        for _ in range(max(0, num_updates)):
            self._simulation_app.update()

    def get_stage(self):
        backend = self._require_backend()
        context = backend.omni_usd.get_context()
        return context.get_stage()

    def new_stage(self):
        backend = self._require_backend()
        context = backend.omni_usd.get_context()
        if not context.new_stage():
            raise RuntimeError("omni.usd.get_context().new_stage() returned False")

        stage = context.get_stage()
        if stage is None:
            raise RuntimeError("Isaac Sim returned no active USD stage")

        backend.UsdGeom.SetStageUpAxis(stage, backend.UsdGeom.Tokens.z)
        backend.UsdGeom.SetStageMetersPerUnit(stage, 1.0)
        self.update(self.config.warmup_updates)
        return stage

    def ensure_stage(self):
        stage = self.get_stage()
        if stage is None:
            return self.new_stage()
        return stage

    def _ensure_camera_prim(self, view: CameraViewSpec) -> str:
        backend = self._require_backend()
        stage = self.ensure_stage()
        view_root_path = "/World/RenderCameras"
        backend.UsdGeom.Xform.Define(stage, view_root_path)

        camera_prim_path = view.camera_prim_path or f"{view_root_path}/{_sanitize_prim_name(view.name)}"
        camera = backend.UsdGeom.Camera.Define(stage, camera_prim_path)
        prim = camera.GetPrim()
        xformable = backend.UsdGeom.Xformable(prim)

        if not prim.HasAttribute("xformOp:translate"):
            xformable.AddTranslateOp()
        if not prim.HasAttribute("xformOp:orient"):
            xformable.AddOrientOp()

        prim.GetAttribute("xformOp:translate").Set(backend.Gf.Vec3d(*view.position))
        eye = backend.Gf.Vec3d(*view.position)
        target = backend.Gf.Vec3d(*view.look_at)
        up_axis = backend.Gf.Vec3d(*view.up_axis)
        look_at_quatd = backend.Gf.Matrix4d().SetLookAt(eye, target, up_axis).GetInverse().ExtractRotation().GetQuat()
        prim.GetAttribute("xformOp:orient").Set(backend.Gf.Quatf(look_at_quatd))

        camera.GetClippingRangeAttr().Set(backend.Gf.Vec2f(*view.clipping_range))
        if view.focal_length is not None:
            camera.GetFocalLengthAttr().Set(float(view.focal_length))
        if view.horizontal_aperture is not None:
            camera.GetHorizontalApertureAttr().Set(float(view.horizontal_aperture))
        if view.vertical_aperture is not None:
            camera.GetVerticalApertureAttr().Set(float(view.vertical_aperture))
        return camera_prim_path

    @staticmethod
    def _save_image(image_data: Any, output_path: Path) -> None:
        from PIL import Image
        import numpy as np

        image_array = np.asarray(image_data)
        if image_array.ndim != 3 or image_array.shape[-1] not in (3, 4):
            raise ValueError(f"Expected RGB/RGBA image data, got shape {image_array.shape}")

        mode = "RGBA" if image_array.shape[-1] == 4 else "RGB"
        image = Image.fromarray(image_array.astype(np.uint8), mode=mode)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)

    def render_rgb_views(
        self,
        views: Sequence[CameraViewSpec],
        output_dir: str | Path,
        *,
        rt_subframes: int | None = None,
    ) -> list[RenderCaptureArtifact]:
        backend = self._require_backend()
        output_root = Path(output_dir)
        output_root.mkdir(parents=True, exist_ok=True)

        render_products: list[Any] = []
        annotators: list[Any] = []
        view_paths: list[str] = []
        artifacts: list[RenderCaptureArtifact] = []

        try:
            for view in views:
                camera_prim_path = self._ensure_camera_prim(view)
                render_product = backend.rep.create.render_product(camera_prim_path, view.resolution, name=view.name)
                annotator = backend.rep.AnnotatorRegistry.get_annotator("rgb")
                annotator.attach(render_product)
                render_products.append(render_product)
                annotators.append(annotator)
                view_paths.append(camera_prim_path)

            backend.rep.orchestrator.preview()
            self.update(self.config.warmup_updates)
            backend.rep.orchestrator.step(
                rt_subframes=rt_subframes or self.config.rt_subframes,
                delta_time=0.0,
                pause_timeline=False,
            )
            self.update(self.config.warmup_updates)

            for view, camera_prim_path, annotator in zip(views, view_paths, annotators, strict=True):
                image_data = annotator.get_data()
                image_path = output_root / f"{view.name}.png"
                self._save_image(image_data, image_path)
                artifacts.append(
                    RenderCaptureArtifact(
                        view_name=view.name,
                        camera_prim_path=camera_prim_path,
                        image_path=image_path,
                    )
                )
        finally:
            for annotator in annotators:
                try:
                    annotator.detach()
                except Exception:
                    pass
            for render_product in render_products:
                try:
                    render_product.destroy()
                except Exception:
                    pass
            try:
                backend.rep.orchestrator.wait_until_complete()
            except Exception:
                pass

        return artifacts

    def close(self) -> None:
        if self._backend is not None:
            settings = self._backend.carb.settings.get_settings()
            for key, value in self._settings_snapshot.items():
                if value is not None:
                    settings.set(key, value)

        if self._simulation_app is not None:
            self._simulation_app.close()

        self._simulation_app = None
        self._backend = None
        self._settings_snapshot = {}

    def __enter__(self) -> "RenderSession":
        self._start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def start_render_app(config: RenderSessionConfig | None = None) -> RenderSession:
    """Start a headless Isaac render session."""

    return RenderSession.start(config=config)


def render_rgb_views(
    session: RenderSession,
    views: Sequence[CameraViewSpec],
    output_dir: str | Path,
    *,
    rt_subframes: int | None = None,
) -> list[RenderCaptureArtifact]:
    """Render a list of camera views to PNG files."""

    return session.render_rgb_views(views=views, output_dir=output_dir, rt_subframes=rt_subframes)
