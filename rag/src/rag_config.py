"""Config for the RAG layer."""
import os

RAG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../rag
PROJECT_ROOT = os.path.dirname(RAG_ROOT)

KNOWLEDGE_BASE_DIR = os.path.join(RAG_ROOT, "knowledge_base")
VECTOR_STORE_DIR = os.path.join(RAG_ROOT, "vector_store")
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# Local, free, no API key -- runs on CPU fine for a knowledge base this size.
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

CHROMA_COLLECTION_NAME = "pcb_defect_knowledge"

# Chunking: the knowledge base docs are already short and single-topic, so
# chunking by markdown section (## headers) rather than a fixed token
# window keeps each retrieved chunk semantically whole (e.g. "Risk if
# unaddressed" never gets split mid-thought from "General inspection response").
CHUNK_MIN_CHARS = 40   # drop near-empty fragments (e.g. a lone header with no body yet)

TOP_K_RETRIEVAL = 4

# --- LLM backend -------------------------------------------------------
# Priority: if LLM_PROVIDER=openai (or anthropic) and an API key is set,
# use that cloud API. Otherwise default to a local Ollama model. If neither
# is reachable, rag_pipeline falls back to a deterministic template built
# directly from the retrieved chunks, so the app still works with zero
# setup beyond what's in requirements.txt.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")   # "ollama" | "openai" | "anthropic" | "template"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

LLM_TIMEOUT_SECONDS = 20
