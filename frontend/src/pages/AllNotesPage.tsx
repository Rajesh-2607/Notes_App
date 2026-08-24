import { NotebookPen } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useNotesQuery } from '../hooks/useNotes'

export default function AllNotesPage() {
  const navigate = useNavigate()
  const { data: notes = [], isLoading } = useNotesQuery()

  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 px-8 text-center">
      <div className="rounded-full bg-indigo-50 p-4">
        <NotebookPen className="h-7 w-7 text-indigo-600" />
      </div>
      {isLoading ? (
        <p className="text-sm text-slate-400">Loading your notes…</p>
      ) : notes.length === 0 ? (
        <>
          <h2 className="text-lg font-semibold text-slate-900">No notes yet</h2>
          <p className="max-w-sm text-sm text-slate-500">
            Create your first note, then ask the chat bot questions about it once it's saved.
          </p>
        </>
      ) : (
        <>
          <h2 className="text-lg font-semibold text-slate-900">Select a note</h2>
          <p className="max-w-sm text-sm text-slate-500">
            Choose a note from the sidebar, or create a new one to get started.
          </p>
        </>
      )}
      <button
        type="button"
        onClick={() => navigate('/notes/new')}
        className="mt-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
      >
        + New note
      </button>
    </div>
  )
}
