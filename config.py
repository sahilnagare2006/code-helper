"""Shared settings. Keys come from .env, never from code."""
import os
from pathlib import Path
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

# The code project the helper studies (the cloned Naive_RAG folder, next to code_helper/)
CODE_PROJECT = Path(os.getenv("CODE_PROJECT_PATH", HERE.parent / "Naive_RAG")).resolve()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
EMBED_MODEL = os.getenv("NVIDIA_EMBED_MODEL", "nvidia/nemotron-3-embed-1b")
CHAT_MODEL = os.getenv("NVIDIA_CHAT_MODEL", "meta/llama-3.2-11b-vision-instruct")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "code-helper")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

EMBED_DIM = 2048          # must match nemotron-3-embed-1b
CHUNK_LINES = 30          # chunk size (lines)
CHUNK_OVERLAP = 5         # overlap (lines)

SKIP_DIRS = {".git", "venv", ".venv", "__pycache__", "node_modules", "code_helper"}
