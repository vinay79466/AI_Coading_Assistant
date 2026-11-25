"""Thin wrapper around the Claude API plus one function per feature."""
import os

from anthropic import Anthropic
from dotenv import load_dotenv

import prompts

load_dotenv()
_client = None
MODEL = os.getenv("MODEL", "claude-sonnet-5-5")


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()  # reads ANTHROPIC_API_KEY
    return _client


def ask(prompt: str, max_tokens: int = 2048) -> str:
    resp = _get_client().messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=prompts.SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def generate_code(request: str, language: str = "Python") -> str:
    return ask(prompts.GENERATE.format(request=request, language=language))


def explain_code(code: str, language: str = "Python") -> str:
    return ask(prompts.EXPLAIN.format(code=code, language=language))


def find_bugs(code: str, language: str = "Python") -> str:
    return ask(prompts.DEBUG.format(code=code, language=language))


def improve_code(code: str, language: str = "Python") -> str:
    return ask(prompts.IMPROVE.format(code=code, language=language))


def generate_tests(code: str, language: str = "Python", framework: str = "pytest") -> str:
    return ask(prompts.TESTS.format(code=code, language=language, framework=framework))


def answer_repo_question(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"### {c['path']} (lines {c['start']}-{c['end']})\n```\n{c['text']}\n```"
        for c in chunks
    )
    return ask(prompts.REPO_QA.format(context=context, question=question), 3000)
