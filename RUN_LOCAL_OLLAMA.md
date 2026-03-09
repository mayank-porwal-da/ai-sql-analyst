# Run Local LLM with Ollama (Step-by-Step)

This guide explains how to run this Streamlit app with local LLMs using Ollama.

## 1. Install Ollama

1. Download Ollama from: https://ollama.com/download
2. Install it for your OS (Windows/macOS/Linux).
3. Verify installation:

```bash
ollama --version
```

## 2. Start Ollama Service

Ollama must be running before starting the app.

- On most systems, Ollama starts automatically after installation.
- If needed, start it manually:

```bash
ollama serve
```

Keep this process running.

## 3. Pull Local Models

From a terminal, pull the models used by this project:

```bash
ollama pull llama3.2
ollama pull qwen2.5:7b
```

Optional: verify local models

```bash
ollama list
```

## 4. Go to Project Folder

```bash
cd learn_to_call_llm_apis/final_project
```

## 5. Create and Activate Virtual Environment

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

## 6. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 7. Run the Streamlit App

```bash
streamlit run app.py
```

If `streamlit` command is not available:

```bash
python -m streamlit run app.py
```

## 8. Select a Local Model in App

1. Open the `Chatbot` tab.
2. In `Chatbot Settings`, select:
   - `llama3.2` or
   - `qwen2.5:7b`
3. Ask a database question.

## Troubleshooting

### Error: `Connection refused` or model not responding

- Ensure Ollama is running: `ollama serve`
- Confirm app expects Ollama at `http://localhost:11434` (already configured in code).

### Error: `model not found`

- Pull model first:

```bash
ollama pull llama3.2
```

or

```bash
ollama pull qwen2.5:7b
```

### App works with Gemini but not local model

- This usually means Ollama is not running or model is not pulled.
- Check:
  - `ollama list`
  - `ollama serve`

## Notes

- Local Ollama models do not require `GOOGLE_API_KEY`.
- You can still use Gemini if configured, but local mode is fully offline after model download.
