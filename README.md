# AI Resume Agent

An AI-powered agent that tailors your resume to job descriptions using **local LLMs via Ollama**. No cloud APIs, no external services—everything runs on your machine.

## What It Does

✅ **Takes** your master resume + a job description  
✅ **Tailors** your Summary, Experience, and Skills  
✅ **Outputs** a job-specific resume  
✅ **Runs locally** with Ollama (privacy-friendly, no API keys)

## Quick Start

### Prerequisites

- Python 3.13
- [Ollama](https://ollama.ai) running locally: `ollama serve`
- `uv` package manager

### Setup & Run

```bash
# 1. Install dependencies
uv sync

# 2. Configure Ollama settings
cp .env.example .env

# 3. Copy example files and fill in your own details
cp examples/my_resume.txt.example examples/my_resume.txt
cp examples/job_description.txt.example examples/job_description.txt

# 4. Edit your files
# - examples/my_resume.txt — your master resume
# - examples/job_description.txt — the job you're applying for

# 5. Tailor your resume
uv run python main.py tailor \
  --resume examples/my_resume.txt \
  --job-description examples/job_description.txt \
  --output tailored_resume.txt
```

That's it! Your tailored resume is saved to `tailored_resume.txt`.

## Resume Format

Store your master resume as plain text with clear sections:

```
## PERSONAL
Name: Your Name
Email: your@email.com
Phone: +1-234-567-8900

## SUMMARY
[2-3 sentences about your professional background]

## EXPERIENCE
* Job Title at Company (Start - End)
  Description of role, achievements, and metrics
  
* Another Job Title at Company (Start - End)
  Details here

## SKILLS
- Python, JavaScript, Go, SQL
- FastAPI, React, PostgreSQL
- System Design, Leadership
```

See [examples/my_resume.txt.example](examples/my_resume.txt.example) for a full example.

## Configuration

Copy `.env.example` to `.env` and customize as needed:

```bash
cp .env.example .env
```

**Available settings** (in `.env`):
- `OLLAMA_HOST` — Ollama server host (default: `localhost`)
- `OLLAMA_PORT` — Ollama server port (default: `11434`)
- `OLLAMA_MODEL` — LLM model name (default: `llama3`; try `mistral`, `llama2`, `neural-chat`, etc.)
- `OLLAMA_TIMEOUT` — Request timeout in seconds (default: `300`)
- `TAILORING_TEMPERATURE` — LLM creativity level 0.0-1.0 (default: `0.7`)
- `TAILORING_MAX_TOKENS` — Max generated text length (default: `2000`)
- `TAILORING_CONTEXT_WINDOW` — LLM context size (default: `4096`)

Settings default to sensible values if `.env` is missing.

## Project Structure

```
.
├── main.py                      # Entry point for CLI
├── pyproject.toml               # uv project config, dependencies, pytest settings
├── .env.example                 # Environment variables template
├── README.md                    # Project documentation
├── LICENSE                      # MIT license
│
src/
├── models.py                    # Pydantic data models (Skill, Experience, Resume, JobDescription)
├── storage.py                   # Parse & save resume/job description files
├── config.py                    # Configuration management (BaseSettings with lazy singleton)
├── llm_client.py                # Ollama HTTP client & error handling
├── prompts.py                   # LLM prompt templates
├── resume_agent.py              # Core tailoring orchestration
└── cli.py                       # Typer CLI (tailor, test-ollama, test-sample commands)

tests/
├── conftest.py                  # pytest fixtures (sample data, temp files)
├── test_models.py               # [Not in use - models are simple data classes]
├── test_storage.py              # 8 test classes, 23 tests, 99% coverage
├── test_llm_client.py           # 6 test classes, 20 tests, 76% coverage
└── test_resume_agent.py         # 9 test classes, 20 tests, 90% coverage

examples/
├── my_resume.txt.example            # Template — copy to my_resume.txt and customize
├── job_description.txt.example      # Template — copy to job_description.txt and customize
├── tailored_sample_resume.txt       # Output from `test-sample` command (git ignored)
└── my_resume.txt                    # [User creates — git ignored]
    job_description.txt             # [User creates — git ignored]

docs/
├── ARCHITECTURE.md              # Project design, phases 1-5, future roadmap
├── TESTING.md                   # Test guide, coverage report, how to write tests
├── DEV_SETUP.md                 # Contributor setup: uv, Ollama, .env, dependencies
├── TROUBLESHOOTING.md           # Common errors & solutions
├── DOCSTRING_GUIDE.md           # Google-style docstring standard for this project
├── EXECUTION_FLOW.md            # Step-by-step walkthrough of CLI tailor command
└── WORKFLOW.drawio              # Visual workflow diagram (open in draw.io)
```

## Architecture & Implementation Plan

For detailed implementation phases, design decisions, and future extensions, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

**Current Status:**
- ✅ Phase 1: Data models & storage
- ✅ Phase 2: Ollama integration
- ✅ Phase 3: Core agent logic
- ✅ Phase 4: CLI interface
- ✅ Phase 5: Tests & documentation

## Development

For full contributor setup instructions, code style conventions, and how to add dependencies, see [docs/DEV_SETUP.md](docs/DEV_SETUP.md).

For common errors and fixes, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Requirements

- **Ollama must be running** locally on `localhost:11434`
- Recommended models: **llama3** (tested & working), **mistral** (fast), **llama2** (higher quality)
- Download a model: `ollama pull llama3`

## Roadmap

- ✅ Phase 1: Core data structures
- ✅ Phase 2: LLM integration
- ✅ Phase 3: Resume tailoring logic
- ✅ Phase 4: CLI interface
- ✅ Phase 5: Testing & documentation
- 🚀 Future: Streamlit UI, PDF support, database backend

## License

MIT — See [LICENSE](LICENSE)

## Contributing

PRs welcome! See [docs/DEV_SETUP.md](docs/DEV_SETUP.md) for contributor setup and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for design details.
