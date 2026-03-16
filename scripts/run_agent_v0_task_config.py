#!/usr/bin/env python3
"""Run one M4 agent runtime v0 episode from a serialized task config."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from isaacsim_agent.contracts import TaskConfig
from isaacsim_agent.planner import BlockAPilotPlannerBackend
from isaacsim_agent.planner import MockPlannerBackend
from isaacsim_agent.planner import PlannerConfig
from isaacsim_agent.runtime import AgentRuntimeConfig
from isaacsim_agent.runtime import run_and_write_agent_v0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one agent-runtime-v0 episode from task_config JSON.")
    parser.add_argument("--task-config", required=True, help="Path to a JSON-serialized TaskConfig payload.")
    parser.add_argument("--run-id", required=True, help="Concrete run identifier.")
    parser.add_argument("--results-root", required=True, help="Root directory for canonical run outputs.")
    parser.add_argument(
        "--planner-backend",
        choices=["mock_rule_based", "mock_block_a"],
        default="mock_rule_based",
        help="Planner backend to use for this run.",
    )
    parser.add_argument("--runtime-policy", required=True, help="Runtime policy label recorded in run artifacts.")
    parser.add_argument(
        "--validation-enabled",
        choices=["true", "false"],
        default="true",
        help="Whether tool validation is enabled for this run.",
    )
    parser.add_argument(
        "--max-validation-retries",
        type=int,
        default=0,
        help="Maximum per-step validation retries.",
    )
    parser.add_argument(
        "--max-invalid-actions",
        type=int,
        default=1,
        help="Maximum invalid actions before termination.",
    )
    return parser


def _build_planner_backend(name: str):
    if name == "mock_rule_based":
        return MockPlannerBackend(planner_name=name)
    if name == "mock_block_a":
        return BlockAPilotPlannerBackend(planner_name=name)
    raise ValueError(f"unsupported planner backend: {name}")


def main() -> int:
    args = build_parser().parse_args()
    task_config_path = Path(args.task_config)
    payload = json.loads(task_config_path.read_text(encoding="utf-8"))
    config = TaskConfig.from_dict(payload)

    planner_backend = _build_planner_backend(args.planner_backend)
    runtime_config = AgentRuntimeConfig(
        planner_config=PlannerConfig(backend=args.planner_backend),
        policy_name=args.runtime_policy,
        validation_enabled=args.validation_enabled == "true",
        max_validation_retries=args.max_validation_retries,
        max_invalid_actions=args.max_invalid_actions,
    )

    run_data, layout = run_and_write_agent_v0(
        config=config,
        run_id=args.run_id,
        results_root=args.results_root,
        planner_backend=planner_backend,
        runtime_config=runtime_config,
    )

    print("Run directory:", layout.run_dir)
    print("Run id:", args.run_id)
    print("Backend:", run_data.result.metrics.get("navigation.backend"))
    print("Termination:", run_data.result.termination_reason.value)
    print("Success:", run_data.result.success)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
