"""
RAG orchestration: given one CV+ML detection (defect type, confidence,
severity), retrieves the relevant knowledge base chunks and asks the LLM
to turn them into a short, grounded explanation for that specific finding.

This is the third link in the CV -> ML -> RAG chain: CV/ML have already
answered "what defect, how confident, how severe" -- this module answers
"what does that mean and what should be done about it," grounded in the
retrieved reference text rather than the LLM's own unconstrained knowledge.
"""
from retriever import retrieve
from llm_client import generate


PROMPT_TEMPLATE = """You are assisting a PCB quality control inspector. \
Using ONLY the reference information below, write a brief, plain-language \
explanation (3-5 sentences) for this specific inspection finding. Cover: \
what the defect is, why it matters at this severity level, and one \
concrete next step. Do not invent information beyond what's given below.

DETECTED DEFECT: {defect_type}
DETECTOR CONFIDENCE: {confidence:.0%}
ASSESSED SEVERITY: {severity_level} (score {severity_score})

REFERENCE INFORMATION:
{context}

Explanation:"""


def explain_detection(defect_type: str, confidence: float, severity_level: str, severity_score: float) -> dict:
    """
    Returns:
        {
          "explanation": str,
          "sources": [{"section":..., "source_doc":...}, ...],
          "backend_used": str,
        }
    """
    query = (
        f"What is a {defect_type} defect, why does severity level "
        f"{severity_level} matter, and what is the recommended inspection response?"
    )
    chunks = retrieve(query, defect_type=defect_type, top_k=4)

    context = "\n\n".join(f"[{c['section']}] {c['text']}" for c in chunks) if chunks else "No reference found."

    prompt = PROMPT_TEMPLATE.format(
        defect_type=defect_type.replace("_", " "),
        confidence=confidence,
        severity_level=severity_level,
        severity_score=severity_score,
        context=context,
    )

    result = generate(prompt, retrieved_chunks=chunks)

    return {
        "explanation": result["text"],
        "sources": [{"section": c["section"], "source_doc": c["source_doc"]} for c in chunks],
        "backend_used": result["backend_used"],
    }


def answer_board_question(question: str, board_defect_types: list) -> dict:
    """
    Free-text Q&A over the board's findings, e.g. "is this board safe to
    assemble?" -- retrieves across all defect types present on the board
    (not filtered to one), so the answer can reason across multiple findings.
    """
    all_chunks = []
    seen_texts = set()
    for defect_type in set(board_defect_types):
        for chunk in retrieve(question, defect_type=defect_type, top_k=2):
            if chunk["text"] not in seen_texts:
                all_chunks.append(chunk)
                seen_texts.add(chunk["text"])

    context = "\n\n".join(f"[{c['source_doc']} - {c['section']}] {c['text']}" for c in all_chunks)

    prompt = (
        "You are assisting a PCB quality control inspector. Using ONLY the "
        "reference information below, answer the question in 3-5 sentences. "
        "Do not invent information beyond what's given.\n\n"
        f"QUESTION: {question}\n\nREFERENCE INFORMATION:\n{context}\n\nAnswer:"
    )

    result = generate(prompt, retrieved_chunks=all_chunks)
    return {
        "answer": result["text"],
        "sources": [{"section": c["section"], "source_doc": c["source_doc"]} for c in all_chunks],
        "backend_used": result["backend_used"],
    }
