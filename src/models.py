"""Data models for resume and job description."""

from typing import List

from pydantic import BaseModel, Field, EmailStr


class Skill(BaseModel):
    """Represents a single skill."""

    name: str = Field(..., min_length=1, description="Skill name")
    category: str = Field(
        default="General",
        description="Skill category (e.g., Programming, Soft Skills, Tools)",
    )

    def __str__(self) -> str:
        return self.name


class Experience(BaseModel):
    """Represents a work experience entry."""

    job_title: str = Field(..., min_length=1, description="Job title")
    company: str = Field(..., min_length=1, description="Company name")
    start_date: str = Field(..., description="Start date (e.g., Jan 2020)")
    end_date: str = Field(..., description="End date (e.g., Dec 2021 or Present)")
    description: str = Field(..., min_length=1, description="Role description")
    achievements: List[str] = Field(
        default_factory=list, description="Key achievements"
    )

    def __str__(self) -> str:
        return (
            f"{self.job_title} at {self.company} ({self.start_date} - {self.end_date})"
        )


class Resume(BaseModel):
    """Represents a complete resume."""

    name: str = Field(..., min_length=1, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(default="", description="Phone number")
    summary: str = Field(default="", description="Professional summary")
    experience: List[Experience] = Field(
        default_factory=list, description="Work experience"
    )
    skills: List[Skill] = Field(default_factory=list, description="Skills list")

    def add_experience(self, experience: Experience) -> None:
        """Add an experience entry to the resume."""
        self.experience.append(experience)

    def add_skill(self, skill: Skill) -> None:
        """Add a skill to the resume."""
        self.skills.append(skill)

    def __str__(self) -> str:
        lines = [
            f"Name: {self.name}",
            f"Email: {self.email}",
        ]
        if self.phone:
            lines.append(f"Phone: {self.phone}")
        if self.summary:
            lines.extend(["\nSUMMARY", self.summary])
        if self.experience:
            lines.append("\nEXPERIENCE")
            for exp in self.experience:
                lines.append(f"- {exp}")
        if self.skills:
            lines.append("\nSKILLS")
            for skill in self.skills:
                lines.append(f"- {skill}")
        return "\n".join(lines)


class JobDescription(BaseModel):
    """Represents a job description."""

    title: str = Field(..., min_length=1, description="Job title")
    company: str = Field(default="", description="Company name")
    description: str = Field(default="", description="Full job description")
    required_skills: List[str] = Field(
        default_factory=list, description="Required skills"
    )
    responsibilities: List[str] = Field(
        default_factory=list, description="Job responsibilities"
    )

    def __str__(self) -> str:
        lines = [
            f"Title: {self.title}",
        ]
        if self.company:
            lines.append(f"Company: {self.company}")
        if self.description:
            lines.append(f"\n{self.description}")
        if self.required_skills:
            lines.append("\nRequired Skills:")
            for skill in self.required_skills:
                lines.append(f"- {skill}")
        if self.responsibilities:
            lines.append("\nResponsibilities:")
            for resp in self.responsibilities:
                lines.append(f"- {resp}")
        return "\n".join(lines)
