# Developer Setup Guide

Step-by-step instructions for setting up the AI Resume Agent project locally for development or contribution.

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.13.x | Runtime |
| [uv](https://docs.astral.sh/uv/) | Latest | Package manager |
| [Ollama](https://ollama.com) | Latest | Local LLM engine |
| Git | Any | Version control |

---

## 1. Install uv

If you don't have `uv` installed:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS (Homebrew)
brew install uv

# Verify
uv --version
```

---

## 2. Clone the Repository

```bash
git clone https://github.com/shatadrusaha/ai-resume-agent.git
cd ai-resume-agent
```

---

## 3. Install Dependencies

`uv` reads `pyproject.toml` and creates a virtual environment automatically:

```bash
uv sync
```

This installs all runtime **and** dev dependencies (pytest, pytest-cov, etc.) into `.venv/`.

> **Note:** Never use `pip install` directly. Always use `uv add` or `uv sync`.

---

## 4. Install and Start Ollama

### Install Ollama

Download and install the Ollama desktop app directly from the official site:

**[https://ollama.com/download](https://ollama.com/download)**

Choose your platform (macOS, Linux, or Windows) and follow the installer instructions. The desktop app also starts the Ollama server automatically.

> Do not use Homebrew for Ollama — the direct installer is the recommended approach.

### Pull a Model

Once Ollama is installed and running:

```bash
ollama pull llama3
```

> Other supported models: `mistral`, `neural-chat`, `codellama`. The default is `llama3`.

### Verify Ollama is Running

```bash
curl http://localhost:11434/api/tags
```

You should see a JSON response listing your installed models.

---

## 5. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` if you need non-default settings:

```bash
# .env (defaults shown)
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=llama3
OLLAMA_TIMEOUT=300
TAILORING_TEMPERATURE=0.7
TAILORING_MAX_TOKENS=2000
```

---

## 6. Verify Setup

Test Ollama connection:

```bash
uv run python main.py test-ollama
```

Run the full test suite to confirm everything is working:

```bash
uv run pytest
```

Expected: **63 tests passed**, ~73% coverage.

---

## 7. Prepare Example Files and Run

```bash
# Copy example files to working copies
cp examples/my_resume.txt.example examples/my_resume.txt
cp examples/job_description.txt.example examples/job_description.txt

# Edit them with your own content, then tailor
uv run python main.py tailor \
  --resume examples/my_resume.txt \
  --job-description examples/job_description.txt \
  --output tailored_resume.txt
```

---

## Adding Dependencies

```bash
# Runtime dependency
uv add package-name

# Dev-only dependency (tests, linting, etc.)
uv add --dev package-name
```

This updates `pyproject.toml` automatically. Commit `pyproject.toml` after adding dependencies.

> Never use `pip install` directly — always use `uv add` or `uv sync`.

---

## Code Style

- **Python 3.13** with full type hints throughout
- **Google-style docstrings** on all public functions and classes — see [DOCSTRING_GUIDE.md](DOCSTRING_GUIDE.md)
- **Pydantic v2** for all data models — use `BaseModel`, not dataclasses
- **`uv add` / `uv sync`** for dependency management — not `pip`

---

## Further Reading

- [ARCHITECTURE.md](ARCHITECTURE.md) — System design and phase overview
- [EXECUTION_FLOW.md](EXECUTION_FLOW.md) — Step-by-step code execution walkthrough
- [TESTING.md](TESTING.md) — Test structure and how to write new tests
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common errors and fixes
