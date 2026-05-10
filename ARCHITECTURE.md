# AI Resume Agent - Architecture & Implementation Plan

## Overview

Build AI-powered resume tailor agent using Python + Ollama (local LLM). The agent takes a job description as input and tailors your resume (summary, experience, skills) to match the position. Everything runs locally with no external APIs.

**Tech Stack:**
- Python 3.13
- Pydantic v2 (data validation)
- Ollama (local LLM via localhost:11434)
- Plain-text resume storage
- Modular package structure (ready for future UI)

**📊 Visual Documentation:**
- See [docs/WORKFLOW.drawio](docs/WORKFLOW.drawio) for the complete workflow diagram (editable in draw.io)
  - Shows config loading → Ollama connection → file parsing → parallel tailoring → output generation
  - Updated whenever significant changes are made to the codebase

---

## Project Phases

### Phase 1: ✅ Project Setup & Data Models
**Status:** COMPLETE

**Deliverables:**
- `src/models.py` — Pydantic models: Resume, Experience, Skill, JobDescription
- `src/storage.py` — Plain-text parser for resumes and job descriptions
- `src/config.py` — Ollama configuration (endpoint, model, temperature)
- `examples/my_resume.txt` — Sample resume template
- `examples/job_description.txt` — Sample job description
- Dependencies: pydantic, requests, python-dotenv, typer

**Resume Data Format (Plain Text):**
```
## PERSONAL
Name: Alex Johnson
Email: alex.johnson@email.com
Phone: +1-555-123-4567

## SUMMARY
[Professional summary - 2-3 sentences]

## EXPERIENCE
* Job Title at Company (Start - End)
  Description of role and achievements

## SKILLS
- Python, JavaScript, Go
- FastAPI, React, PostgreSQL
```

**Verification:** ✅ All imports successful, resume/job parsing validated

---

### Phase 2: ✅ Ollama Integration Layer
**Status:** COMPLETE

**Deliverables:**
- `src/llm_client.py` — Ollama client wrapper with connection management
  - `test_connection()` — Verify Ollama is running
  - `call_ollama(prompt, model)` — Send prompts to LLM
  - `call_ollama_with_retry()` — Automatic retry with exponential backoff
  - Error handling: `OllamaConnectionError`, `OllamaTimeoutError`
  
- `src/prompts.py` — Prompt templates for resume tailoring
  - `tailor_summary_prompt()` — Rewrite summary for job
  - `tailor_experience_prompt()` — Reorder and tailor experiences
  - `tailor_skills_prompt()` — Filter and rank skills
  - `evaluate_relevance_prompt()` — Assess resume-job fit

**Features:**
- Connection testing and model discovery
- Configurable temperature, max_tokens, timeout
- Retry logic with exponential backoff
- Comprehensive error handling
- Structured prompts for consistent LLM output

**Verification:**
```bash
uv run python3 -c "from src.llm_client import OllamaClient; client.test_connection()"
```

---

### Phase 3: ✅ Core Agent Logic
**Status:** COMPLETE

**Deliverables:**
- `src/resume_agent.py` — Main orchestration class `ResumeAgent`
  - `load_resume(file_path)` — Load resume from file
  - `load_job_description(file_path)` — Load job description
  - `tailor_summary()` — Generate tailored summary
  - `tailor_experience()` — Reorder and enhance experiences
  - `tailor_skills()` — Filter and rank skills
  - `evaluate_fit()` — Assess resume-job match
  - `generate_tailored_resume()` — Full end-to-end tailoring

**Features:**
- Orchestrates LLM client + prompt templates
- Parses LLM responses back into Pydantic models
- Handles parsing failures gracefully
- Comprehensive logging throughout
- Error handling with fallbacks

**Verification:** ✅ All methods callable, prompt generation verified

---

### Phase 4: ✅ CLI & Prototype Validation
**Status:** COMPLETE

**Deliverables:**
- `src/cli.py` — CLI application using Typer with 3 commands:
  - `tailor` — Main command to tailor resume to job
    - Options: `--resume`, `--job-description`, `--output`, `--model`, `--evaluate`
  - `test-ollama` — Test Ollama connection and list available models
  - `test-sample` — Quick test with sample files

- `main.py` — Entry point updated to invoke CLI

**Usage:**
```bash
# Main tailoring command
uv run python main.py tailor --resume my_resume.txt \
                             --job-description job.txt \
                             --output tailored_resume.txt

# Test Ollama connection
uv run python main.py test-ollama

# Quick test with samples
uv run python main.py test-sample

# Show help
uv run python main.py --help
uv run python main.py tailor --help
```

**Features:**
- Rich logging output with ✓ checkmarks and status indicators
- Proper error handling and exit codes
- Optional resume-job fit evaluation before tailoring
- Configurable Ollama model override
- Sample data testing

**Verification:** ✅ All CLI commands working, help text displays correctly

---

### Phase 5: Testing & Documentation
**Status:** NOT STARTED

**Tasks:**
1. Create `tests/` directory:
   - `test_storage.py` — Resume/job description parsing
   - `test_llm_client.py` — Ollama client with mocks
   - `test_resume_agent.py` — Agent logic

2. Create `PROTOTYPE_USAGE.md` — Quick start guide
3. Add docstrings throughout
4. Document plain-text format examples

**Verification:** `uv run pytest tests/`

---

## File Structure

```
ai-resume-agent/
├── src/
│   ├── __init__.py
│   ├── models.py                           # Pydantic models
│   ├── storage.py                          # Parsing utilities
│   ├── config.py                           # Configuration
│   ├── llm_client.py                       # Ollama integration (Phase 2)
│   ├── prompts.py                          # Prompt templates (Phase 2)
│   ├── resume_agent.py                     # Core logic (Phase 3)
│   └── cli.py                              # CLI interface (Phase 4)
├── examples/
│   ├── my_resume.txt.example               # ✅ Template (in git)
│   ├── my_resume.txt                       # ❌ User's personal data (git-ignored)
│   ├── job_description.txt.example         # ✅ Template (in git)
│   ├── job_description.txt                 # ❌ User's personal data (git-ignored)
│   └── tailored_*.txt                      # ❌ Generated (git-ignored)
├── tests/                                  # Unit tests (Phase 5)
├── main.py                                 # Entry point
├── pyproject.toml
├── .env.example                            # Configuration template (in git)
├── .env                                    # Local config (git-ignored)
├── .gitignore
├── ARCHITECTURE.md                         # This file
├── PROTOTYPE_USAGE.md                      # Usage guide (Phase 5)
└── README.md
```

**Git Strategy:**
- ✅ **In repository:** Source code, example templates (`.example`), config template (`.env.example`)
- ❌ **Git-ignored:** User's personal data, generated tailored resumes, user's `.env`, venv, cache

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Plain-text resume storage** | Human-editable, git-friendly, easy version control |
| **Pydantic models** | Type-safe validation, serialization to JSON/dict |
| **Modular architecture** | Enables future UI (Streamlit/FastAPI) without refactoring |
| **Ollama local-only** | No API keys, no cloud costs, privacy-preserving |
| **Tailor 3 sections MVP** | Summary + Experience + Skills (can expand later) |
| **File-based for prototype** | Can migrate to SQLite/PostgreSQL if needed |
| **Mistral 7B recommended** | Balance of speed + quality for feedback loops |

---

## Implementation Checklist

- [x] Phase 1: Models, storage, config
- [x] Phase 2: Ollama client, prompt templates
- [x] Phase 3: Resume agent orchestration
- [x] Phase 4: CLI interface
- [ ] Phase 5: Tests, docs, usage guide

---

## Future Extensions (Out of Scope for MVP)

- ❌ UI layer (Streamlit/web app) — **Phase 6 future**
- ❌ Database backend (SQLite/PostgreSQL) — **Future**
- ❌ Multi-user support / auth — **Future**
- ❌ Resume PDF parsing — **Future**
- ❌ LinkedIn API integration — **Future**
- ❌ Cloud deployment / Docker — **Future**

---

## Commands Reference

### Setup
```bash
uv sync              # Install dependencies
```

### Run
```bash
uv run python main.py --resume examples/my_resume.txt \
                      --job-description examples/job_description.txt \
                      --output tailored_resume.txt
```

### Test
```bash
uv run pytest tests/
```

### Development
```bash
# Run Phase 1 verification
uv run python3 << 'EOF'
from src.storage import load_resume_from_file, load_job_description_from_file
resume = load_resume_from_file('examples/my_resume.txt')
job = load_job_description_from_file('examples/job_description.txt')
print(f"Resume: {resume.name}")
print(f"Job: {job.title}")
EOF
```

---

## Notes

1. **Ollama Setup:** Ensure Ollama is running locally (`ollama serve`)
2. **Model Selection:** Start with Mistral 7B, benchmark, upgrade if needed
3. **Prompt Iteration:** Tailor quality depends on prompt clarity—iterate based on output
4. **Error Handling:** Both storage parsing and LLM calls need robust error handling
