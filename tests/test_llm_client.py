"""Tests for llm_client.py — Ollama API communication with mocked responses."""

import pytest
from unittest.mock import Mock, patch
import requests

from src.llm_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaTimeoutError,
)
from src.config import Config


def create_test_config(
    host="localhost",
    port=11434,
    model="llama3",
    timeout=300,
    temperature=0.7,
    max_tokens=2000,
    context_window=4096,
) -> Config:
    """Helper function to create Config for tests."""
    return Config(
        ollama_host=host,
        ollama_port=port,
        ollama_model=model,
        ollama_timeout=timeout,
        tailoring_temperature=temperature,
        tailoring_max_tokens=max_tokens,
        tailoring_context_window=context_window,
    )


class TestOllamaClientInit:
    """Test OllamaClient initialization."""

    def test_ollama_client_with_config(self):
        """Initialize OllamaClient with Config object."""
        config = create_test_config()
        client = OllamaClient(config=config)

        assert client.base_url == "http://localhost:11434"
        assert client.model == "llama3"
        assert client.timeout == 300
        assert client.config.tailoring_temperature == 0.7

    def test_ollama_client_base_url_construction(self):
        """Verify base_url is correctly constructed from host/port."""
        config = create_test_config(
            host="api.example.com",
            port=8080,
            model="mistral",
        )
        client = OllamaClient(config=config)
        assert client.base_url == "http://api.example.com:8080"

    def test_ollama_client_model_override(self):
        """Allow model to be overridden after initialization."""
        config = create_test_config()
        client = OllamaClient(config=config)
        assert client.model == "llama3"

        client.model = "mistral"
        assert client.model == "mistral"


class TestOllamaExceptions:
    """Test exception classes."""

    def test_ollama_connection_error_creation(self):
        """Create OllamaConnectionError with message."""
        error = OllamaConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, Exception)

    def test_ollama_timeout_error_creation(self):
        """Create OllamaTimeoutError with message."""
        error = OllamaTimeoutError("Request timeout")
        assert str(error) == "Request timeout"
        assert isinstance(error, Exception)


class TestOllamaTestConnection:
    """Test Ollama connection testing."""

    @patch("requests.get")
    def test_test_connection_success(self, mock_get):
        """Test successful connection to Ollama."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "llama3"}]}
        mock_get.return_value = mock_response

        config = create_test_config()
        client = OllamaClient(config=config)
        result = client.test_connection()

        assert result is True
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_test_connection_failure(self, mock_get):
        """Test connection failure to Ollama."""
        mock_get.side_effect = requests.ConnectionError("Connection refused")

        config = create_test_config()
        client = OllamaClient(config=config)

        with pytest.raises(OllamaConnectionError):
            client.test_connection()

    @patch("requests.get")
    def test_test_connection_timeout(self, mock_get):
        """Test connection timeout."""
        mock_get.side_effect = requests.Timeout("Connection timeout")

        config = create_test_config()
        client = OllamaClient(config=config)

        with pytest.raises(OllamaTimeoutError):
            client.test_connection()


class TestOllamaGetModels:
    """Test getting available models from Ollama."""

    @patch("requests.get")
    def test_get_available_models_success(self, mock_get):
        """Get list of available models."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3:latest"},
                {"name": "mistral:latest"},
                {"name": "neural-chat:latest"},
            ]
        }
        mock_get.return_value = mock_response

        config = create_test_config()
        client = OllamaClient(config=config)
        models = client.get_available_models()

        assert len(models) == 3
        assert "llama3:latest" in models
        assert "mistral:latest" in models

    @patch("requests.get")
    def test_get_available_models_connection_error(self, mock_get):
        """Handle connection error when getting models."""
        mock_get.side_effect = requests.ConnectionError("Connection refused")

        config = create_test_config()
        client = OllamaClient(config=config)
        with pytest.raises(OllamaConnectionError):
            client.get_available_models()

    @patch("requests.get")
    def test_get_available_models_empty(self, mock_get):
        """Handle empty model list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response

        config = create_test_config()
        client = OllamaClient(config=config)
        models = client.get_available_models()

        assert models == []


class TestOllamaCallOllama:
    """Test making LLM calls to Ollama."""

    @patch("requests.post")
    def test_call_ollama_success(self, mock_post):
        """Successfully call Ollama API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "This is a test response."}
        mock_post.return_value = mock_response

        config = create_test_config()
        client = OllamaClient(config=config)
        response = client.call_ollama("What is Python?")

        assert response == "This is a test response."
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_call_ollama_with_temperature(self, mock_post):
        """Call Ollama with custom temperature."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Response"}
        mock_post.return_value = mock_response

        config = create_test_config()
        client = OllamaClient(config=config)
        client.call_ollama("Prompt", temperature=0.3)

        call_args = mock_post.call_args
        assert call_args.kwargs["json"]["options"]["temperature"] == 0.3

    @patch("requests.post")
    def test_call_ollama_with_max_tokens(self, mock_post):
        """Call Ollama with custom max_tokens."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Response"}
        mock_post.return_value = mock_response

        config = create_test_config()
        client = OllamaClient(config=config)
        client.call_ollama("Prompt", max_tokens=1000)

        call_args = mock_post.call_args
        assert call_args.kwargs["json"]["options"]["num_predict"] == 1000

    @patch("requests.post")
    def test_call_ollama_connection_error(self, mock_post):
        """Handle connection error during API call."""
        mock_post.side_effect = requests.ConnectionError("Connection refused")

        config = create_test_config()
        client = OllamaClient(config=config)
        with pytest.raises(OllamaConnectionError):
            client.call_ollama("Prompt")

    @patch("requests.post")
    def test_call_ollama_timeout_error(self, mock_post):
        """Handle timeout during API call."""
        mock_post.side_effect = requests.Timeout("Request timeout")

        config = create_test_config()
        client = OllamaClient(config=config)
        with pytest.raises(OllamaTimeoutError):
            client.call_ollama("Prompt")


class TestOllamaRetry:
    """Test Ollama calls with automatic retry logic."""

    @patch("requests.post")
    def test_retry_success_first_try(self, mock_post):
        """Succeed on first try without retries."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Success"}
        mock_post.return_value = mock_response

        config = create_test_config()
        client = OllamaClient(config=config)
        response = client.call_ollama_with_retry("Prompt", max_retries=3)

        assert response == "Success"
        assert mock_post.call_count == 1

    @patch("requests.post")
    def test_retry_success_after_transient_errors(self, mock_post):
        """Succeed after retries due to transient errors."""
        mock_post.side_effect = [
            requests.Timeout("Timeout"),
            requests.Timeout("Timeout"),
            Mock(status_code=200, json=lambda: {"response": "Success"}),
        ]

        config = create_test_config()
        client = OllamaClient(config=config)
        response = client.call_ollama_with_retry("Prompt", max_retries=3)

        assert response == "Success"
        assert mock_post.call_count == 3

    @patch("requests.post")
    def test_retry_exhausts_retries(self, mock_post):
        """Exhaust all retries on transient errors."""
        mock_post.side_effect = requests.Timeout("Timeout")

        config = create_test_config()
        client = OllamaClient(config=config)
        with pytest.raises(OllamaTimeoutError):
            client.call_ollama_with_retry("Prompt", max_retries=2)

        assert mock_post.call_count >= 2

    @patch("requests.post")
    def test_retry_with_custom_count(self, mock_post):
        """Test custom retry count."""
        mock_post.side_effect = requests.Timeout("Timeout")

        config = create_test_config()
        client = OllamaClient(config=config)
        with pytest.raises(OllamaTimeoutError):
            client.call_ollama_with_retry("Prompt", max_retries=5)

        assert mock_post.call_count >= 1
