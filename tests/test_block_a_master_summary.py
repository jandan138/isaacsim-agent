"""Coverage for the Block A master checkpoint post-processing summary."""

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
MASTER_SCRIPT = REPO_ROOT / "scripts" / "summarize_block_a_master.py"

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
    episode_time_s: float,
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "run_dir": f"results/runs/{run_id}",
        "task_family": task_family,
        "task_id": f"{task_family}_task_{prompt_variant.lower()}_{runtime_variant.lower()}",
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
        "episode_time_s": episode_time_s,
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


def _write_cross_family_reference(processed_dir: Path) -> None:
    processed_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for task_family in ("navigation", "pick_place"):
        rows.extend(
            [
                {
                    "task_family": task_family,
                    "prompt_variant": "P0",
                    "runtime_variant": "R0",
                    "run_count": 2,
                    "successful_runs": 0,
                    "success_rate": 0.0,
                    "average_planner_calls": 1.0,
                    "average_tool_calls": 0.0,
                },
                {
                    "task_family": task_family,
                    "prompt_variant": "P0",
                    "runtime_variant": "R1",
                    "run_count": 2,
                    "successful_runs": 2,
                    "success_rate": 1.0,
                    "average_planner_calls": 4.0 if task_family == "navigation" else 8.0,
                    "average_tool_calls": 3.0 if task_family == "navigation" else 7.0,
                },
                {
                    "task_family": task_family,
                    "prompt_variant": "P1",
                    "runtime_variant": "R0",
                    "run_count": 2,
                    "successful_runs": 2,
                    "success_rate": 1.0,
                    "average_planner_calls": 5.0 if task_family == "navigation" else 9.0,
                    "average_tool_calls": 5.0 if task_family == "navigation" else 9.0,
                },
                {
                    "task_family": task_family,
                    "prompt_variant": "P1",
                    "runtime_variant": "R1",
                    "run_count": 2,
                    "successful_runs": 2,
                    "success_rate": 1.0,
                    "average_planner_calls": 5.0 if task_family == "navigation" else 9.0,
                    "average_tool_calls": 5.0 if task_family == "navigation" else 9.0,
                },
                {
                    "task_family": task_family,
                    "prompt_variant": "P2",
                    "runtime_variant": "R0",
                    "run_count": 2,
                    "successful_runs": 2,
                    "success_rate": 1.0,
                    "average_planner_calls": 4.0 if task_family == "navigation" else 8.0,
                    "average_tool_calls": 4.0 if task_family == "navigation" else 8.0,
                },
                {
                    "task_family": task_family,
                    "prompt_variant": "P2",
                    "runtime_variant": "R1",
                    "run_count": 2,
                    "successful_runs": 2,
                    "success_rate": 1.0,
                    "average_planner_calls": 4.0 if task_family == "navigation" else 8.0,
                    "average_tool_calls": 4.0 if task_family == "navigation" else 8.0,
                },
            ]
        )

    payload = {
        "summary_title": "Block A Cross-Family Summary",
        "output_dir": str(processed_dir.resolve()),
        "group_by_task_family": [
            {"task_family": "navigation"},
            {"task_family": "pick_place"},
        ],
        "group_by_task_family_prompt_runtime": rows,
    }
    (processed_dir / "cross_family_summary.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def _build_source_rows(
    *,
    prefix: str,
    task_family: str,
    planner_base: int,
    tool_base: int,
    episode_time_base: float,
) -> list[dict[str, object]]:
    return [
        _build_summary_row(
            run_id=f"{prefix}-p0-r0",
            task_family=task_family,
            prompt_variant="P0",
            runtime_variant="R0",
            success=False,
            termination_reason="invalid_action_limit",
            planner_calls=1,
            tool_calls=0,
            invalid_actions=1,
            retries=0,
            episode_time_s=episode_time_base,
        ),
        _build_summary_row(
            run_id=f"{prefix}-p0-r1",
            task_family=task_family,
            prompt_variant="P0",
            runtime_variant="R1",
            success=True,
            termination_reason="success",
            planner_calls=planner_base,
            tool_calls=tool_base,
            invalid_actions=1,
            retries=1,
            episode_time_s=episode_time_base + 0.1,
        ),
        _build_summary_row(
            run_id=f"{prefix}-p1-r0",
            task_family=task_family,
            prompt_variant="P1",
            runtime_variant="R0",
            success=True,
            termination_reason="success",
            planner_calls=planner_base + 1,
            tool_calls=tool_base + 2,
            invalid_actions=0,
            retries=0,
            episode_time_s=episode_time_base + 0.2,
        ),
        _build_summary_row(
            run_id=f"{prefix}-p1-r1",
            task_family=task_family,
            prompt_variant="P1",
            runtime_variant="R1",
            success=True,
            termination_reason="success",
            planner_calls=planner_base + 1,
            tool_calls=tool_base + 2,
            invalid_actions=0,
            retries=0,
            episode_time_s=episode_time_base + 0.2,
        ),
        _build_summary_row(
            run_id=f"{prefix}-p2-r0",
            task_family=task_family,
            prompt_variant="P2",
            runtime_variant="R0",
            success=True,
            termination_reason="success",
            planner_calls=planner_base,
            tool_calls=tool_base + 1,
            invalid_actions=0,
            retries=0,
            episode_time_s=episode_time_base + 0.15,
        ),
        _build_summary_row(
            run_id=f"{prefix}-p2-r1",
            task_family=task_family,
            prompt_variant="P2",
            runtime_variant="R1",
            success=True,
            termination_reason="success",
            planner_calls=planner_base,
            tool_calls=tool_base + 1,
            invalid_actions=0,
            retries=0,
            episode_time_s=episode_time_base + 0.15,
        ),
    ]


class BlockAMasterSummaryTest(unittest.TestCase):
    def test_library_builds_master_summary_outputs_and_answers(self) -> None:
        from isaacsim_agent.eval import summarize_block_a_master_processed_dirs

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            navigation_pilot_dir = temp_path / "navigation_pilot"
            navigation_expanded_dir = temp_path / "navigation_expanded"
            manipulation_pilot_dir = temp_path / "manipulation_pilot"
            cross_family_dir = temp_path / "cross_family"
            navigation_robustness_dir = temp_path / "navigation_robustness"
            output_dir = temp_path / "processed" / "block_a_master_summary"

            _write_processed_input(
                navigation_pilot_dir,
                _build_source_rows(
                    prefix="nav-pilot",
                    task_family="navigation",
                    planner_base=4,
                    tool_base=3,
                    episode_time_base=1.0,
                ),
            )
            _write_processed_input(
                navigation_expanded_dir,
                _build_source_rows(
                    prefix="nav-expanded",
                    task_family="navigation",
                    planner_base=5,
                    tool_base=4,
                    episode_time_base=1.2,
                ),
            )
            _write_processed_input(
                manipulation_pilot_dir,
                _build_source_rows(
                    prefix="pick-pilot",
                    task_family="pick_place",
                    planner_base=8,
                    tool_base=7,
                    episode_time_base=1.4,
                ),
            )
            _write_processed_input(
                navigation_robustness_dir,
                _build_source_rows(
                    prefix="nav-robust",
                    task_family="navigation",
                    planner_base=7,
                    tool_base=6,
                    episode_time_base=1.6,
                ),
            )
            _write_cross_family_reference(cross_family_dir)

            result = summarize_block_a_master_processed_dirs(
                navigation_pilot_dir=navigation_pilot_dir,
                navigation_expanded_dir=navigation_expanded_dir,
                manipulation_pilot_dir=manipulation_pilot_dir,
                cross_family_dir=cross_family_dir,
                navigation_robustness_dir=navigation_robustness_dir,
                output_dir=output_dir,
            )

            self.assertEqual(result.bundle.aggregate.total_runs, 24)
            self.assertEqual(result.bundle.aggregate.run_complete_runs, 24)
            self.assertEqual(result.bundle.aggregate.successful_runs, 20)

            self.assertTrue((output_dir / "run_summary.jsonl").is_file())
            self.assertTrue((output_dir / "run_summary.csv").is_file())
            self.assertTrue((output_dir / "aggregate.json").is_file())
            self.assertTrue((output_dir / "validation.json").is_file())
            self.assertTrue((output_dir / "block_a_master_summary.json").is_file())
            self.assertTrue((output_dir / "block_a_master_summary.csv").is_file())
            self.assertTrue((output_dir / "block_a_master_summary.md").is_file())

            summary_payload = json.loads((output_dir / "block_a_master_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary_payload["overall"]["merged_runs"], 24)
            self.assertEqual(len(summary_payload["processed_sources"]), 4)
            self.assertEqual(len(summary_payload["reference_summaries"]), 1)
            self.assertEqual(len(summary_payload["group_by_task_family_difficulty_prompt_runtime"]), 18)
            self.assertEqual(len(summary_payload["coverage"]), 3)

            nav_easy_p0_r0 = next(
                row
                for row in summary_payload["group_by_task_family_difficulty_prompt_runtime"]
                if row["task_family"] == "navigation"
                and row["task_difficulty"] == "easy"
                and row["prompt_variant"] == "P0"
                and row["runtime_variant"] == "R0"
            )
            self.assertEqual(nav_easy_p0_r0["run_count"], 2)
            self.assertEqual(nav_easy_p0_r0["success_rate"], 0.0)
            self.assertEqual(nav_easy_p0_r0["total_invalid_actions"], 2)

            pick_easy_p2_r0 = next(
                row
                for row in summary_payload["group_by_task_family_difficulty_prompt_runtime"]
                if row["task_family"] == "manipulation"
                and row["task_difficulty"] == "easy"
                and row["prompt_variant"] == "P2"
                and row["runtime_variant"] == "R0"
            )
            self.assertEqual(pick_easy_p2_r0["run_count"], 1)
            self.assertEqual(pick_easy_p2_r0["success_rate"], 1.0)
            self.assertEqual(pick_easy_p2_r0["average_planner_calls"], 8.0)
            self.assertEqual(pick_easy_p2_r0["average_tool_calls"], 8.0)

            self.assertIn("main_success_table", summary_payload["tables"])
            self.assertIn("invalid_action_table", summary_payload["tables"])
            self.assertIn("efficiency_table", summary_payload["tables"])
            self.assertIn("recovery_table", summary_payload["tables"])
            self.assertIn("difficulty_comparison_table", summary_payload["tables"])

            self.assertIn("q1_main_effect_stable", summary_payload["answers"])
            self.assertTrue(summary_payload["answers"]["q1_main_effect_stable"]["answer"])
            self.assertTrue(summary_payload["answers"]["q2_cross_family_trends"]["answer"])
            self.assertTrue(summary_payload["answers"]["q3_harder_navigation_changes_conclusion"]["answer"])
            self.assertFalse(summary_payload["answers"]["q4_manipulation_harder_slice_necessary"]["answer"])
            self.assertEqual(
                summary_payload["answers"]["q5_next_step"]["answer"],
                "paper_block_a_cleanup",
            )

            with (output_dir / "block_a_master_summary.csv").open("r", encoding="utf-8", newline="") as handle:
                csv_rows = list(csv.DictReader(handle))
            self.assertEqual(len(csv_rows), 18)
            csv_pick_row = next(
                row
                for row in csv_rows
                if row["task_family"] == "manipulation"
                and row["task_difficulty"] == "easy"
                and row["prompt_variant"] == "P0"
                and row["runtime_variant"] == "R1"
            )
            self.assertEqual(csv_pick_row["run_count"], "1")
            self.assertEqual(csv_pick_row["success_rate"], "1.0")
            self.assertEqual(csv_pick_row["recovery_success_rate"], "1.0")

            markdown_summary = (output_dir / "block_a_master_summary.md").read_text(encoding="utf-8")
            self.assertIn("# Block A Master Summary", markdown_summary)
            self.assertIn("Block A 的主效应是否已经稳定成立？", markdown_summary)
            self.assertIn("## Table 1: Main Success", markdown_summary)
            self.assertIn("## Table 2: Invalid Actions", markdown_summary)
            self.assertIn("## Table 3: Efficiency", markdown_summary)
            self.assertIn("## Table 4: Recovery", markdown_summary)
            self.assertIn("## Table 5: Difficulty Comparison", markdown_summary)

    def test_cli_smoke_writes_master_summary_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            navigation_pilot_dir = temp_path / "navigation_pilot"
            navigation_expanded_dir = temp_path / "navigation_expanded"
            manipulation_pilot_dir = temp_path / "manipulation_pilot"
            cross_family_dir = temp_path / "cross_family"
            navigation_robustness_dir = temp_path / "navigation_robustness"
            output_dir = temp_path / "processed" / "block_a_master_summary"

            _write_processed_input(
                navigation_pilot_dir,
                _build_source_rows(
                    prefix="nav-pilot-cli",
                    task_family="navigation",
                    planner_base=4,
                    tool_base=3,
                    episode_time_base=1.0,
                ),
            )
            _write_processed_input(
                navigation_expanded_dir,
                _build_source_rows(
                    prefix="nav-expanded-cli",
                    task_family="navigation",
                    planner_base=5,
                    tool_base=4,
                    episode_time_base=1.2,
                ),
            )
            _write_processed_input(
                manipulation_pilot_dir,
                _build_source_rows(
                    prefix="pick-pilot-cli",
                    task_family="pick_place",
                    planner_base=8,
                    tool_base=7,
                    episode_time_base=1.4,
                ),
            )
            _write_processed_input(
                navigation_robustness_dir,
                _build_source_rows(
                    prefix="nav-robust-cli",
                    task_family="navigation",
                    planner_base=7,
                    tool_base=6,
                    episode_time_base=1.6,
                ),
            )
            _write_cross_family_reference(cross_family_dir)

            command = [
                sys.executable,
                str(MASTER_SCRIPT),
                "--navigation-pilot-dir",
                str(navigation_pilot_dir),
                "--navigation-expanded-dir",
                str(navigation_expanded_dir),
                "--manipulation-pilot-dir",
                str(manipulation_pilot_dir),
                "--cross-family-dir",
                str(cross_family_dir),
                "--navigation-robustness-dir",
                str(navigation_robustness_dir),
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
            self.assertIn("Merged runs: 24", combined_output)
            self.assertIn("Master Summary JSON:", combined_output)
            self.assertTrue((output_dir / "block_a_master_summary.json").is_file())
            self.assertTrue((output_dir / "block_a_master_summary.csv").is_file())
            self.assertTrue((output_dir / "block_a_master_summary.md").is_file())


if __name__ == "__main__":
    unittest.main()
