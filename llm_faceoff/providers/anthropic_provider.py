"""Anthropic LLM provider implementation."""

from typing import Any, Dict, List

from anthropic import AsyncAnthropic

from .base_provider import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic LLM provider."""

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        """Initialize Anthropic provider."""
        super().__init__(api_key, model)
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate response using Anthropic API."""
        self._validate_inputs(messages, max_tokens)

        formatted_messages = self._format_messages_for_anthropic(messages)

        try:
            response = await self.client.messages.create(
                model=self.model,
                system=system_prompt if system_prompt else "You are a helpful assistant.",
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            if response.content and len(response.content) > 0:
                return response.content[0].text
            else:
                raise ValueError("No response generated from Anthropic API")

        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")

    def _format_messages_for_anthropic(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format messages for Anthropic API (no system messages in messages array)."""
        formatted_messages = []

        for message in messages:
            if message.get("role") != "system":
                formatted_messages.append(message)

        return formatted_messages

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "Anthropic"

    def get_available_models(self) -> List[str]:
        """Get available Anthropic models."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ]