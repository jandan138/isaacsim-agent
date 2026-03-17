#!/usr/bin/env python3
"""Generate RA-L paper assets from the frozen Block A summaries."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from isaacsim_agent.eval import package_block_a_ral_assets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate RA-L figure/table assets from the frozen Block A summaries.",
    )
    parser.add_argument(
        "--final-closure-summary-path",
        default="results/processed/block_a_final_closure/block_a_final_closure_summary.json",
    )
    parser.add_argument(
        "--master-summary-path",
        default="results/processed/block_a_master_summary/block_a_master_summary.json",
    )
    parser.add_argument(
        "--prompt-only-summary-path",
        default="results/processed/block_a_prompt_only_ablation/block_a_prompt_only_summary.json",
    )
    parser.add_argument(
        "--runtime-only-summary-path",
        default="results/processed/block_a_runtime_only_ablation/block_a_runtime_only_summary.json",
    )
    parser.add_argument(
        "--manipulation-harder-summary-path",
        default="results/processed/block_a_manipulation_harder/block_a_manipulation_harder_summary.json",
    )
    parser.add_argument(
        "--cross-family-summary-path",
        default="results/processed/block_a_cross_family_summary/cross_family_summary.json",
    )
    parser.add_argument(
        "--output-dir",
        default="paper/versions/ral",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = package_block_a_ral_assets(
        final_closure_summary_path=args.final_closure_summary_path,
        master_summary_path=args.master_summary_path,
        prompt_only_summary_path=args.prompt_only_summary_path,
        runtime_only_summary_path=args.runtime_only_summary_path,
        manipulation_harder_summary_path=args.manipulation_harder_summary_path,
        cross_family_summary_path=args.cross_family_summary_path,
        output_dir=args.output_dir,
    )
    print("Output dir:", result.output_dir.resolve())
    print("Figures dir:", result.figures_dir.resolve())
    print("Tables dir:", result.tables_dir.resolve())
    for key in sorted(result.validation):
        print(f"{key}: {result.validation[key]}")
    for key in sorted(result.written_outputs):
        print(f"{key}: {result.written_outputs[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
