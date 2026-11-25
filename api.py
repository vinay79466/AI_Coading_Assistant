"""FastAPI backend. Run: uvicorn api:app --reload"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import llm
import rag

app = FastAPI(title="AI Coding Assistant")


class CodeIn(BaseModel):
    code: str
    language: str = "Python"


class GenIn(BaseModel):
    request: str
    language: str = "Python"


class TestIn(CodeIn):
    framework: str = "pytest"


class RepoIn(BaseModel):
    repo_url: str


class AskIn(RepoIn):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
def generate(body: GenIn):
    return {"result": llm.generate_code(body.request, body.language)}


@app.post("/explain")
def explain(body: CodeIn):
    return {"result": llm.explain_code(body.code, body.language)}


@app.post("/debug")
def debug(body: CodeIn):
    return {"result": llm.find_bugs(body.code, body.language)}


@app.post("/improve")
def improve(body: CodeIn):
    return {"result": llm.improve_code(body.code, body.language)}


@app.post("/tests")
def tests(body: TestIn):
    return {"result": llm.generate_tests(body.code, body.language, body.framework)}


@app.post("/repo/index")
def repo_index(body: RepoIn):
    try:
        return {"chunks": rag.index_repo(body.repo_url)}
    except Exception as e:
        raise HTTPException(400, f"Could not index repo: {e}")


@app.post("/repo/ask")
def repo_ask(body: AskIn):
    try:
        chunks = rag.retrieve(body.repo_url, body.question)
    except Exception:
        raise HTTPException(404, "Repo not indexed yet. Call /repo/index first.")
    return {"result": llm.answer_repo_question(body.question, chunks),
            "sources": [f"{c['path']}:{c['start']}-{c['end']}" for c in chunks]}
