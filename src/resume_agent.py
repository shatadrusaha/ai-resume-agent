"""Core resume tailoring agent."""

import logging
from typing import Optional

from src.llm_client import OllamaClient, OllamaConnectionError
from src.models import JobDescription, Resume, Experience, Skill
from src.prompts import PromptTemplates
from src.storage import load_job_description_from_file, load_resume_from_file

logger = logging.getLogger(__name__)


class ResumeAgent:
    """Main agent for tailoring resumes to job descriptions."""

    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        """
        Initialize the resume agent.

        Args:
            ollama_client: OllamaClient instance. If None, creates default client.
        """
        self.ollama_client = ollama_client or OllamaClient()
        logger.info("ResumeAgent initialized")

    def load_resume(self, file_path: str) -> Resume:
        """
        Load resume from file.

        Args:
            file_path: Path to resume text file

        Returns:
            Resume object
        """
        logger.info(f"Loading resume from {file_path}")
        resume = load_resume_from_file(file_path)
        logger.info(f"Loaded resume for {resume.name} with {len(resume.experience)} experiences")
        return resume

    def load_job_description(self, file_path: str) -> JobDescription:
        """
        Load job description from file.

        Args:
            file_path: Path to job description text file

        Returns:
            JobDescription object
        """
        logger.info(f"Loading job description from {file_path}")
        job = load_job_description_from_file(file_path)
        logger.info(f"Loaded job: {job.title} at {job.company}")
        return job

    def tailor_summary(self, resume: Resume, job_description: JobDescription) -> str:
        """
        Generate a tailored summary for the job.

        Args:
            resume: User's resume
            job_description: Target job description

        Returns:
            Tailored summary text
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
        """
        Generate tailored and reordered experience entries.

        Args:
            resume: User's resume
            job_description: Target job description

        Returns:
            List of tailored Experience objects
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
        """
        Generate tailored and ranked skills.

        Args:
            resume: User's resume
            job_description: Target job description

        Returns:
            List of tailored Skill objects, ranked by relevance
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
        """
        Evaluate how well the resume fits the job.

        Args:
            resume: User's resume
            job_description: Target job description

        Returns:
            Dictionary with match percentage and gap analysis
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
        """
        Generate a fully tailored resume for the job.

        Args:
            resume: User's resume
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
    def _parse_experience_from_text(text: str, original_resume: Resume) -> list[Experience]:
        """
        Parse LLM response back into Experience objects.

        Args:
            text: LLM-generated experience text
            original_resume: Original resume for reference

        Returns:
            List of Experience objects
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
            logger.warning("Could not parse experiences from LLM output, using original top 3")
            return original_resume.experience[:3]

        return experiences

    @staticmethod
    def _create_experience_from_text(position_line: str, description: str) -> Optional[Experience]:
        """
        Create an Experience object from parsed text.

        Args:
            position_line: Line with position info
            description: Description text

        Returns:
            Experience object or None if parsing fails
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
        """
        Parse comma-separated skills from LLM response.

        Args:
            text: LLM-generated skills text

        Returns:
            List of Skill objects
        """
        skills = []

        # Split by comma and clean up
        skill_names = [s.strip() for s in text.split(",")]

        for skill_name in skill_names:
            if skill_name:
                skills.append(Skill(name=skill_name))

        return skills

    @staticmethod
    def _parse_evaluation(text: str) -> dict:
        """
        Parse evaluation response from LLM.

        Args:
            text: LLM-generated evaluation

        Returns:
            Dictionary with match percentage and gaps
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
            result["matches"] = [m.strip() for m in matches_text.split(",") if m.strip()]

        # Extract gaps
        gaps_line = re.search(r"Gaps:\s*(.+?)$", text, re.DOTALL)
        if gaps_line:
            gaps_text = gaps_line.group(1).strip()
            result["gaps"] = [g.strip() for g in gaps_text.split(",") if g.strip()]

        return result
