"""Core resume tailoring agent orchestration.

The ResumeAgent class coordinates file I/O, LLM calls, and parsing
to transform a master resume into a job-specific tailored version.
"""

import logging
from typing import Optional

from src.llm_client import OllamaClient, OllamaConnectionError
from src.models import JobDescription, Resume, Experience, Skill
from src.prompts import PromptTemplates
from src.storage import load_job_description_from_file, load_resume_from_file

logger = logging.getLogger(__name__)


class ResumeAgent:
    """Main orchestrator for tailoring resumes to specific job descriptions.

    Coordinates loading resumes and job descriptions, calling the LLM to tailor
    each section (summary, experiences, skills), and assembling the final result.

    Attributes:
        ollama_client: OllamaClient for LLM communication
    """

    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        """Initialize the resume tailoring agent.

        Args:
            ollama_client: OllamaClient instance. If None, creates a default client
                using configuration from .env
        """
        self.ollama_client = ollama_client or OllamaClient()
        logger.info("ResumeAgent initialized")

    def load_resume(self, file_path: str) -> Resume:
        """Load a resume from a text file.

        Args:
            file_path: Path to resume text file (e.g., 'examples/my_resume.txt')

        Returns:
            Resume object with all sections populated

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If resume format is invalid
        """
        logger.info(f"Loading resume from {file_path}")
        resume = load_resume_from_file(file_path)
        logger.info(
            f"Loaded resume for {resume.name} with {len(resume.experience)} experiences"
        )
        return resume

    def load_job_description(self, file_path: str) -> JobDescription:
        """Load a job description from a text file.

        Args:
            file_path: Path to job description file (e.g., 'examples/job_description.txt')

        Returns:
            JobDescription object with all fields populated

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If job description format is invalid
        """
        logger.info(f"Loading job description from {file_path}")
        job = load_job_description_from_file(file_path)
        logger.info(f"Loaded job: {job.title} at {job.company}")
        return job

    def tailor_summary(self, resume: Resume, job_description: JobDescription) -> str:
        """Generate a tailored summary for the target job.

        Uses the LLM to rewrite the professional summary to emphasize
        job-relevant accomplishments and keywords.

        Args:
            resume: User's resume with original summary
            job_description: Target job description

        Returns:
            Tailored summary text

        Raises:
            OllamaConnectionError: If LLM communication fails
        """
        logger.info("Tailoring summary...")
        prompt = PromptTemplates.tailor_summary_prompt(resume, job_description)

        try:
            tailored_summary = self.ollama_client.call_ollama_with_retry(
                prompt,
                max_retries=3,
            )
            logger.info(f"Summary tailored ({len(tailored_summary)} chars)")
            return tailored_summary
        except OllamaConnectionError as e:
            logger.error(f"Failed to tailor summary: {str(e)}")
            raise

    def tailor_experience(
        self, resume: Resume, job_description: JobDescription
    ) -> list[Experience]:
        """Tailor and reorder experiences to match the target job.

        Uses the LLM to reorder work history by relevance and rewrite
        achievements to highlight job-required skills.

        Args:
            resume: User's resume with original experiences
            job_description: Target job description

        Returns:
            List of tailored Experience objects, most relevant first

        Raises:
            OllamaConnectionError: If LLM communication fails
        """
        logger.info("Tailoring experience...")
        prompt = PromptTemplates.tailor_experience_prompt(resume, job_description)

        try:
            tailored_text = self.ollama_client.call_ollama_with_retry(
                prompt,
                max_retries=3,
            )
            logger.debug(f"Experience response from LLM: {len(tailored_text)} chars")

            # Parse LLM response back into Experience objects
            experiences = self._parse_experience_from_text(tailored_text, resume)
            logger.info(f"Parsed {len(experiences)} tailored experiences")
            return experiences

        except OllamaConnectionError as e:
            logger.error(f"Failed to tailor experience: {str(e)}")
            raise

    def tailor_skills(
        self, resume: Resume, job_description: JobDescription
    ) -> list[Skill]:
        """Tailor and rank skills by job relevance.

        Uses the LLM to filter skills and reorder by importance to the
        target role. Keeps top 15-20 most relevant skills.

        Args:
            resume: User's resume with original skills
            job_description: Target job description

        Returns:
            List of tailored Skill objects, ranked by relevance

        Raises:
            OllamaConnectionError: If LLM communication fails
        """
        logger.info("Tailoring skills...")
        prompt = PromptTemplates.tailor_skills_prompt(resume, job_description)

        try:
            tailored_text = self.ollama_client.call_ollama_with_retry(
                prompt,
                max_retries=3,
            )
            logger.debug(f"Skills response from LLM: {len(tailored_text)} chars")

            # Parse LLM response (comma-separated) into Skill objects
            skills = self._parse_skills_from_text(tailored_text)
            logger.info(f"Parsed {len(skills)} tailored skills")
            return skills

        except OllamaConnectionError as e:
            logger.error(f"Failed to tailor skills: {str(e)}")
            raise

    def evaluate_fit(self, resume: Resume, job_description: JobDescription) -> dict:
        """Evaluate how well the resume matches the target job.

        Uses the LLM to analyze resume-job fit and identify strengths
        and skill gaps.

        Args:
            resume: User's resume
            job_description: Target job description

        Returns:
            Dictionary with 'match_percentage', 'matches', and 'gaps' keys
        """
        logger.info("Evaluating resume-job fit...")
        prompt = PromptTemplates.evaluate_relevance_prompt(resume, job_description)

        try:
            evaluation = self.ollama_client.call_ollama_with_retry(
                prompt,
                max_retries=2,
            )
            logger.debug(f"Evaluation from LLM: {evaluation}")

            # Parse evaluation text
            result = self._parse_evaluation(evaluation)
            logger.info(f"Resume-job fit: {result.get('match_percentage')}%")
            return result

        except OllamaConnectionError as e:
            logger.error(f"Failed to evaluate fit: {str(e)}")
            return {"error": str(e), "match_percentage": 0}

    def generate_tailored_resume(
        self, resume: Resume, job_description: JobDescription
    ) -> Resume:
        """Generate a complete resume tailored to the target job.

        Coordinates tailoring of all resume sections (summary, experiences,
        skills) and returns a new Resume object with job-specific content.

        Args:
            resume: User's master resume
            job_description: Target job description

        Returns:
            New Resume object with tailored content
        """
        logger.info(f"Generating tailored resume for {job_description.title}...")

        # Tailor each section
        tailored_summary = self.tailor_summary(resume, job_description)
        tailored_experiences = self.tailor_experience(resume, job_description)
        tailored_skills = self.tailor_skills(resume, job_description)

        # Create new resume with tailored content
        tailored_resume = Resume(
            name=resume.name,
            email=resume.email,
            phone=resume.phone,
            summary=tailored_summary,
            experience=tailored_experiences,
            skills=tailored_skills,
        )

        logger.info("Tailored resume generated successfully")
        return tailored_resume

    @staticmethod
    def _parse_experience_from_text(
        text: str, original_resume: Resume
    ) -> list[Experience]:
        """Parse LLM-generated experience text back into Experience objects.

        Extracts position information and descriptions from LLM output,
        with fallback to original experiences if parsing fails.

        Args:
            text: LLM-generated experience text
            original_resume: Original resume for fallback reference

        Returns:
            List of parsed Experience objects
        """
        experiences = []
        lines = text.strip().split("\n")

        current_position = None
        current_description = []

        for line in lines:
            line = line.strip()
            if not line:
                if current_position and current_description:
                    # Save previous experience
                    try:
                        exp = ResumeAgent._create_experience_from_text(
                            current_position, "\n".join(current_description)
                        )
                        if exp:
                            experiences.append(exp)
                    except Exception as e:
                        logger.warning(f"Could not parse experience: {e}")

                    current_position = None
                    current_description = []
            elif line.startswith("Position"):
                # New position starting
                if current_position and current_description:
                    try:
                        exp = ResumeAgent._create_experience_from_text(
                            current_position, "\n".join(current_description)
                        )
                        if exp:
                            experiences.append(exp)
                    except Exception as e:
                        logger.warning(f"Could not parse experience: {e}")

                current_position = line
                current_description = []
            elif line.startswith("Description:"):
                current_description.append(line.replace("Description:", "").strip())
            else:
                if current_position:
                    current_description.append(line)

        # Don't forget last experience
        if current_position and current_description:
            try:
                exp = ResumeAgent._create_experience_from_text(
                    current_position, "\n".join(current_description)
                )
                if exp:
                    experiences.append(exp)
            except Exception as e:
                logger.warning(f"Could not parse experience: {e}")

        # If parsing failed, return top experiences from original resume
        if not experiences:
            logger.warning(
                "Could not parse experiences from LLM output, using original top 3"
            )
            return original_resume.experience[:3]

        return experiences

    @staticmethod
    def _create_experience_from_text(
        position_line: str, description: str
    ) -> Optional[Experience]:
        """Create an Experience object from parsed text lines.

        Extracts job title, company, dates, and description from
        LLM-formatted position and description lines.

        Args:
            position_line: Line containing position info (e.g., 'Position 1: ...')
            description: Description text with achievements

        Returns:
            Experience object if parsing succeeds, None otherwise
        """
        import re

        # Parse: "Position X: [Title] at [Company] ([Start] - [End])"
        match = re.search(
            r"Position\s+\d+:\s+(.+?)\s+at\s+(.+?)\s*\((.+?)\s*-\s*(.+?)\)",
            position_line,
        )

        if match:
            job_title = match.group(1).strip()
            company = match.group(2).strip()
            start_date = match.group(3).strip()
            end_date = match.group(4).strip()
            description = description.strip()

            return Experience(
                job_title=job_title,
                company=company,
                start_date=start_date,
                end_date=end_date,
                description=description,
            )

        return None

    @staticmethod
    def _parse_skills_from_text(text: str) -> list[Skill]:
        """Parse skills from LLM response, supporting grouped format.

        Handles both grouped format (Category: skill1, skill2) and
        legacy flat comma-separated format. Preserves category information
        from grouped format or defaults to General.

        Args:
            text: LLM-generated skills text (grouped or comma-separated)

        Returns:
            List of Skill objects in order from most to least relevant
        """
        skills = []
        lines = text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line has category format (Category: skill1, skill2)
            if ":" in line:
                parts = line.split(":", 1)
                category = parts[0].strip()
                skills_text = parts[1].strip()
                # Parse skills for this category
                for skill_name in skills_text.split(","):
                    skill_name = skill_name.strip()
                    if skill_name:
                        skills.append(Skill(name=skill_name, category=category))
            else:
                # Flat format - treat as comma-separated skills without category
                for skill_name in line.split(","):
                    skill_name = skill_name.strip()
                    if skill_name:
                        skills.append(Skill(name=skill_name, category="General"))

        return skills

    @staticmethod
    def _parse_evaluation(text: str) -> dict:
        """Parse LLM evaluation response for resume-job fit.

        Extracts match percentage, strengths, and skill gaps from
        LLM analysis output.

        Args:
            text: LLM-generated evaluation text

        Returns:
            Dictionary with keys: 'match_percentage', 'matches', 'gaps'
        """
        import re

        result = {
            "match_percentage": 0,
            "matches": [],
            "gaps": [],
        }

        # Extract match percentage
        match_pct = re.search(r"Match:\s*(\d+)%", text)
        if match_pct:
            result["match_percentage"] = int(match_pct.group(1))

        # Extract matches
        matches_line = re.search(r"Matches:\s*(.+?)(?:Gaps:|$)", text, re.DOTALL)
        if matches_line:
            matches_text = matches_line.group(1).strip()
            result["matches"] = [
                m.strip() for m in matches_text.split(",") if m.strip()
            ]

        # Extract gaps
        gaps_line = re.search(r"Gaps:\s*(.+?)$", text, re.DOTALL)
        if gaps_line:
            gaps_text = gaps_line.group(1).strip()
            result["gaps"] = [g.strip() for g in gaps_text.split(",") if g.strip()]

        return result
