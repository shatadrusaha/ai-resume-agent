# Streamlit Web UI Guide

## Overview

The Streamlit UI provides a user-friendly, browser-based interface for tailoring resumes without using the command line.

**Quick Start:**
```bash
./run_ui.sh
# Opens http://localhost:8501 in your browser
```

## Features

### 1. **File Upload**
- Drag-and-drop resume and job description files
- Supports plain-text `.txt` files
- Visual feedback showing loaded file names

### 2. **Ollama Connection Status**
- Real-time connection checker
- Shows Ollama server status (running/not running)
- Configure host, port, and timeout settings
- Color-coded indicators (✅ green = connected, ❌ red = disconnected)

### 3. **LLM Configuration**
- **Model**: Select which Ollama model to use (default: `llama3`)
- **Temperature**: Adjust creativity level (0.0-1.0)
  - Lower = more deterministic, higher = more creative
- **Max Tokens**: Control response length (512-8000)
- **Timeout**: Set request timeout in seconds

### 4. **Resume Tailoring**
- Single-click tailoring button
- Live progress indicator while processing
- Real-time feedback during LLM processing

### 5. **Results Display**
- Preview of tailored resume in text area
- Optional fit evaluation score showing how well the resume matches the job
- Shows tailoring confidence and key matching areas

### 6. **Download**
- Direct download button for tailored resume
- Saved as `tailored_resume.txt`
- Ready to use or further edit

## Workflow

1. **Ensure Ollama is running:**
   ```bash
   ollama serve
   ```

2. **Install dependencies (one-time):**
   ```bash
   uv sync
   ```

3. **Start the Streamlit app:**
   ```bash
   ./run_ui.sh
   ```
   Browser opens automatically at `http://localhost:8501`

4. **Use the app:**
   - Check Ollama connection status
   - Upload resume and job description
   - Configure LLM settings if desired
   - Click "✨ Tailor Resume"
   - Review results and download

## Settings Explained

### Ollama Settings
- **Host**: Where Ollama server is running (default: `localhost`)
- **Port**: Ollama server port (default: `11434`)
- **Timeout**: How long to wait for responses in seconds (default: `300`)

### Model Settings
- **Model Name**: Which Ollama model to use
  - Recommended: `llama3` (tested, balanced quality/speed)
  - Fast: `mistral`
  - Quality: `llama2`
  - Check available: `ollama list`

- **Temperature**: 
  - `0.0` = Most deterministic (good for consistent tailoring)
  - `0.7` = Default (balanced)
  - `1.0` = Most creative (may produce unusual suggestions)

- **Max Tokens**: Maximum words in response
  - Higher = longer tailored sections
  - Typical range: 2000-4000

### Evaluation
- Enable/disable fit score calculation
- Disabling speeds up tailoring slightly

## Troubleshooting

### "Ollama is not reachable"
1. Start Ollama: `ollama serve`
2. Verify it's running: `curl http://localhost:11434`
3. Check host/port settings in sidebar

### "Model not found"
1. Pull the model: `ollama pull llama3`
2. List available: `ollama list`
3. Update model name in sidebar

### Streamlit connection errors
- Restart the app: Ctrl+C, then `./run_ui.sh`
- Check Ollama is running: `ollama serve`

### File upload fails
- Ensure files are plain text (.txt)
- Check file encoding is UTF-8
- Files should be < 1 MB

## File Format

### Resume Format
```
## PERSONAL
Name: Your Name
Email: your@email.com

## SUMMARY
Your professional summary here

## EXPERIENCE
* Job Title at Company (2020 - 2023)
  Description of role and achievements

## SKILLS
- Python, JavaScript
- FastAPI, React
```

See [examples/my_resume.txt.example](../examples/my_resume.txt.example) for a complete example.

### Job Description Format
```
## JOB TITLE
Senior Software Engineer

## COMPANY
TechCorp Inc.

## REQUIRED SKILLS
- Python
- System Design
- Leadership

## RESPONSIBILITIES
- Lead engineering team
- Design scalable systems
```

See [examples/job_description.txt.example](../examples/job_description.txt.example) for a complete example.

## Privacy & Security

✅ **All processing is local** — Your resume never leaves your machine  
✅ **No cloud APIs** — Everything runs on your computer  
✅ **No external calls** — Ollama runs locally  
✅ **No data collection** — The app doesn't track or log your data

## Performance Tips

1. **Use llama3 model** (tested, good balance)
2. **Lower temperature** (0.5-0.7) for consistent results
3. **Set reasonable timeout** (300 seconds default)
4. **Keep resume under 2 pages** (for better tailoring)
5. **Ensure Ollama has enough memory** (usually 4GB+)

## Advanced Configuration

To customize Streamlit behavior, create `.streamlit/config.toml` in your project:

```toml
[client]
showErrorDetails = true
logger.level = "debug"

[server]
port = 8501
headless = true
```

## Development

### Running tests
```bash
uv run pytest
```

### Adding new features
1. Edit `src/streamlit_app.py`
2. Test with `./run_ui.sh`
3. Commit changes to git

### Code structure
```
src/streamlit_app.py
├── init_session_state()        # Initialize Streamlit session variables
├── check_ollama_connection()   # Test Ollama connectivity
├── tailor_resume()             # Core tailoring logic
└── main()                      # Main UI layout and components
```

## See Also

- [DEV_SETUP.md](DEV_SETUP.md) - Developer setup guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common errors & fixes
- [TESTING.md](TESTING.md) - Test guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Project architecture
