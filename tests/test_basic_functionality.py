"""Basic functionality tests for the LLM debate system."""

import pytest
from datetime import datetime
from uuid import uuid4

from llm_faceoff.core import (
    DebateConfig,
    DebateMessage,
    DebateRole,
    DebateSession,
    DebateStatus,
    MessageType,
    Participant,
)
from llm_faceoff.config import get_available_formats, get_debate_format
from llm_faceoff.providers import ProviderFactory
from llm_faceoff.output import BasicTranscriptGenerator


def test_debate_config_creation():
    """Test creating a debate configuration."""
    config = DebateConfig(
        topic="Test topic",
        format="oxford",
        max_turns=6,
        max_response_length=800
    )

    assert config.topic == "Test topic"
    assert config.format == "oxford"
    assert config.max_turns == 6
    assert config.max_response_length == 800


def test_participant_creation():
    """Test creating debate participants."""
    participant = Participant(
        name="Test Bot",
        provider="openai",
        model="gpt-4",
        role=DebateRole.PROPOSITION
    )

    assert participant.name == "Test Bot"
    assert participant.provider == "openai"
    assert participant.model == "gpt-4"
    assert participant.role == DebateRole.PROPOSITION
    assert participant.id is not None


def test_debate_session_creation():
    """Test creating a debate session."""
    config = DebateConfig(topic="Test", format="oxford")
    participants = [
        Participant(name="Bot1", provider="openai", model="gpt-4", role=DebateRole.PROPOSITION),
        Participant(name="Bot2", provider="anthropic", model="claude-3-haiku", role=DebateRole.OPPOSITION)
    ]

    session = DebateSession(config=config, participants=participants)

    assert session.config.topic == "Test"
    assert len(session.participants) == 2
    assert session.status == DebateStatus.CREATED
    assert session.current_turn == 0


def test_debate_message_creation():
    """Test creating debate messages."""
    participant_id = uuid4()
    message = DebateMessage(
        participant_id=participant_id,
        content="This is a test message",
        message_type=MessageType.OPENING_STATEMENT
    )

    assert message.participant_id == participant_id
    assert message.content == "This is a test message"
    assert message.message_type == MessageType.OPENING_STATEMENT
    assert isinstance(message.timestamp, datetime)


def test_available_debate_formats():
    """Test that debate formats are available."""
    formats = get_available_formats()

    assert "oxford" in formats
    assert "lincoln_douglas" in formats
    assert "parliamentary" in formats
    assert len(formats) > 0


def test_debate_format_configuration():
    """Test getting debate format configuration."""
    oxford_config = get_debate_format("oxford")

    assert oxford_config["name"] == "Oxford Style"
    assert "description" in oxford_config
    assert "structure" in oxford_config
    assert "rules" in oxford_config
    assert "system_prompts" in oxford_config


def test_provider_factory():
    """Test provider factory functionality."""
    factory = ProviderFactory()

    available_providers = factory.get_available_providers()
    assert "openai" in available_providers
    assert "anthropic" in available_providers


def test_transcript_generator():
    """Test basic transcript generation."""
    config = DebateConfig(topic="Test Topic", format="oxford")
    participants = [
        Participant(name="Bot1", provider="openai", model="gpt-4", role=DebateRole.PROPOSITION),
        Participant(name="Bot2", provider="anthropic", model="claude-3-haiku", role=DebateRole.OPPOSITION)
    ]

    session = DebateSession(config=config, participants=participants)
    session.messages = [
        DebateMessage(
            participant_id=participants[0].id,
            content="Opening statement",
            message_type=MessageType.OPENING_STATEMENT
        )
    ]

    generator = BasicTranscriptGenerator()

    markdown = generator.generate_markdown(session)
    assert "Test Topic" in markdown
    assert "Opening statement" in markdown

    json_data = generator.generate_json(session)
    assert json_data["config"]["topic"] == "Test Topic"
    assert len(json_data["messages"]) == 1

    html = generator.generate_html(session)
    assert "Test Topic" in html
    assert "Opening statement" in html


def test_enums():
    """Test that enums work correctly."""
    assert DebateRole.PROPOSITION.value == "proposition"
    assert DebateRole.OPPOSITION.value == "opposition"

    assert MessageType.OPENING_STATEMENT.value == "opening_statement"
    assert MessageType.CLOSING_STATEMENT.value == "closing_statement"

    assert DebateStatus.CREATED.value == "created"
    assert DebateStatus.IN_PROGRESS.value == "in_progress"
    assert DebateStatus.COMPLETED.value == "completed"


if __name__ == "__main__":
    pytest.main([__file__])