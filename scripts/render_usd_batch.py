#!/usr/bin/env python3
"""Placeholder CLI for the later batch external-USD render flow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PHASE2_NOT_IMPLEMENTED_EXIT = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render a batch of external USD assets (phase 2 placeholder).")
    parser.add_argument("--input-root", required=True, help="Root directory containing USD assets.")
    parser.add_argument("--output-root", required=True, help="Directory where rendered outputs would be written.")
    parser.add_argument(
        "--glob",
        default="**/*.usd*",
        help="Glob pattern used to discover USD assets under the input root.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional cap on the number of assets to visit.")
    parser.add_argument("--skip-existing", action="store_true", help="Skip assets whose outputs already exist.")
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Launch the future render path headless. Use --no-headless for local debugging.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_root = Path(args.input_root)
    output_root = Path(args.output_root)

    print("Input root:", input_root)
    print("Output root:", output_root)
    print(
        "PHASE2_NOT_IMPLEMENTED: external USD batch rendering is reserved for the second implementation phase.",
        file=sys.stderr,
    )
    return PHASE2_NOT_IMPLEMENTED_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
