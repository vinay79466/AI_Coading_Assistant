"""Prompt templates for each assistant feature."""

SYSTEM = (
    "You are an expert software engineer acting as a coding assistant. "
    "Be accurate and concise. Always put code in fenced blocks with the "
    "language tag. Never invent APIs; say so when unsure."
)

GENERATE = """Write {language} code for the following request.
Include brief comments and a short usage example.

Request: {request}"""

EXPLAIN = """Explain this {language} code line by line.
Start with a 2-sentence overview, then go through it in order,
then list any edge cases or gotchas.

```{language}
{code}
```"""

DEBUG = """Find bugs in this {language} code.
For each bug give: (1) location, (2) why it is wrong, (3) the fix.
Finish with the full corrected code.

```{language}
{code}
```"""

IMPROVE = """Review this {language} code for inefficiency, poor style and
readability problems. Show an improved version, then list what changed
and why (performance, readability, safety).

```{language}
{code}
```"""

TESTS = """Write thorough unit tests for this {language} code using
{framework}. Cover normal cases, edge cases and error cases.

```{language}
{code}
```"""

REPO_QA = """Answer the question using ONLY the repository excerpts below.
Cite file paths and line ranges. If the excerpts don't contain the answer,
say so instead of guessing.

{context}

Question: {question}"""
