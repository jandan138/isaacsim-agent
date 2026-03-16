# configs

Configuration files for runtime variants, task families, experiment sweeps, and paper-facing reproducibility settings live here as milestones land.

- `experiments/pilot/easy_navigation_minimal.yaml`: a 3-task x 2-prompt x 1-runtime post-M5 easy-navigation pilot matrix consumed by `scripts/run_suite.py`
- `experiments/block_a/navigation_prompt_runtime_pilot.yaml`: a 3-task x 3-prompt x 2-runtime M6 block A pilot subset that keeps navigation-only scope and writes `block_a_pilot_summary.{json,md}`
- `experiments/block_a/navigation_prompt_runtime_expanded.yaml`: an 8-task x 3-prompt x 2-runtime M6 block A navigation-only expansion with 6 toy tasks plus a 2-task Isaac-backed slice, writing `block_a_summary.{json,md}`
- the current pilot configs are JSON-compatible YAML files so the repo can stay dependency-light before a real YAML parser is introduced in a later milestone
