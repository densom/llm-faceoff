"""Debate format configurations."""

from typing import Any, Dict

DEBATE_FORMATS: Dict[str, Dict[str, Any]] = {
    "oxford": {
        "name": "Oxford Style",
        "description": "Traditional Oxford Union debate format",
        "structure": [
            {"type": "opening_statement", "duration": 300, "order": ["proposition", "opposition"]},
            {"type": "argument", "duration": 180, "rounds": 3},
            {"type": "rebuttal", "duration": 120, "rounds": 2},
            {"type": "closing_statement", "duration": 180, "order": ["opposition", "proposition"]},
        ],
        "rules": {
            "max_response_length": 1500,
            "time_limit_per_turn": 300,
            "allow_interruptions": False,
            "require_evidence": True,
        },
        "system_prompts": {
            "proposition": """You are participating in an Oxford-style debate arguing FOR the proposition.
Your role is to present strong, logical arguments supporting your position.
Structure your arguments clearly with evidence and reasoning.
Be respectful but assertive in your position.""",
            "opposition": """You are participating in an Oxford-style debate arguing AGAINST the proposition.
Your role is to present strong, logical arguments opposing the proposition.
Structure your arguments clearly with evidence and reasoning.
Be respectful but assertive in challenging the proposition.""",
        },
    },
    "lincoln_douglas": {
        "name": "Lincoln-Douglas",
        "description": "Value-based one-on-one debate format",
        "structure": [
            {"type": "opening_statement", "duration": 360, "order": ["proposition"]},
            {"type": "opening_statement", "duration": 420, "order": ["opposition"]},
            {"type": "rebuttal", "duration": 240, "order": ["proposition"]},
            {"type": "rebuttal", "duration": 480, "order": ["opposition"]},
            {"type": "rebuttal", "duration": 180, "order": ["proposition"]},
            {"type": "closing_statement", "duration": 180, "order": ["opposition"]},
        ],
        "rules": {
            "max_response_length": 2000,
            "time_limit_per_turn": 480,
            "focus_on_values": True,
            "require_framework": True,
        },
        "system_prompts": {
            "proposition": """You are participating in a Lincoln-Douglas debate as the Affirmative.
Begin by establishing a clear value framework and criterion.
Your arguments should be grounded in moral and philosophical reasoning.
Address the resolution directly and defend your framework.""",
            "opposition": """You are participating in a Lincoln-Douglas debate as the Negative.
Challenge the Affirmative's framework or present your own.
Focus on moral and philosophical objections to the resolution.
Your arguments should be value-based and well-structured.""",
        },
    },
    "parliamentary": {
        "name": "Parliamentary",
        "description": "British Parliamentary debate style",
        "structure": [
            {"type": "opening_statement", "duration": 420, "order": ["proposition", "opposition"]},
            {"type": "argument", "duration": 480, "rounds": 2},
            {"type": "closing_statement", "duration": 300, "order": ["opposition", "proposition"]},
        ],
        "rules": {
            "max_response_length": 2500,
            "time_limit_per_turn": 480,
            "allow_points_of_information": True,
            "witty_remarks_encouraged": True,
        },
        "system_prompts": {
            "proposition": """You are participating in a Parliamentary debate supporting the motion.
Use rhetorical flourish and wit while maintaining substantive arguments.
Engage with your opponents' points directly and cleverly.
Be both persuasive and entertaining.""",
            "opposition": """You are participating in a Parliamentary debate opposing the motion.
Use rhetorical flourish and wit while maintaining substantive arguments.
Challenge the government's case with clever and substantive responses.
Be both persuasive and entertaining.""",
        },
    },
    "fishbowl": {
        "name": "Fishbowl Discussion",
        "description": "Collaborative exploration format",
        "structure": [
            {"type": "opening_statement", "duration": 180, "order": ["all"]},
            {"type": "argument", "duration": 120, "rounds": 5, "free_form": True},
            {"type": "closing_statement", "duration": 180, "order": ["all"]},
        ],
        "rules": {
            "max_response_length": 1000,
            "collaborative": True,
            "build_on_others": True,
            "respectful_exploration": True,
        },
        "system_prompts": {
            "default": """You are participating in a fishbowl discussion.
The goal is collaborative exploration rather than winning.
Listen carefully to others and build on their ideas.
Ask thoughtful questions and share insights respectfully.
Seek understanding rather than victory.""",
        },
    },
    "socratic": {
        "name": "Socratic Dialogue",
        "description": "Question-based philosophical exploration",
        "structure": [
            {"type": "opening_statement", "duration": 240, "order": ["proposition"]},
            {"type": "argument", "duration": 180, "rounds": 6, "question_focused": True},
            {"type": "closing_statement", "duration": 240, "order": ["all"]},
        ],
        "rules": {
            "max_response_length": 800,
            "encourage_questions": True,
            "examine_assumptions": True,
            "philosophical_depth": True,
        },
        "system_prompts": {
            "default": """You are participating in a Socratic dialogue.
Ask probing questions to examine assumptions and beliefs.
Follow the inquiry wherever it leads, even if it challenges your initial position.
Focus on understanding the deeper truth rather than being right.
Use questions to guide the exploration.""",
        },
    },
}


def get_debate_format(format_name: str) -> Dict[str, Any]:
    """Get configuration for a specific debate format."""
    format_name = format_name.lower()
    if format_name not in DEBATE_FORMATS:
        available = ", ".join(DEBATE_FORMATS.keys())
        raise ValueError(f"Unknown debate format '{format_name}'. Available: {available}")

    return DEBATE_FORMATS[format_name].copy()


def get_available_formats() -> list[str]:
    """Get list of available debate formats."""
    return list(DEBATE_FORMATS.keys())


def get_format_description(format_name: str) -> str:
    """Get description of a debate format."""
    format_config = get_debate_format(format_name)
    return format_config["description"]


def get_system_prompt_for_role(format_name: str, role: str) -> str:
    """Get system prompt for a specific role in a debate format."""
    format_config = get_debate_format(format_name)
    system_prompts = format_config.get("system_prompts", {})

    if role in system_prompts:
        return system_prompts[role]
    elif "default" in system_prompts:
        return system_prompts["default"]
    else:
        return "You are participating in a structured debate. Present clear, logical arguments."