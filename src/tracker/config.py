"""Configuration management"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="sqlite:///~/.config/tracker/tracker.db",
        description="Database connection URL",
    )
    encryption_key: Optional[str] = Field(
        default=None, description="Encryption key for sensitive fields"
    )

    # AI Provider
    ai_provider: str = Field(default="anthropic", description="AI provider (openai, anthropic, openrouter, local)")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openrouter_api_key: Optional[str] = Field(default=None, description="OpenRouter API key")
    local_api_url: str = Field(default="http://localhost:1234/v1", description="Local API URL (Ollama/LM Studio)")
    ai_model: Optional[str] = Field(default=None, description="AI model name")

    # API Server
    api_host: str = Field(default="localhost", description="API server host")
    api_port: int = Field(default=2424, description="API server port")
    jwt_secret: str = Field(
        default="change-me-in-production", description="JWT signing secret"
    )
    jwt_expiry_days: int = Field(default=90, description="JWT token expiry in days")

    # MCP Server
    mcp_transport: str = Field(default="stdio", description="MCP transport (stdio or http)")
    mcp_http_port: int = Field(default=2425, description="MCP HTTP port")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    def get_database_path(self) -> Path:
        """Get resolved database path"""
        url = self.database_url.replace("sqlite:///", "")
        return Path(os.path.expanduser(url))

    def get_ai_api_key(self) -> Optional[str]:
        """Get API key for configured provider"""
        if self.ai_provider == "openai":
            return self.openai_api_key
        elif self.ai_provider == "anthropic":
            return self.anthropic_api_key
        elif self.ai_provider == "openrouter":
            return self.openrouter_api_key
        elif self.ai_provider == "local":
            return None  # Local models don't need API keys
        return None


# Global settings instance
settings = Settings()
