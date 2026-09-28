"""
RAG service singleton. Imports rag/src directly, same reasoning as
detection_service.py -- one definition of the retrieval+generation logic,
reused by the backend rather than duplicated.
"""
import os
import sys

_BACKEND_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(os.path.dirname(_BACKEND_APP_DIR))
_RAG_SRC = os.path.join(_REPO_ROOT, "rag", "src")
if _RAG_SRC not in sys.path:
    sys.path.insert(0, _RAG_SRC)

import chromadb  # noqa: E402
from rag_config import VECTOR_STORE_DIR, CHROMA_COLLECTION_NAME, LLM_PROVIDER  # noqa: E402  (rag/src/config.py)
from rag_pipeline import explain_detection, answer_board_question  # noqa: E402


class RAGService:
    def __init__(self):
        self.index_loaded = False
        self.llm_provider = LLM_PROVIDER

    def check_index(self) -> bool:
        """Confirms the Chroma index exists and is non-empty (build_index.py has been run)."""
        try:
            client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
            collection = client.get_collection(CHROMA_COLLECTION_NAME)
            self.index_loaded = collection.count() > 0
        except Exception:
            self.index_loaded = False
        return self.index_loaded

    def explain(self, defect_type: str, confidence: float, severity_level: str, severity_score: float) -> dict:
        if not self.index_loaded:
            raise RuntimeError(
                "RAG index not built. Run: cd rag/src && python build_index.py"
            )
        return explain_detection(defect_type, confidence, severity_level, severity_score)

    def answer(self, question: str, defect_types: list) -> dict:
        if not self.index_loaded:
            raise RuntimeError("RAG index not built. Run: cd rag/src && python build_index.py")
        return answer_board_question(question, defect_types)


rag_service = RAGService()
