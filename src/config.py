"""Configuration settings for the resume agent."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class OllamaConfig:
    """Configuration for Ollama LLM connection."""

    host: str = "localhost"
    port: int = 11434
    model: str = "mistral"  # Default to Mistral; can override with env var
    timeout: int = 300  # 5 minutes

    @property
    def base_url(self) -> str:
        """Get the base URL for Ollama API."""
        return f"http://{self.host}:{self.port}"

    @classmethod
    def from_env(cls) -> "OllamaConfig":
        """Load Ollama config from environment variables."""
        return cls(
            host=os.getenv("OLLAMA_HOST", "localhost"),
            port=int(os.getenv("OLLAMA_PORT", "11434")),
            model=os.getenv("OLLAMA_MODEL", "mistral"),
            timeout=int(os.getenv("OLLAMA_TIMEOUT", "300")),
        )


@dataclass
class TailoringConfig:
    """Configuration for resume tailoring behavior."""

    temperature: float = 0.7  # Creativity level (0.0-1.0)
    max_tokens: int = 2000  # Max length of generated content
    context_window: int = 4096  # LLM context window size

    @classmethod
    def from_env(cls) -> "TailoringConfig":
        """Load tailoring config from environment variables."""
        return cls(
            temperature=float(os.getenv("TAILORING_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("TAILORING_MAX_TOKENS", "2000")),
            context_window=int(os.getenv("TAILORING_CONTEXT_WINDOW", "4096")),
        )


class Config:
    """Main application configuration."""

    def __init__(self):
        self.ollama = OllamaConfig.from_env()
        self.tailoring = TailoringConfig.from_env()

    def __repr__(self) -> str:
        return f"Config(\n  ollama={self.ollama},\n  tailoring={self.tailoring}\n)"


# Global config instance
_config = None


def get_config() -> Config:
    """Get or create the global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
