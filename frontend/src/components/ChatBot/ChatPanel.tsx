import { MessageCircleQuestion, X } from 'lucide-react'
import { useEffect, useRef } from 'react'
import { useChat } from '../../hooks/useChat'
import { useChatStore } from '../../store/chatStore'
import ChatInput from './ChatInput'
import ChatMessage from './ChatMessage'

export default function ChatPanel() {
  const isOpen = useChatStore((state) => state.isOpen)
  const toggle = useChatStore((state) => state.toggle)
  const messages = useChatStore((state) => state.messages)
  const { ask, isPending } = useChat()
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, isPending])

  return (
    <>
      <button
        type="button"
        onClick={toggle}
        className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-600 text-white shadow-lg shadow-indigo-300 transition hover:bg-indigo-700"
        aria-label="Toggle chat"
      >
        {isOpen ? <X className="h-6 w-6" /> : <MessageCircleQuestion className="h-6 w-6" />}
      </button>

      <div
        className={`fixed bottom-24 right-6 z-30 flex h-[32rem] w-96 max-w-[calc(100vw-3rem)] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl transition-all duration-200 ${
          isOpen ? 'translate-y-0 opacity-100' : 'pointer-events-none translate-y-4 opacity-0'
        }`}
      >
        <div className="border-b border-slate-200 px-4 py-3">
          <p className="text-sm font-semibold text-slate-900">Ask your notes</p>
          <p className="text-xs text-slate-400">Answers are grounded only in your saved notes.</p>
        </div>

        <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto bg-slate-50 px-3 py-4">
          {messages.length === 0 ? (
            <p className="px-2 text-sm text-slate-400">
              Ask a question about something you've written down.
            </p>
          ) : (
            messages.map((message) => <ChatMessage key={message.id} message={message} />)
          )}
          {isPending && (
            <div className="flex justify-start">
              <div className="rounded-2xl rounded-bl-sm border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-400">
                Thinking…
              </div>
            </div>
          )}
        </div>

        <ChatInput onSend={ask} isPending={isPending} />
      </div>
    </>
  )
}
