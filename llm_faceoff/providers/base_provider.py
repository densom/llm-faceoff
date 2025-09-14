"""Base LLM provider implementation."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..core.types import LLMProvider


class BaseLLMProvider(ABC, LLMProvider):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str = "", model: str = ""):
        """Initialize the provider with API key and default model."""
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider."""
        pass

    def _format_messages_for_api(self, messages: List[Dict[str, str]], system_prompt: str = "") -> List[Dict[str, str]]:
        """Format messages for API consumption."""
        formatted_messages = []

        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        for message in messages:
            formatted_messages.append(message)

        return formatted_messages

    def _validate_inputs(self, messages: List[Dict[str, str]], max_tokens: int) -> None:
        """Validate input parameters."""
        if not messages:
            raise ValueError("Messages list cannot be empty")

        if max_tokens < 1 or max_tokens > 4000:
            raise ValueError("max_tokens must be between 1 and 4000")

        for message in messages:
            if "role" not in message or "content" not in message:
                raise ValueError("Each message must have 'role' and 'content' keys")