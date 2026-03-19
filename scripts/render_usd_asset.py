#!/usr/bin/env python3
"""Placeholder CLI for the later external-USD render flow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PHASE2_NOT_IMPLEMENTED_EXIT = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render one external USD asset (phase 2 placeholder).")
    parser.add_argument("--usd-path", required=True, help="Path to the USD or USDA asset to render.")
    parser.add_argument("--output-dir", required=True, help="Directory where rendered outputs would be written.")
    parser.add_argument("--width", type=int, default=1280, help="Requested output width in pixels.")
    parser.add_argument("--height", type=int, default=720, help="Requested output height in pixels.")
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Launch the future render path headless. Use --no-headless for local debugging.",
    )
    parser.add_argument("--skip-existing", action="store_true", help="Skip work if the requested outputs exist.")
    parser.add_argument("--save-stage", action="store_true", help="Request stage export alongside PNG output.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    usd_path = Path(args.usd_path)
    output_dir = Path(args.output_dir)

    print("USD path:", usd_path)
    print("Output directory:", output_dir)
    print(
        "PHASE2_NOT_IMPLEMENTED: external USD asset rendering is reserved for the second implementation phase.",
        file=sys.stderr,
    )
    return PHASE2_NOT_IMPLEMENTED_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
