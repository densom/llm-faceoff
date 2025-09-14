"""Core type definitions for the LLM debate system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DebateRole(Enum):
    """Roles participants can take in a debate."""

    PROPOSITION = "proposition"
    OPPOSITION = "opposition"
    MODERATOR = "moderator"


class MessageType(Enum):
    """Types of messages in a debate."""

    OPENING_STATEMENT = "opening_statement"
    ARGUMENT = "argument"
    REBUTTAL = "rebuttal"
    CLOSING_STATEMENT = "closing_statement"
    MODERATOR_COMMENT = "moderator_comment"


class DebateStatus(Enum):
    """Status of a debate session."""

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABORTED = "aborted"


@dataclass
class Participant:
    """A participant in a debate."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    provider: str = ""
    model: str = ""
    role: DebateRole = DebateRole.PROPOSITION
    system_prompt: str = ""


@dataclass
class DebateMessage:
    """A message in a debate conversation."""

    id: UUID = field(default_factory=uuid4)
    participant_id: UUID = field(default_factory=uuid4)
    content: str = ""
    message_type: MessageType = MessageType.ARGUMENT
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DebateConfig:
    """Configuration for a debate session."""

    topic: str = ""
    format: str = "oxford"
    max_turns: int = 10
    max_response_length: int = 1000
    turn_time_limit: Optional[int] = None
    rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DebateSession:
    """A complete debate session."""

    id: UUID = field(default_factory=uuid4)
    config: DebateConfig = field(default_factory=DebateConfig)
    participants: List[Participant] = field(default_factory=list)
    messages: List[DebateMessage] = field(default_factory=list)
    status: DebateStatus = DebateStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_turn: int = 0
    current_participant_index: int = 0


class LLMProvider(Protocol):
    """Protocol for LLM providers."""

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a response from the LLM."""
        ...

    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        ...

    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider."""
        ...


class DebateController(Protocol):
    """Protocol for debate controllers."""

    async def start_debate(self, session: DebateSession) -> None:
        """Start a debate session."""
        ...

    async def process_turn(self, session: DebateSession) -> DebateMessage:
        """Process the current turn in the debate."""
        ...

    async def end_debate(self, session: DebateSession) -> None:
        """End a debate session."""
        ...

    def get_current_participant(self, session: DebateSession) -> Optional[Participant]:
        """Get the participant whose turn it is."""
        ...


class TranscriptGenerator(Protocol):
    """Protocol for generating debate transcripts."""

    def generate_markdown(self, session: DebateSession) -> str:
        """Generate a markdown transcript."""
        ...

    def generate_json(self, session: DebateSession) -> Dict[str, Any]:
        """Generate a JSON transcript."""
        ...

    def generate_html(self, session: DebateSession) -> str:
        """Generate an HTML transcript."""
        ...


class DebateRequest(BaseModel):
    """Pydantic model for debate requests."""

    topic: str = Field(..., description="The debate topic")
    format: str = Field(default="oxford", description="Debate format")
    participants: List[Dict[str, str]] = Field(..., description="Participant configurations")
    max_turns: int = Field(default=10, ge=1, le=100, description="Maximum number of turns")
    max_response_length: int = Field(default=1000, ge=100, le=5000, description="Max response length")


class DebateResponse(BaseModel):
    """Pydantic model for debate responses."""

    session_id: str
    status: str
    transcript_markdown: Optional[str] = None
    transcript_json: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None