"""Configuration module for debate system."""

from .debate_formats import (
    DEBATE_FORMATS,
    get_available_formats,
    get_debate_format,
    get_format_description,
    get_system_prompt_for_role,
)
from .settings import DebateSettings, settings

__all__ = [
    "DEBATE_FORMATS",
    "DebateSettings",
    "get_available_formats",
    "get_debate_format",
    "get_format_description",
    "get_system_prompt_for_role",
    "settings",
]