"""Command-line interface for the AI Resume Agent.

Provides Typer-based CLI commands for tailoring resumes to job descriptions
and testing Ollama connection.
"""

import logging
from pathlib import Path

import typer

from src.resume_agent import ResumeAgent
from src.storage import save_resume_to_file

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = typer.Typer(help="AI-powered resume tailoring agent")


@app.command()
def tailor(
    resume: str = typer.Option(
        ...,
        "--resume",
        "-r",
        help="Path to your resume file",
        exists=True,
    ),
    job_description: str = typer.Option(
        ...,
        "--job-description",
        "-j",
        help="Path to job description file",
        exists=True,
    ),
    output: str = typer.Option(
        "tailored_resume.txt",
        "--output",
        "-o",
        help="Output file for tailored resume",
    ),
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Ollama model to use (default from config)",
    ),
    evaluate: bool = typer.Option(
        False,
        "--evaluate",
        "-e",
        help="Show resume-job fit evaluation",
    ),
) -> None:
    """Tailor a resume to match a specific job description.

    Loads your master resume and a job description, then uses the LLM
    to tailor your summary, experiences, and skills to match the role.

    Args:
        resume: Path to your resume text file
        job_description: Path to job description text file
        output: Output path for tailored resume (default: tailored_resume.txt)
        model: Override default LLM model (e.g., 'llama3', 'mistral')
        evaluate: Show resume-job fit analysis before tailoring

    Example:
        uv run python main.py tailor \\\n            --resume examples/my_resume.txt \\\n            --job-description examples/job_description.txt \\\n            --output my_tailored_resume.txt
    """
    try:
        # Initialize agent
        logger.info("🚀 Starting resume tailoring agent...")
        agent = ResumeAgent()

        if model:
            agent.ollama_client.model = model
            logger.info(f"Using model: {model}")

        # Test Ollama connection
        logger.info("Checking Ollama connection...")
        agent.ollama_client.test_connection()

        # Load files
        logger.info(f"📄 Loading resume from {resume}")
        resume_obj = agent.load_resume(resume)

        logger.info(f"📋 Loading job description from {job_description}")
        job_obj = agent.load_job_description(job_description)

        # Optional: Evaluate fit first
        if evaluate:
            logger.info("Evaluating resume-job fit...")
            fit = agent.evaluate_fit(resume_obj, job_obj)
            logger.info(f"📊 Match: {fit.get('match_percentage', 0)}%")
            if fit.get("matches"):
                logger.info(f"✓ Matches: {', '.join(fit['matches'][:3])}")
            if fit.get("gaps"):
                logger.info(f"⚠ Gaps: {', '.join(fit['gaps'][:3])}")
            logger.info("")

        # Generate tailored resume
        logger.info("✨ Tailoring resume...")
        tailored_resume = agent.generate_tailored_resume(resume_obj, job_obj)

        # Save output
        logger.info(f"💾 Saving tailored resume to {output}")
        save_resume_to_file(tailored_resume, output)

        logger.info(f"✅ Success! Tailored resume saved to {output}")

    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def test_ollama() -> None:
    """Test connection to Ollama server."""
    try:
        logger.info("Testing Ollama connection...")
        agent = ResumeAgent()

        # Test connection
        agent.ollama_client.test_connection()
        logger.info("✅ Connection successful!")

        # Get available models
        logger.info("Fetching available models...")
        models = agent.ollama_client.get_available_models()

        if models:
            logger.info(f"✅ Found {len(models)} model(s):")
            for model in models:
                logger.info(f"  - {model}")
        else:
            logger.warning("⚠ No models found. Download one with:")
            logger.warning("  ollama pull mistral    # or llama2, neural-chat, etc.")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def test_sample() -> None:
    """Test tailoring with sample resume and job description."""
    try:
        sample_resume = "examples/my_resume.txt"
        sample_job = "examples/job_description.txt"

        # Check if examples exist
        if not Path(sample_resume).exists():
            logger.error(f"❌ Sample resume not found: {sample_resume}")
            raise typer.Exit(code=1)

        if not Path(sample_job).exists():
            logger.error(f"❌ Sample job description not found: {sample_job}")
            raise typer.Exit(code=1)

        logger.info("Testing with sample files...")
        logger.info(f"Resume: {sample_resume}")
        logger.info(f"Job: {sample_job}")

        # Run tailoring
        agent = ResumeAgent()
        agent.ollama_client.test_connection()

        resume = agent.load_resume(sample_resume)
        job = agent.load_job_description(sample_job)

        logger.info("✨ Generating tailored resume...")
        tailored = agent.generate_tailored_resume(resume, job)

        # Save to sample output
        output_file = "examples/tailored_sample_resume.txt"
        save_resume_to_file(tailored, output_file)

        logger.info(f"✅ Sample tailored resume saved to {output_file}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
