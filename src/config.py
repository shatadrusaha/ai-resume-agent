"""Configuration settings for the AI Resume Agent.

Loads configuration from .env file using Pydantic BaseSettings.
Provides a single flat Config class for all application settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration combining Ollama and tailoring settings.

    Loads from .env file. All settings are flat but organized with prefixes:
    - ollama_* for Ollama server settings
    - tailoring_* for resume tailoring parameters

    Attributes:
        ollama_host: Ollama server hostname (default: localhost)
        ollama_port: Ollama server port (default: 11434)
        ollama_model: LLM model to use (default: llama3)
        ollama_timeout: Request timeout in seconds (default: 300)
        tailoring_temperature: Creativity level 0.0-1.0 (default: 0.7)
        tailoring_max_tokens: Max tokens to generate (default: 2000)
        tailoring_context_window: LLM context size (default: 4096)
    """

    ollama_host: str = Field(default="localhost", description="Ollama server host")
    ollama_port: int = Field(default=11434, description="Ollama server port")
    ollama_model: str = Field(default="llama3", description="LLM model name")
    ollama_timeout: int = Field(default=300, description="Request timeout in seconds")

    tailoring_temperature: float = Field(
        default=0.7, description="Creativity level (0.0-1.0)"
    )
    tailoring_max_tokens: int = Field(
        default=2000, description="Max length of generated content"
    )
    tailoring_context_window: int = Field(
        default=4096, description="LLM context window size"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def ollama_base_url(self) -> str:
        """Construct Ollama server base URL from host and port.

        Returns:
            URL string in format 'http://host:port'
        """
        return f"http://{self.ollama_host}:{self.ollama_port}"

    def __repr__(self) -> str:
        return (
            f"Config(\n"
            f"  ollama_host={self.ollama_host},\n"
            f"  ollama_port={self.ollama_port},\n"
            f"  ollama_model={self.ollama_model},\n"
            f"  ollama_timeout={self.ollama_timeout},\n"
            f"  tailoring_temperature={self.tailoring_temperature},\n"
            f"  tailoring_max_tokens={self.tailoring_max_tokens},\n"
            f"  tailoring_context_window={self.tailoring_context_window}\n"
            f")"
        )


# Global config instance
_config = None


def get_config() -> Config:
    """Get or create the global config instance.

    Implements lazy singleton pattern. Config is loaded from .env
    file on first call and cached for subsequent calls.

    Returns:
        Global Config instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config
