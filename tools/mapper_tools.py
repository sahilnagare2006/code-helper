"""Plain-Python tools (NO AI): they read the code with the `ast` module."""
import ast
from .common import project_root, py_files


def _parse(path):
    return ast.parse(path.read_text(encoding="utf-8", errors="ignore"))


def _imports(path) -> set[str]:
    try:
        tree = _parse(path)
    except SyntaxError:
        return set()
    found = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            found.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module:
            found.add(n.module.split(".")[0])
    return found


def list_functions(file_name: str) -> str:
    """List the functions and classes defined in one Python file of the
    project, for example 'vector_store.py'. Uses plain Python, no AI."""
    p = project_root() / file_name
    if not p.exists():
        return f"I could not find {file_name}."
    try:
        tree = _parse(p)
    except SyntaxError as e:
        return f"Could not parse {file_name}: {e}"
    items = [f"{type(n).__name__}: {n.name} (line {n.lineno})"
             for n in ast.walk(tree)
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    return "\n".join(items) or "No functions or classes found."


def find_importers(module_name: str) -> str:
    """Find which project files import a given module. Example: 'config.py'
    returns every file that imports config. Uses plain Python, no AI."""
    module = module_name.replace(".py", "").strip()
    hits = [f.name for f in py_files() if module in _imports(f)]
    return ", ".join(hits) if hits else f"No file imports {module}."


def project_graph() -> str:
    """Return a Mermaid flowchart showing which project files import which
    other project files. Use this when asked for an architecture diagram."""
    files = {f.stem: f for f in py_files()}
    lines = ["flowchart LR"]
    for stem, f in files.items():
        for dep in sorted(_imports(f)):
            if dep in files and dep != stem:
                lines.append(f"    {stem} --> {dep}")
    if len(lines) == 1:
        return "No imports between project files were found."
    return "\n".join(lines)


def get_project_summary() -> str:
    """Return the list of project files, each file's first docstring line,
    and the project's reference notes. Use this to explain what the project
    does, how to run it and where a new person should start reading."""
    root = project_root()
    out = []
    for f in py_files():
        try:
            doc = ast.get_docstring(_parse(f))
        except SyntaxError:
            doc = None
        first = doc.splitlines()[0] if doc else "no docstring"
        out.append(f"{f.relative_to(root)}: {first}")
    for name in ("STUDENT_CODE_REFERENCE.md", "README.md"):
        p = root / name
        if p.exists():
            out.append(f"\n--- {name} ---\n" + p.read_text(encoding="utf-8", errors="ignore")[:3000])
    return "\n".join(out)
