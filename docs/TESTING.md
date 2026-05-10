# Testing Guide

This project uses **pytest** with **pytest-cov** for unit testing and coverage reporting. All tests run without requiring Ollama to be running — external dependencies are mocked.

---

## Quick Start

```bash
# Run all tests
uv run pytest

# Run a specific test file
uv run pytest tests/test_storage.py

# Run a specific test class
uv run pytest tests/test_storage.py::TestParseResumeFromText

# Run a specific test
uv run pytest tests/test_storage.py::TestParseResumeFromText::test_parse_resume_basic

# Run tests without coverage (faster)
uv run pytest --no-cov
```

---

## Test Results Overview

```
63 tests passed  |  0 failed  |  73% overall coverage
```

| File | Tests | Coverage |
|------|-------|----------|
| `tests/test_storage.py` | 23 | `src/storage.py` → 99% |
| `tests/test_llm_client.py` | 20 | `src/llm_client.py` → 76% |
| `tests/test_resume_agent.py` | 20 | `src/resume_agent.py` → 90% |

---

## Test File Breakdown

### `tests/conftest.py` — Shared Fixtures

Provides reusable test data for all test files. No tests live here — it only defines **pytest fixtures** that other test files use automatically.

| Fixture | Type | Description |
|---------|------|-------------|
| `sample_resume_text` | `str` | Plain-text resume in the standard `## SECTION` format |
| `sample_job_description_text` | `str` | Plain-text job description in the standard format |
| `sample_resume` | `Resume` | Pre-built Resume Pydantic object |
| `sample_job_description` | `JobDescription` | Pre-built JobDescription Pydantic object |
| `tmp_resume_file` | `Path` | Temporary resume file on disk (auto-deleted after test) |
| `tmp_job_description_file` | `Path` | Temporary job description file on disk |

To use a fixture in a test, just declare it as a parameter:

```python
def test_something(self, sample_resume):  # fixture injected automatically
    assert sample_resume.name == "Alex Johnson"
```

---

### `tests/test_storage.py` — File Parsing Tests

Tests the `src/storage.py` module: parsing plain-text files into Pydantic objects and saving them back to disk.

**Test Classes:**

| Class | What It Tests |
|-------|---------------|
| `TestParseResumeFromText` | Parsing name, email, summary, experiences, skills from text |
| `TestLoadResumeFromFile` | Loading resume from a file path, handling missing files |
| `TestSaveResumeToFile` | Saving resume to file, round-trip (save then reload) |
| `TestParseJobDescriptionFromText` | Parsing title, company, requirements, responsibilities |
| `TestLoadJobDescriptionFromFile` | Loading job description from file, handling missing files |

**Key edge cases covered:**
- Resume missing a `## SUMMARY` section → empty string, no crash
- Invalid email format → raises `ValueError`
- File not found → raises `FileNotFoundError`
- Save and reload preserves all data correctly

---

### `tests/test_llm_client.py` — Ollama Client Tests

Tests the `src/llm_client.py` module. **All HTTP calls are mocked** with `unittest.mock.patch`, so Ollama does not need to be running.

**Test Classes:**

| Class | What It Tests |
|-------|---------------|
| `TestOllamaClientInit` | Client initialization, base URL construction, model override |
| `TestOllamaExceptions` | `OllamaConnectionError` and `OllamaTimeoutError` creation |
| `TestOllamaTestConnection` | Connection success, `ConnectionError`, `Timeout` cases |
| `TestOllamaGetModels` | Listing models, connection errors, empty list |
| `TestOllamaCallOllama` | Successful LLM call, temperature/max_tokens parameters, errors |
| `TestOllamaRetry` | Retry logic — first try success, retry after timeout, exhausted retries |

**How mocking works:**

```python
@patch("requests.post")          # intercepts all requests.post calls
def test_call_ollama_success(self, mock_post):
    mock_post.return_value = Mock(
        status_code=200,
        json=lambda: {"response": "Mocked LLM response"}
    )
    # Call real code — it calls requests.post, which hits the mock
    result = client.call_ollama("Prompt")
    assert result == "Mocked LLM response"
```

---

### `tests/test_resume_agent.py` — Agent Orchestration Tests

Tests the `src/resume_agent.py` module — the core orchestration class that coordinates file loading, LLM calls, and result assembly. **The OllamaClient is mocked** so no real LLM calls are made.

**Test Classes:**

| Class | What It Tests |
|-------|---------------|
| `TestResumeAgentInit` | Default and custom client initialization |
| `TestResumeAgentLoadResume` | Loading resume files, missing file errors |
| `TestResumeAgentLoadJobDescription` | Loading job description files, missing file errors |
| `TestResumeAgentTailorSummary` | Summary tailoring success and connection errors |
| `TestResumeAgentTailorExperience` | Experience tailoring, fallback to original on parse failure |
| `TestResumeAgentTailorSkills` | Skills tailoring, empty response handling |
| `TestResumeAgentEvaluateFit` | Fit evaluation success, connection error graceful return |
| `TestResumeAgentGenerateTailoredResume` | Full tailoring pipeline, contact info preservation |
| `TestResumeAgentParsingMethods` | Internal parsing of LLM output (experience, skills, evaluation) |

**How the agent is mocked:**

```python
mock_client = Mock(spec=OllamaClient)
mock_client.call_ollama_with_retry.return_value = "Tailored summary text."

agent = ResumeAgent(ollama_client=mock_client)
result = agent.tailor_summary(resume, job)

assert result == "Tailored summary text."
```

---

## Coverage Report

Run tests with coverage (enabled by default in config):

```bash
uv run pytest
```

For an HTML report you can open in a browser:

```bash
uv run pytest --cov-report=html
open htmlcov/index.html
```

**Current coverage by module:**

| Module | Coverage | Notes |
|--------|----------|-------|
| `src/__init__.py` | 100% | |
| `src/prompts.py` | 100% | |
| `src/storage.py` | 99% | |
| `src/config.py` | 97% | |
| `src/resume_agent.py` | 90% | Some error branches |
| `src/llm_client.py` | 76% | HTTP error edge cases |
| `src/models.py` | 49% | `__str__` methods not directly tested |
| `src/cli.py` | 0% | Requires integration tests (Phase 6) |

---

## Configuration

pytest is configured in `pyproject.toml` — no separate `pytest.ini` needed:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --cov=src --cov-report=term-missing"
pythonpath = ["."]
```

| Option | Purpose |
|--------|---------|
| `testpaths` | Only look in `tests/` directory |
| `addopts` | Always run verbose with coverage |
| `pythonpath = ["."]` | Makes `src/` importable as a package |

---

## Writing New Tests

### 1. Place tests in `tests/`

Name files `test_<module>.py`. Each file maps to one source module.

### 2. Use test classes

Group related tests in a class named `Test<Feature>`:

```python
class TestMyFeature:
    def test_happy_path(self, sample_resume):
        ...

    def test_error_case(self):
        ...
```

### 3. Use fixtures from conftest.py

```python
def test_something(self, sample_resume, sample_job_description):
    # fixtures are injected automatically
```

### 4. Mock external dependencies

Never call real Ollama or real files in unit tests:

```python
from unittest.mock import Mock, patch

@patch("requests.post")
def test_api_call(self, mock_post):
    mock_post.return_value = Mock(status_code=200, json=lambda: {"response": "..."})
    ...
```

### 5. Follow Google-style docstrings

Each test method needs a one-line docstring:

```python
def test_parse_resume_name_extraction(self, sample_resume_text):
    """Verify name is correctly extracted from PERSONAL section."""
    ...
```

---

## Resources

- [pytest documentation](https://docs.pytest.org)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io)
- [DOCSTRING_GUIDE.md](DOCSTRING_GUIDE.md) — Docstring standards for this project
