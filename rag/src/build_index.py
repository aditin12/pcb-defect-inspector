"""
Builds the Chroma vector index from the markdown knowledge base.

Chunking strategy: splits each markdown file on its '## ' section headers,
so every chunk is one complete, self-contained topic ("Risk if
unaddressed", "General inspection response", etc.) rather than an
arbitrary fixed-length token window that could cut a thought in half.
Each chunk is tagged with metadata (source file / defect type, section
title) so the retriever can filter by defect type before falling back to
pure semantic search.

Run:
    cd rag/src
    python build_index.py
"""
import os
import re

import chromadb
from sentence_transformers import SentenceTransformer

from rag_config import (
    KNOWLEDGE_BASE_DIR, VECTOR_STORE_DIR, EMBEDDING_MODEL_NAME,
    CHROMA_COLLECTION_NAME, CHUNK_MIN_CHARS,
)


def chunk_markdown_file(filepath: str) -> list:
    """Returns a list of {"text":..., "section":..., "source_doc":...} dicts,
    one per '## ' section in the file (the '# Title' line is prepended to
    every chunk's text so the defect name is always present for embedding)."""
    with open(filepath, "r") as f:
        content = f.read()

    doc_name = os.path.splitext(os.path.basename(filepath))[0]

    title_match = re.match(r"# (.+)\n", content)
    title = title_match.group(1).strip() if title_match else doc_name

    # Split on '## ' section headers, keeping the header text.
    sections = re.split(r"\n## ", content)
    chunks = []
    for i, section in enumerate(sections):
        if i == 0:
            continue  # this is the '# Title' preamble before the first '##', skip as its own chunk
        lines = section.strip().split("\n", 1)
        section_title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        if len(body) < CHUNK_MIN_CHARS:
            continue
        chunk_text = f"{title} — {section_title}\n{body}"
        chunks.append({"text": chunk_text, "section": section_title, "source_doc": doc_name})

    return chunks


def main():
    print(f"Loading embedding model '{EMBEDDING_MODEL_NAME}' (first run downloads it, ~80MB)...")
    embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

    client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
    # Fresh build every run -- simplest correct behavior for a knowledge
    # base this small; avoids stale/duplicate chunks from previous builds.
    try:
        client.delete_collection(CHROMA_COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(CHROMA_COLLECTION_NAME)

    all_chunks = []
    for fname in sorted(os.listdir(KNOWLEDGE_BASE_DIR)):
        if not fname.endswith(".md"):
            continue
        filepath = os.path.join(KNOWLEDGE_BASE_DIR, fname)
        chunks = chunk_markdown_file(filepath)
        all_chunks.extend(chunks)
        print(f"  {fname}: {len(chunks)} chunks")

    if not all_chunks:
        raise RuntimeError(f"No chunks produced from {KNOWLEDGE_BASE_DIR}. Check the markdown files exist.")

    texts = [c["text"] for c in all_chunks]
    embeddings = embedder.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        ids=[f"chunk_{i}" for i in range(len(all_chunks))],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"section": c["section"], "source_doc": c["source_doc"]} for c in all_chunks],
    )

    print(f"\nIndexed {len(all_chunks)} chunks into Chroma collection "
          f"'{CHROMA_COLLECTION_NAME}' at {VECTOR_STORE_DIR}")


if __name__ == "__main__":
    main()
