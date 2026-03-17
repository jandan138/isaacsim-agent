# configs

Configuration files for runtime variants, task families, experiment sweeps, and paper-facing reproducibility settings live here as milestones land.

- `experiments/pilot/easy_navigation_minimal.yaml`: a 3-task x 2-prompt x 1-runtime post-M5 easy-navigation pilot matrix consumed by `scripts/run_suite.py`
- `experiments/block_a/navigation_prompt_runtime_pilot.yaml`: a 3-task x 3-prompt x 2-runtime M6 block A pilot subset that keeps navigation-only scope and writes `block_a_pilot_summary.{json,md}`
- `experiments/block_a/navigation_prompt_runtime_expanded.yaml`: an 8-task x 3-prompt x 2-runtime M6 block A navigation-only expansion with 6 toy tasks plus a 2-task Isaac-backed slice, writing `block_a_summary.{json,md}`
- `experiments/block_a/runtime_only_ablation.yaml`: a 4-task mixed-family M6 Block A closure slice that fixes `P1`, compares `R0` vs `R1`, and writes `block_a_runtime_only_summary.{json,md}`
- `experiments/block_a/prompt_only_ablation.yaml`: a 4-task mixed-family M6 Block A closure slice that fixes `R0`, compares `P0/P1/P2`, and writes `block_a_prompt_only_summary.{json,md}`
- `experiments/block_a/manipulation_prompt_runtime_harder.yaml`: a 3-task manipulation-only M6 Block A closure slice with longer scripted transfer waypoint sequences, writing `block_a_manipulation_harder_summary.{json,md}`
- the current pilot configs are JSON-compatible YAML files so the repo can stay dependency-light before a real YAML parser is introduced in a later milestone
