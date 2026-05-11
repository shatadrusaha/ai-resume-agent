"""Data models for resume and job description."""

from typing import List

from pydantic import BaseModel, Field, EmailStr


class Skill(BaseModel):
    """Represents a single professional skill.

    Attributes:
        name: The skill name (e.g., Python, Leadership, Communication)
        category: Optional category for organizing skills (e.g., Programming, Soft Skills)
    """

    name: str = Field(..., min_length=1, description="Skill name")
    category: str = Field(
        default="General",
        description="Skill category (e.g., Programming, Soft Skills, Tools)",
    )

    def __str__(self) -> str:
        """Return the skill name as a string."""
        return self.name


class Experience(BaseModel):
    """Represents a work experience entry in a resume.

    Attributes:
        job_title: Position title (e.g., Senior Software Engineer)
        company: Company name where the role was held
        start_date: Employment start date (e.g., "Jan 2020")
        end_date: Employment end date (e.g., "Dec 2021" or "Present")
        description: Role description and main responsibilities
        achievements: Optional list of key achievements or metrics
    """

    job_title: str = Field(..., min_length=1, description="Job title")
    company: str = Field(..., min_length=1, description="Company name")
    start_date: str = Field(..., description="Start date (e.g., Jan 2020)")
    end_date: str = Field(..., description="End date (e.g., Dec 2021 or Present)")
    description: str = Field(..., min_length=1, description="Role description")
    achievements: List[str] = Field(
        default_factory=list, description="Key achievements"
    )

    def __str__(self) -> str:
        """Return formatted experience as a string."""
        lines = [
            f"{self.job_title} at {self.company} ({self.start_date} - {self.end_date})"
        ]
        if self.description:
            lines.append(f"  {self.description}")
        if self.achievements:
            for achievement in self.achievements:
                lines.append(f"  - {achievement}")
        return "\n".join(lines)


class Resume(BaseModel):
    """Represents a complete professional resume.

    Contains personal information, professional summary, work experience,
    and skills. Used as the master resume and also for tailored versions.

    Attributes:
        name: Full name of the person
        email: Valid email address
        phone: Optional phone number
        summary: Professional summary or objective (2-3 sentences)
        experience: List of work experience entries (chronological order)
        skills: List of professional skills
    """

    name: str = Field(..., min_length=1, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(default="", description="Phone number")
    summary: str = Field(default="", description="Professional summary")
    experience: List[Experience] = Field(
        default_factory=list, description="Work experience"
    )
    skills: List[Skill] = Field(default_factory=list, description="Skills list")

    def add_experience(self, experience: Experience) -> None:
        """Add an experience entry to the resume.

        Args:
            experience: Experience object to add
        """
        self.experience.append(experience)

    def add_skill(self, skill: Skill) -> None:
        """Add a skill to the resume.

        Args:
            skill: Skill object to add
        """
        self.skills.append(skill)

    def __str__(self) -> str:
        """Return formatted resume as a string."""
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
    """Represents a job posting description.

    Used to extract requirements and responsibilities that guide the
    resume tailoring process. Helps the AI understand the target role.

    Attributes:
        title: Job title (e.g., Senior Backend Engineer)
        company: Company name
        description: Full job description text
        required_skills: List of required or desired skills
        responsibilities: List of key job responsibilities
    """

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
