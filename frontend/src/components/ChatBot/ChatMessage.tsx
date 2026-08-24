import { Link } from 'react-router-dom'
import type { ChatMessage as ChatMessageType } from '../../types/chat.types'

interface ChatMessageProps {
  message: ChatMessageType
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm ${
          isUser
            ? 'rounded-br-sm bg-indigo-600 text-white'
            : 'rounded-bl-sm border border-slate-200 bg-white text-slate-700'
        }`}
      >
        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>

        {message.sources && message.sources.length > 0 && (
          <div className="mt-2.5 space-y-1.5 border-t border-slate-100 pt-2.5">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Sources
            </p>
            {message.sources.map((source, index) => (
              <Link
                key={`${source.note_id}-${index}`}
                to={`/notes/${source.note_id}`}
                className="block rounded-lg bg-indigo-50 px-2.5 py-1.5 text-xs text-indigo-700 transition hover:bg-indigo-100"
              >
                <span className="font-medium">{source.title}</span>
                <p className="mt-0.5 line-clamp-2 text-indigo-600/80">{source.chunk_text}</p>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
