"""Provider factory for creating LLM providers."""

from typing import Dict, Type

from .anthropic_provider import AnthropicProvider
from .base_provider import BaseLLMProvider
from .openai_provider import OpenAIProvider


class ProviderFactory:
    """Factory for creating LLM providers."""

    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }

    @classmethod
    def create_provider(self, provider_name: str, api_key: str, model: str = "") -> BaseLLMProvider:
        """Create a provider instance."""
        provider_name = provider_name.lower()

        if provider_name not in self._providers:
            available = ", ".join(self._providers.keys())
            raise ValueError(f"Unknown provider '{provider_name}'. Available: {available}")

        provider_class = self._providers[provider_name]

        if model:
            return provider_class(api_key=api_key, model=model)
        else:
            return provider_class(api_key=api_key)

    @classmethod
    def get_available_providers(self) -> list[str]:
        """Get list of available provider names."""
        return list(self._providers.keys())

    @classmethod
    def register_provider(self, name: str, provider_class: Type[BaseLLMProvider]) -> None:
        """Register a new provider class."""
        self._providers[name.lower()] = provider_class