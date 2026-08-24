import type { Note } from '../../types/note.types'
import NoteCard from '../NoteCard/NoteCard'

interface NoteListProps {
  notes: Note[]
  isLoading: boolean
  isError?: boolean
}

export default function NoteList({ notes, isLoading, isError }: NoteListProps) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {[0, 1, 2].map((key) => (
          <div key={key} className="h-16 animate-pulse rounded-xl bg-slate-100" />
        ))}
      </div>
    )
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-4 text-center text-sm text-red-600">
        Couldn't load your notes. Check that the backend is running and try refreshing.
      </div>
    )
  }

  if (notes.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 px-3 py-6 text-center text-sm text-slate-400">
        No notes yet — create your first one.
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {notes.map((note) => (
        <NoteCard key={note.id} note={note} />
      ))}
    </div>
  )
}
