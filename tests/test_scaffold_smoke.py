"""Smoke tests for the repository scaffold."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class ScaffoldSmokeTest(unittest.TestCase):
    def test_required_top_level_directories_exist(self) -> None:
        required_directories = [
            REPO_ROOT / "configs",
            REPO_ROOT / "docs",
            REPO_ROOT / "paper",
            REPO_ROOT / "results",
            REPO_ROOT / "scripts",
            REPO_ROOT / "skills",
            REPO_ROOT / "src",
            REPO_ROOT / "tests",
        ]

        missing = [str(path.relative_to(REPO_ROOT)) for path in required_directories if not path.is_dir()]
        self.assertEqual(missing, [], f"Missing scaffold directories: {missing}")

    def test_placeholder_packages_import(self) -> None:
        import isaacsim_agent
        from isaacsim_agent.experiments import ExperimentManifest
        from isaacsim_agent.memory import MemoryRecord
        from isaacsim_agent.paper import PaperSection
        from isaacsim_agent.planner import PlannerConfig
        from isaacsim_agent.runtime import RuntimeSession
        from isaacsim_agent.tools import ToolSpec

        self.assertEqual(isaacsim_agent.__version__, "0.1.0")
        self.assertEqual(PlannerConfig().backend, "placeholder")
        self.assertEqual(MemoryRecord(key="k", value="v").source, "placeholder")
        self.assertEqual(RuntimeSession(session_id="demo").policy_name, "placeholder")
        self.assertEqual(ToolSpec(name="move", description="placeholder").name, "move")
        self.assertEqual(ExperimentManifest(name="baseline", task_family="navigation").seed, 0)
        self.assertEqual(PaperSection(title="Introduction").status, "placeholder")


if __name__ == "__main__":
    unittest.main()
