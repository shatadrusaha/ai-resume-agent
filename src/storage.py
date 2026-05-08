"""Storage and parsing utilities for resume files."""

import re
from pathlib import Path
from typing import List

from src.models import Resume, Experience, Skill, JobDescription


def parse_resume_from_text(text: str) -> Resume:
    """
    Parse a resume from plain-text format.

    Expected format:
    ## PERSONAL
    Name: John Doe
    Email: john@example.com
    Phone: +1-234-567-8900

    ## SUMMARY
    [Summary text]

    ## EXPERIENCE
    * Job Title at Company (Start - End)
      Description of role and achievements

    ## SKILLS
    - Python, JavaScript, Go
    - FastAPI, React
    """
    sections = _split_sections(text)

    name = ""
    email = ""
    phone = ""

    # Parse personal info
    if "PERSONAL" in sections:
        personal = sections["PERSONAL"].strip()
        name_match = re.search(r"Name:\s*(.+)", personal, re.IGNORECASE)
        email_match = re.search(r"Email:\s*(.+)", personal, re.IGNORECASE)
        phone_match = re.search(r"Phone:\s*(.+)", personal, re.IGNORECASE)

        if name_match:
            name = name_match.group(1).strip()
        if email_match:
            email = email_match.group(1).strip()
        if phone_match:
            phone = phone_match.group(1).strip()

    summary = ""
    if "SUMMARY" in sections:
        summary = sections["SUMMARY"].strip()

    experience = []
    if "EXPERIENCE" in sections:
        experience = _parse_experience_section(sections["EXPERIENCE"])

    skills = []
    if "SKILLS" in sections:
        skills = _parse_skills_section(sections["SKILLS"])

    return Resume(
        name=name,
        email=email,
        phone=phone,
        summary=summary,
        experience=experience,
        skills=skills,
    )


def _split_sections(text: str) -> dict:
    """Split resume text into sections by ## headers."""
    sections = {}
    current_section = None
    current_content = []

    for line in text.split("\n"):
        if line.startswith("##"):
            # Save previous section
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            # Start new section
            current_section = line.replace("##", "").strip().upper()
            current_content = []
        else:
            if current_section:
                current_content.append(line)

    # Save last section
    if current_section:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def _parse_experience_section(text: str) -> List[Experience]:
    """Parse experience section into Experience objects."""
    experiences = []
    entries = text.split("*")[1:]  # Split by * bullet points

    for entry in entries:
        lines = entry.strip().split("\n")
        if not lines:
            continue

        # First line: "Job Title at Company (Start - End)"
        first_line = lines[0].strip()
        job_match = re.search(r"(.+?)\s+at\s+(.+?)\s*\((.+?)\s*-\s*(.+?)\)", first_line)

        if job_match:
            job_title = job_match.group(1).strip()
            company = job_match.group(2).strip()
            start_date = job_match.group(3).strip()
            end_date = job_match.group(4).strip()

            # Rest is description
            description = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

            exp = Experience(
                job_title=job_title,
                company=company,
                start_date=start_date,
                end_date=end_date,
                description=description,
            )
            experiences.append(exp)

    return experiences


def _parse_skills_section(text: str) -> List[Skill]:
    """Parse skills section into Skill objects."""
    skills = []
    lines = text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if line.startswith("-"):
            line = line[1:].strip()

        # Handle comma-separated skills on same line
        for skill_name in line.split(","):
            skill_name = skill_name.strip()
            if skill_name:
                skills.append(Skill(name=skill_name))

    return skills


def load_resume_from_file(file_path: str) -> Resume:
    """Load a resume from a text file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    return parse_resume_from_text(text)


def save_resume_to_file(resume: Resume, file_path: str) -> None:
    """Save a resume to a text file in the standard format."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "## PERSONAL",
        f"Name: {resume.name}",
        f"Email: {resume.email}",
    ]

    if resume.phone:
        lines.append(f"Phone: {resume.phone}")

    if resume.summary:
        lines.extend(
            [
                "",
                "## SUMMARY",
                resume.summary,
            ]
        )

    if resume.experience:
        lines.append("")
        lines.append("## EXPERIENCE")
        for exp in resume.experience:
            lines.append(
                f"* {exp.job_title} at {exp.company} ({exp.start_date} - {exp.end_date})"
            )
            lines.append(f"  {exp.description}")

    if resume.skills:
        lines.append("")
        lines.append("## SKILLS")
        skill_names = [skill.name for skill in resume.skills]
        lines.append("- " + ", ".join(skill_names))

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_job_description_from_text(text: str) -> JobDescription:
    """
    Parse a job description from plain-text format.

    Expected format:
    ## JOB TITLE
    Senior Software Engineer

    ## COMPANY
    TechCorp

    ## DESCRIPTION
    [Full job description]

    ## REQUIRED SKILLS
    - Python
    - Go
    - Kubernetes

    ## RESPONSIBILITIES
    - Lead team projects
    - Code reviews
    """
    sections = _split_sections(text)

    title = sections.get("JOB TITLE", "").strip()
    company = sections.get("COMPANY", "").strip()
    description = sections.get("DESCRIPTION", "").strip()
    required_skills = _parse_list_section(sections.get("REQUIRED SKILLS", ""))
    responsibilities = _parse_list_section(sections.get("RESPONSIBILITIES", ""))

    return JobDescription(
        title=title if title else "Untitled Position",
        company=company,
        description=description,
        required_skills=required_skills,
        responsibilities=responsibilities,
    )


def _parse_list_section(text: str) -> List[str]:
    """Parse a simple list section (lines starting with -)."""
    items = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("-"):
            line = line[1:].strip()
            if line:
                items.append(line)
    return items


def load_job_description_from_file(file_path: str) -> JobDescription:
    """Load a job description from a text file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Job description file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    return parse_job_description_from_text(text)
