import { useMutation } from '@tanstack/react-query'
import { askQuestion } from '../api/chat.api'
import { useChatStore } from '../store/chatStore'

export function useChat() {
  const addMessage = useChatStore((state) => state.addMessage)

  const mutation = useMutation({
    mutationFn: (question: string) => askQuestion(question),
  })

  const ask = (question: string) => {
    const trimmed = question.trim()
    if (!trimmed) return

    addMessage({ id: crypto.randomUUID(), role: 'user', content: trimmed })

    mutation.mutate(trimmed, {
      onSuccess: (response) => {
        addMessage({
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
        })
      },
      onError: () => {
        addMessage({
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Something went wrong reaching the RAG bot. Please try again.',
        })
      },
    })
  }

  return { ask, isPending: mutation.isPending }
}
