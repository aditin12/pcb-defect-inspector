"""
LLM client abstraction. Supports three backends behind one interface:

  - "ollama"    : local, free, no API key (default) -- requires Ollama
                  installed and running (https://ollama.com)
  - "openai"    : cloud API, requires OPENAI_API_KEY
  - "anthropic" : cloud API, requires ANTHROPIC_API_KEY
  - "template"  : no LLM at all -- deterministically formats the retrieved
                  chunks into readable prose. This is the automatic
                  fallback if the configured provider is unreachable, so
                  the app degrades gracefully instead of erroring out.

Switch providers with the LLM_PROVIDER env var; no code changes needed.
"""
import logging

import requests

from rag_config import (
    LLM_PROVIDER, OLLAMA_MODEL, OLLAMA_BASE_URL,
    OPENAI_API_KEY, OPENAI_MODEL, ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    LLM_TIMEOUT_SECONDS,
)

logger = logging.getLogger("rag.llm_client")


def _call_ollama(prompt: str) -> str:
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=LLM_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def _call_openai(prompt: str) -> str:
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={
            "model": OPENAI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.3,
        },
        timeout=LLM_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def _call_anthropic(prompt: str) -> str:
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": ANTHROPIC_MODEL,
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=LLM_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()["content"][0]["text"].strip()


def _template_fallback(prompt: str, retrieved_chunks: list) -> str:
    """No-LLM fallback: stitches the retrieved chunks into readable prose
    directly. Used automatically if the configured LLM backend errors, and
    can also be selected explicitly via LLM_PROVIDER=template."""
    if not retrieved_chunks:
        return "No reference information was found for this defect type."

    parts = []
    for chunk in retrieved_chunks:
        parts.append(f"**{chunk['section']}:** {chunk['text'].split(chr(10), 1)[-1]}")
    return "\n\n".join(parts)


def generate(prompt: str, retrieved_chunks: list = None) -> dict:
    """
    Returns {"text": str, "backend_used": str} -- backend_used lets the
    frontend/API response be transparent about whether a real LLM or the
    template fallback produced the explanation, rather than presenting a
    fallback as if it were a generated response.
    """
    provider = LLM_PROVIDER

    if provider == "template":
        return {"text": _template_fallback(prompt, retrieved_chunks or []), "backend_used": "template"}

    try:
        if provider == "ollama":
            return {"text": _call_ollama(prompt), "backend_used": "ollama"}
        elif provider == "openai":
            if not OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY not set")
            return {"text": _call_openai(prompt), "backend_used": "openai"}
        elif provider == "anthropic":
            if not ANTHROPIC_API_KEY:
                raise RuntimeError("ANTHROPIC_API_KEY not set")
            return {"text": _call_anthropic(prompt), "backend_used": "anthropic"}
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {provider}")
    except Exception as e:
        logger.warning(f"LLM backend '{provider}' unavailable ({e}); falling back to template.")
        return {"text": _template_fallback(prompt, retrieved_chunks or []), "backend_used": "template_fallback"}
