#!/bin/bash
# Run the Streamlit UI for the AI Resume Agent
# Usage: ./run_ui.sh

echo "Starting AI Resume Agent UI..."
echo "Opening browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Set PYTHONPATH to project root so imports work correctly
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

uv run streamlit run src/streamlit_app.py
