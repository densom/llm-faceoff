"""OpenAI LLM provider implementation."""

import asyncio
from typing import Any, Dict, List

from openai import AsyncOpenAI

from .base_provider import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """Initialize OpenAI provider."""
        super().__init__(api_key, model)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate response using OpenAI API."""
        self._validate_inputs(messages, max_tokens)

        formatted_messages = self._format_messages_for_api(messages, system_prompt)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            if response.choices and response.choices[0].message:
                return response.choices[0].message.content or ""
            else:
                raise ValueError("No response generated from OpenAI API")

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "OpenAI"

    def get_available_models(self) -> List[str]:
        """Get available OpenAI models."""
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
        ]