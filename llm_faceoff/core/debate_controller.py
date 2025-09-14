"""Debate controller implementation for managing debate sessions."""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from ..config.settings import DebateSettings
from ..providers import ProviderFactory
from .types import (
    DebateMessage,
    DebateRole,
    DebateSession,
    DebateStatus,
    MessageType,
    Participant,
)


class BasicDebateController:
    """Basic implementation of debate controller."""

    def __init__(self):
        """Initialize the debate controller."""
        self.settings = DebateSettings()
        self.provider_factory = ProviderFactory()

    async def start_debate(self, session: DebateSession) -> None:
        """Start a debate session."""
        if session.status != DebateStatus.CREATED:
            raise ValueError("Can only start debates with CREATED status")

        if len(session.participants) < 2:
            raise ValueError("Need at least 2 participants to start a debate")

        session.status = DebateStatus.IN_PROGRESS
        session.started_at = datetime.now()
        session.current_turn = 1
        session.current_participant_index = 0

        await self._add_opening_message(session)

    async def process_turn(self, session: DebateSession) -> DebateMessage:
        """Process the current turn in the debate."""
        if session.status != DebateStatus.IN_PROGRESS:
            raise ValueError("Can only process turns for debates in progress")

        current_participant = self.get_current_participant(session)
        if not current_participant:
            raise ValueError("No current participant found")

        conversation_history = self._build_conversation_history(session)
        system_prompt = self._build_system_prompt(session, current_participant)

        try:
            provider = self.provider_factory.create_provider(
                provider_name=current_participant.provider,
                api_key=self._get_api_key(current_participant.provider),
                model=current_participant.model,
            )

            response_content = await provider.generate_response(
                messages=conversation_history,
                system_prompt=system_prompt,
                max_tokens=session.config.max_response_length,
                temperature=0.7,
            )

            message_type = self._determine_message_type(session, current_participant)

            message = DebateMessage(
                participant_id=current_participant.id,
                content=response_content,
                message_type=message_type,
                timestamp=datetime.now(),
                metadata={"turn": session.current_turn, "provider": current_participant.provider},
            )

            session.messages.append(message)
            self._advance_turn(session)

            return message

        except Exception as e:
            raise RuntimeError(f"Failed to process turn: {str(e)}")

    async def end_debate(self, session: DebateSession) -> None:
        """End a debate session."""
        session.status = DebateStatus.COMPLETED
        session.completed_at = datetime.now()

    def get_current_participant(self, session: DebateSession) -> Optional[Participant]:
        """Get the participant whose turn it is."""
        if session.current_participant_index < len(session.participants):
            return session.participants[session.current_participant_index]
        return None

    def _build_conversation_history(self, session: DebateSession) -> List[Dict[str, str]]:
        """Build conversation history for the current participant."""
        history = []

        for message in session.messages[-10:]:
            participant = self._get_participant_by_id(session, message.participant_id)
            if participant:
                role = "user" if participant.role != DebateRole.MODERATOR else "assistant"
                history.append({"role": role, "content": message.content})

        return history

    def _build_system_prompt(self, session: DebateSession, participant: Participant) -> str:
        """Build system prompt for the current participant."""
        base_prompt = participant.system_prompt or "You are participating in a structured debate."

        role_context = {
            DebateRole.PROPOSITION: "You are arguing FOR the proposition",
            DebateRole.OPPOSITION: "You are arguing AGAINST the proposition",
            DebateRole.MODERATOR: "You are moderating this debate",
        }

        debate_context = f"""
{base_prompt}

DEBATE TOPIC: {session.config.topic}
YOUR ROLE: {role_context[participant.role]}
DEBATE FORMAT: {session.config.format}
TURN: {session.current_turn} of {session.config.max_turns}

Rules:
- Keep responses under {session.config.max_response_length} characters
- Stay focused on the topic
- Be respectful and constructive
- Present clear arguments with reasoning
"""

        return debate_context

    def _determine_message_type(self, session: DebateSession, participant: Participant) -> MessageType:
        """Determine the type of message based on debate progress."""
        if session.current_turn == 1:
            return MessageType.OPENING_STATEMENT
        elif session.current_turn >= session.config.max_turns - len(session.participants):
            return MessageType.CLOSING_STATEMENT
        else:
            return MessageType.ARGUMENT

    def _advance_turn(self, session: DebateSession) -> None:
        """Advance to the next turn."""
        session.current_participant_index = (session.current_participant_index + 1) % len(session.participants)

        if session.current_participant_index == 0:
            session.current_turn += 1

        if session.current_turn > session.config.max_turns:
            session.status = DebateStatus.COMPLETED
            session.completed_at = datetime.now()

    def _get_participant_by_id(self, session: DebateSession, participant_id: str) -> Optional[Participant]:
        """Get participant by ID."""
        for participant in session.participants:
            if str(participant.id) == str(participant_id):
                return participant
        return None

    def _get_api_key(self, provider_name: str) -> str:
        """Get API key for provider from settings."""
        provider_lower = provider_name.lower()

        if provider_lower == "openai":
            api_key = self.settings.openai_api_key
            env_var = "OPENAI_API_KEY"
        elif provider_lower == "anthropic":
            api_key = self.settings.anthropic_api_key
            env_var = "CLAUDE_API_KEY"
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

        if not api_key:
            raise ValueError(f"Missing API key for {provider_name}. Set {env_var} environment variable.")

        return api_key

    async def _add_opening_message(self, session: DebateSession) -> None:
        """Add initial moderator message to start the debate."""
        opening_message = DebateMessage(
            participant_id=session.participants[0].id,  # Use first participant ID as placeholder
            content=f"Welcome to this debate on: {session.config.topic}\\n\\nLet's begin with opening statements.",
            message_type=MessageType.MODERATOR_COMMENT,
            timestamp=datetime.now(),
            metadata={"turn": 0, "provider": "system"},
        )
        session.messages.append(opening_message)