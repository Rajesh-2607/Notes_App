from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.dependencies import SupabaseUser, get_current_user
from app.schemas.chat_schema import ChatQuery, ChatResponse
from app.services.embedding_service import embed_texts, get_embedding_client
from app.services.rag_service import answer_question
from app.services.retrieval_service import retrieve_relevant_chunks
from app.supabase_client import get_supabase

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat_with_notes(
    payload: ChatQuery,
    supabase: Client = Depends(get_supabase),
    current_user: SupabaseUser = Depends(get_current_user),
):
    if not payload.question.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty")

    if get_embedding_client() is None:
        return answer_question(question=payload.question, context_chunks=[], api_key_missing=True)

    question_vector = embed_texts([payload.question])[0]
    if not question_vector:
        return answer_question(question=payload.question, context_chunks=[], api_key_missing=True)

    relevant = retrieve_relevant_chunks(supabase, current_user.id, question_vector, limit=3)
    return answer_question(question=payload.question, context_chunks=relevant, api_key_missing=False)
