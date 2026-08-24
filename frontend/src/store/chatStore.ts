import { create } from 'zustand'
import type { ChatMessage } from '../types/chat.types'

interface ChatState {
  isOpen: boolean
  messages: ChatMessage[]
  open: () => void
  close: () => void
  toggle: () => void
  addMessage: (message: ChatMessage) => void
  reset: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  isOpen: false,
  messages: [],
  open: () => set({ isOpen: true }),
  close: () => set({ isOpen: false }),
  toggle: () => set((state) => ({ isOpen: !state.isOpen })),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  reset: () => set({ messages: [] }),
}))
