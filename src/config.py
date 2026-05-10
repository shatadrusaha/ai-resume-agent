"""Configuration settings for the AI Resume Agent.

Loads configuration from .env file using Pydantic BaseSettings.
Provides two main config objects: OllamaConfig (LLM server settings)
and TailoringConfig (resume tailoring parameters).
"""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaConfig(BaseModel):
    """Configuration for Ollama LLM server connection.

    Used to specify the Ollama server location and default model.

    Attributes:
        host: Ollama server hostname (default: localhost)
        port: Ollama server port (default: 11434)
        model: Default LLM model to use (default: llama3)
        timeout: Request timeout in seconds (default: 300)
    """

    host: str = Field(default="localhost", description="Ollama server host")
    port: int = Field(default=11434, description="Ollama server port")
    model: str = Field(default="llama3", description="LLM model name")
    timeout: int = Field(default=300, description="Request timeout in seconds")

    @property
    def base_url(self) -> str:
        """Ollama server base URL.

        Constructed from host and port configuration.

        Returns:
            URL string in format 'http://host:port'
        """
        return f"http://{self.host}:{self.port}"


class TailoringConfig(BaseModel):
    """Configuration for resume tailoring behavior.

    Controls LLM generation parameters when tailoring resumes.

    Attributes:
        temperature: Creativity level 0.0-1.0. Lower = predictable,
            Higher = more creative. Default: 0.7
        max_tokens: Maximum tokens to generate per request. Default: 2000
        context_window: LLM context size. Used for prompt planning. Default: 4096
    """

    temperature: float = Field(default=0.7, description="Creativity level (0.0-1.0)")
    max_tokens: int = Field(default=2000, description="Max length of generated content")
    context_window: int = Field(default=4096, description="LLM context window size")


class AppSettings(BaseSettings):
    """Application settings loaded from environment variables.

    Reads from .env file and provides values for OllamaConfig and
    TailoringConfig. Automatically converts types (e.g., str to int).

    Attributes:
        ollama_host: OLLAMA_HOST env var
        ollama_port: OLLAMA_PORT env var
        ollama_model: OLLAMA_MODEL env var
        ollama_timeout: OLLAMA_TIMEOUT env var
        tailoring_temperature: TAILORING_TEMPERATURE env var
        tailoring_max_tokens: TAILORING_MAX_TOKENS env var
        tailoring_context_window: TAILORING_CONTEXT_WINDOW env var
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


class AppConfig:
    """Main application configuration combining all settings.

    Loads environment settings and constructs nested config objects
    for Ollama and tailoring parameters. Acts as the single source
    of truth for all configuration across the application.

    Attributes:
        ollama: OllamaConfig instance with server settings
        tailoring: TailoringConfig instance with LLM parameters
    """

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
    """Get or create the global config instance.

    Implements lazy singleton pattern. Config is loaded from .env
    file on first call and cached for subsequent calls.

    Returns:
        Global AppConfig instance
    """
    global _config
    if _config is None:
        _config = AppConfig()
    return _config
