#!/usr/bin/env python3
"""Package the existing Block A master summary into paper-facing assets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from isaacsim_agent.eval import package_block_a_master_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package the existing Block A master summary into paper-facing tables, figures, and analysis.",
    )
    parser.add_argument(
        "--master-summary-path",
        "--master-summary-json",
        dest="master_summary_path",
        default="results/processed/block_a_master_summary/block_a_master_summary.json",
        help="Path to the existing Block A master summary JSON.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/processed/block_a_master_summary",
        help="Output directory that will receive paper_tables/, paper_figures/, and analysis/.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = package_block_a_master_summary(
        master_summary_path=args.master_summary_path,
        output_dir=args.output_dir,
    )

    print("Output dir:", result.output_dir.resolve())
    print("Master Summary JSON:", result.master_summary_json_path.resolve())
    print("Paper Tables Dir:", result.paper_tables_dir.resolve())
    print("Paper Figures Dir:", result.paper_figures_dir.resolve())
    print("Analysis Dir:", result.analysis_dir.resolve())
    print("Covered master cells:", result.consistency_checks["covered_master_cells"])
    print("Missing cohorts:", ",".join(result.consistency_checks["missing_cohorts"]))
    print("Table consistency checks:", result.validation["table_validation"]["checks"])
    print("Figure consistency checks:", result.validation["figure_validation"]["checks"])
    print("All consistency checks passed:", result.validation["all_consistent"])
    for key in sorted(result.written_outputs):
        print(f"{key}: {result.written_outputs[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
