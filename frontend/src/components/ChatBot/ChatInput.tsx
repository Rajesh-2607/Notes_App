import { Send } from 'lucide-react'
import { useState } from 'react'

interface ChatInputProps {
  onSend: (question: string) => void
  isPending: boolean
}

export default function ChatInput({ onSend, isPending }: ChatInputProps) {
  const [value, setValue] = useState('')

  const submit = () => {
    if (!value.trim() || isPending) return
    onSend(value)
    setValue('')
  }

  return (
    <div className="flex items-end gap-2 border-t border-slate-200 p-3">
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault()
            submit()
          }
        }}
        rows={1}
        placeholder="Ask about your notes…"
        className="max-h-32 flex-1 resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
      />
      <button
        type="button"
        onClick={submit}
        disabled={isPending || !value.trim()}
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        aria-label="Send question"
      >
        <Send className="h-4 w-4" />
      </button>
    </div>
  )
}
