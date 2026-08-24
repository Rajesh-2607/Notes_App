import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import ProtectedRoute from './components/ProtectedRoute'
import AllNotesPage from './pages/AllNotesPage'
import LoginPage from './pages/LoginPage'
import NoteDetailPage from './pages/NoteDetailPage'
import RegisterPage from './pages/RegisterPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/notes" element={<AllNotesPage />} />
              <Route path="/notes/:noteId" element={<NoteDetailPage />} />
            </Route>
          </Route>

          <Route path="/" element={<Navigate to="/notes" replace />} />
          <Route path="*" element={<Navigate to="/notes" replace />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App
