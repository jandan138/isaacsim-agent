"""Minimal prompt-variant helpers for the M6 block A pilot."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PromptVariantDefinition:
    """One prompting variant used by the block A pilot subset."""

    variant_id: str
    response_format: str
    uses_explicit_tool_json: bool
    requires_self_check: bool


_PROMPT_VARIANTS: dict[str, PromptVariantDefinition] = {
    "P0": PromptVariantDefinition(
        variant_id="P0",
        response_format="direct_action_json",
        uses_explicit_tool_json=False,
        requires_self_check=False,
    ),
    "P1": PromptVariantDefinition(
        variant_id="P1",
        response_format="tool_json",
        uses_explicit_tool_json=True,
        requires_self_check=False,
    ),
    "P2": PromptVariantDefinition(
        variant_id="P2",
        response_format="tool_json_with_self_check",
        uses_explicit_tool_json=True,
        requires_self_check=True,
    ),
}


def normalize_prompt_variant(variant_id: str | None) -> str:
    """Normalize possibly-missing prompt variant identifiers."""

    if isinstance(variant_id, str):
        normalized = variant_id.strip().upper()
        if normalized in _PROMPT_VARIANTS:
            return normalized
    return "P0"


def prompt_variant_definition(variant_id: str | None) -> PromptVariantDefinition:
    """Return the canonical definition for one prompt variant."""

    return _PROMPT_VARIANTS[normalize_prompt_variant(variant_id)]


def render_prompt_template(instruction_template: str, values: dict[str, Any]) -> str:
    """Render one prompt template with best-effort formatting."""

    try:
        return instruction_template.format(**values)
    except (KeyError, ValueError):
        return instruction_template


def build_retry_instruction(
    base_instruction: str,
    validation_error: str,
    repair_instruction_template: str | None = None,
) -> str:
    """Append a short explicit repair instruction for one retry."""

    template = repair_instruction_template or (
        "Repair the previous step. Return one valid JSON action only.\n"
        "Previous validation error: {validation_error}"
    )
    repair_text = render_prompt_template(
        template,
        {"validation_error": validation_error.strip() or "the previous action was invalid"},
    ).strip()
    return f"{base_instruction.rstrip()}\n{repair_text}"
