from typing import Any

from supabase import Client


def retrieve_relevant_chunks(
    supabase: Client,
    user_id: str,
    question_vector: list[float],
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Call the match_notes Supabase RPC for pgvector cosine similarity search."""
    response = supabase.rpc(
        "match_notes",
        {
            "query_embedding": question_vector,
            "match_user_id": user_id,
            "match_count": limit,
        },
    ).execute()

    return [
        {
            "id": row["id"],
            "note_id": row["note_id"],
            "note_title": row["note_title"],
            "chunk_text": row["chunk_text"],
        }
        for row in (response.data or [])
    ]
