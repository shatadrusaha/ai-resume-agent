# AI Resume Agent - Architecture & Implementation Plan

## Overview

Build AI-powered resume tailor agent using Python + Ollama (local LLM). The agent takes a job description as input and tailors your resume (summary, experience, skills) to match the position. Everything runs locally with no external APIs.

**Tech Stack:**
- Python 3.13
- Pydantic v2 (data validation)
- Ollama (local LLM via localhost:11434)
- Plain-text resume storage
- Modular package structure (ready for future UI)

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

### Phase 3: Core Agent Logic
**Status:** NOT STARTED

**Tasks:**
1. Create `src/resume_agent.py`:
   ```python
   class ResumeAgent:
       def load_resume(file_path: str) -> Resume
       def tailor_summary(resume, job_desc) -> str
       def tailor_experience(resume, job_desc) -> List[Experience]
       def tailor_skills(resume, job_desc) -> List[Skill]
       def generate_tailored_resume(resume, job_desc) -> Resume
   ```

2. Orchestrate LLM calls using prompts
3. Parse LLM responses back into Pydantic models
4. Handle formatting inconsistencies from LLM output

**Verification:** Manual testing with sample resume + job description

---

### Phase 4: CLI & Prototype Validation
**Status:** NOT STARTED

**Tasks:**
1. Create `src/cli.py`:
   - Arguments: `--resume FILE`, `--job-description FILE`, `--output FILE`, `--model NAME`
   - Output tailored resume to file or stdout

2. Update `main.py`:
   ```bash
   uv run python main.py --resume examples/my_resume.txt \
                         --job-description examples/job_description.txt \
                         --output tailored_resume.txt
   ```

3. End-to-end testing

**Verification:** CLI works with sample files

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
│   ├── models.py              # Pydantic models
│   ├── storage.py             # Parsing utilities
│   ├── config.py              # Configuration
│   ├── llm_client.py          # Ollama integration (Phase 2)
│   ├── prompts.py             # Prompt templates (Phase 2)
│   ├── resume_agent.py        # Core logic (Phase 3)
│   └── cli.py                 # CLI interface (Phase 4)
├── examples/
│   ├── my_resume.txt
│   └── job_description.txt
├── tests/                     # Unit tests (Phase 5)
├── main.py                    # Entry point
├── pyproject.toml
├── .env.example               # Configuration template
├── .env                       # Local config (git-ignored)
├── .gitignore
├── ARCHITECTURE.md            # This file
├── PROTOTYPE_USAGE.md         # Usage guide (Phase 5)
└── README.md
```

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
- [ ] Phase 3: Resume agent orchestration
- [ ] Phase 4: CLI interface
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
