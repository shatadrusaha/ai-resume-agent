"""AI Resume Agent - Tailor resumes to job descriptions using local LLMs."""

__version__ = "0.1.0"
__author__ = "shaz"

from src.models import Resume, Experience, Skill, JobDescription

__all__ = [
    "Resume",
    "Experience",
    "Skill",
    "JobDescription",
]
