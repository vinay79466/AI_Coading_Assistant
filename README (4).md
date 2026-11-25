# AI Coding Assistant

Generate, explain, debug, improve and test code, and chat with any GitHub repo (RAG).

## Architecture

```
Streamlit UI / FastAPI
        ↓
   llm.py + prompts.py  →  Claude API
        ↓
   rag.py: clone → split → embed → ChromaDB → retrieve
        ↓
   GitHub repository
```

## Files

| File | Purpose |
|---|---|
| `prompts.py` | Prompt template per feature |
| `llm.py` | Claude API wrapper, one function per feature |
| `rag.py` | Repo cloning, chunking, embeddings, retrieval |
| `api.py` | FastAPI REST endpoints |
| `app.py` | Streamlit web UI |
| `Dockerfile` | Container for deployment |

## Run locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add your ANTHROPIC_API_KEY
streamlit run app.py        # UI at http://localhost:8501
uvicorn api:app --reload    # API docs at http://localhost:8000/docs
```

## Docker

```bash
docker build -t ai-coding-assistant .
docker run -p 8501:8501 --env-file .env ai-coding-assistant
```

## Roadmap

1. **Stage 1** – generate / explain / debug (done)
2. **Stage 2** – file upload, multi-language, tests (done)
3. **Stage 3** – RAG over a codebase (done, basic line-based chunking)
4. **Stage 4** – portfolio polish: AST-aware chunking, chat history,
   streaming responses, auth, deploy to a live URL, CI with pytest.

## Deploying

Streamlit Community Cloud, Render, Railway or Fly.io all work with the Dockerfile.
Set `ANTHROPIC_API_KEY` as a secret in the host's dashboard.
