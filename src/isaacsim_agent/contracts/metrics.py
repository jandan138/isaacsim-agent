"""Project-wide metrics contract definitions."""

from __future__ import annotations


ALWAYS_EXPECTED_EPISODE_METRICS: tuple[str, ...] = (
    "success",
    "termination_reason",
    "step_count",
    "elapsed_time_sec",
    "sim_time_sec",
    "invalid_action_count",
    "collision_count",
    "recovery_count",
    "tool_call_count",
    "planner_call_count",
)

OPTIONAL_EPISODE_METRICS: tuple[str, ...] = (
    "token_usage.prompt_tokens",
    "token_usage.completion_tokens",
    "token_usage.total_tokens",
    "token_usage.estimated_cost_usd",
    "planner_latency_sec",
    "notes",
)

TASK_SPECIFIC_METRICS: dict[str, tuple[str, ...]] = {
    "navigation": (
        "navigation.goal_reached",
        "navigation.final_goal_distance_m",
        "navigation.path_length_m",
        "navigation.waypoints_completed",
    ),
    "pick_place": (
        "pick_place.object_picked",
        "pick_place.object_placed",
        "pick_place.grasp_attempt_count",
        "pick_place.place_attempt_count",
    ),
    "instruction_following": (
        "instruction_following.instructions_completed",
        "instruction_following.subgoal_success_count",
        "instruction_following.constraint_violation_count",
    ),
}
