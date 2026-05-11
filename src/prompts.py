"""Prompt templates for tailoring resumes using LLMs.

Defines prompts that guide the language model to rewrite resume sections
(summary, experiences, skills) to match target job descriptions.
"""

from src.models import JobDescription, Resume


class PromptTemplates:
    """Collection of prompt templates for resume tailoring.

    Each static method generates a specific prompt to instruct the LLM
    on how to transform resume content to match a job description.
    """

    @staticmethod
    def tailor_summary_prompt(resume: Resume, job_description: JobDescription) -> str:
        """Generate a prompt to tailor the resume summary.

        Creates a prompt that instructs the LLM to rewrite the professional
        summary to match the target job. Emphasizes relevance and keyword incorporation.

        Args:
            resume: User's resume with original summary
            job_description: Target job with requirements and focus areas

        Returns:
            LLM prompt string ready to send to Ollama
        """
        return f"""You are an expert resume writer. Your task is to tailor a professional summary to match a job description.

JOB DESCRIPTION:
Title: {job_description.title}
Company: {job_description.company or "Not specified"}
Description: {job_description.description}

REQUIRED SKILLS:
{chr(10).join(f"- {skill}" for skill in job_description.required_skills)}

CURRENT SUMMARY:
{resume.summary}

Please rewrite the professional summary to:
1. Highlight relevant experience for this specific role
2. Incorporate keywords from the job description
3. Match the tone and focus of what the company is looking for
4. Keep it to 2-3 sentences
5. Make it compelling and specific to this position

Return ONLY the new summary text, without any preamble or explanation."""

    @staticmethod
    def tailor_experience_prompt(
        resume: Resume, job_description: JobDescription
    ) -> str:
        """Generate a prompt to tailor and reorder work experiences.

        Creates a prompt that instructs the LLM to rewrite and reorder
        experience entries to highlight job-relevant achievements.
        Returns top 3-4 most relevant experiences.

        Args:
            resume: User's resume with original experiences
            job_description: Target job with responsibilities and required skills

        Returns:
            LLM prompt string ready to send to Ollama
        """
        experience_text = "\n\n".join([
            f"Position {i + 1}: {exp.job_title} at {exp.company} ({exp.start_date} - {exp.end_date})\n"
            f"Description: {exp.description}"
            for i, exp in enumerate(resume.experience)
        ])

        return f"""You are an expert resume writer. Your task is to tailor work experience entries to match a job description.

JOB DESCRIPTION:
Title: {job_description.title}
Company: {job_description.company or "Not specified"}
Key Focus Areas:
{chr(10).join(f"- {item}" for item in job_description.responsibilities[:5])}

REQUIRED SKILLS:
{chr(10).join(f"- {skill}" for skill in job_description.required_skills)}

CURRENT EXPERIENCE:
{experience_text}

For each relevant experience entry, please:
1. Rewrite the description to emphasize achievements matching the job requirements
2. Highlight technical skills mentioned in the job description
3. Use metrics and quantifiable results when possible
4. Focus on impact and responsibility levels matching the target role
5. Reorder by relevance to this specific job (most relevant first)

Return the tailored experience entries in this format:
Position 1: [Title] at [Company] ([Start] - [End])
Description: [Rewritten description]

Position 2: [Title] at [Company] ([Start] - [End])
Description: [Rewritten description]

Only include the top 3-4 most relevant positions. Do NOT include preamble or explanation."""

    @staticmethod
    def tailor_skills_prompt(resume: Resume, job_description: JobDescription) -> str:
        """Generate a prompt to tailor and rank skills by job relevance.

        Creates a prompt that instructs the LLM to filter, prioritize,
        and rank skills to match the job description. Returns top 15-20 skills.

        Args:
            resume: User's resume with original skills
            job_description: Target job with required skills

        Returns:
            LLM prompt string ready to send to Ollama
        """
        current_skills = ", ".join([skill.name for skill in resume.skills])

        return f"""You are an expert recruiter. Your task is to rank and filter skills to match a job description.

JOB DESCRIPTION:
Title: {job_description.title}
Company: {job_description.company or "Not specified"}

REQUIRED SKILLS (explicit):
{chr(10).join(f"- {skill}" for skill in job_description.required_skills)}

CANDIDATE'S CURRENT SKILLS:
{current_skills}

Please:
1. Identify which of the candidate's skills match the job requirements
2. Prioritize skills that exactly match the job description requirements
3. Include related skills that are valuable for the position
4. Create a skill list organized by category/relevance
5. Focus on top 15-20 most relevant skills

Return the skills as a comma-separated list, ordered by relevance to the job:
[Skill1], [Skill2], [Skill3], ...

Do NOT include preamble or explanation. Return ONLY the comma-separated skills list."""

    @staticmethod
    def evaluate_relevance_prompt(
        resume: Resume, job_description: JobDescription
    ) -> str:
        """Generate a prompt to evaluate resume-job fit.

        Creates a prompt that instructs the LLM to analyze how well
        the resume matches the job and provide a match percentage.

        Args:
            resume: User's resume
            job_description: Target job

        Returns:
            LLM prompt string ready to send to Ollama
        """
        return f"""You are an expert recruiter evaluating resume-job fit. Analyze the following resume against the job description.

JOB DESCRIPTION:
Title: {job_description.title}
Company: {job_description.company or "Not specified"}
Required Skills: {", ".join(job_description.required_skills)}
Responsibilities: {", ".join(job_description.responsibilities)}

RESUME:
Summary: {resume.summary}
Skills: {", ".join([s.name for s in resume.skills])}
Experience: {chr(10).join([f"- {e.job_title} at {e.company}" for e in resume.experience])}

Provide ONLY the following output (no preamble, no explanation):
Match: [0-100]%
Matches: [item1], [item2], [item3]
Gaps: [item1], [item2], [item3]

Where:
- Match: Percentage of job requirements met (0-100)
- Matches: 3 key matching skills/experiences the candidate has
- Gaps: 3 key missing skills/experiences the candidate lacks

Output format MUST be exactly as shown above with no additional text."""
