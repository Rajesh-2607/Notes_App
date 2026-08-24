import { NavLink } from 'react-router-dom'
import { formatDate } from '../../utils/formatDate'
import type { Note } from '../../types/note.types'

interface NoteCardProps {
  note: Note
}

export default function NoteCard({ note }: NoteCardProps) {
  return (
    <NavLink
      to={`/notes/${note.id}`}
      className={({ isActive }) =>
        `block rounded-xl border px-3 py-2.5 transition ${
          isActive
            ? 'border-indigo-300 bg-indigo-50'
            : 'border-transparent bg-slate-50 hover:border-slate-200 hover:bg-white'
        }`
      }
    >
      <p className="truncate text-sm font-semibold text-slate-900">
        {note.title || 'Untitled note'}
      </p>
      <p className="mt-0.5 truncate text-xs text-slate-500">
        {note.content ? note.content.slice(0, 80) : 'No content yet'}
      </p>
      <p className="mt-1.5 text-[11px] font-medium text-slate-400">{formatDate(note.updated_at)}</p>
    </NavLink>
  )
}
