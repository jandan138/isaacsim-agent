# AGENTS.md

## Repo rules

- Read `plan.md` first on every run and treat it as the project source of truth.
- Read `STATUS.md` before changing files and update it at the end of the run.
- Work one milestone at a time; do not implement future milestones early.
- Keep diffs scoped, minimal, and honest about what is still a placeholder.
- Prefer lightweight validation first, then record the exact command and result in `STATUS.md`.
- Do not start heavy Isaac Sim, ROS, or experiment workflows unless the active milestone explicitly requires them.

## Structure conventions

- Put Python source under `src/isaacsim_agent/`.
- Keep simulator/runtime code separate from experiment orchestration and paper assets.
- Use `docs/` for setup and process notes, `scripts/` for runnable utilities, and `results/` for generated artifacts only.

## Handoff expectations

- If a task is blocked, document the blocker in `STATUS.md` instead of guessing.
- End each run with the next recommended sub-milestone.
