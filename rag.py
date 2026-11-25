"""RAG over a GitHub repo: clone -> split -> embed -> store -> retrieve.

Uses ChromaDB's built-in local embedding model, so no extra API key is needed.
"""
import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

import chromadb

CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".c", ".cpp", ".h",
             ".go", ".rs", ".rb", ".php", ".cs", ".kt", ".swift", ".md",
             ".html", ".css", ".sql", ".yml", ".yaml", ".json", ".toml"}
SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist",
             "build", ".next", "target"}
CHUNK_LINES, OVERLAP = 60, 10
MAX_FILE_BYTES = 200_000

_db = chromadb.PersistentClient(path="chroma_db")


def _collection_name(repo_url: str) -> str:
    return "repo_" + hashlib.md5(repo_url.encode()).hexdigest()[:16]


def clone_repo(repo_url: str) -> Path:
    dest = Path(tempfile.mkdtemp(prefix="repo_"))
    subprocess.run(["git", "clone", "--depth", "1", repo_url, str(dest)],
                   check=True, capture_output=True, timeout=120)
    return dest


def split_file(path: Path, root: Path) -> list[dict]:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []
    rel = str(path.relative_to(root))
    chunks, step = [], CHUNK_LINES - OVERLAP
    for start in range(0, max(len(lines), 1), step):
        piece = lines[start:start + CHUNK_LINES]
        if not "".join(piece).strip():
            continue
        chunks.append({"path": rel, "start": start + 1,
                       "end": start + len(piece), "text": "\n".join(piece)})
    return chunks


def index_repo(repo_url: str) -> int:
    """Clone and index a repo. Returns number of chunks stored."""
    root = clone_repo(repo_url)
    try:
        chunks = []
        for p in root.rglob("*"):
            if (p.is_file() and p.suffix in CODE_EXTS
                    and not (set(p.relative_to(root).parts) & SKIP_DIRS)
                    and p.stat().st_size < MAX_FILE_BYTES):
                chunks.extend(split_file(p, root))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    name = _collection_name(repo_url)
    try:
        _db.delete_collection(name)
    except Exception:
        pass
    col = _db.create_collection(name)
    for i in range(0, len(chunks), 200):
        batch = chunks[i:i + 200]
        col.add(
            ids=[f"{i + j}" for j in range(len(batch))],
            documents=[c["text"] for c in batch],
            metadatas=[{"path": c["path"], "start": c["start"], "end": c["end"]}
                       for c in batch],
        )
    return len(chunks)


def retrieve(repo_url: str, question: str, k: int = 6) -> list[dict]:
    col = _db.get_collection(_collection_name(repo_url))
    res = col.query(query_texts=[question], n_results=k)
    return [{"text": d, **m} for d, m in zip(res["documents"][0], res["metadatas"][0])]
