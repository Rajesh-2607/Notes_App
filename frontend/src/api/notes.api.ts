import { apiClient } from './client'
import type { Note, NoteInput } from '../types/note.types'

export async function fetchNotes(): Promise<Note[]> {
  const { data } = await apiClient.get<Note[]>('/notes')
  return data
}

export async function fetchNote(noteId: string): Promise<Note> {
  const { data } = await apiClient.get<Note>(`/notes/${noteId}`)
  return data
}

export async function createNote(input: NoteInput): Promise<Note> {
  const { data } = await apiClient.post<Note>('/notes', input)
  return data
}

export async function updateNote(noteId: string, input: Partial<NoteInput>): Promise<Note> {
  const { data } = await apiClient.put<Note>(`/notes/${noteId}`, input)
  return data
}

export async function deleteNote(noteId: string): Promise<void> {
  await apiClient.delete(`/notes/${noteId}`)
}
