"""
Retrieval layer: given a defect type (and optionally a free-text question),
returns the most relevant knowledge base chunks.

Retrieval strategy is two-tiered:
1. Metadata filter first -- restrict the search to chunks whose source_doc
   matches the detected defect type (e.g. "short.md"), since we already
   know exactly which document is authoritative for a given CV detection.
   This avoids a purely semantic search occasionally pulling in a
   similarly-worded chunk from the wrong defect's document.
2. Semantic similarity search within that filtered set to rank chunks by
   relevance to the specific question being asked (e.g. "why is this
   severe" vs. "how do I fix this" pull different sections of the same doc).

Falls back to unfiltered semantic search if no defect-specific chunks
exist (e.g. a general question not tied to one defect type), so the
retriever degrades gracefully rather than returning nothing.
"""
import chromadb
from sentence_transformers import SentenceTransformer

from rag_config import VECTOR_STORE_DIR, EMBEDDING_MODEL_NAME, CHROMA_COLLECTION_NAME, TOP_K_RETRIEVAL

_embedder = None
_collection = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedder


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
        _collection = client.get_collection(CHROMA_COLLECTION_NAME)
    return _collection


def retrieve(query: str, defect_type: str = None, top_k: int = TOP_K_RETRIEVAL) -> list:
    """
    query: free-text question, e.g. "why is this defect risky and how is it fixed?"
    defect_type: one of ml/src/config.py's CLASS_NAMES, or None for unfiltered search
    Returns: list of {"text":..., "section":..., "source_doc":..., "distance":...}
    """
    embedder = _get_embedder()
    collection = _get_collection()
    query_embedding = embedder.encode([query]).tolist()

    where_filter = {"source_doc": defect_type} if defect_type else None

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where=where_filter,
    )

    # Fallback: if a defect-specific filter returned nothing (e.g. defect_type
    # doesn't match any indexed doc name), retry unfiltered rather than
    # surfacing an empty explanation.
    if where_filter and not results["documents"][0]:
        results = collection.query(query_embeddings=query_embedding, n_results=top_k)

    chunks = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        chunks.append({
            "text": doc,
            "section": meta.get("section"),
            "source_doc": meta.get("source_doc"),
            "distance": dist,
        })
    return chunks
