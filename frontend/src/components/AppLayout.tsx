import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar/Sidebar'
import ChatPanel from './ChatBot/ChatPanel'

export default function AppLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar />
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
      <ChatPanel />
    </div>
  )
}
