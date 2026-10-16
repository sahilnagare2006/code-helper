"""RAG steps 3-5: embed, store, search. Tool #1 = rag_search."""
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from .. import config as c

_client = OpenAI(api_key=c.NVIDIA_API_KEY, base_url=c.NVIDIA_BASE_URL)


def embed(texts: list[str], kind: str = "passage") -> list[list[float]]:
    """Turn texts into vectors. kind = 'passage' for chunks, 'query' for questions."""
    resp = _client.embeddings.create(
        model=c.EMBED_MODEL,
        input=texts,
        encoding_format="float",
        extra_body={"input_type": kind, "truncate": "END"},
    )
    return [d.embedding for d in resp.data]


def get_index(create: bool = False):
    pc = Pinecone(api_key=c.PINECONE_API_KEY)
    if create and c.INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=c.INDEX_NAME,
            dimension=c.EMBED_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud=c.PINECONE_CLOUD, region=c.PINECONE_REGION),
        )
    return pc.Index(c.INDEX_NAME)


def rag_search(question: str) -> str:
    """Search the code project for chunks that match the question.
    Use this to find WHERE something is (which file, which lines)."""
    vec = embed([question], kind="query")[0]
    res = get_index().query(vector=vec, top_k=4, include_metadata=True)
    matches = [m for m in res.matches if m.score >= 0.05]
    if not matches:
        return "I could not find that."
    out = []
    for m in matches:
        md = m.metadata
        out.append(f"[{md['file']} lines {md['start_line']}-{md['end_line']}] (score {m.score:.2f})\n{md['text']}")
    return "\n\n---\n\n".join(out)
