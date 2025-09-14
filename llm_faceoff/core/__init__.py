"""Core module for LLM debate system."""

from .debate_controller import BasicDebateController
from .message_processor import MessageProcessor
from .types import (
    DebateConfig,
    DebateController,
    DebateMessage,
    DebateRequest,
    DebateResponse,
    DebateRole,
    DebateSession,
    DebateStatus,
    LLMProvider,
    MessageType,
    Participant,
    TranscriptGenerator,
)

__all__ = [
    "BasicDebateController",
    "DebateConfig",
    "DebateController",
    "DebateMessage",
    "DebateRequest",
    "DebateResponse",
    "DebateRole",
    "DebateSession",
    "DebateStatus",
    "LLMProvider",
    "MessageType",
    "MessageProcessor",
    "Participant",
    "TranscriptGenerator",
]