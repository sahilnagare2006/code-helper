"""Run once: python code_helper/index_codebase.py
RAG steps 1-4: read -> split -> embed -> store in Pinecone."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from code_helper import config as c
from code_helper.tools.rag import embed, get_index


def chunk_file(text: str):
    lines = text.splitlines()
    step = c.CHUNK_LINES - c.CHUNK_OVERLAP
    for start in range(0, max(len(lines), 1), step):
        piece = lines[start:start + c.CHUNK_LINES]
        if piece:
            yield start + 1, start + len(piece), "\n".join(piece)
        if start + c.CHUNK_LINES >= len(lines):
            break


def main():
    files = [p for p in c.CODE_PROJECT.rglob("*.py")
             if not any(part in c.SKIP_DIRS for part in p.parts)]
    print(f"Found {len(files)} files in {c.CODE_PROJECT}")
    records = []
    for p in files:
        rel = str(p.relative_to(c.CODE_PROJECT))
        for s, e, text in chunk_file(p.read_text(encoding="utf-8", errors="ignore")):
            records.append((f"{rel}:{s}", rel, s, e, text))
    print(f"{len(records)} chunks")

    index = get_index(create=True)
    for i in range(0, len(records), 16):
        batch = records[i:i + 16]
        vecs = embed([r[4] for r in batch], kind="passage")
        index.upsert(vectors=[
            {"id": r[0], "values": v,
             "metadata": {"file": r[1], "start_line": r[2], "end_line": r[3], "text": r[4]}}
            for r, v in zip(batch, vecs)
        ])
        print(f"  stored {i + len(batch)}/{len(records)}")
    print("Done.")


if __name__ == "__main__":
    main()
