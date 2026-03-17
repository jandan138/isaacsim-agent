#!/usr/bin/env python3
"""Build the unified Block A final closure summary from processed Block A outputs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from isaacsim_agent.eval import summarize_block_a_final_closure_processed_dirs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the Block A final closure summary from processed Block A outputs.",
    )
    parser.add_argument(
        "--master-summary-dir",
        default="results/processed/block_a_master_summary",
        help="Processed Block A master summary directory containing run_summary.jsonl, validation.json, and block_a_master_summary.json.",
    )
    parser.add_argument(
        "--runtime-only-dir",
        default="results/processed/block_a_runtime_only_ablation",
        help="Processed runtime-only ablation directory.",
    )
    parser.add_argument(
        "--prompt-only-dir",
        default="results/processed/block_a_prompt_only_ablation",
        help="Processed prompt-only ablation directory.",
    )
    parser.add_argument(
        "--manipulation-harder-dir",
        default="results/processed/block_a_manipulation_harder",
        help="Processed harder-manipulation directory.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/processed/block_a_final_closure",
        help="Output directory for the unified final closure summary artifacts.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = summarize_block_a_final_closure_processed_dirs(
        master_summary_dir=args.master_summary_dir,
        runtime_only_dir=args.runtime_only_dir,
        prompt_only_dir=args.prompt_only_dir,
        manipulation_harder_dir=args.manipulation_harder_dir,
        output_dir=args.output_dir,
    )

    print("Output dir:", result.output_dir.resolve())
    for source in result.processed_sources:
        print("Processed source:", source.source_name)
        print("Processed source dir:", source.input_dir.resolve())
        print("Processed source runs:", source.run_count)
        print("Processed source success rate:", source.success_rate)
    print("Merged runs:", result.bundle.aggregate.total_runs)
    print("Successful runs:", result.bundle.aggregate.successful_runs)
    print("Final Closure Summary JSON:", result.written_outputs["final_closure_summary_json"])
    print("Final Closure Summary CSV:", result.written_outputs["final_closure_summary_csv"])
    print("Final Closure Summary Markdown:", result.written_outputs["final_closure_summary_md"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
