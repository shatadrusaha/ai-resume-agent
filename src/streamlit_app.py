"""Streamlit web UI for the AI Resume Agent.

This module provides a user-friendly web interface for tailoring resumes
using the AI Resume Agent. Users can upload their resume and job description,
configure LLM settings, and download the tailored resume.

Features:
    - Drag-and-drop file upload for resume and job description
    - Real-time Ollama connection status
    - Configurable LLM settings (model, temperature, timeout)
    - Progress indicators during processing
    - Download tailored resume
    - View evaluation score

Typical usage:
    uv run streamlit run src/streamlit_app.py
"""

import streamlit as st
import os

from src.config import OllamaConfig
from src.llm_client import OllamaClient
from src.resume_agent import ResumeAgent
from src.storage import (
    parse_resume_from_text,
    parse_job_description_from_text,
)


def init_session_state():
    """Initialize Streamlit session state variables.

    Creates session state keys for tracking:
        - resume_text: Parsed resume text
        - job_text: Parsed job description text
        - tailored_resume: Generated tailored resume
        - ollama_status: Ollama connection status
    """
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = None
    if "job_text" not in st.session_state:
        st.session_state.job_text = None
    if "tailored_resume" not in st.session_state:
        st.session_state.tailored_resume = None
    if "ollama_status" not in st.session_state:
        st.session_state.ollama_status = None


def check_ollama_connection(host: str, port: int, timeout: int) -> bool:
    """Check if Ollama server is running and reachable.

    Args:
        host: Ollama server hostname (e.g., "localhost")
        port: Ollama server port (e.g., 11434)
        timeout: Connection timeout in seconds

    Returns:
        True if Ollama is reachable, False otherwise
    """
    try:
        config = OllamaConfig(host=host, port=port, timeout=timeout)
        client = OllamaClient(config=config)
        client.test_connection()
        return True
    except Exception:
        return False


def tailor_resume(
    resume_text: str,
    job_text: str,
    model: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
    evaluate: bool = True,
) -> tuple:
    """Tailor resume to job description using ResumeAgent.

    Args:
        resume_text: Plain-text resume content
        job_text: Plain-text job description content
        model: LLM model name (e.g., "llama3")
        temperature: LLM creativity (0.0-1.0)
        max_tokens: Max generated tokens
        timeout: Request timeout in seconds
        evaluate: Whether to evaluate fit score

    Returns:
        Tuple of (tailored_resume, evaluation_text) or (None, error_msg)
    """
    try:
        # Parse resume and job description from text
        resume = parse_resume_from_text(resume_text)
        job = parse_job_description_from_text(job_text)

        # Create Ollama config with user-provided settings
        ollama_config = OllamaConfig(
            host=os.getenv("OLLAMA_HOST", "localhost"),
            port=int(os.getenv("OLLAMA_PORT", "11434")),
            model=model,
            timeout=timeout,
        )

        # Create OllamaClient with config and ResumeAgent with that client
        client = OllamaClient(config=ollama_config)
        agent = ResumeAgent(ollama_client=client)

        # Generate tailored resume
        tailored = agent.generate_tailored_resume(resume, job)

        # Evaluate fit if requested
        evaluation = None
        if evaluate:
            evaluation = agent.evaluate_fit(resume, job)

        return tailored, evaluation

    except Exception as e:
        return None, f"Error: {str(e)}"


def main():
    """Main Streamlit app entry point."""
    st.set_page_config(
        page_title="AI Resume Agent",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()

    # Header
    st.title("📄 AI Resume Agent")
    st.markdown(
        """
    Tailor your resume to any job description using **local AI** (Ollama).
    No cloud APIs, no external services—everything runs on your machine.
    """
    )

    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")

        # Ollama connection status
        st.subheader("Ollama Status")
        ollama_host = st.text_input("Ollama Host", value="localhost")
        ollama_port = st.number_input(
            "Ollama Port", value=11434, min_value=1024, max_value=65535
        )
        ollama_timeout = st.number_input(
            "Timeout (seconds)", value=300, min_value=10, max_value=3600
        )

        if st.button("🔗 Check Connection"):
            with st.spinner("Testing Ollama connection..."):
                is_connected = check_ollama_connection(
                    ollama_host, ollama_port, ollama_timeout
                )
                st.session_state.ollama_status = is_connected

        if st.session_state.ollama_status is True:
            st.success("✅ Ollama is running")
        elif st.session_state.ollama_status is False:
            st.error("❌ Ollama is not reachable")
        else:
            st.info("Click 'Check Connection' to test")

        st.divider()

        # Model settings
        st.subheader("Model Settings")
        model = st.text_input("Model Name", value="llama3")
        temperature = st.slider(
            "Temperature (creativity)",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
        )
        max_tokens = st.number_input(
            "Max Tokens", value=2000, min_value=512, max_value=8000, step=256
        )

        st.divider()

        # Options
        st.subheader("Options")
        evaluate = st.checkbox("Evaluate Resume-Job Fit", value=True)

    # Main content
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Upload Resume")
        resume_file = st.file_uploader(
            "Upload your master resume (text file)",
            type=["txt"],
            key="resume_uploader",
        )
        if resume_file:
            st.session_state.resume_text = resume_file.read().decode("utf-8")
            st.success(f"Loaded: {resume_file.name}")

    with col2:
        st.subheader("💼 Upload Job Description")
        job_file = st.file_uploader(
            "Upload job description (text file)",
            type=["txt"],
            key="job_uploader",
        )
        if job_file:
            st.session_state.job_text = job_file.read().decode("utf-8")
            st.success(f"Loaded: {job_file.name}")

    st.divider()

    # Action button
    if st.session_state.resume_text and st.session_state.job_text:
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if st.button("✨ Tailor Resume", type="primary", use_container_width=True):
                if st.session_state.ollama_status is not True:
                    st.error("⚠️ Please check Ollama connection first!")
                else:
                    with st.spinner("Tailoring your resume..."):
                        tailored, evaluation = tailor_resume(
                            st.session_state.resume_text,
                            st.session_state.job_text,
                            model=model,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            timeout=ollama_timeout,
                            evaluate=evaluate,
                        )

                        if tailored:
                            st.session_state.tailored_resume = tailored
                            st.success("✅ Resume tailored successfully!")

                            # Display results
                            st.subheader("📋 Tailored Resume Preview")
                            st.text_area(
                                "Tailored Resume",
                                value=str(tailored),
                                height=400,
                                disabled=True,
                            )

                            # Evaluation score
                            if evaluation and evaluate:
                                st.divider()
                                st.subheader("🎯 Fit Evaluation")

                                # Format evaluation nicely
                                match_pct = evaluation.get("match_percentage", 0)
                                matches = evaluation.get("matches", [])
                                gaps = evaluation.get("gaps", [])

                                # Display match percentage with progress bar
                                col1, col2, col3 = st.columns([1, 2, 1])
                                with col2:
                                    # Determine color based on match score
                                    if match_pct >= 80:
                                        color = "🟢"
                                        quality = "Excellent Match"
                                    elif match_pct >= 60:
                                        color = "🟡"
                                        quality = "Good Match"
                                    elif match_pct >= 40:
                                        color = "🟠"
                                        quality = "Fair Match"
                                    else:
                                        color = "🔴"
                                        quality = "Needs Work"

                                    st.write(f"### {color} {match_pct}% Match")
                                    st.write(f"*{quality}*")

                                # Full-width progress bar
                                st.progress(match_pct / 100.0)

                                # Display matches
                                if matches:
                                    st.write("**✅ Your Strengths:**")
                                    for match in matches:
                                        st.write(f"- {match}")

                                # Display gaps
                                if gaps:
                                    st.write("**⚠️ Skill Gaps:**")
                                    for gap in gaps:
                                        st.write(f"- {gap}")

                            # Download button
                            st.divider()
                            st.download_button(
                                label="⬇️ Download Tailored Resume",
                                data=str(tailored),
                                file_name="tailored_resume.txt",
                                mime="text/plain",
                            )
                        else:
                            st.error(f"Failed to tailor resume: {evaluation}")

    else:
        st.info(
            "👆 Upload your resume and job description to get started",
            icon="ℹ️",
        )

    # Footer
    st.divider()
    st.caption(
        "🔒 Privacy: Everything runs locally on your machine. "
        "Your data never leaves your computer."
    )


if __name__ == "__main__":
    main()
