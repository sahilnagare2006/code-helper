"""Plain-Python tools. No AI involved."""
import ast
from .. import config as c


def _py_files():
    return sorted(
        p for p in c.CODE_PROJECT.rglob("*.py")
        if not any(part in c.SKIP_DIRS for part in p.parts)
    )


def _imports(path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    found = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            found.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module:
            found.add(n.module.split(".")[0])
        elif isinstance(n, ast.ImportFrom):  # "from . import x"
            found.update(a.name for a in n.names)
    return found


def list_files_and_functions() -> str:
    """List every Python file in the project with its functions and classes."""
    lines = []
    for p in _py_files():
        tree = ast.parse(p.read_text(encoding="utf-8", errors="ignore"))
        names = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
        lines.append(f"{p.relative_to(c.CODE_PROJECT)}: {', '.join(names) or '(no functions)'}")
    return "\n".join(lines) or "No Python files found."


def find_importers(module_name: str) -> str:
    """Say which files import a given module, e.g. 'config' (use without .py)."""
    module_name = module_name.replace(".py", "")
    hits = [str(p.relative_to(c.CODE_PROJECT)) for p in _py_files() if module_name in _imports(p)]
    return f"Files importing {module_name}: {', '.join(hits)}" if hits else f"No file imports {module_name}."


def build_architecture_diagram() -> str:
    """Return a Mermaid flowchart showing which project files import which."""
    files = {p.stem: p for p in _py_files()}
    edges = []
    for stem, p in files.items():
        for imp in _imports(p):
            if imp in files and imp != stem:
                edges.append(f"    {stem} --> {imp}")
    return "```mermaid\nflowchart TD\n" + "\n".join(sorted(set(edges))) + "\n```"


def get_project_overview() -> str:
    """Return the project README and the start of main.py, for onboarding questions."""
    parts = []
    for name in ("README.md", "readme.md"):
        f = c.CODE_PROJECT / name
        if f.exists():
            parts.append("README:\n" + f.read_text(encoding="utf-8", errors="ignore")[:3000])
            break
    main = c.CODE_PROJECT / "main.py"
    if main.exists():
        parts.append("main.py (start):\n" + main.read_text(encoding="utf-8", errors="ignore")[:1500])
    req = c.CODE_PROJECT / "requirements.txt"
    if req.exists():
        parts.append("requirements.txt:\n" + req.read_text(encoding="utf-8", errors="ignore"))
    return "\n\n".join(parts) or "No README or main.py found."
