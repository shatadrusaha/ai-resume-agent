"""Tests for storage.py — resume and job description parsing functions."""

import pytest
from pathlib import Path

from src.storage import (
    parse_resume_from_text,
    load_resume_from_file,
    save_resume_to_file,
    parse_job_description_from_text,
    load_job_description_from_file,
)
from src.models import Resume, JobDescription


class TestParseResumeFromText:
    """Test resume text parsing."""

    def test_parse_resume_basic(self, sample_resume_text: str):
        """Parse a basic resume from text."""
        resume = parse_resume_from_text(sample_resume_text)

        assert resume.name == "Alex Johnson"
        assert resume.email == "alex@example.com"
        assert resume.phone == "(555) 123-4567"
        assert len(resume.experience) == 3
        assert len(resume.skills) == 10

    def test_parse_resume_name_extraction(self, sample_resume_text: str):
        """Verify name is correctly extracted."""
        resume = parse_resume_from_text(sample_resume_text)
        assert resume.name == "Alex Johnson"

    def test_parse_resume_email_validation(self, sample_resume_text: str):
        """Verify email is valid."""
        resume = parse_resume_from_text(sample_resume_text)
        assert "@" in resume.email
        assert "example.com" in resume.email

    def test_parse_resume_summary_extraction(self, sample_resume_text: str):
        """Verify summary is extracted."""
        resume = parse_resume_from_text(sample_resume_text)
        assert "software engineer" in resume.summary.lower()
        assert len(resume.summary) > 10

    def test_parse_resume_experience_count(self, sample_resume_text: str):
        """Verify all experiences are parsed."""
        resume = parse_resume_from_text(sample_resume_text)
        assert len(resume.experience) == 3

    def test_parse_resume_experience_details(self, sample_resume_text: str):
        """Verify experience details are correct."""
        resume = parse_resume_from_text(sample_resume_text)

        first_exp = resume.experience[0]
        assert first_exp.job_title == "Senior Backend Engineer"
        assert first_exp.company == "TechCorp"
        assert first_exp.start_date == "2020"
        assert first_exp.end_date == "Present"

    def test_parse_resume_skills_parsed(self, sample_resume_text: str):
        """Verify skills are parsed."""
        resume = parse_resume_from_text(sample_resume_text)
        skill_names = [s.name for s in resume.skills]

        assert "Python" in skill_names
        assert "FastAPI" in skill_names
        assert "AWS" in skill_names

    def test_parse_resume_missing_summary_section(self):
        """Handle resume without summary section."""
        text = """## PERSONAL
Name: Jane Doe
Email: jane@example.com
Phone: (555) 987-6543

## SKILLS
Java, Spring, MySQL
"""
        resume = parse_resume_from_text(text)
        assert resume.name == "Jane Doe"
        assert resume.summary == ""  # Empty summary

    def test_parse_resume_invalid_email_raises_error(self):
        """Invalid email should raise ValidationError."""
        text = """## PERSONAL
Name: John Smith
Email: not-an-email
Phone: (555) 111-2222

## SUMMARY
A developer.

## SKILLS
Python
"""
        with pytest.raises(ValueError):
            parse_resume_from_text(text)


class TestLoadResumeFromFile:
    """Test loading resume from file."""

    def test_load_resume_from_file(self, tmp_resume_file):
        """Load resume from temporary file."""
        resume = load_resume_from_file(str(tmp_resume_file))

        assert isinstance(resume, Resume)
        assert resume.name == "Alex Johnson"
        assert len(resume.experience) == 3

    def test_load_resume_file_not_found(self):
        """Raise error for missing file."""
        with pytest.raises(FileNotFoundError):
            load_resume_from_file("/nonexistent/path/resume.txt")

    def test_load_resume_with_path_object(self, tmp_resume_file):
        """Load resume using Path object."""
        resume = load_resume_from_file(str(tmp_resume_file))
        assert resume.name == "Alex Johnson"


class TestSaveResumeToFile:
    """Test saving resume to file."""

    def test_save_resume_to_file(self, sample_resume, tmp_path):
        """Save resume to file."""
        output_file = tmp_path / "output_resume.txt"
        save_resume_to_file(sample_resume, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert "Alex Johnson" in content
        assert "TechCorp" in content

    def test_save_and_reload_resume(self, sample_resume, tmp_path):
        """Save and reload resume maintains data."""
        output_file = tmp_path / "resume.txt"
        save_resume_to_file(sample_resume, str(output_file))

        reloaded = load_resume_from_file(str(output_file))
        assert reloaded.name == sample_resume.name
        assert reloaded.email == sample_resume.email
        assert len(reloaded.experience) == len(sample_resume.experience)

    def test_save_resume_creates_directory(self, sample_resume, tmp_path):
        """Save creates parent directory if needed."""
        nested_dir = tmp_path / "nested" / "output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_file = nested_dir / "resume.txt"

        save_resume_to_file(sample_resume, str(output_file))
        assert output_file.exists()


class TestParseJobDescriptionFromText:
    """Test job description text parsing."""

    def test_parse_job_description_basic(self, sample_job_description_text: str):
        """Parse basic job description from text."""
        job = parse_job_description_from_text(sample_job_description_text)

        assert job.title == "Staff Backend Engineer"
        assert job.company == "CloudInnovate Solutions"
        assert len(job.required_skills) > 0

    def test_parse_job_description_company(self, sample_job_description_text: str):
        """Verify company extraction."""
        job = parse_job_description_from_text(sample_job_description_text)
        assert job.company == "CloudInnovate Solutions"

    def test_parse_job_description_requirements(self, sample_job_description_text: str):
        """Verify required skills are parsed."""
        job = parse_job_description_from_text(sample_job_description_text)
        assert len(job.required_skills) > 0
        assert any("backend" in req.lower() for req in job.required_skills)

    def test_parse_job_description_responsibilities(
        self, sample_job_description_text: str
    ):
        """Verify responsibilities are parsed."""
        job = parse_job_description_from_text(sample_job_description_text)
        assert len(job.responsibilities) > 0
        assert any("mentor" in resp.lower() for resp in job.responsibilities)

    def test_parse_job_description_minimal(self):
        """Parse minimal job description."""
        text = """## JOB TITLE
Developer

## COMPANY
Acme Corp

## DESCRIPTION
Looking for a developer.

## REQUIRED SKILLS
- Python

## RESPONSIBILITIES
- Write code
"""
        job = parse_job_description_from_text(text)
        assert job.title == "Developer"
        assert job.company == "Acme Corp"


class TestLoadJobDescriptionFromFile:
    """Test loading job description from file."""

    def test_load_job_description_from_file(self, tmp_job_description_file):
        """Load job description from temporary file."""
        job = load_job_description_from_file(str(tmp_job_description_file))

        assert isinstance(job, JobDescription)
        assert job.title == "Staff Backend Engineer"
        assert job.company == "CloudInnovate Solutions"

    def test_load_job_description_file_not_found(self):
        """Raise error for missing file."""
        with pytest.raises(FileNotFoundError):
            load_job_description_from_file("/nonexistent/job.txt")

    def test_load_job_description_with_path_object(self, tmp_job_description_file):
        """Load job description using Path object."""
        job = load_job_description_from_file(str(tmp_job_description_file))
        assert job.title == "Staff Backend Engineer"
