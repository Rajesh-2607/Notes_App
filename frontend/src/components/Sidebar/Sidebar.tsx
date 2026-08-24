import { Plus, LogOut, NotebookText } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useNotesQuery } from '../../hooks/useNotes'
import { useAuthStore } from '../../store/authStore'
import NoteList from '../NoteList/NoteList'

export default function Sidebar() {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)
  const email = useAuthStore((state) => state.email)
  const { data: notes = [], isLoading, isError } = useNotesQuery()

  return (
    <aside className="flex h-full w-80 shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="flex items-center gap-2 border-b border-slate-200 px-5 py-4">
        <NotebookText className="h-5 w-5 text-indigo-600" />
        <span className="text-sm font-semibold text-slate-900">Notes + RAG Bot</span>
      </div>

      <div className="px-4 pt-4">
        <button
          type="button"
          onClick={() => navigate('/notes/new')}
          className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
        >
          <Plus className="h-4 w-4" />
          New note
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4">
        <p className="mb-2 px-1 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Your notes {notes.length > 0 && `(${notes.length})`}
        </p>
        <NoteList notes={notes} isLoading={isLoading} isError={isError} />
      </div>

      <div className="flex items-center justify-between gap-2 border-t border-slate-200 px-4 py-3">
        <span className="truncate text-xs text-slate-500">{email ?? 'Signed in'}</span>
        <button
          type="button"
          onClick={logout}
          className="flex items-center gap-1 rounded-lg px-2 py-1.5 text-xs font-medium text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
        >
          <LogOut className="h-3.5 w-3.5" />
          Log out
        </button>
      </div>
    </aside>
  )
}
