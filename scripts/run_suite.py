#!/usr/bin/env python3
"""Run a minimal config-driven easy pilot suite on top of the M4/M5 paths."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from isaacsim_agent.experiments import run_pilot_suite


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the minimal post-M5 pilot suite.")
    parser.add_argument(
        "--config",
        required=True,
        help="Pilot experiment config file under configs/experiments/pilot/ or another compatible path.",
    )
    parser.add_argument(
        "--results-root",
        default=None,
        help="Results root for canonical run artifacts. Defaults to the config value or results/pilot/<experiment>.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Processed output directory for summary artifacts. Defaults to <results-root>/processed/<experiment>.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run_pilot_suite(
        config_path=args.config,
        results_root=args.results_root,
        output_dir=args.output_dir,
    )

    print("Config:", result.config_path.resolve())
    print("Experiment:", result.config.experiment_name)
    print("Results root:", result.results_root.resolve())
    print("Output dir:", result.output_dir.resolve())
    print("Planned runs:", len(result.planned_runs))
    print("Runs scanned:", result.bundle.aggregate.total_runs)
    print("Contract-complete runs:", result.bundle.aggregate.contract_complete_runs)
    print("Run-complete runs:", result.bundle.aggregate.run_complete_runs)
    print("Successful runs:", result.bundle.aggregate.successful_runs)
    print("Run plan:", result.run_plan_path)
    if "summary_jsonl" in result.written_outputs:
        print("Summary JSONL:", result.written_outputs["summary_jsonl"])
    if "summary_csv" in result.written_outputs:
        print("Summary CSV:", result.written_outputs["summary_csv"])
    print("Aggregate JSON:", result.written_outputs["aggregate_json"])
    print("Validation JSON:", result.written_outputs["validation_json"])
    print("Pilot summary JSON:", result.pilot_summary_json_path)
    print("Pilot summary Markdown:", result.pilot_summary_md_path)

    missing_run_ids = result.pilot_summary["missing_run_ids"]
    if missing_run_ids:
        print("Missing runs:", ", ".join(missing_run_ids))
        return 1

    incomplete_runs = [summary.run_id for summary in result.bundle.summaries if not summary.run_complete]
    if incomplete_runs:
        print("Incomplete runs:", ", ".join(incomplete_runs))
        return 1

    unsuccessful_runs = [summary.run_id for summary in result.bundle.summaries if summary.success is False]
    if unsuccessful_runs:
        print("Unsuccessful runs:", ", ".join(unsuccessful_runs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
