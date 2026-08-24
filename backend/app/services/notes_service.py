from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from supabase import Client

from app.services.chunking_service import split_note_into_chunks
from app.services.embedding_service import embed_texts


def list_user_notes(supabase: Client, user_id: str) -> list[dict[str, Any]]:
    response = supabase.table("note").select("*").eq("user_id", user_id).execute()
    return response.data or []


def create_note(supabase: Client, user_id: str, title: str, content: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    note_row = {
        "user_id": user_id,
        "title": title,
        "content": content,
        "created_at": now,
        "updated_at": now,
    }
    response = supabase.table("note").insert(note_row).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create note")

    note = response.data[0]
    note_id = note["id"]

    # Chunk and embed the content
    chunks = split_note_into_chunks(content)
    if chunks:
        vectors = embed_texts(chunks)
        chunk_rows = [
            {
                "note_id": note_id,
                "chunk_index": index,
                "chunk_text": chunk_text,
                "embedding": vectors[index] if index < len(vectors) else None,
            }
            for index, chunk_text in enumerate(chunks)
        ]
        supabase.table("note_chunk").insert(chunk_rows).execute()

    return note


def get_note_for_user(supabase: Client, note_id: str, user_id: str) -> dict[str, Any]:
    response = supabase.table("note").select("*").eq("id", note_id).eq("user_id", user_id).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return response.data[0]


def update_note(
    supabase: Client, note_id: str, user_id: str, title: str | None, content: str | None
) -> dict[str, Any]:
    # Verify ownership first
    get_note_for_user(supabase, note_id, user_id)

    updates: dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if title is not None:
        updates["title"] = title
    if content is not None:
        updates["content"] = content

    response = supabase.table("note").update(updates).eq("id", note_id).eq("user_id", user_id).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update note")

    if content is not None:
        # Re-chunk and re-embed
        supabase.table("note_chunk").delete().eq("note_id", note_id).execute()
        chunks = split_note_into_chunks(content)
        if chunks:
            vectors = embed_texts(chunks)
            chunk_rows = [
                {
                    "note_id": note_id,
                    "chunk_index": index,
                    "chunk_text": chunk_text,
                    "embedding": vectors[index] if index < len(vectors) else None,
                }
                for index, chunk_text in enumerate(chunks)
            ]
            supabase.table("note_chunk").insert(chunk_rows).execute()

    return response.data[0]


def delete_note(supabase: Client, note_id: str, user_id: str) -> None:
    get_note_for_user(supabase, note_id, user_id)
    supabase.table("note").delete().eq("id", note_id).eq("user_id", user_id).execute()
