"""Configuration settings for the resume agent."""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaConfig(BaseModel):
    """Configuration for Ollama LLM connection."""

    host: str = Field(default="localhost", description="Ollama server host")
    port: int = Field(default=11434, description="Ollama server port")
    model: str = Field(default="mistral", description="LLM model name")
    timeout: int = Field(default=300, description="Request timeout in seconds")

    @property
    def base_url(self) -> str:
        """Get the base URL for Ollama API."""
        return f"http://{self.host}:{self.port}"


class TailoringConfig(BaseModel):
    """Configuration for resume tailoring behavior."""

    temperature: float = Field(default=0.7, description="Creativity level (0.0-1.0)")
    max_tokens: int = Field(default=2000, description="Max length of generated content")
    context_window: int = Field(default=4096, description="LLM context window size")


class AppSettings(BaseSettings):
    """Settings loaded from environment variables."""

    ollama_host: str = Field(default="localhost", description="Ollama server host")
    ollama_port: int = Field(default=11434, description="Ollama server port")
    ollama_model: str = Field(default="mistral", description="LLM model name")
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


class AppConfig:
    """Main application configuration."""

    def __init__(self):
        settings = AppSettings()

        self.ollama = OllamaConfig(
            host=settings.ollama_host,
            port=settings.ollama_port,
            model=settings.ollama_model,
            timeout=settings.ollama_timeout,
        )

        self.tailoring = TailoringConfig(
            temperature=settings.tailoring_temperature,
            max_tokens=settings.tailoring_max_tokens,
            context_window=settings.tailoring_context_window,
        )

    def __repr__(self) -> str:
        return f"AppConfig(\n  ollama={self.ollama},\n  tailoring={self.tailoring}\n)"


# Global config instance
_config = None


def get_config() -> AppConfig:
    """Get or create the global config instance."""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config
