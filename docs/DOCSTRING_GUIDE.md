# Docstring Style Guide

This project uses **Google-style docstrings** for all Python code. This guide ensures consistency and maintainability.

## Style: Google Format

Google-style docstrings are concise, readable, and widely used in modern Python projects (Google, FastAPI, Pydantic, etc.).

---

## Basic Structure

```python
def function_name(arg1: Type1, arg2: Type2) -> ReturnType:
    """One-line summary ending with period.

    Optional longer description with more details about what the function
    does, why it exists, and any important context or caveats.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of what is returned

    Raises:
        CustomError: When this specific error occurs
        AnotherError: When that other error occurs
    """
```

---

## Detailed Examples

### Example 1: Simple Function
```python
def parse_resume_from_text(text: str) -> Resume:
    """Parse a resume from plain-text format.

    Expects text with clear section headers (## PERSONAL, ## EXPERIENCE, etc.)
    and extracts all information into a structured Resume object.

    Args:
        text: Resume text in the standard format

    Returns:
        Resume object with all sections parsed

    Raises:
        ValueError: If required sections are missing
        ValidationError: If extracted data is invalid (e.g., bad email)
    """
```

### Example 2: Method with Multiple Args
```python
def tailor_experience(
    self,
    resume: Resume,
    job_description: JobDescription,
) -> list[Experience]:
    """Generate tailored and reordered experience entries.

    Sends the resume and job description to the LLM, which rewrites
    experience entries to highlight relevant skills and achievements
    for the target position. Results are sorted by relevance.

    Args:
        resume: The user's full resume
        job_description: The target job description

    Returns:
        List of Experience objects, reordered by relevance (top first)

    Raises:
        OllamaConnectionError: If unable to connect to Ollama
        OllamaTimeoutError: If LLM call exceeds timeout
    """
```

### Example 3: Property
```python
@property
def base_url(self) -> str:
    """Ollama server base URL.

    Constructed from host and port configuration.

    Returns:
        URL string in format "http://host:port"
    """
    return f"http://{self.host}:{self.port}"
```

### Example 4: Class Docstring
```python
class ResumeAgent:
    """Main orchestration class for tailoring resumes to job descriptions.

    This agent coordinates between file I/O, LLM calls, and parsing to
    transform a master resume into a job-specific tailored version.

    Attributes:
        ollama_client: OllamaClient instance for LLM communication
    """
```

---

## Rules & Best Practices

### 1. One-Line Summary
- **Always** start with a concise one-liner (under 80 chars)
- **Always** end with a period
- Use imperative mood: "Parse the file" not "Parses the file" or "This parses"

✅ **Good:**
```python
"""Parse a resume from plain-text format."""
```

❌ **Bad:**
```python
"""Parsing a resume from plain-text format."""
"""This function parses a resume from plain-text format."""
```

### 2. Args Section
- List each argument on its own line
- Include **type** in the function signature, not in Args
- Keep descriptions short and clear

✅ **Good:**
```python
def tailor_summary(self, resume: Resume, job: JobDescription) -> str:
    """Generate a tailored summary.

    Args:
        resume: User's resume object
        job: Target job description
    """
```

❌ **Bad:**
```python
def tailor_summary(self, resume, job):
    """Generate a tailored summary.

    Args:
        resume (Resume): User's resume object
        job (JobDescription): Target job description
    """
```

### 3. Returns Section
- Describe what is returned, not the type (type is in signature)
- If return type is simple (str, int), one line is fine
- If complex, explain the structure

✅ **Good:**
```python
"""...
Returns:
    Tailored summary text for the job
"""
```

❌ **Bad:**
```python
"""...
Returns:
    str: The tailored summary text
"""
```

### 4. Raises Section
- List exceptions that **should be caught** by caller
- Don't list base exceptions (TypeError, AttributeError)
- Explain when each error occurs

✅ **Good:**
```python
"""...
Raises:
    OllamaConnectionError: If unable to reach Ollama server
    ValidationError: If resume data is invalid
"""
```

❌ **Bad:**
```python
"""...
Raises:
    Exception: Generic exception
"""
```

### 5. Long Descriptions
- Use blank line after one-liner before longer description
- Keep descriptions practical and concise
- Mention edge cases or important behaviors

✅ **Good:**
```python
def call_ollama_with_retry(self, prompt: str) -> str:
    """Call Ollama with automatic retry on transient failures.

    Implements exponential backoff for temporary errors like timeouts.
    Permanent errors (connection refused, model not found) fail immediately
    without retries.
    """
```

### 6. No Docstring Needed For
- Private methods starting with `_` (unless complex logic)
- Trivial getters/setters (unless they do more than just return)
- Override methods (if parent class is well-documented)

---

## Section Order

Always use this order:

1. One-line summary
2. Blank line (if longer description follows)
3. Longer description (optional)
4. Args (if method has parameters)
5. Returns (if method returns something)
6. Raises (if method raises exceptions)
7. Examples (rarely needed, only for complex usage)

---

## File-Level Docstrings

Each Python file should start with a module docstring:

```python
"""Storage and parsing utilities for resume and job description files.

This module provides functions to load resume and job description text files
and convert them into Pydantic models for type-safe manipulation.
"""

import re
from pathlib import Path

# ... rest of file
```

---

## Validation

Before committing, check:
- [ ] All public functions have docstrings
- [ ] All parameters documented in Args
- [ ] All return values documented in Returns
- [ ] All exceptions documented in Raises
- [ ] One-liners end with period
- [ ] No type info repeated in docstring (it's in signature)

---

## Tools & Linting

Consider using these tools (optional, for Phase 5+):

- **`pydocstyle`** — Validates docstring format
- **`darglint`** — Checks docstrings against function signatures

Install with:
```bash
uv add pydocstyle darglint
```

Run validation:
```bash
pydocstyle src/  # Check all docstrings
darglint src/    # Check Args/Returns match signature
```

---

## Resources

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257 Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [NumPy (alternative style)](https://numpydoc.readthedocs.io/en/latest/format.html)
