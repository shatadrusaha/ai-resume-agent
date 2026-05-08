"""Ollama LLM client for resume tailoring."""

import json
import logging
from typing import Optional

import requests

from src.config import get_config

logger = logging.getLogger(__name__)


class OllamaConnectionError(Exception):
    """Raised when unable to connect to Ollama."""

    pass


class OllamaTimeoutError(Exception):
    """Raised when Ollama request times out."""

    pass


class OllamaClient:
    """Client for interacting with Ollama local LLM."""

    def __init__(self, config=None):
        """
        Initialize Ollama client.

        Args:
            config: OllamaConfig instance. If None, uses global config.
        """
        if config is None:
            config = get_config().ollama

        self.config = config
        self.base_url = config.base_url
        self.model = config.model
        self.timeout = config.timeout

    def test_connection(self) -> bool:
        """
        Test connection to Ollama server.

        Returns:
            True if connection successful, False otherwise.

        Raises:
            OllamaConnectionError: If unable to connect to Ollama.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            response.raise_for_status()
            logger.info(f"✓ Connected to Ollama at {self.base_url}")
            return True
        except requests.exceptions.ConnectionError as e:
            msg = (
                f"Failed to connect to Ollama at {self.base_url}. "
                f"Is Ollama running? Error: {str(e)}"
            )
            logger.error(msg)
            raise OllamaConnectionError(msg) from e
        except requests.exceptions.Timeout as e:
            msg = f"Connection to Ollama timed out at {self.base_url}. Error: {str(e)}"
            logger.error(msg)
            raise OllamaTimeoutError(msg) from e
        except requests.exceptions.RequestException as e:
            msg = f"Error testing Ollama connection: {str(e)}"
            logger.error(msg)
            raise OllamaConnectionError(msg) from e

    def get_available_models(self) -> list[str]:
        """
        Get list of available models from Ollama.

        Returns:
            List of model names available on the server.

        Raises:
            OllamaConnectionError: If unable to connect to Ollama.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
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
        """
        Call Ollama with a prompt and get response.

        Args:
            prompt: The prompt to send to the model
            model: Model name (uses default if not specified)
            temperature: Creativity level 0.0-1.0 (uses config default if not specified)
            max_tokens: Maximum tokens to generate (uses config default if not specified)

        Returns:
            Generated text from the model

        Raises:
            OllamaConnectionError: If unable to connect to Ollama
            OllamaTimeoutError: If request times out
        """
        if model is None:
            model = self.model

        if temperature is None:
            temperature = get_config().tailoring.temperature

        if max_tokens is None:
            max_tokens = get_config().tailoring.max_tokens

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
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            generated_text = data.get("response", "").strip()

            logger.debug(f"Generated {len(generated_text)} characters")
            return generated_text

        except requests.exceptions.Timeout as e:
            msg = f"Ollama request timed out after {self.timeout}s"
            logger.error(msg)
            raise OllamaTimeoutError(msg) from e
        except requests.exceptions.ConnectionError as e:
            msg = f"Failed to connect to Ollama at {self.base_url}"
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
