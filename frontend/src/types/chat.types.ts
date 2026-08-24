export interface ChatSource {
  note_id: string
  title: string
  chunk_text: string
}

export interface ChatResponse {
  answer: string
  sources: ChatSource[]
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: ChatSource[]
}
