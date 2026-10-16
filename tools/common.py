"""Shared helpers: load .env, find the code project, list its .py files."""
import os
from pathlib import Path
from dotenv import load_dotenv

HELPER_DIR = Path(__file__).resolve().parents[1]
load_dotenv(HELPER_DIR / ".env")

SKIP = {"venv", ".venv", "__pycache__", ".git", "node_modules", "site-packages"}


def project_root() -> Path:
    """The code project the helper studies (the cloned Naive_RAG folder)."""
    p = os.getenv("PROJECT_PATH")
    root = Path(p).expanduser() if p else HELPER_DIR.parent / "Naive_RAG"
    return root.resolve()


def py_files(root: Path | None = None) -> list[Path]:
    """Every .py file in the project, skipping venv/cache folders."""
    root = root or project_root()
    return [f for f in sorted(root.rglob("*.py"))
            if not SKIP & set(f.relative_to(root).parts)]
