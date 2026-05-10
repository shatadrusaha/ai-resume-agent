# Execution Flow Walkthrough

This document explains **exactly** what happens when you run the resume tailoring command — step by step, function by function. Use this as a reference when debugging or understanding how the code works.

**Command being traced:**
```bash
uv run python main.py tailor -r examples/my_resume.txt -j examples/job_description.txt -o tailored_resume.txt
```

---

## Table of Contents
1. [Entry Point — main.py](#1-entry-point--mainpy)
2. [CLI Parses Arguments — cli.py](#2-cli-parses-arguments--clipy)
3. [Configuration Loads — config.py](#3-configuration-loads--configpy)
4. [Agent Initializes — resume_agent.py](#4-agent-initializes--resume_agentpy)
5. [Ollama Connection Check — llm_client.py](#5-ollama-connection-check--llm_clientpy)
6. [Resume File is Parsed — storage.py](#6-resume-file-is-parsed--storagepy)
7. [Job Description is Parsed — storage.py](#7-job-description-is-parsed--storagepy)
8. [Tailoring Begins — resume_agent.py](#8-tailoring-begins--resume_agentpy)
9. [Summary is Tailored](#9-summary-is-tailored)
10. [Experiences are Tailored](#10-experiences-are-tailored)
11. [Skills are Tailored](#11-skills-are-tailored)
12. [Final Resume is Assembled and Saved](#12-final-resume-is-assembled-and-saved)
13. [Error Reference Guide](#13-error-reference-guide)

---

## 1. Entry Point — `main.py`

**File:** `main.py`

```python
from src.cli import app

if __name__ == "__main__":
    app()
```

**What happens:**
- Python runs `main.py`
- It imports the `app` object from `src/cli.py`
- `app()` is called — this hands control over to the Typer CLI framework
- Typer reads your command-line arguments (`tailor`, `-r`, `-j`, `-o`) and routes execution to the `tailor()` function in `cli.py`

**Think of it like:** A front door. All it does is open the door and point you to the right room.

---

## 2. CLI Parses Arguments — `cli.py`

**File:** `src/cli.py` → `tailor()` function

```python
@app.command()
def tailor(
    resume: str = typer.Option(..., "--resume", "-r", ...),
    job_description: str = typer.Option(..., "--job-description", "-j", ...),
    output: str = typer.Option("tailored_resume.txt", "--output", "-o", ...),
    model: str = typer.Option(None, "--model", "-m", ...),
    evaluate: bool = typer.Option(False, "--evaluate", "-e", ...),
):
```

**What happens:**
- Typer captures the values you passed in the terminal:
  - `resume = "examples/my_resume.txt"`
  - `job_description = "examples/job_description.txt"`
  - `output = "tailored_resume.txt"`
  - `model = None` (not passed, so defaults to `None`)
  - `evaluate = False` (not passed, so defaults to `False`)
- Typer also **validates** that the file paths exist. If `-r bad_path.txt` is given and the file doesn't exist, it stops here with an error before any code runs.

**Think of it like:** A receptionist who checks your ID and reads your request form before letting you through.

---

## 3. Configuration Loads — `config.py`

**File:** `src/config.py` — triggered automatically when `OllamaClient()` is created

```python
class AppSettings(BaseSettings):
    ollama_host: str = Field(default="localhost")
    ollama_port: int = Field(default=11434)
    ollama_model: str = Field(default="mistral")
    ...

    model_config = SettingsConfigDict(env_file=".env")
```

**What happens:**
1. Pydantic's `BaseSettings` automatically reads your `.env` file
2. It maps each variable: `OLLAMA_HOST` → `ollama_host`, `OLLAMA_MODEL` → `ollama_model`, etc.
3. It converts types: `"11434"` (string in .env) → `11434` (integer in Python)
4. `AppConfig` is built from `AppSettings`, creating two nested objects:
   - `config.ollama` → host, port, model, timeout, base_url
   - `config.tailoring` → temperature, max_tokens, context_window

**What the config looks like after loading:**
```
config.ollama.host         = "localhost"
config.ollama.port         = 11434
config.ollama.model        = "llama3"       ← from your .env
config.ollama.base_url     = "http://localhost:11434"
config.tailoring.temperature   = 0.7
config.tailoring.max_tokens    = 2000
```

**Potential error here:** If `.env` has a typo like `OLLAMA_PORT=abc`, Pydantic will fail with a `ValidationError` because `abc` can't be converted to an integer.

---

## 4. Agent Initializes — `resume_agent.py`

**File:** `src/resume_agent.py` → `ResumeAgent.__init__()`

```python
class ResumeAgent:
    def __init__(self, ollama_client=None):
        self.ollama_client = ollama_client or OllamaClient()
        logger.info("ResumeAgent initialized")
```

**What happens:**
1. `ResumeAgent()` is called with no arguments
2. Since `ollama_client=None`, it creates a new `OllamaClient()`
3. `OllamaClient.__init__()` reads the config:
   - Sets `self.base_url = "http://localhost:11434"`
   - Sets `self.model = "llama3"`
   - Sets `self.timeout = 300`
4. You see in the terminal: `INFO: ResumeAgent initialized`

**Think of it like:** Setting up your workstation before starting work. You're loading your tools and making sure you know where everything is.

---

## 5. Ollama Connection Check — `llm_client.py`

**File:** `src/llm_client.py` → `test_connection()`

```python
def test_connection(self) -> bool:
    response = requests.get(
        f"{self.base_url}/api/tags",  # → http://localhost:11434/api/tags
        timeout=5,
    )
    response.raise_for_status()
    logger.info(f"✓ Connected to Ollama at {self.base_url}")
    return True
```

**What happens:**
1. Sends an HTTP GET request to `http://localhost:11434/api/tags`
2. This is Ollama's API endpoint that lists all available models
3. If Ollama is running → returns HTTP 200 → logs "✓ Connected"
4. If Ollama is NOT running → `ConnectionError` is raised → program stops with a clear error message

**Think of it like:** Calling a colleague to check if they're at their desk before sending them a task.

**Potential errors here:**
| Error | Cause | Fix |
|-------|-------|-----|
| `OllamaConnectionError` | Ollama not running | Run `ollama serve` in a terminal |
| `OllamaTimeoutError` | Connection timed out (5s) | Check if Ollama is slow to start |

---

## 6. Resume File is Parsed — `storage.py`

**File:** `src/storage.py` → `load_resume_from_file()` → `parse_resume_from_text()`

**Step 1:** Read the file
```python
def load_resume_from_file(file_path: str) -> Resume:
    text = Path(file_path).read_text(encoding="utf-8")
    return parse_resume_from_text(text)
```

**Step 2:** Split text into sections
```python
def _split_sections(text: str) -> dict:
    # Splits on "## PERSONAL", "## SUMMARY", "## EXPERIENCE", "## SKILLS"
```

Given:
```
## PERSONAL
Name: Alex Johnson
Email: alex.johnson@email.com

## SUMMARY
Highly accomplished engineer...

## EXPERIENCE
* Senior Engineer at TechCorp (Mar 2021 - Present)
  Led redesign of payment services...
```

Produces:
```python
sections = {
    "PERSONAL":    "Name: Alex Johnson\nEmail: alex.johnson@email.com",
    "SUMMARY":     "Highly accomplished engineer...",
    "EXPERIENCE":  "* Senior Engineer at TechCorp...",
    "SKILLS":      "- Python, Go, Kubernetes...",
}
```

**Step 3:** Extract fields using regex (pattern matching)
```python
# Example: Extracting name from "Name: Alex Johnson"
name_match = re.search(r"Name:\s*(.+)", personal, re.IGNORECASE)
name = name_match.group(1).strip()  # → "Alex Johnson"
```

**Step 4:** Build a `Resume` Pydantic model
```python
return Resume(
    name="Alex Johnson",
    email="alex.johnson@email.com",
    phone="+1-555-123-4567",
    summary="Highly accomplished engineer...",
    experience=[Experience(...), Experience(...), Experience(...)],
    skills=[Skill(name="Python"), Skill(name="Go"), ...],
)
```

**What you see in terminal:**
```
INFO: Loading resume from examples/my_resume.txt
INFO: Loaded resume for Alex Johnson with 3 experiences
```

**Potential errors here:**
| Error | Cause | Fix |
|-------|-------|-----|
| `FileNotFoundError` | Wrong file path | Check `-r` argument |
| Missing fields | Resume format wrong | Check `## PERSONAL`, `## EXPERIENCE` headers exist |
| Pydantic `ValidationError` | Invalid email format | Fix email in resume file |

---

## 7. Job Description is Parsed — `storage.py`

**File:** `src/storage.py` → `load_job_description_from_file()` → `parse_job_description_from_text()`

Same process as the resume, but for the job description file. It produces a `JobDescription` object:

```python
JobDescription(
    title="Staff Backend Engineer",
    company="CloudInnovate Solutions",
    description="We are looking for a...",
    required_skills=["Go", "Kubernetes", "AWS", "PostgreSQL", ...],
    responsibilities=["Lead architecture decisions", "Mentor engineers", ...],
)
```

**What you see in terminal:**
```
INFO: Loading job description from examples/job_description.txt
INFO: Loaded job: Staff Backend Engineer at CloudInnovate Solutions
```

---

## 8. Tailoring Begins — `resume_agent.py`

**File:** `src/resume_agent.py` → `generate_tailored_resume()`

```python
def generate_tailored_resume(self, resume: Resume, job_description: JobDescription) -> Resume:
    logger.info(f"Generating tailored resume for {job_description.title}...")

    tailored_summary     = self.tailor_summary(resume, job_description)
    tailored_experiences = self.tailor_experience(resume, job_description)
    tailored_skills      = self.tailor_skills(resume, job_description)

    # Assemble new Resume object from tailored parts
    tailored_resume = Resume(name=resume.name, ..., summary=tailored_summary, ...)
    return tailored_resume
```

**What happens:**
- Three tailoring functions are called **sequentially** (one after another, not at the same time)
- Each one calls the LLM and parses the response
- Results are assembled into a new `Resume` object at the end

---

## 9. Summary is Tailored

**File:** `src/resume_agent.py` → `tailor_summary()` + `src/prompts.py` + `src/llm_client.py`

### Step 1: Build the prompt
```python
prompt = PromptTemplates.tailor_summary_prompt(resume, job_description)
```

The prompt is a long text string that tells the LLM what to do. It contains:
- The job title and description
- Required skills from the job
- The current resume summary
- Instructions: "Rewrite in 2-3 sentences, use these keywords, match this tone"

The full prompt looks like this (simplified):
```
You are an expert resume writer. Tailor this summary to the job.

JOB: Staff Backend Engineer at CloudInnovate Solutions
REQUIRED SKILLS: Go, Kubernetes, AWS, PostgreSQL

CURRENT SUMMARY:
Experienced software engineer with 8+ years...

Please rewrite the summary to highlight relevant experience.
Return ONLY the new summary text.
```

### Step 2: Send prompt to Ollama
```python
tailored_summary = self.ollama_client.call_ollama_with_retry(prompt, max_retries=3)
```

Inside `call_ollama_with_retry()`:
1. Tries up to 3 times if there's a transient error
2. Calls `call_ollama()` internally

Inside `call_ollama()`:
```python
payload = {
    "model": "llama3",
    "prompt": "You are an expert resume writer...",
    "stream": False,
    "options": {
        "temperature": 0.7,   # Higher = more creative, lower = more predictable
        "num_predict": 2000,  # Max words to generate
    }
}

response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=300)
generated_text = response.json()["response"].strip()
```

### Step 3: Return result
The LLM returns a plain text string like:
```
"Highly accomplished Staff Backend Engineer with 8+ years designing scalable distributed systems. Proficient in Go and Kubernetes with expertise in cloud platforms (AWS, GCP). Proven track record of leading architecture decisions and mentoring teams in fast-paced environments."
```

**What you see in terminal:**
```
INFO: Tailoring summary...
INFO: Summary tailored (411 chars)
```

---

## 10. Experiences are Tailored

**File:** `src/resume_agent.py` → `tailor_experience()` → `_parse_experience_from_text()`

Same LLM flow as summary, but:
1. The prompt includes ALL your experience entries
2. The LLM rewrites each one to emphasize skills relevant to the job
3. The LLM returns structured text like:
   ```
   Position 1: Senior Engineer at TechCorp (Mar 2021 - Present)
   Description: Led redesign of payment processing using Kubernetes and Go...

   Position 2: Software Engineer at DataSystems Inc (Jan 2019 - Feb 2021)
   Description: Designed scalable microservices using Go and PostgreSQL...
   ```
4. `_parse_experience_from_text()` uses regex to extract each `Position N:` block and convert it back into `Experience` Pydantic objects

**What you see in terminal:**
```
INFO: Tailoring experience...
INFO: Parsed 2 tailored experiences
```

> **Note:** If the LLM gives an unexpected format, the regex may not match → parser falls back to the original experiences and logs a warning.

---

## 11. Skills are Tailored

**File:** `src/resume_agent.py` → `tailor_skills()` → `_parse_skills_from_text()`

1. Prompt includes your full skills list + job's required skills
2. LLM reorders and filters them by relevance to the job
3. LLM returns a comma-separated string:
   ```
   "Go, Kubernetes, AWS, PostgreSQL, Docker, Python, Leadership, System Design, Redis, CI/CD"
   ```
4. `_parse_skills_from_text()` splits by comma and creates `Skill` objects for each

**What you see in terminal:**
```
INFO: Tailoring skills...
INFO: Parsed 15 tailored skills
```

---

## 12. Final Resume is Assembled and Saved

**File:** `src/resume_agent.py` → `generate_tailored_resume()`, then `src/cli.py` → `save_resume_to_file()`

### Assembling the new Resume
```python
tailored_resume = Resume(
    name=resume.name,                  # unchanged: "Alex Johnson"
    email=resume.email,                # unchanged: "alex.johnson@email.com"
    phone=resume.phone,                # unchanged: "+1-555-123-4567"
    summary=tailored_summary,          # ← new tailored summary
    experience=tailored_experiences,   # ← new tailored experiences
    skills=tailored_skills,            # ← new tailored skills
)
```

### Saving to file
```python
save_resume_to_file(tailored_resume, output)
```

The `save_resume_to_file()` function converts the `Resume` object back into plain text format:
```
## PERSONAL
Name: Alex Johnson
Email: alex.johnson@email.com

## SUMMARY
Highly accomplished Staff Backend Engineer...

## EXPERIENCE
* Senior Engineer at TechCorp (Mar 2021 - Present)
  Led redesign of payment processing...

## SKILLS
- Go, Kubernetes, AWS, PostgreSQL...
```

**What you see in terminal:**
```
INFO: 💾 Saving tailored resume to tailored_resume.txt
INFO: ✅ Success! Tailored resume saved to tailored_resume.txt
```

---

## 13. Error Reference Guide

Use this when you see an error you don't understand.

### Configuration Errors
| Error Message | Where it happens | Cause | Fix |
|---|---|---|---|
| `ValidationError: value is not a valid integer` | `config.py` on startup | Bad value in `.env` (e.g. `OLLAMA_PORT=abc`) | Fix the `.env` value |
| `FileNotFoundError: .env` | `config.py` on startup | `.env` file missing | Copy `.env.example` to `.env` |

### Connection Errors
| Error Message | Where it happens | Cause | Fix |
|---|---|---|---|
| `OllamaConnectionError: Failed to connect to Ollama` | `llm_client.py` → `test_connection()` | Ollama not running | Run `ollama serve` |
| `OllamaConnectionError: Model 'x' not found` | `llm_client.py` → `call_ollama()` | Model not downloaded | Run `ollama pull llama3` |
| `OllamaTimeoutError: Request timed out after 300s` | `llm_client.py` → `call_ollama()` | LLM took too long | Increase `OLLAMA_TIMEOUT` in `.env` or use a faster model |

### File Errors
| Error Message | Where it happens | Cause | Fix |
|---|---|---|---|
| `Error: Invalid value for '--resume'` | `cli.py` arg parsing | File path doesn't exist | Check the `-r` path |
| `FileNotFoundError: examples/job_description.txt` | `storage.py` | Wrong job desc path | Check the `-j` path |

### Parsing Warnings (not errors — program continues)
| Warning Message | Where it happens | Cause | What happens |
|---|---|---|---|
| `WARNING: Could not parse experiences from LLM output` | `resume_agent.py` → `_parse_experience_from_text()` | LLM returned unexpected format | Falls back to original experiences |
| `WARNING: Parsed 0 tailored skills` | `resume_agent.py` → `_parse_skills_from_text()` | LLM returned no parseable skills | Skills section may be empty |

---

## Summary: The Call Stack

Here's the complete call sequence in order:

```
main.py
  └─ cli.py: tailor()
       ├─ config.py: AppConfig()  ← loads .env
       ├─ resume_agent.py: ResumeAgent()
       │    └─ llm_client.py: OllamaClient()  ← reads config
       ├─ llm_client.py: test_connection()  ← pings Ollama
       ├─ storage.py: load_resume_from_file()
       │    └─ storage.py: parse_resume_from_text()
       │         ├─ storage.py: _split_sections()
       │         ├─ storage.py: _parse_experience_section()
       │         └─ storage.py: _parse_skills_section()
       ├─ storage.py: load_job_description_from_file()
       │    └─ storage.py: parse_job_description_from_text()
       └─ resume_agent.py: generate_tailored_resume()
            ├─ resume_agent.py: tailor_summary()
            │    ├─ prompts.py: tailor_summary_prompt()  ← builds prompt
            │    └─ llm_client.py: call_ollama_with_retry()
            │         └─ llm_client.py: call_ollama()  ← HTTP POST to Ollama
            ├─ resume_agent.py: tailor_experience()
            │    ├─ prompts.py: tailor_experience_prompt()
            │    ├─ llm_client.py: call_ollama_with_retry()
            │    └─ resume_agent.py: _parse_experience_from_text()
            ├─ resume_agent.py: tailor_skills()
            │    ├─ prompts.py: tailor_skills_prompt()
            │    ├─ llm_client.py: call_ollama_with_retry()
            │    └─ resume_agent.py: _parse_skills_from_text()
            └─ storage.py: save_resume_to_file()  ← writes output file
```

---

> **Keep this file updated** whenever new steps, functions, or error types are added to the codebase.
