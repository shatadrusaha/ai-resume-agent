"""Tests for resume_agent.py — Resume tailoring orchestration."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.resume_agent import ResumeAgent
from src.models import Resume, Experience, Skill, JobDescription
from src.llm_client import OllamaClient, OllamaConnectionError


class TestResumeAgentInit:
    """Test ResumeAgent initialization."""

    def test_resume_agent_init_with_default_client(self):
        """Initialize ResumeAgent with default client."""
        with patch("src.resume_agent.OllamaClient") as mock_ollama:
            agent = ResumeAgent()
            assert agent.ollama_client is not None

    def test_resume_agent_init_with_custom_client(self):
        """Initialize ResumeAgent with custom OllamaClient."""
        mock_client = Mock(spec=OllamaClient)
        agent = ResumeAgent(ollama_client=mock_client)
        assert agent.ollama_client is mock_client


class TestResumeAgentLoadResume:
    """Test loading resume from file."""

    def test_load_resume_from_file(self, tmp_resume_file):
        """Load resume from temporary file."""
        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = Mock()

            resume = agent.load_resume(str(tmp_resume_file))
            assert resume.name == "Alex Johnson"
            assert len(resume.experience) == 3
            assert len(resume.skills) == 10

    def test_load_resume_file_not_found(self):
        """Handle missing resume file."""
        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = Mock()

            with pytest.raises(FileNotFoundError):
                agent.load_resume("/nonexistent/file.txt")


class TestResumeAgentLoadJobDescription:
    """Test loading job description from file."""

    def test_load_job_description_from_file(self, tmp_job_description_file):
        """Load job description from temporary file."""
        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = Mock()

            job = agent.load_job_description(str(tmp_job_description_file))
            assert job.title == "Staff Backend Engineer"
            assert job.company == "CloudInnovate Solutions"

    def test_load_job_description_file_not_found(self):
        """Handle missing job description file."""
        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = Mock()

            with pytest.raises(FileNotFoundError):
                agent.load_job_description("/nonexistent/file.txt")


class TestResumeAgentTailorSummary:
    """Test summary tailoring."""

    def test_tailor_summary_success(self, sample_resume, sample_job_description):
        """Successfully tailor resume summary."""
        mock_client = Mock(spec=OllamaClient)
        mock_client.call_ollama_with_retry.return_value = "Tailored summary text."

        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = mock_client

            result = agent.tailor_summary(sample_resume, sample_job_description)
            assert result == "Tailored summary text."
            mock_client.call_ollama_with_retry.assert_called_once()

    def test_tailor_summary_connection_error(
        self, sample_resume, sample_job_description
    ):
        """Handle connection error during summary tailoring."""
        mock_client = Mock(spec=OllamaClient)
        mock_client.call_ollama_with_retry.side_effect = OllamaConnectionError(
            "Connection failed"
        )

        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = mock_client

            with pytest.raises(OllamaConnectionError):
                agent.tailor_summary(sample_resume, sample_job_description)


class TestResumeAgentTailorExperience:
    """Test experience tailoring."""

    def test_tailor_experience_success(self, sample_resume, sample_job_description):
        """Successfully tailor experiences."""
        llm_response = """Position 1: Senior Backend Engineer at TechCorp (2020 - Present)
Description: Led architecture migration
Position 2: Backend Engineer at StartupXYZ (2018 - 2020)
Description: Built API services"""

        mock_client = Mock(spec=OllamaClient)
        mock_client.call_ollama_with_retry.return_value = llm_response

        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = mock_client

            result = agent.tailor_experience(sample_resume, sample_job_description)
            assert isinstance(result, list)
            assert len(result) > 0

    def test_tailor_experience_fallback_to_original(
        self, sample_resume, sample_job_description
    ):
        """Fallback to original experiences if parsing fails."""
        mock_client = Mock(spec=OllamaClient)
        # Return unparseable text
        mock_client.call_ollama_with_retry.return_value = (
            "This is not parseable experience text"
        )

        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = mock_client

            result = agent.tailor_experience(sample_resume, sample_job_description)
            # Should return fallback (original top 3)
            assert isinstance(result, list)
            assert len(result) > 0


class TestResumeAgentTailorSkills:
    """Test skills tailoring."""

    def test_tailor_skills_success(self, sample_resume, sample_job_description):
        """Successfully tailor skills."""
        llm_response = "Python, FastAPI, PostgreSQL, Docker, Kubernetes, AWS"

        mock_client = Mock(spec=OllamaClient)
        mock_client.call_ollama_with_retry.return_value = llm_response

        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = mock_client

            result = agent.tailor_skills(sample_resume, sample_job_description)
            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(skill, Skill) for skill in result)

    def test_tailor_skills_empty_response(self, sample_resume, sample_job_description):
        """Handle empty skills response."""
        mock_client = Mock(spec=OllamaClient)
        mock_client.call_ollama_with_retry.return_value = ""

        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = mock_client

            result = agent.tailor_skills(sample_resume, sample_job_description)
            assert isinstance(result, list)


class TestResumeAgentEvaluateFit:
    """Test resume-job fit evaluation."""

    def test_evaluate_fit_success(self, sample_resume, sample_job_description):
        """Successfully evaluate resume-job fit."""
        llm_response = """Match: 75%
Strengths: Python, Backend experience, Leadership
Gaps: Cloud experience, Go language"""

        mock_client = Mock(spec=OllamaClient)
        mock_client.call_ollama_with_retry.return_value = llm_response

        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = mock_client

            result = agent.evaluate_fit(sample_resume, sample_job_description)
            assert isinstance(result, dict)
            assert "match_percentage" in result

    def test_evaluate_fit_connection_error(self, sample_resume, sample_job_description):
        """Handle connection error during evaluation."""
        mock_client = Mock(spec=OllamaClient)
        mock_client.call_ollama_with_retry.side_effect = OllamaConnectionError("Failed")

        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = mock_client

            result = agent.evaluate_fit(sample_resume, sample_job_description)
            # Should return error dict
            assert isinstance(result, dict)
            assert "error" in result


class TestResumeAgentGenerateTailoredResume:
    """Test full resume tailoring generation."""

    def test_generate_tailored_resume_success(
        self, sample_resume, sample_job_description
    ):
        """Successfully generate a complete tailored resume."""
        mock_client = Mock(spec=OllamaClient)
        mock_client.call_ollama_with_retry.side_effect = [
            "Tailored summary",
            "Position 1: Role at Company (2020 - Present)\nDescription: Achievement",
            "Skill1, Skill2, Skill3",
        ]

        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = mock_client

            result = agent.generate_tailored_resume(
                sample_resume, sample_job_description
            )
            assert isinstance(result, Resume)
            assert result.name == sample_resume.name
            assert result.summary == "Tailored summary"

    def test_generate_tailored_resume_preserves_contact(
        self, sample_resume, sample_job_description
    ):
        """Ensure contact info is preserved in tailored resume."""
        mock_client = Mock(spec=OllamaClient)
        mock_client.call_ollama_with_retry.side_effect = [
            "New summary",
            "Position 1: Role at Company (2020 - Present)\nDescription: Achievement",
            "Skill1, Skill2",
        ]

        with patch.object(ResumeAgent, "__init__", lambda x: None):
            agent = ResumeAgent()
            agent.ollama_client = mock_client

            result = agent.generate_tailored_resume(
                sample_resume, sample_job_description
            )
            assert result.name == sample_resume.name
            assert result.email == sample_resume.email
            assert result.phone == sample_resume.phone


class TestResumeAgentParsingMethods:
    """Test internal parsing methods."""

    def test_parse_experience_from_text_success(self, sample_resume):
        """Parse experience from LLM text."""
        text = """Position 1: Senior Engineer at TechCorp (2020 - Present)
  Led team and improved performance
  
Position 2: Junior Engineer at StartupXYZ (2018 - 2020)
  Wrote backend code"""

        result = ResumeAgent._parse_experience_from_text(text, sample_resume)
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(exp, Experience) for exp in result)

    def test_parse_skills_from_text(self):
        """Parse comma-separated skills."""
        text = "Python, FastAPI, PostgreSQL, Docker, Kubernetes"

        result = ResumeAgent._parse_skills_from_text(text)
        assert isinstance(result, list)
        assert len(result) == 5
        assert all(isinstance(skill, Skill) for skill in result)

    def test_parse_evaluation_with_percentage(self):
        """Parse evaluation with match percentage."""
        text = """Match: 80%
Strengths: Python skills, leadership
Gaps: Cloud infrastructure"""

        result = ResumeAgent._parse_evaluation(text)
        assert isinstance(result, dict)
        assert result["match_percentage"] == 80

    def test_parse_evaluation_default_percentage(self):
        """Parse evaluation with missing percentage."""
        text = "Some evaluation text without match percentage"

        result = ResumeAgent._parse_evaluation(text)
        assert isinstance(result, dict)
        assert "match_percentage" in result
