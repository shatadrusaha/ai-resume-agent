"""Prompt templates for resume tailoring."""

from src.models import JobDescription, Resume


class PromptTemplates:
    """Collection of prompt templates for resume tailoring."""

    @staticmethod
    def tailor_summary_prompt(resume: Resume, job_description: JobDescription) -> str:
        """
        Generate a prompt to tailor the resume summary.

        Args:
            resume: The user's resume
            job_description: The target job description

        Returns:
            A prompt string for the LLM
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
        """
        Generate a prompt to tailor and reorder experience entries.

        Args:
            resume: The user's resume
            job_description: The target job description

        Returns:
            A prompt string for the LLM
        """
        experience_text = "\n\n".join(
            [
                f"Position {i + 1}: {exp.job_title} at {exp.company} ({exp.start_date} - {exp.end_date})\n"
                f"Description: {exp.description}"
                for i, exp in enumerate(resume.experience)
            ]
        )

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
    def tailor_skills_prompt(
        resume: Resume, job_description: JobDescription
    ) -> str:
        """
        Generate a prompt to tailor and rank skills.

        Args:
            resume: The user's resume
            job_description: The target job description

        Returns:
            A prompt string for the LLM
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
        """
        Generate a prompt to evaluate resume-job fit.

        Args:
            resume: The user's resume
            job_description: The target job description

        Returns:
            A prompt string for the LLM
        """
        return f"""Analyze how well this resume matches the job description.

JOB DESCRIPTION:
Title: {job_description.title}
Required Skills: {", ".join(job_description.required_skills)}
Responsibilities: {", ".join(job_description.responsibilities)}

RESUME SUMMARY:
{resume.summary}

CANDIDATE SKILLS:
{", ".join([s.name for s in resume.skills])}

CANDIDATE EXPERIENCE:
{chr(10).join([f"- {e.job_title} at {e.company}" for e in resume.experience])}

Provide a brief assessment:
1. Match percentage (0-100%)
2. Top 3 matching skills/experiences
3. Top 3 missing skills/experiences

Format:
Match: [X]%
Matches: [item1], [item2], [item3]
Gaps: [item1], [item2], [item3]"""
