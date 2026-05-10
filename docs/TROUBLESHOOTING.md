# Troubleshooting Guide

Common errors, their causes, and how to fix them.

---

## Ollama Issues

### `OllamaConnectionError: Failed to connect to Ollama`

**Symptom:**
```
ERROR: OllamaConnectionError: Failed to connect to Ollama at http://localhost:11434.
Is Ollama running? (ollama serve)
```

**Cause:** Ollama server is not running.

**Fix:**
```bash
# Start Ollama in a terminal
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

---

### `Model 'llama3' not found on Ollama server`

**Symptom:**
```
ERROR: Model 'llama3' not found on Ollama server. Pull it with: ollama pull llama3
```

**Cause:** The model hasn't been downloaded yet.

**Fix:**
```bash
ollama pull llama3

# Or switch to a model you already have
uv run python main.py tailor -r resume.txt -j job.txt --model mistral
```

List models you have installed:
```bash
ollama list
```

---

### `OllamaTimeoutError: Connection to Ollama timed out`

**Symptom:**
```
ERROR: OllamaTimeoutError: Connection to Ollama timed out
```

**Cause:** The LLM is taking too long to generate a response. Common on first run or with large models on slow hardware.

**Fix — increase timeout in `.env`:**
```bash
OLLAMA_TIMEOUT=600   # 10 minutes (default: 300)
```

**Fix — use a smaller/faster model:**
```bash
ollama pull mistral   # Faster than llama3 on most hardware
uv run python main.py tailor -r resume.txt -j job.txt --model mistral
```

---

## Installation Issues

### `ModuleNotFoundError: No module named 'src'`

**Symptom:**
```
ModuleNotFoundError: No module named 'src'
```

**Cause:** Running pytest or Python directly without `uv run`, bypassing the virtual environment.

**Fix:**
```bash
# Always use uv run
uv run pytest
uv run python main.py tailor ...

# Never use
python main.py   # Wrong — uses system Python, not .venv
pytest           # Wrong — may use wrong environment
```

---

### `uv sync` fails with dependency conflicts

**Symptom:**
```
error: No solution found when resolving dependencies
```

**Fix:**
```bash
# Remove and recreate virtual environment
rm -rf .venv
uv sync
```

---

### `ValidationError` on startup

**Symptom:**
```
pydantic_core._pydantic_core.ValidationError: ...
```

**Cause:** Missing or incorrectly typed environment variable in `.env`.

**Fix:**

1. Check your `.env` file exists:
   ```bash
   ls -la .env
   ```

2. Copy from example if missing:
   ```bash
   cp .env.example .env
   ```

3. Verify values are correct types (no quotes around numbers):
   ```bash
   # Correct
   OLLAMA_PORT=11434
   OLLAMA_TIMEOUT=300
   
   # Wrong (will cause ValidationError)
   OLLAMA_PORT="11434"
   ```

---

## Resume Parsing Issues

### Experiences or skills not extracted (parsed as empty)

**Symptom:** Resume loads but `experience=[]` or `skills=[]`.

**Cause:** Resume file doesn't follow the expected `## SECTION` format.

**Fix:** Check your resume file matches the format in `examples/my_resume.txt.example`:

```
## PERSONAL
Name: Your Name
Email: you@example.com
Phone: (555) 123-4567

## SUMMARY
Your professional summary here.

## EXPERIENCE
* Job Title at Company (Start Year - End Year)
  Description of role and achievements

## SKILLS
Skill1, Skill2, Skill3
```

Key formatting rules:
- Section headers must start with `##`
- Section names must be: `PERSONAL`, `SUMMARY`, `EXPERIENCE`, `SKILLS`
- Experience entries must start with `*` and follow `Title at Company (Start - End)` format
- Skills must be comma-separated on one line (or lines starting with `-`)

---

### LLM output not parsing correctly — fallback to original

**Symptom:**
```
WARNING: Could not parse experiences from LLM output, using original top 3
```

**Cause:** The LLM returned output in an unexpected format that the parser couldn't extract structured data from.

**What happens:** The agent automatically falls back to the original resume sections rather than failing.

**Fix:** This is expected occasionally. If it happens consistently:
- Try a different model: `--model mistral` or `--model neural-chat`
- Adjust `TAILORING_TEMPERATURE` in `.env` (lower = more deterministic, try `0.3`)

---

## Test Issues

### Tests fail with `FileNotFoundError` in CI or fresh clone

**Cause:** `examples/my_resume.txt` and `examples/job_description.txt` are in `.gitignore` (user-specific files). The tests use temporary files created by fixtures, so this shouldn't affect tests — but the CLI examples require the files to exist.

**Fix for CLI usage:**
```bash
cp examples/my_resume.txt.example examples/my_resume.txt
cp examples/job_description.txt.example examples/job_description.txt
```

---

### `pytest: command not found`

**Fix:**
```bash
# Always run via uv
uv run pytest
```

---

### Coverage drops unexpectedly

**Cause:** New code added without corresponding tests.

**Fix:** Add tests for the new code, or check which lines are uncovered:
```bash
uv run pytest --cov-report=html
open htmlcov/index.html
```

---

## CLI Issues

### `Error: Invalid value for '--resume' / '--job-description': Path does not exist`

**Cause:** Typer validates that file paths exist before running.

**Fix:** Provide the correct path to existing files:
```bash
# Check the file exists
ls examples/my_resume.txt

# Use correct path
uv run python main.py tailor \
  --resume examples/my_resume.txt \
  --job-description examples/job_description.txt
```

---

### Output file not created

**Cause:** Permission error or invalid output path.

**Fix:** Ensure the output directory exists and is writable:
```bash
# Write to current directory (always works)
uv run python main.py tailor -r resume.txt -j job.txt -o tailored_resume.txt

# Nested path — make sure parent exists
mkdir -p output/
uv run python main.py tailor -r resume.txt -j job.txt -o output/tailored.txt
```

---

## Getting Help

1. Check this guide first
2. Run with verbose logging to see what's happening:
   ```bash
   uv run python main.py tailor -r resume.txt -j job.txt 2>&1 | tee debug.log
   ```
3. Test Ollama independently:
   ```bash
   uv run python main.py test-ollama
   ```
4. Check the [EXECUTION_FLOW.md](EXECUTION_FLOW.md) to understand exactly what the code does at each step
