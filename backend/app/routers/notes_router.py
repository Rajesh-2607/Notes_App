from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.dependencies import SupabaseUser, get_current_user
from app.schemas.note_schema import NoteCreate, NoteRead, NoteUpdate
from app.services.notes_service import create_note, delete_note, get_note_for_user, list_user_notes, update_note
from app.supabase_client import get_supabase

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteRead])
def list_notes(
    supabase: Client = Depends(get_supabase),
    current_user: SupabaseUser = Depends(get_current_user),
):
    return list_user_notes(supabase, current_user.id)


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note_route(
    payload: NoteCreate,
    supabase: Client = Depends(get_supabase),
    current_user: SupabaseUser = Depends(get_current_user),
):
    return create_note(supabase, current_user.id, payload.title, payload.content)


@router.get("/{note_id}", response_model=NoteRead)
def read_note(
    note_id: str,
    supabase: Client = Depends(get_supabase),
    current_user: SupabaseUser = Depends(get_current_user),
):
    return get_note_for_user(supabase, note_id, current_user.id)


@router.put("/{note_id}", response_model=NoteRead)
def update_note_route(
    note_id: str,
    payload: NoteUpdate,
    supabase: Client = Depends(get_supabase),
    current_user: SupabaseUser = Depends(get_current_user),
):
    return update_note(supabase, note_id, current_user.id, payload.title, payload.content)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note_route(
    note_id: str,
    supabase: Client = Depends(get_supabase),
    current_user: SupabaseUser = Depends(get_current_user),
):
    delete_note(supabase, note_id, current_user.id)
    return None
