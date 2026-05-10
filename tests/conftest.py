"""Pytest configuration and shared fixtures for AI Resume Agent tests."""

import pytest
from src.models import Resume, Experience, Skill, JobDescription


@pytest.fixture
def sample_resume_text() -> str:
    """Sample resume in plain text format."""
    return """## PERSONAL
Name: Alex Johnson
Email: alex@example.com
Phone: (555) 123-4567

## SUMMARY
Experienced software engineer with 8+ years building scalable backend systems.

## EXPERIENCE
* Senior Backend Engineer at TechCorp (2020 - Present)
  Led team of 5 engineers on microservices migration
  Reduced API latency by 40% through caching optimization
  Implemented CI/CD pipeline using Kubernetes

* Backend Engineer at StartupXYZ (2018 - 2020)
  Built REST APIs using Python and FastAPI
  Designed PostgreSQL schema for 1M+ daily active users
  Mentored 2 junior developers

* Junior Developer at DevShop (2016 - 2018)
  Maintained legacy monolith codebase
  Implemented payment processing integration
  Wrote unit tests achieving 70% coverage

## SKILLS
Python, FastAPI, PostgreSQL, Docker, Kubernetes, AWS, Redis, GraphQL, React, Microservices
"""


@pytest.fixture
def sample_job_description_text() -> str:
    """Sample job description in plain text format."""
    return """## JOB TITLE
Staff Backend Engineer

## COMPANY
CloudInnovate Solutions

## DESCRIPTION
We are seeking a Staff Backend Engineer to lead our infrastructure team.

## REQUIRED SKILLS
- 10+ years of backend development experience
- Expert in distributed systems and microservices architecture
- Strong experience with Python or Go
- Proven track record leading technical teams
- Experience with cloud platforms (AWS, GCP)
- Knowledge of system design and scalability

## RESPONSIBILITIES
- Design and implement high-performance backend services
- Mentor junior and senior engineers
- Lead architectural decisions and code reviews
- Own deployment and monitoring infrastructure
- Collaborate with product team on technical roadmap
"""


@pytest.fixture
def sample_resume(sample_resume_text: str) -> Resume:
    """Parsed sample resume object."""
    return Resume(
        name="Alex Johnson",
        email="alex@example.com",
        phone="(555) 123-4567",
        summary="Experienced software engineer with 8+ years building scalable backend systems.",
        experience=[
            Experience(
                job_title="Senior Backend Engineer",
                company="TechCorp",
                start_date="2020",
                end_date="Present",
                description="Led team of 5 engineers on microservices migration. Reduced API latency by 40% through caching optimization. Implemented CI/CD pipeline using Kubernetes.",
            ),
            Experience(
                job_title="Backend Engineer",
                company="StartupXYZ",
                start_date="2018",
                end_date="2020",
                description="Built REST APIs using Python and FastAPI. Designed PostgreSQL schema for 1M+ daily active users. Mentored 2 junior developers.",
            ),
            Experience(
                job_title="Junior Developer",
                company="DevShop",
                start_date="2016",
                end_date="2018",
                description="Maintained legacy monolith codebase. Implemented payment processing integration. Wrote unit tests achieving 70% coverage.",
            ),
        ],
        skills=[
            Skill(name="Python"),
            Skill(name="FastAPI"),
            Skill(name="PostgreSQL"),
            Skill(name="Docker"),
            Skill(name="Kubernetes"),
            Skill(name="AWS"),
            Skill(name="Redis"),
            Skill(name="GraphQL"),
            Skill(name="React"),
            Skill(name="Microservices"),
        ],
    )


@pytest.fixture
def sample_job_description(sample_job_description_text: str) -> JobDescription:
    """Parsed sample job description object."""
    return JobDescription(
        title="Staff Backend Engineer",
        company="CloudInnovate Solutions",
        description="We are seeking a Staff Backend Engineer to lead our infrastructure team.",
        required_skills=[
            "10+ years of backend development experience",
            "Expert in distributed systems and microservices architecture",
            "Strong experience with Python or Go",
            "Proven track record leading technical teams",
            "Experience with cloud platforms (AWS, GCP)",
            "Knowledge of system design and scalability",
        ],
        responsibilities=[
            "Design and implement high-performance backend services",
            "Mentor junior and senior engineers",
            "Lead architectural decisions and code reviews",
            "Own deployment and monitoring infrastructure",
            "Collaborate with product team on technical roadmap",
        ],
    )


@pytest.fixture
def tmp_resume_file(tmp_path, sample_resume_text: str):
    """Create a temporary resume file for testing."""
    resume_file = tmp_path / "test_resume.txt"
    resume_file.write_text(sample_resume_text)
    return resume_file


@pytest.fixture
def tmp_job_description_file(tmp_path, sample_job_description_text: str):
    """Create a temporary job description file for testing."""
    job_file = tmp_path / "test_job.txt"
    job_file.write_text(sample_job_description_text)
    return job_file
