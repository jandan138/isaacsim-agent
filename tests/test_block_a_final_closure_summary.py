"""Coverage for the Block A final closure summary."""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_block_a_master_summary import _build_source_rows
from tests.test_block_a_master_summary import _build_summary_row
from tests.test_block_a_master_summary import _write_cross_family_reference
from tests.test_block_a_master_summary import _write_processed_input


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
CLOSURE_SCRIPT = REPO_ROOT / "scripts" / "summarize_block_a_final_closure.py"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _write_summary_payload(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _build_runtime_only_summary_payload() -> dict[str, object]:
    return {
        "summary_title": "Block A Runtime-Only Summary",
        "by_prompt_runtime": [
            {
                "prompt_variant": "P1",
                "runtime_variant": "R0",
                "run_count": 4,
                "successful_runs": 2,
                "success_rate": 0.5,
                "invalid_action_run_count": 2,
                "successful_invalid_action_runs": 0,
                "total_retries": 0,
            },
            {
                "prompt_variant": "P1",
                "runtime_variant": "R1",
                "run_count": 4,
                "successful_runs": 4,
                "success_rate": 1.0,
                "invalid_action_run_count": 2,
                "successful_invalid_action_runs": 2,
                "total_retries": 2,
            },
        ],
        "analysis": {
            "mode": "block_a_runtime_only_ablation",
            "questions": {
                "q1_runtime_has_independent_value": {"answer": True},
                "q2_value_concentrates_in_recovery": {"answer": True},
                "q3_cross_family_consistency": {"answer": True},
            },
            "findings": [
                "Under fixed prompt P1, runtime validation plus one retry improves outcomes over the bare runtime.",
            ],
        },
    }


def _build_prompt_only_summary_payload() -> dict[str, object]:
    return {
        "summary_title": "Block A Prompt-Only Summary",
        "by_prompt_runtime": [
            {
                "prompt_variant": "P0",
                "runtime_variant": "R0",
                "run_count": 4,
                "successful_runs": 0,
                "success_rate": 0.0,
                "total_invalid_actions": 4,
                "invalid_action_run_count": 4,
                "average_planner_calls": 1.0,
                "average_tool_calls": 0.0,
            },
            {
                "prompt_variant": "P1",
                "runtime_variant": "R0",
                "run_count": 4,
                "successful_runs": 4,
                "success_rate": 1.0,
                "total_invalid_actions": 0,
                "invalid_action_run_count": 0,
                "average_planner_calls": 6.5,
                "average_tool_calls": 6.0,
            },
            {
                "prompt_variant": "P2",
                "runtime_variant": "R0",
                "run_count": 4,
                "successful_runs": 4,
                "success_rate": 1.0,
                "total_invalid_actions": 0,
                "invalid_action_run_count": 0,
                "average_planner_calls": 5.5,
                "average_tool_calls": 5.0,
            },
        ],
        "analysis": {
            "mode": "block_a_prompt_only_ablation",
            "questions": {
                "q1_prompt_structure_reduces_invalid_actions": {"answer": True},
                "q2_p2_more_efficient_than_p1": {"answer": True},
                "q3_cross_family_consistency": {"answer": True},
            },
            "findings": [
                "With runtime fixed at R0, prompt structure independently lowers invalid actions.",
            ],
        },
    }


def _build_manipulation_harder_summary_payload(reference_path: Path) -> dict[str, object]:
    return {
        "summary_title": "Block A Manipulation Harder Summary",
        "reference_summary_path": str(reference_path),
        "by_prompt_runtime": [
            {
                "prompt_variant": "P0",
                "runtime_variant": "R0",
                "run_count": 3,
                "successful_runs": 0,
                "success_rate": 0.0,
            },
            {
                "prompt_variant": "P0",
                "runtime_variant": "R1",
                "run_count": 3,
                "successful_runs": 3,
                "success_rate": 1.0,
            },
            {
                "prompt_variant": "P1",
                "runtime_variant": "R0",
                "run_count": 3,
                "successful_runs": 3,
                "success_rate": 1.0,
                "average_planner_calls": 11.5,
                "average_tool_calls": 11.5,
            },
            {
                "prompt_variant": "P1",
                "runtime_variant": "R1",
                "run_count": 3,
                "successful_runs": 3,
                "success_rate": 1.0,
                "average_planner_calls": 11.5,
                "average_tool_calls": 11.5,
            },
            {
                "prompt_variant": "P2",
                "runtime_variant": "R0",
                "run_count": 3,
                "successful_runs": 3,
                "success_rate": 1.0,
                "average_planner_calls": 9.5,
                "average_tool_calls": 9.5,
            },
            {
                "prompt_variant": "P2",
                "runtime_variant": "R1",
                "run_count": 3,
                "successful_runs": 3,
                "success_rate": 1.0,
                "average_planner_calls": 9.5,
                "average_tool_calls": 9.5,
            },
        ],
        "analysis": {
            "mode": "block_a_manipulation_harder",
            "reference_summary_path": str(reference_path),
            "questions": {
                "q1_p0_r0_worst": {"answer": True},
                "q2_r1_recovers_p0": {"answer": True},
                "q3_p1_p2_success": {"answer": True},
                "q4_p2_more_efficient_than_p1": {"answer": True},
                "q5_harder_tasks_amplify_differences": {
                    "answer": True,
                    "reference_summary_path": str(reference_path),
                    "details": [
                        "P0/R1 planner/tool `9.0`/`8.0` -> `10.5`/`9.5`",
                        "P1/R0 planner/tool `10.0`/`10.0` -> `11.5`/`11.5`",
                        "P2/R0 planner/tool `8.0`/`8.0` -> `9.5`/`9.5`",
                    ],
                },
            },
            "findings": [
                "Relative to the easy manipulation pilot, the harder manipulation slice increases planner/tool overhead while preserving the same qualitative ordering.",
            ],
        },
    }


def _stage_final_closure_inputs(temp_path: Path) -> tuple[Path, Path, Path, Path, Path]:
    from isaacsim_agent.eval import summarize_block_a_master_processed_dirs

    navigation_pilot_dir = temp_path / "navigation_pilot"
    navigation_expanded_dir = temp_path / "navigation_expanded"
    manipulation_pilot_dir = temp_path / "manipulation_pilot"
    cross_family_dir = temp_path / "cross_family"
    navigation_robustness_dir = temp_path / "navigation_robustness"
    master_output_dir = temp_path / "block_a_master_summary"

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
            prefix="manip-pilot",
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

    summarize_block_a_master_processed_dirs(
        navigation_pilot_dir=navigation_pilot_dir,
        navigation_expanded_dir=navigation_expanded_dir,
        manipulation_pilot_dir=manipulation_pilot_dir,
        cross_family_dir=cross_family_dir,
        navigation_robustness_dir=navigation_robustness_dir,
        output_dir=master_output_dir,
    )

    runtime_only_dir = temp_path / "runtime_only"
    runtime_rows = [
        _build_summary_row(
            run_id="runtime-nav-p1-r0",
            task_family="navigation",
            prompt_variant="P1",
            runtime_variant="R0",
            success=False,
            termination_reason="invalid_action_limit",
            planner_calls=1,
            tool_calls=0,
            invalid_actions=1,
            retries=0,
            episode_time_s=1.0,
        ),
        _build_summary_row(
            run_id="runtime-nav-p1-r1",
            task_family="navigation",
            prompt_variant="P1",
            runtime_variant="R1",
            success=True,
            termination_reason="success",
            planner_calls=4,
            tool_calls=3,
            invalid_actions=1,
            retries=1,
            episode_time_s=1.1,
        ),
        _build_summary_row(
            run_id="runtime-pick-p1-r0",
            task_family="pick_place",
            prompt_variant="P1",
            runtime_variant="R0",
            success=False,
            termination_reason="invalid_action_limit",
            planner_calls=1,
            tool_calls=0,
            invalid_actions=1,
            retries=0,
            episode_time_s=1.2,
        ),
        _build_summary_row(
            run_id="runtime-pick-p1-r1",
            task_family="pick_place",
            prompt_variant="P1",
            runtime_variant="R1",
            success=True,
            termination_reason="success",
            planner_calls=9,
            tool_calls=8,
            invalid_actions=1,
            retries=1,
            episode_time_s=1.3,
        ),
    ]
    _write_processed_input(runtime_only_dir, runtime_rows)
    _write_summary_payload(runtime_only_dir / "block_a_runtime_only_summary.json", _build_runtime_only_summary_payload())

    prompt_only_dir = temp_path / "prompt_only"
    prompt_rows = [
        _build_summary_row(
            run_id="prompt-nav-p0-r0",
            task_family="navigation",
            prompt_variant="P0",
            runtime_variant="R0",
            success=False,
            termination_reason="invalid_action_limit",
            planner_calls=1,
            tool_calls=0,
            invalid_actions=1,
            retries=0,
            episode_time_s=1.0,
        ),
        _build_summary_row(
            run_id="prompt-nav-p1-r0",
            task_family="navigation",
            prompt_variant="P1",
            runtime_variant="R0",
            success=True,
            termination_reason="success",
            planner_calls=4,
            tool_calls=3,
            invalid_actions=0,
            retries=0,
            episode_time_s=1.1,
        ),
        _build_summary_row(
            run_id="prompt-nav-p2-r0",
            task_family="navigation",
            prompt_variant="P2",
            runtime_variant="R0",
            success=True,
            termination_reason="success",
            planner_calls=3,
            tool_calls=2,
            invalid_actions=0,
            retries=0,
            episode_time_s=1.1,
        ),
        _build_summary_row(
            run_id="prompt-pick-p0-r0",
            task_family="pick_place",
            prompt_variant="P0",
            runtime_variant="R0",
            success=False,
            termination_reason="invalid_action_limit",
            planner_calls=1,
            tool_calls=0,
            invalid_actions=1,
            retries=0,
            episode_time_s=1.2,
        ),
        _build_summary_row(
            run_id="prompt-pick-p1-r0",
            task_family="pick_place",
            prompt_variant="P1",
            runtime_variant="R0",
            success=True,
            termination_reason="success",
            planner_calls=10,
            tool_calls=10,
            invalid_actions=0,
            retries=0,
            episode_time_s=1.3,
        ),
        _build_summary_row(
            run_id="prompt-pick-p2-r0",
            task_family="pick_place",
            prompt_variant="P2",
            runtime_variant="R0",
            success=True,
            termination_reason="success",
            planner_calls=8,
            tool_calls=8,
            invalid_actions=0,
            retries=0,
            episode_time_s=1.3,
        ),
    ]
    _write_processed_input(prompt_only_dir, prompt_rows)
    _write_summary_payload(prompt_only_dir / "block_a_prompt_only_summary.json", _build_prompt_only_summary_payload())

    manipulation_harder_dir = temp_path / "manipulation_harder"
    manipulation_rows = []
    for prompt_variant, runtime_variant, success, planner_calls, tool_calls, invalid_actions, retries in (
        ("P0", "R0", False, 1, 0, 1, 0),
        ("P0", "R1", True, 10, 9, 1, 1),
        ("P1", "R0", True, 12, 12, 0, 0),
        ("P1", "R1", True, 12, 12, 0, 0),
        ("P2", "R0", True, 10, 10, 0, 0),
        ("P2", "R1", True, 10, 10, 0, 0),
    ):
        manipulation_rows.append(
            _build_summary_row(
                run_id=f"manip-harder-{prompt_variant.lower()}-{runtime_variant.lower()}",
                task_family="pick_place",
                prompt_variant=prompt_variant,
                runtime_variant=runtime_variant,
                success=success,
                termination_reason="success" if success else "invalid_action_limit",
                planner_calls=planner_calls,
                tool_calls=tool_calls,
                invalid_actions=invalid_actions,
                retries=retries,
                episode_time_s=1.5,
            )
        )
    _write_processed_input(manipulation_harder_dir, manipulation_rows)
    _write_summary_payload(
        manipulation_harder_dir / "block_a_manipulation_harder_summary.json",
        _build_manipulation_harder_summary_payload(manipulation_pilot_dir / "block_a_summary.json"),
    )

    return master_output_dir, runtime_only_dir, prompt_only_dir, manipulation_harder_dir, temp_path / "closure_output"


class BlockAFinalClosureSummaryTest(unittest.TestCase):
    def test_build_final_closure_summary_outputs_answers(self) -> None:
        from isaacsim_agent.eval import summarize_block_a_final_closure_processed_dirs

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            master_dir, runtime_dir, prompt_dir, manipulation_dir, output_dir = _stage_final_closure_inputs(temp_path)

            result = summarize_block_a_final_closure_processed_dirs(
                master_summary_dir=master_dir,
                runtime_only_dir=runtime_dir,
                prompt_only_dir=prompt_dir,
                manipulation_harder_dir=manipulation_dir,
                output_dir=output_dir,
            )

            self.assertEqual(result.summary["summary_title"], "Block A Final Closure Summary")
            self.assertEqual(result.bundle.aggregate.total_runs, 40)
            self.assertEqual(len(result.summary["questions"]), 6)
            self.assertTrue(result.summary["closure_verdict"]["answer"])
            self.assertEqual(result.summary["closure_verdict"]["recommended_next_step"], "freeze_block_a_and_write_paper")

            question_map = {
                row["question_id"]: row
                for row in result.summary["questions"]
            }
            self.assertTrue(question_map["q1_main_effect_stable"]["answer"])
            self.assertTrue(question_map["q2_runtime_independent_value"]["answer"])
            self.assertTrue(question_map["q3_prompt_independent_value"]["answer"])
            self.assertTrue(question_map["q4_cross_family_consistency"]["answer"])
            self.assertTrue(question_map["q5_harder_cost_not_ordering"]["answer"])
            self.assertTrue(question_map["q6_block_a_closed_for_paper"]["answer"])

            self.assertTrue((output_dir / "block_a_final_closure_summary.json").is_file())
            self.assertTrue((output_dir / "block_a_final_closure_summary.csv").is_file())
            self.assertTrue((output_dir / "block_a_final_closure_summary.md").is_file())

            with (output_dir / "block_a_final_closure_summary.csv").open(encoding="utf-8") as handle:
                csv_rows = list(csv.DictReader(handle))
            self.assertEqual(len(csv_rows), 6)
            self.assertEqual(csv_rows[0]["question_id"], "q1_main_effect_stable")

            markdown_summary = (output_dir / "block_a_final_closure_summary.md").read_text(encoding="utf-8")
            self.assertIn("# Block A Final Closure Summary", markdown_summary)
            self.assertIn("1. Prompt × Runtime 的主效应是否已经稳定成立？", markdown_summary)
            self.assertIn("6. Block A 是否已实验封闭到足以单独支撑一整篇系统设计论文？", markdown_summary)

    def test_cli_wrapper_writes_final_closure_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            master_dir, runtime_dir, prompt_dir, manipulation_dir, output_dir = _stage_final_closure_inputs(temp_path)
            command = [
                sys.executable,
                str(CLOSURE_SCRIPT),
                "--master-summary-dir",
                str(master_dir),
                "--runtime-only-dir",
                str(runtime_dir),
                "--prompt-only-dir",
                str(prompt_dir),
                "--manipulation-harder-dir",
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
            self.assertIn("Merged runs: 40", combined_output)
            self.assertIn("Final Closure Summary JSON:", combined_output)
            self.assertTrue((output_dir / "block_a_final_closure_summary.json").is_file())
            self.assertTrue((output_dir / "block_a_final_closure_summary.csv").is_file())
            self.assertTrue((output_dir / "block_a_final_closure_summary.md").is_file())


if __name__ == "__main__":
    unittest.main()
