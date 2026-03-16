"""Smoke tests for the minimal M5 eval harness."""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SUMMARY_SCRIPT = REPO_ROOT / "scripts" / "summarize_results.py"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def build_sample_results(results_root: Path) -> dict[str, Path]:
    from isaacsim_agent.runtime import build_agent_v0_navigation_task_config
    from isaacsim_agent.runtime import run_and_write_agent_v0
    from isaacsim_agent.tasks.manipulation import build_minimal_pickplace_task_config
    from isaacsim_agent.tasks.manipulation import run_and_write_pickplace_baseline
    from isaacsim_agent.tasks.navigation import build_minimal_navigation_task_config
    from isaacsim_agent.tasks.navigation import run_and_write_navigation_baseline

    run_and_write_navigation_baseline(
        config=build_minimal_navigation_task_config(backend="toy"),
        run_id="eval-baseline-nav-good",
        results_root=results_root,
    )
    run_and_write_agent_v0(
        config=build_agent_v0_navigation_task_config(backend="toy"),
        run_id="eval-agent-runtime-good",
        results_root=results_root,
    )
    _, bad_layout = run_and_write_pickplace_baseline(
        config=build_minimal_pickplace_task_config(backend="toy"),
        run_id="eval-pickplace-missing-artifact",
        results_root=results_root,
    )
    (bad_layout.artifacts_dir / "trajectory.json").unlink()

    return {
        "baseline": results_root / "runs" / "eval-baseline-nav-good",
        "agent": results_root / "runs" / "eval-agent-runtime-good",
        "bad": results_root / "runs" / "eval-pickplace-missing-artifact",
    }


class EvalHarnessSmokeTest(unittest.TestCase):
    def test_summarize_results_root_emits_complete_and_bad_rows(self) -> None:
        from isaacsim_agent.eval import summarize_results_root
        from isaacsim_agent.eval import write_summary_outputs

        with tempfile.TemporaryDirectory() as temp_dir:
            results_root = Path(temp_dir) / "results"
            output_dir = results_root / "processed" / "smoke"
            build_sample_results(results_root)

            bundle = summarize_results_root(results_root)
            written = write_summary_outputs(bundle=bundle, output_dir=output_dir)

            self.assertEqual(bundle.aggregate.total_runs, 3)
            self.assertEqual(bundle.aggregate.contract_complete_runs, 3)
            self.assertEqual(bundle.aggregate.run_complete_runs, 2)
            self.assertEqual(bundle.aggregate.bad_runs, 1)

            by_run_id = {summary.run_id: summary for summary in bundle.summaries}
            baseline = by_run_id["eval-baseline-nav-good"]
            agent = by_run_id["eval-agent-runtime-good"]
            bad = by_run_id["eval-pickplace-missing-artifact"]

            self.assertTrue(baseline.run_complete)
            self.assertTrue(baseline.contract_complete)
            self.assertEqual(baseline.task_family, "navigation")
            self.assertEqual(baseline.runtime_variant, "navigation_baseline")
            self.assertEqual(baseline.backend_variant, "toy")
            self.assertEqual(baseline.planner_calls, 0)
            self.assertEqual(baseline.tool_variant, "scripted_navigate_step")

            self.assertTrue(agent.run_complete)
            self.assertTrue(agent.contract_complete)
            self.assertEqual(agent.runtime_variant, "agent_runtime_v0")
            self.assertEqual(agent.planner_backend, "mock_rule_based")
            self.assertGreater(agent.planner_calls or 0, 0)
            self.assertEqual(agent.tool_variant, "get_robot_state|get_goal_state|navigate_to")

            self.assertFalse(bad.run_complete)
            self.assertTrue(bad.contract_complete)
            self.assertIn("missing_artifact", bad.validation_issue_codes)
            self.assertEqual(bad.task_family, "pick_place")
            self.assertEqual(bad.runtime_variant, "manipulation_baseline")

            self.assertTrue(written["summary_jsonl"].is_file())
            self.assertTrue(written["summary_csv"].is_file())
            self.assertTrue(written["aggregate_json"].is_file())
            self.assertTrue(written["validation_json"].is_file())

            jsonl_rows = [
                json.loads(line)
                for line in written["summary_jsonl"].read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(jsonl_rows), 3)

            with written["summary_csv"].open("r", encoding="utf-8", newline="") as handle:
                csv_rows = list(csv.DictReader(handle))
            self.assertEqual(len(csv_rows), 3)

            validation_rows = json.loads(written["validation_json"].read_text(encoding="utf-8"))
            bad_validation = next(item for item in validation_rows if item["run_id"] == "eval-pickplace-missing-artifact")
            self.assertFalse(bad_validation["run_complete"])
            self.assertEqual(bad_validation["missing_artifacts"], ["artifacts/trajectory.json"])

    def test_cli_summarize_and_validate_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            results_root = Path(temp_dir) / "results"
            summarize_output_dir = results_root / "processed" / "cli"
            validate_output_dir = results_root / "processed" / "validate"
            build_sample_results(results_root)

            summarize_command = [
                sys.executable,
                str(SUMMARY_SCRIPT),
                "summarize",
                "--results-root",
                str(results_root),
                "--output-dir",
                str(summarize_output_dir),
            ]
            summarize_completed = subprocess.run(
                summarize_command,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PYTHONPATH": str(SRC_ROOT), "PYTHONUNBUFFERED": "1"},
            )
            summarize_output = f"{summarize_completed.stdout}\n{summarize_completed.stderr}"
            self.assertEqual(summarize_completed.returncode, 0, summarize_output)
            self.assertIn("Runs scanned: 3", summarize_output)
            self.assertTrue((summarize_output_dir / "run_summary.jsonl").is_file())
            self.assertTrue((summarize_output_dir / "run_summary.csv").is_file())

            validate_command = [
                sys.executable,
                str(SUMMARY_SCRIPT),
                "validate",
                "--results-root",
                str(results_root),
                "--output-dir",
                str(validate_output_dir),
            ]
            validate_completed = subprocess.run(
                validate_command,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PYTHONPATH": str(SRC_ROOT), "PYTHONUNBUFFERED": "1"},
            )
            validate_output = f"{validate_completed.stdout}\n{validate_completed.stderr}"
            self.assertEqual(validate_completed.returncode, 1, validate_output)
            self.assertIn("Incomplete runs: eval-pickplace-missing-artifact", validate_output)
            self.assertTrue((validate_output_dir / "validation.json").is_file())


if __name__ == "__main__":
    unittest.main()
