from __future__ import annotations

from typing import Any

from google import genai
from google.genai import types

from app.config import settings

SYSTEM_INSTRUCTION = (
    "You are a note-taking assistant. Answer the user's question using ONLY the "
    "provided note excerpts as context. If the excerpts don't contain the answer, "
    "say plainly that the notes don't cover it instead of guessing or using "
    "outside knowledge. Be concise."
)


def _get_chat_client() -> genai.Client | None:
    if not settings.GEMINI_API_KEY:
        return None
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _build_prompt(question: str, context_chunks: list[dict[str, Any]]) -> str:
    excerpts = "\n\n".join(
        f"[Note: {chunk.get('note_title', 'Untitled')}]\n{chunk.get('chunk_text', '')}"
        for chunk in context_chunks
        if chunk.get("chunk_text")
    )
    return f"Note excerpts:\n{excerpts}\n\nQuestion: {question}"


def _sources(context_chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "note_id": chunk.get("note_id", "unknown"),
            "title": chunk.get("note_title", "Unknown note"),
            "chunk_text": chunk.get("chunk_text", ""),
        }
        for chunk in context_chunks
    ]


def answer_question(
    *,
    question: str,
    context_chunks: list[dict[str, Any]],
    api_key_missing: bool = False,
) -> dict[str, Any]:
    if api_key_missing:
        return {
            "answer": "Gemini is not configured yet. Add your API key to backend/.env to enable note-based answers.",
            "sources": _sources(context_chunks),
        }

    if not context_chunks:
        return {
            "answer": "I could not find any relevant note context for that question.",
            "sources": [],
        }

    client = _get_chat_client()
    if client is None:
        return {
            "answer": "Gemini is not configured yet. Add your API key to backend/.env to enable note-based answers.",
            "sources": _sources(context_chunks),
        }

    response = client.models.generate_content(
        model=settings.GEMINI_CHAT_MODEL,
        contents=_build_prompt(question, context_chunks),
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
    )

    answer = (response.text or "").strip() or "I could not generate an answer from your notes."

    return {"answer": answer, "sources": _sources(context_chunks)}
