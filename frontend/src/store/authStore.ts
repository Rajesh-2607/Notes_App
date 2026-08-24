import { create } from 'zustand'

const STORAGE_KEY = 'notes_app_token'

interface AuthState {
  token: string | null
  email: string | null
  setSession: (token: string, email: string | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem(STORAGE_KEY),
  email: null,
  setSession: (token, email) => {
    localStorage.setItem(STORAGE_KEY, token)
    set({ token, email })
  },
  logout: () => {
    localStorage.removeItem(STORAGE_KEY)
    set({ token: null, email: null })
  },
}))
