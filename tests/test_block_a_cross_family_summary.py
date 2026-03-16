"""Coverage for the block A cross-family post-processing summary."""

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
CROSS_FAMILY_SCRIPT = REPO_ROOT / "scripts" / "summarize_block_a_cross_family.py"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _build_summary_row(
    *,
    run_id: str,
    task_family: str,
    prompt_variant: str,
    runtime_variant: str,
    success: bool,
    termination_reason: str,
    planner_calls: int,
    tool_calls: int,
    invalid_actions: int,
    retries: int,
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "run_dir": f"results/runs/{run_id}",
        "task_family": task_family,
        "task_id": f"{task_family}_task",
        "scene_id": f"{task_family}_scene",
        "robot_id": "agent_under_test",
        "seed": 0,
        "success": success,
        "termination_reason": termination_reason,
        "failure_reason": None if success else termination_reason,
        "step_count": planner_calls,
        "planner_calls": planner_calls,
        "tool_calls": tool_calls,
        "invalid_actions": invalid_actions,
        "episode_time_s": 1.0,
        "planner_latency_s": 0.1,
        "backend_variant": "toy",
        "model_variant": None,
        "prompt_variant": prompt_variant,
        "runtime_variant": runtime_variant,
        "runtime_policy": f"policy_{runtime_variant.lower()}",
        "planner_backend": "mock_block_a",
        "tool_variant": "tool_a|tool_b",
        "retries": retries,
        "contract_complete": True,
        "run_complete": True,
        "validation_issue_count": 0,
        "validation_issue_codes": [],
        "validation_issue_messages": [],
    }


def _build_validation_row(run_id: str) -> dict[str, object]:
    return {
        "run_id": run_id,
        "run_dir": f"results/runs/{run_id}",
        "required_files_present": True,
        "parsed_files_ok": True,
        "event_count": 5,
        "has_episode_end": True,
        "expected_artifact_count": 2,
        "missing_artifacts": [],
        "contract_complete": True,
        "run_complete": True,
        "issues": [],
    }


def _write_processed_input(processed_dir: Path, rows: list[dict[str, object]]) -> None:
    processed_dir.mkdir(parents=True, exist_ok=True)
    with (processed_dir / "run_summary.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    (processed_dir / "validation.json").write_text(
        json.dumps([_build_validation_row(str(row["run_id"])) for row in rows], indent=2) + "\n",
        encoding="utf-8",
    )


class BlockACrossFamilySummaryTest(unittest.TestCase):
    def test_library_merges_processed_summaries_and_builds_tables(self) -> None:
        from isaacsim_agent.eval import summarize_cross_family_processed_dirs

        navigation_rows = [
            _build_summary_row(
                run_id="nav-p0-r0-1",
                task_family="navigation",
                prompt_variant="P0",
                runtime_variant="R0",
                success=False,
                termination_reason="invalid_action_limit",
                planner_calls=1,
                tool_calls=0,
                invalid_actions=1,
                retries=0,
            ),
            _build_summary_row(
                run_id="nav-p0-r0-2",
                task_family="navigation",
                prompt_variant="P0",
                runtime_variant="R0",
                success=False,
                termination_reason="invalid_action_limit",
                planner_calls=1,
                tool_calls=0,
                invalid_actions=1,
                retries=0,
            ),
            _build_summary_row(
                run_id="nav-p2-r0-1",
                task_family="navigation",
                prompt_variant="P2",
                runtime_variant="R0",
                success=True,
                termination_reason="success",
                planner_calls=4,
                tool_calls=4,
                invalid_actions=0,
                retries=0,
            ),
        ]
        manipulation_rows = [
            _build_summary_row(
                run_id="pick-p0-r1-1",
                task_family="pick_place",
                prompt_variant="P0",
                runtime_variant="R1",
                success=True,
                termination_reason="success",
                planner_calls=9,
                tool_calls=8,
                invalid_actions=1,
                retries=1,
            ),
            _build_summary_row(
                run_id="pick-p2-r0-1",
                task_family="pick_place",
                prompt_variant="P2",
                runtime_variant="R0",
                success=True,
                termination_reason="success",
                planner_calls=8,
                tool_calls=8,
                invalid_actions=0,
                retries=0,
            ),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            navigation_dir = temp_path / "navigation"
            manipulation_dir = temp_path / "manipulation"
            output_dir = temp_path / "processed" / "block_a_cross_family_summary"
            _write_processed_input(navigation_dir, navigation_rows)
            _write_processed_input(manipulation_dir, manipulation_rows)

            result = summarize_cross_family_processed_dirs(
                input_dirs=[navigation_dir, manipulation_dir],
                output_dir=output_dir,
            )

            self.assertEqual(result.bundle.aggregate.total_runs, 5)
            self.assertEqual(result.bundle.aggregate.run_complete_runs, 5)
            self.assertEqual(result.bundle.aggregate.successful_runs, 3)
            self.assertTrue((output_dir / "run_summary.jsonl").is_file())
            self.assertTrue((output_dir / "run_summary.csv").is_file())
            self.assertTrue((output_dir / "aggregate.json").is_file())
            self.assertTrue((output_dir / "validation.json").is_file())
            self.assertTrue((output_dir / "cross_family_summary.json").is_file())
            self.assertTrue((output_dir / "cross_family_summary.csv").is_file())
            self.assertTrue((output_dir / "block_a_cross_family_summary.md").is_file())

            merged_rows = [
                json.loads(line)
                for line in (output_dir / "run_summary.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(merged_rows), 5)

            summary_payload = json.loads((output_dir / "cross_family_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary_payload["overall"]["merged_runs"], 5)
            self.assertEqual(len(summary_payload["sources"]), 2)
            self.assertIn("table_1_success_rate", summary_payload["tables"])
            self.assertIn("table_2_invalid_action_frequency", summary_payload["tables"])
            self.assertIn("table_3_planner_tool_efficiency", summary_payload["tables"])

            grouped_rows = summary_payload["group_by_task_family_prompt_runtime"]
            self.assertEqual(len(grouped_rows), 4)

            nav_p0_r0 = next(
                row
                for row in grouped_rows
                if row["task_family"] == "navigation"
                and row["prompt_variant"] == "P0"
                and row["runtime_variant"] == "R0"
            )
            self.assertEqual(nav_p0_r0["task_family_display"], "Navigation")
            self.assertEqual(nav_p0_r0["run_count"], 2)
            self.assertEqual(nav_p0_r0["successful_runs"], 0)
            self.assertEqual(nav_p0_r0["success_rate"], 0.0)
            self.assertEqual(nav_p0_r0["total_invalid_actions"], 2)
            self.assertEqual(nav_p0_r0["average_planner_calls"], 1.0)
            self.assertEqual(nav_p0_r0["average_tool_calls"], 0.0)
            self.assertEqual(nav_p0_r0["total_retries"], 0)

            pick_p0_r1 = next(
                row
                for row in grouped_rows
                if row["task_family"] == "pick_place"
                and row["prompt_variant"] == "P0"
                and row["runtime_variant"] == "R1"
            )
            self.assertEqual(pick_p0_r1["task_family_display"], "Manipulation")
            self.assertEqual(pick_p0_r1["success_rate"], 1.0)
            self.assertEqual(pick_p0_r1["total_invalid_actions"], 1)
            self.assertEqual(pick_p0_r1["average_planner_calls"], 9.0)
            self.assertEqual(pick_p0_r1["average_tool_calls"], 8.0)
            self.assertEqual(pick_p0_r1["total_retries"], 1)

            table_1_row = next(
                row
                for row in summary_payload["tables"]["table_1_success_rate"]
                if row["prompt_variant"] == "P0" and row["runtime_variant"] == "R1"
            )
            self.assertEqual(table_1_row["manipulation_run_count"], 1)
            self.assertEqual(table_1_row["manipulation_success_rate"], 1.0)

            with (output_dir / "cross_family_summary.csv").open("r", encoding="utf-8", newline="") as handle:
                csv_rows = list(csv.DictReader(handle))
            self.assertEqual(len(csv_rows), 4)
            csv_pick_row = next(
                row
                for row in csv_rows
                if row["task_family"] == "pick_place"
                and row["prompt_variant"] == "P0"
                and row["runtime_variant"] == "R1"
            )
            self.assertEqual(csv_pick_row["task_family_display"], "Manipulation")
            self.assertEqual(csv_pick_row["total_retries"], "1")

            markdown_summary = (output_dir / "block_a_cross_family_summary.md").read_text(encoding="utf-8")
            self.assertIn("# Block A Cross-Family Summary", markdown_summary)
            self.assertIn("## Table 1: Success rate (Navigation vs Manipulation)", markdown_summary)
            self.assertIn("## Table 2: Invalid action frequency", markdown_summary)
            self.assertIn("## Table 3: Planner / tool efficiency", markdown_summary)

    def test_cli_smoke_writes_cross_family_outputs(self) -> None:
        navigation_rows = [
            _build_summary_row(
                run_id="nav-cli-p0-r0",
                task_family="navigation",
                prompt_variant="P0",
                runtime_variant="R0",
                success=False,
                termination_reason="invalid_action_limit",
                planner_calls=1,
                tool_calls=0,
                invalid_actions=1,
                retries=0,
            ),
        ]
        manipulation_rows = [
            _build_summary_row(
                run_id="pick-cli-p0-r1",
                task_family="pick_place",
                prompt_variant="P0",
                runtime_variant="R1",
                success=True,
                termination_reason="success",
                planner_calls=9,
                tool_calls=8,
                invalid_actions=1,
                retries=1,
            ),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            navigation_dir = temp_path / "navigation"
            manipulation_dir = temp_path / "manipulation"
            output_dir = temp_path / "processed" / "block_a_cross_family_summary"
            _write_processed_input(navigation_dir, navigation_rows)
            _write_processed_input(manipulation_dir, manipulation_rows)

            command = [
                sys.executable,
                str(CROSS_FAMILY_SCRIPT),
                "--navigation-dir",
                str(navigation_dir),
                "--manipulation-dir",
                str(manipulation_dir),
                "--output-dir",
                str(output_dir),
            ]
            completed = subprocess.run(
                command,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PYTHONPATH": str(SRC_ROOT), "PYTHONUNBUFFERED": "1"},
            )

            combined_output = f"{completed.stdout}\n{completed.stderr}"
            self.assertEqual(completed.returncode, 0, combined_output)
            self.assertIn("Merged runs: 2", combined_output)
            self.assertIn("Cross-family Summary JSON:", combined_output)
            self.assertTrue((output_dir / "cross_family_summary.json").is_file())
            self.assertTrue((output_dir / "cross_family_summary.csv").is_file())
            self.assertTrue((output_dir / "block_a_cross_family_summary.md").is_file())


if __name__ == "__main__":
    unittest.main()
