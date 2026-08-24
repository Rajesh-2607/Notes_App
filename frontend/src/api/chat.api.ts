import { apiClient } from './client'
import type { ChatResponse } from '../types/chat.types'

export async function askQuestion(question: string): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>('/chat', { question })
  return data
}
