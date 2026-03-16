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

## Agent teaming

- Treat spawned sub-agents as potentially important work on the critical path; default to patient waiting rather than repeated polling or early interruption.
- When a sub-agent is running, prefer longer `wait` windows and avoid busy-loop checking unless the next action is truly blocked on its result.
- Use a soft-timeout check before intervening: first look for new output, status changes, stage-complete summaries, or an explicit blocker report.
- Do not interrupt a sub-agent just because it is slow. Intervene only after multiple wait windows pass with no new output or status change and the result is still blocking the main task.
- If intervention is needed, escalate in order: wait longer once, send one focused progress/blocker check, then interrupt or reassign only if the sub-agent still appears stalled.
- When a sub-agent is interrupted for suspected stall, record the reason in `STATUS.md`, including the wait duration, observed lack of progress, and the action taken.

## Handoff expectations

- If a task is blocked, document the blocker in `STATUS.md` instead of guessing.
- End each run with the next recommended sub-milestone.
