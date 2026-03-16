#!/usr/bin/env python3
"""Build the unified Block A master checkpoint from existing processed summaries."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from isaacsim_agent.eval import summarize_block_a_master_processed_dirs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the Block A master checkpoint summary from processed Block A outputs.",
    )
    parser.add_argument(
        "--navigation-pilot-dir",
        default="results/processed/block_a_navigation_prompt_runtime_pilot",
        help="Processed easy-navigation pilot directory containing run_summary.jsonl and validation.json.",
    )
    parser.add_argument(
        "--navigation-expanded-dir",
        default="results/processed/block_a_navigation_prompt_runtime_expanded",
        help="Processed navigation expanded directory containing run_summary.jsonl and validation.json.",
    )
    parser.add_argument(
        "--manipulation-pilot-dir",
        default="results/processed/block_a_manipulation_prompt_runtime_pilot",
        help="Processed manipulation pilot directory containing run_summary.jsonl and validation.json.",
    )
    parser.add_argument(
        "--cross-family-dir",
        default="results/processed/block_a_cross_family_summary",
        help="Processed cross-family directory containing cross_family_summary.json.",
    )
    parser.add_argument(
        "--navigation-robustness-dir",
        default="results/processed/block_a_navigation_prompt_runtime_robustness",
        help="Processed navigation robustness directory containing run_summary.jsonl and validation.json.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/processed/block_a_master_summary",
        help="Output directory for the merged Block A master checkpoint artifacts.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = summarize_block_a_master_processed_dirs(
        navigation_pilot_dir=args.navigation_pilot_dir,
        navigation_expanded_dir=args.navigation_expanded_dir,
        manipulation_pilot_dir=args.manipulation_pilot_dir,
        cross_family_dir=args.cross_family_dir,
        navigation_robustness_dir=args.navigation_robustness_dir,
        output_dir=args.output_dir,
    )

    print("Output dir:", result.output_dir.resolve())
    for source in result.processed_sources:
        print("Processed source:", source.source_slice)
        print("Processed source dir:", source.input_dir.resolve())
        print("Processed source runs:", source.run_count)
        print("Processed source difficulty:", source.task_difficulty)
    for reference in result.reference_summaries:
        print("Reference summary:", reference.source_name)
        print("Reference summary dir:", reference.input_dir.resolve())
        print("Reference summary cells:", reference.prompt_runtime_cell_count)
    print("Merged runs:", result.bundle.aggregate.total_runs)
    print("Run-complete runs:", result.bundle.aggregate.run_complete_runs)
    print("Successful runs:", result.bundle.aggregate.successful_runs)
    print("Master Summary JSON:", result.written_outputs["master_summary_json"])
    print("Master Summary CSV:", result.written_outputs["master_summary_csv"])
    print("Master Summary Markdown:", result.written_outputs["master_summary_md"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
