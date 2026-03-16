#!/usr/bin/env python3
"""Merge existing processed block A summaries into one cross-family report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from isaacsim_agent.eval import summarize_cross_family_processed_dirs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the block A cross-family summary from existing processed summaries.",
    )
    parser.add_argument(
        "--navigation-dir",
        default="results/processed/block_a_navigation_prompt_runtime_expanded",
        help="Processed navigation summary directory containing run_summary.jsonl and validation.json.",
    )
    parser.add_argument(
        "--manipulation-dir",
        default="results/processed/block_a_manipulation_prompt_runtime_pilot",
        help="Processed manipulation summary directory containing run_summary.jsonl and validation.json.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/processed/block_a_cross_family_summary",
        help="Output directory for merged run summaries and cross-family summary artifacts.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = summarize_cross_family_processed_dirs(
        input_dirs=[args.navigation_dir, args.manipulation_dir],
        output_dir=args.output_dir,
    )

    print("Output dir:", result.output_dir.resolve())
    for index, source in enumerate(result.sources, start=1):
        print(f"Input {index}:", source.input_dir.resolve())
        print(f"Input {index} runs:", source.run_count)
        print(f"Input {index} task families:", ",".join(source.task_families))
    print("Merged runs:", result.bundle.aggregate.total_runs)
    print("Run-complete runs:", result.bundle.aggregate.run_complete_runs)
    print("Successful runs:", result.bundle.aggregate.successful_runs)
    print("Merged Summary JSONL:", result.written_outputs["summary_jsonl"])
    print("Merged Summary CSV:", result.written_outputs["summary_csv"])
    print("Aggregate JSON:", result.written_outputs["aggregate_json"])
    print("Validation JSON:", result.written_outputs["validation_json"])
    print("Cross-family Summary JSON:", result.written_outputs["cross_family_summary_json"])
    print("Cross-family Summary CSV:", result.written_outputs["cross_family_summary_csv"])
    print("Cross-family Summary Markdown:", result.written_outputs["cross_family_summary_md"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
