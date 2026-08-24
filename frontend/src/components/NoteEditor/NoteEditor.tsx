import { useEffect, useState } from 'react'
import { Trash2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useCreateNote, useDeleteNote, useNoteQuery, useUpdateNote } from '../../hooks/useNotes'
import { formatDate } from '../../utils/formatDate'

interface NoteEditorProps {
  noteId: string
}

export default function NoteEditor({ noteId }: NoteEditorProps) {
  const isNew = noteId === 'new'
  const navigate = useNavigate()

  const { data: note, isLoading } = useNoteQuery(isNew ? undefined : noteId)
  const createNote = useCreateNote()
  const updateNote = useUpdateNote(noteId)
  const deleteNote = useDeleteNote()

  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [dirty, setDirty] = useState(false)

  useEffect(() => {
    if (note) {
      setTitle(note.title)
      setContent(note.content)
      setDirty(false)
    } else if (isNew) {
      setTitle('')
      setContent('')
      setDirty(false)
    }
  }, [note, isNew])

  const handleSave = () => {
    if (isNew) {
      createNote.mutate(
        { title: title || 'Untitled note', content },
        {
          onSuccess: (created) => {
            setDirty(false)
            navigate(`/notes/${created.id}`, { replace: true })
          },
        },
      )
    } else {
      updateNote.mutate({ title, content }, { onSuccess: () => setDirty(false) })
    }
  }

  const handleDelete = () => {
    if (isNew) return
    deleteNote.mutate(noteId, { onSuccess: () => navigate('/notes', { replace: true }) })
  }

  const isSaving = createNote.isPending || updateNote.isPending

  if (!isNew && isLoading) {
    return (
      <div className="space-y-3 p-8">
        <div className="h-8 w-1/3 animate-pulse rounded bg-slate-100" />
        <div className="h-64 animate-pulse rounded bg-slate-100" />
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-8 py-5">
        <div>
          <h1 className="text-lg font-semibold text-slate-900">
            {isNew ? 'New note' : 'Edit note'}
          </h1>
          {note && (
            <p className="mt-0.5 text-xs text-slate-400">
              Created {formatDate(note.created_at)}
              {note.updated_at !== note.created_at && ` · Edited ${formatDate(note.updated_at)}`}
            </p>
          )}
        </div>

        <div className="flex shrink-0 items-center gap-2">
          {!isNew && (
            <button
              type="button"
              onClick={handleDelete}
              disabled={deleteNote.isPending}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-red-600 transition hover:border-red-200 hover:bg-red-50 disabled:opacity-60"
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </button>
          )}
          <button
            type="button"
            onClick={handleSave}
            disabled={isSaving || (!dirty && !isNew)}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSaving ? 'Saving…' : isNew ? 'Create note' : dirty ? 'Save changes' : 'Saved'}
          </button>
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-8 py-6">
        <input
          value={title}
          onChange={(event) => {
            setTitle(event.target.value)
            setDirty(true)
          }}
          placeholder="Note title"
          className="w-full border-none bg-transparent text-2xl font-semibold text-slate-900 outline-none placeholder:text-slate-300"
        />
        <textarea
          value={content}
          onChange={(event) => {
            setContent(event.target.value)
            setDirty(true)
          }}
          placeholder="Start writing…"
          className="min-h-[50vh] w-full flex-1 resize-none border-none bg-transparent text-[15px] leading-relaxed text-slate-700 outline-none placeholder:text-slate-300"
        />
      </div>
    </div>
  )
}
