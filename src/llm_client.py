"""Ollama LLM client for communicating with local language models.

Provides a client class to interact with Ollama, including connection
testing, model discovery, and prompt generation with retry logic.
"""

import json
import logging
from typing import Optional

import requests

from src.config import Config, get_config

logger = logging.getLogger(__name__)


class OllamaConnectionError(Exception):
    """Raised when unable to connect to Ollama server.

    Can indicate Ollama is not running, network issues, or server is unreachable.
    """

    pass


class OllamaTimeoutError(Exception):
    """Raised when Ollama request exceeds timeout threshold.

    Indicates the LLM took too long to respond. Can be retried.
    """

    pass


class OllamaClient:
    """Client for interacting with Ollama local LLM.

    Handles HTTP communication with Ollama server, including connection
    verification, model discovery, and prompt generation.

    Attributes:
        config: Config instance with Ollama server and tailoring settings
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize Ollama client.

        Args:
            config: Config instance. If None, loads from global config.
        """
        if config is None:
            config = get_config()

        self.config = config

    @property
    def base_url(self) -> str:
        """Convenience alias for config.ollama_base_url."""
        return self.config.ollama_base_url

    @property
    def model(self) -> str:
        """Convenience alias for config.ollama_model."""
        return self.config.ollama_model

    @model.setter
    def model(self, value: str) -> None:
        """Allow overriding the model at runtime."""
        self.config.ollama_model = value

    @property
    def timeout(self) -> int:
        """Convenience alias for config.ollama_timeout."""
        return self.config.ollama_timeout

    def test_connection(self) -> bool:
        """Test connection to Ollama server.

        Pings the Ollama /api/tags endpoint to verify the server
        is running and responding.

        Returns:
            True if connection successful

        Raises:
            OllamaConnectionError: If unable to connect
            OllamaTimeoutError: If connection times out
        """
        try:
            response = requests.get(
                f"{self.config.ollama_base_url}/api/tags",
                timeout=5,
            )
            response.raise_for_status()
            logger.info(f"✓ Connected to Ollama at {self.config.ollama_base_url}")
            return True
        except requests.exceptions.ConnectionError as e:
            msg = (
                f"Failed to connect to Ollama at {self.config.ollama_base_url}. "
                f"Is Ollama running? Error: {str(e)}"
            )
            logger.error(msg)
            raise OllamaConnectionError(msg) from e
        except requests.exceptions.Timeout as e:
            msg = f"Connection to Ollama timed out at {self.config.ollama_base_url}. Error: {str(e)}"
            logger.error(msg)
            raise OllamaTimeoutError(msg) from e
        except requests.exceptions.RequestException as e:
            msg = f"Error testing Ollama connection: {str(e)}"
            logger.error(msg)
            raise OllamaConnectionError(msg) from e

    def get_available_models(self) -> list[str]:
        """Get list of available models from Ollama server.

        Returns:
            List of model names available on the Ollama server.

        Raises:
            OllamaConnectionError: If unable to reach Ollama
        """
        try:
            response = requests.get(
                f"{self.config.ollama_base_url}/api/tags",
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return models
        except Exception as e:
            msg = f"Failed to get available models: {str(e)}"
            logger.error(msg)
            raise OllamaConnectionError(msg) from e

    def call_ollama(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Call Ollama with a prompt and get response.

        Sends a prompt to the LLM and waits for generated text response.
        Uses configuration defaults if model/temperature/max_tokens not specified.

        Args:
            prompt: The prompt text to send to the model
            model: Model name. Defaults to self.model if not specified
            temperature: Creativity level 0.0-1.0. Defaults to config if not specified
            max_tokens: Maximum tokens to generate. Defaults to config if not specified

        Returns:
            Generated text from the model

        Raises:
            OllamaConnectionError: If unable to connect to Ollama
            OllamaTimeoutError: If request exceeds timeout
        """
        if model is None:
            model = self.config.ollama_model

        if temperature is None:
            temperature = self.config.tailoring_temperature

        if max_tokens is None:
            max_tokens = self.config.tailoring_max_tokens

        logger.debug(f"Calling Ollama with model={model}, temp={temperature}")

        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            response = requests.post(
                f"{self.config.ollama_base_url}/api/generate",
                json=payload,
                timeout=self.config.ollama_timeout,
            )

            # Handle 404: Model not found
            if response.status_code == 404:
                msg = (
                    f"Model '{model}' not found on Ollama server. "
                    f"Pull it with: ollama pull {model}"
                )
                logger.error(msg)
                raise OllamaConnectionError(msg)

            response.raise_for_status()

            data = response.json()
            generated_text = data.get("response", "").strip()

            # Debug: Log the raw response if empty
            if not generated_text:
                logger.warning(f"Empty response from Ollama. Raw data: {data}")

            logger.debug(f"Generated {len(generated_text)} characters")
            return generated_text

        except requests.exceptions.Timeout as e:
            msg = f"Ollama request timed out after {self.config.ollama_timeout}s"
            logger.error(msg)
            raise OllamaTimeoutError(msg) from e
        except requests.exceptions.ConnectionError as e:
            msg = f"Failed to connect to Ollama at {self.config.ollama_base_url}. Is Ollama running? (ollama serve)"
            logger.error(msg)
            raise OllamaConnectionError(msg) from e
        except requests.exceptions.HTTPError as e:
            msg = f"Ollama HTTP error: {str(e)}"
            logger.error(msg)
            raise OllamaConnectionError(msg) from e
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON response from Ollama: {str(e)}"
            logger.error(msg)
            raise OllamaConnectionError(msg) from e
        except Exception as e:
            msg = f"Ollama call failed: {str(e)}"
            logger.error(msg)
            raise OllamaConnectionError(msg) from e

    def call_ollama_with_retry(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
    ) -> str:
        """
        Call Ollama with automatic retry on transient failures.

        Args:
            prompt: The prompt to send to the model
            model: Model name (uses default if not specified)
            max_retries: Number of retries on transient failures
            backoff_factor: Multiplier for backoff delay (not used for now)

        Returns:
            Generated text from the model

        Raises:
            OllamaConnectionError: If all retries fail
        """
        import time

        last_error = None

        for attempt in range(max_retries):
            try:
                return self.call_ollama(prompt, model=model)
            except OllamaTimeoutError as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # exponential backoff
                    logger.warning(
                        f"Ollama timeout (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Ollama timeout after {max_retries} retries")
            except OllamaConnectionError as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Ollama connection error (attempt {attempt + 1}/{max_retries}), "
                        f"retrying..."
                    )
                else:
                    logger.error(
                        f"Ollama connection failed after {max_retries} retries"
                    )

        raise last_error or OllamaConnectionError("Ollama call failed after retries")
