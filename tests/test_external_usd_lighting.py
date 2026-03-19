"""Portable tests for the external-USD fallback lighting behavior."""

from __future__ import annotations

import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from isaacsim_agent.render import external_usd


class _FakeContext:
    def __init__(self, stage) -> None:
        self._stage = stage
        self.disabled_recent = False
        self.enabled_recent = False
        self.opened_path: str | None = None

    def disable_save_to_recent_files(self) -> None:
        self.disabled_recent = True

    def enable_save_to_recent_files(self) -> None:
        self.enabled_recent = True

    def open_stage(self, path: str) -> bool:
        self.opened_path = path
        return True

    def get_stage_loading_status(self):
        return (0, 0, 0)

    def get_stage(self):
        return self._stage


class _FakeBackend:
    def __init__(self, context) -> None:
        self._context = context
        self.Usd = types.SimpleNamespace(
            Stage=types.SimpleNamespace(IsSupportedFile=lambda path: True),
        )
        self.Gf = object()
        self.UsdGeom = object()
        self.UsdLux = object()
        self.omni_usd = types.SimpleNamespace(get_context=lambda: self._context)


class _FakeSession:
    def __init__(self, backend) -> None:
        self._backend = backend
        self.config = types.SimpleNamespace(warmup_updates=2)
        self.update_calls: list[int] = []

    def _require_backend(self):
        return self._backend

    def update(self, count: int) -> None:
        self.update_calls.append(count)


class _FakePrim:
    def __init__(self, *, is_light: bool) -> None:
        self._is_light = is_light

    def IsValid(self) -> bool:
        return True

    def IsDefined(self) -> bool:
        return True

    def IsActive(self) -> bool:
        return True

    def HasAPI(self, schema) -> bool:
        return self._is_light

    def IsA(self, schema) -> bool:
        return self._is_light


class _FakeStageForTraversal:
    def __init__(self, prims: list[_FakePrim]) -> None:
        self._prims = prims

    def Traverse(self):
        return list(self._prims)


@unittest.skipUnless(
    hasattr(external_usd, "ensure_external_usd_lighting"),
    "lighting helper is not integrated in this workspace",
)
class LoadExternalUsdStageLightingTest(unittest.TestCase):
    def test_load_external_usd_stage_calls_lighting_helper(self) -> None:
        stage = object()
        context = _FakeContext(stage)
        backend = _FakeBackend(context)
        session = _FakeSession(backend)

        with tempfile.TemporaryDirectory() as temp_dir:
            usd_path = Path(temp_dir) / "asset.usda"
            usd_path.write_text("#usda 1.0\n", encoding="utf-8")
            with mock.patch.object(external_usd, "ensure_external_usd_lighting", return_value=True) as helper:
                returned_stage = external_usd.load_external_usd_stage(session, usd_path)

        self.assertIs(returned_stage, stage)
        helper.assert_called_once()
        args, kwargs = helper.call_args
        self.assertEqual(args, (stage,))
        self.assertEqual(kwargs["Gf_module"], backend.Gf)
        self.assertEqual(kwargs["UsdGeom_module"], backend.UsdGeom)
        self.assertEqual(kwargs["UsdLux_module"], backend.UsdLux)
        self.assertEqual(context.opened_path, str(usd_path.resolve()))
        self.assertTrue(context.disabled_recent)
        self.assertTrue(context.enabled_recent)
        self.assertEqual(session.update_calls, [2, 2])


@unittest.skipUnless(
    hasattr(external_usd, "stage_has_lights"),
    "light-detection helper is not integrated in this workspace",
)
class StageHasLightsTest(unittest.TestCase):
    def _patch_pxr(self):
        fake_pxr = types.ModuleType("pxr")
        fake_pxr.UsdLux = types.SimpleNamespace(LightAPI=object())
        return mock.patch.dict("sys.modules", {"pxr": fake_pxr})

    def test_stage_has_lights_returns_false_when_no_light_prims_exist(self) -> None:
        stage = _FakeStageForTraversal([_FakePrim(is_light=False), _FakePrim(is_light=False)])
        with self._patch_pxr():
            self.assertFalse(external_usd.stage_has_lights(stage))

    def test_stage_has_lights_returns_true_when_any_light_prim_exists(self) -> None:
        stage = _FakeStageForTraversal([_FakePrim(is_light=False), _FakePrim(is_light=True)])
        with self._patch_pxr():
            self.assertTrue(external_usd.stage_has_lights(stage))


if __name__ == "__main__":
    unittest.main()
