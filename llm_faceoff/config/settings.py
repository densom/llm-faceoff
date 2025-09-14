"""Configuration settings for the LLM debate system."""

import os
from typing import Dict, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class DebateSettings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="CLAUDE_API_KEY")

    default_format: str = Field(default="oxford", alias="DEFAULT_DEBATE_FORMAT")
    default_max_turns: int = Field(default=10, alias="DEFAULT_MAX_TURNS")
    default_max_response_length: int = Field(default=1000, alias="DEFAULT_MAX_RESPONSE_LENGTH")
    default_temperature: float = Field(default=0.7, alias="DEFAULT_TEMPERATURE")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, alias="LOG_FILE")

    output_directory: str = Field(default="./outputs", alias="OUTPUT_DIRECTORY")
    save_transcripts: bool = Field(default=True, alias="SAVE_TRANSCRIPTS")
    transcript_format: str = Field(default="markdown", alias="TRANSCRIPT_FORMAT")  # markdown, json, html, all

    rate_limit_requests_per_minute: int = Field(default=60, alias="RATE_LIMIT_RPM")
    request_timeout_seconds: int = Field(default=30, alias="REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        provider = provider.lower()
        if provider == "openai":
            return self.openai_api_key
        elif provider == "anthropic":
            return self.anthropic_api_key
        return None

    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate that required API keys are available."""
        return {
            "openai": bool(self.openai_api_key),
            "anthropic": bool(self.anthropic_api_key),
        }


settings = DebateSettings()