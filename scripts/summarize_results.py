#!/usr/bin/env python3
"""Summarize and validate canonical run artifacts for the M5 eval harness."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from isaacsim_agent.eval import summarize_results_root
from isaacsim_agent.eval import write_summary_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize or validate run outputs under a results root.")
    subparsers = parser.add_subparsers(dest="command", required=False)

    summarize_parser = subparsers.add_parser(
        "summarize",
        help="Scan runs, validate them, and write summary outputs.",
    )
    _add_common_arguments(summarize_parser)
    summarize_parser.add_argument(
        "--jsonl-only",
        action="store_true",
        help="Write only JSONL summary output plus aggregate/validation JSON files.",
    )
    summarize_parser.add_argument(
        "--csv-only",
        action="store_true",
        help="Write only CSV summary output plus aggregate/validation JSON files.",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate runs and return a non-zero exit code when any run is incomplete.",
    )
    _add_common_arguments(validate_parser)

    return parser


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--results-root",
        default="results",
        help="Results root containing `runs/` or a direct `runs/` directory.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for summary artifacts. Defaults to `<results-root>/processed/summary`.",
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    command = args.command or "summarize"

    bundle = summarize_results_root(args.results_root)
    output_dir = Path(args.output_dir) if args.output_dir else _default_output_dir(args.results_root)

    jsonl_only = getattr(args, "jsonl_only", False)
    csv_only = getattr(args, "csv_only", False)
    write_jsonl = command == "validate" or not csv_only
    write_csv = command == "validate" or not jsonl_only
    if jsonl_only and csv_only:
        parser.error("--jsonl-only and --csv-only cannot be used together")

    written = write_summary_outputs(
        bundle=bundle,
        output_dir=output_dir,
        write_jsonl=write_jsonl,
        write_csv=write_csv,
    )

    print("Results root:", Path(args.results_root).resolve())
    print("Runs scanned:", bundle.aggregate.total_runs)
    print("Contract-complete runs:", bundle.aggregate.contract_complete_runs)
    print("Run-complete runs:", bundle.aggregate.run_complete_runs)
    print("Successful runs:", bundle.aggregate.successful_runs)
    print("Bad runs:", bundle.aggregate.bad_runs)

    if "summary_jsonl" in written:
        print("Summary JSONL:", written["summary_jsonl"])
    if "summary_csv" in written:
        print("Summary CSV:", written["summary_csv"])
    print("Aggregate JSON:", written["aggregate_json"])
    print("Validation JSON:", written["validation_json"])

    if command == "validate":
        incomplete_runs = [summary.run_id for summary in bundle.summaries if not summary.run_complete]
        if incomplete_runs:
            print("Incomplete runs:", ", ".join(incomplete_runs))
            return 1
    return 0


def _default_output_dir(results_root: str | Path) -> Path:
    results_root = Path(results_root)
    if results_root.name == "runs":
        return results_root.parent / "processed" / "summary"
    return results_root / "processed" / "summary"


if __name__ == "__main__":
    raise SystemExit(main())
