# configs

Configuration files for runtime variants, task families, experiment sweeps, and paper-facing reproducibility settings live here as milestones land.

- `experiments/pilot/easy_navigation_minimal.yaml`: a 3-task x 2-prompt x 1-runtime post-M5 easy-navigation pilot matrix consumed by `scripts/run_suite.py`
- the current pilot configs are JSON-compatible YAML files so the repo can stay dependency-light before a real YAML parser is introduced in a later milestone
