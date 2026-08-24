import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createNote, deleteNote, fetchNote, fetchNotes, updateNote } from '../api/notes.api'
import type { NoteInput } from '../types/note.types'

const notesKey = ['notes'] as const
const noteKey = (id: string) => ['notes', id] as const

export function useNotesQuery() {
  return useQuery({ queryKey: notesKey, queryFn: fetchNotes })
}

export function useNoteQuery(noteId: string | undefined) {
  return useQuery({
    queryKey: noteKey(noteId ?? ''),
    queryFn: () => fetchNote(noteId as string),
    enabled: Boolean(noteId),
  })
}

export function useCreateNote() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: NoteInput) => createNote(input),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: notesKey })
    },
  })
}

export function useUpdateNote(noteId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: Partial<NoteInput>) => updateNote(noteId, input),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: notesKey })
      void queryClient.invalidateQueries({ queryKey: noteKey(noteId) })
    },
  })
}

export function useDeleteNote() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (noteId: string) => deleteNote(noteId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: notesKey })
    },
  })
}
