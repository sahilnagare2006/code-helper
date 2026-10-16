"""RAG search tool (Step 5 of the RAG: embed the question, ask Pinecone)."""
import os
import time
from openai import OpenAI
from pinecone import Pinecone

from .common import HELPER_DIR  # noqa: F401  (also loads .env)

EMBED_MODEL = os.getenv("NVIDIA_EMBED_MODEL", "nvidia/nemotron-3-embed-1b")
_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("NVIDIA_API_KEY"),
                         base_url=os.getenv("NVIDIA_BASE_URL"))
    return _client


def embed(texts: list[str], kind: str = "passage") -> list[list[float]]:
    """Embed texts with the NVIDIA NIM embedding model.
    kind is 'passage' (for stored chunks) or 'query' (for questions)."""
    for attempt in range(4):
        try:
            resp = _get_client().embeddings.create(
                model=EMBED_MODEL,
                input=texts,
                extra_body={"input_type": kind, "truncate": "END"},
            )
            return [d.embedding for d in resp.data]
        except Exception as e:  # rate limit etc.
            if attempt == 3:
                raise
            print(f"Embedding retry {attempt + 1} after error: {e}")
            time.sleep(10 * (attempt + 1))


def get_index():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    return pc.Index(os.getenv("PINECONE_INDEX_NAME", "code-helper"))


def rag_search(question: str) -> str:
    """Search the code project for the chunks of code that best match the
    question. Use this to find WHERE something is done in the code, for
    example where search, embedding, chunking or configuration happens."""
    try:
        vec = embed([question], kind="query")[0]
        res = get_index().query(vector=vec, top_k=4, include_metadata=True)
    except Exception as e:
        return f"Search failed: {e}"
    if not res.matches:
        return "I could not find that."
    parts = []
    for m in res.matches:
        md = m.metadata
        parts.append(f"[{md['file']} | chunk {md['chunk_id']} | score {m.score:.2f}]\n{md['text']}")
    return "\n\n---\n\n".join(parts)
