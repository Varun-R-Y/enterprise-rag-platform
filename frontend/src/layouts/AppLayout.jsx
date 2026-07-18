import { Outlet, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function AppLayout() {
  const { logout, currentUser } = useAuth();

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900">
      {/* Sidebar Placeholder */}
      <aside className="w-64 bg-slate-800 text-slate-100 flex flex-col p-4 border-r border-slate-700">
        <div className="font-bold text-lg mb-6 tracking-wide text-white">Enterprise RAG</div>
        <nav className="flex flex-col gap-2 flex-grow">
          <Link to="/dashboard" className="px-3 py-2 rounded hover:bg-slate-700 transition">Dashboard</Link>
          <Link to="/documents" className="px-3 py-2 rounded hover:bg-slate-700 transition">Documents</Link>
          <Link to="/chat" className="px-3 py-2 rounded hover:bg-slate-700 transition">Chat</Link>
        </nav>
        <button
          onClick={logout}
          className="mt-auto w-full py-2 px-3 bg-red-800 text-white rounded text-left hover:bg-red-700 transition"
        >
          Logout
        </button>
      </aside>

      {/* Main Wrapper */}
      <div className="flex-1 flex flex-col">
        {/* Topbar Placeholder */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6">
          <div className="text-slate-500 font-medium">Platform Infrastructure</div>
          <div className="flex items-center gap-4">
            {currentUser && (
              <span className="text-sm text-slate-700 font-medium">
                {currentUser.full_name} ({currentUser.email})
              </span>
            )}
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
