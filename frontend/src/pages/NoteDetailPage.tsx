import { useParams } from 'react-router-dom'
import NoteEditor from '../components/NoteEditor/NoteEditor'

export default function NoteDetailPage() {
  const { noteId } = useParams<{ noteId: string }>()

  if (!noteId) return null

  return <NoteEditor noteId={noteId} />
}
