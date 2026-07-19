import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/ui/Navbar';

export default function AppLayout() {
  const { logout, currentUser } = useAuth();
  const location = useLocation();

  return (
    <div className="h-screen flex flex-col bg-slate-50 text-slate-900 overflow-hidden">
      <Navbar />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-slate-800 text-slate-100 flex flex-col p-4 border-r border-slate-700 shrink-0">
          <nav className="flex flex-col gap-2 flex-grow">
            <Link 
              to="/dashboard" 
              className={`px-3 py-2 rounded transition ${
                location.pathname === '/dashboard' 
                  ? 'bg-slate-700 text-white font-medium border-l-4 border-indigo-500 pl-2' 
                  : 'hover:bg-slate-700'
              }`}
            >
              Dashboard
            </Link>
            <Link 
              to="/documents" 
              className={`px-3 py-2 rounded transition ${
                location.pathname === '/documents' 
                  ? 'bg-slate-700 text-white font-medium border-l-4 border-indigo-500 pl-2' 
                  : 'hover:bg-slate-700'
              }`}
            >
              Documents
            </Link>
            <Link 
              to="/chat" 
              className={`px-3 py-2 rounded transition ${
                location.pathname === '/chat' 
                  ? 'bg-slate-700 text-white font-medium border-l-4 border-indigo-500 pl-2' 
                  : 'hover:bg-slate-700'
              }`}
            >
              Chat
            </Link>
            {currentUser?.role === 'SUPER_ADMIN' && (
              <Link 
                to="/super-admin" 
                className={`px-3 py-2 rounded transition ${
                  location.pathname === '/super-admin' 
                    ? 'bg-slate-700 text-white font-medium border-l-4 border-indigo-500 pl-2' 
                    : 'hover:bg-slate-700'
                }`}
              >
                Super Admin Portal
              </Link>
            )}
            {currentUser?.role === 'ADMIN' && (
              <>
                <Link 
                  to="/users" 
                  className={`px-3 py-2 rounded transition ${
                    location.pathname === '/users' 
                      ? 'bg-slate-700 text-white font-medium border-l-4 border-indigo-500 pl-2' 
                      : 'hover:bg-slate-700'
                  }`}
                >
                  User Management
                </Link>
                <Link 
                  to="/settings" 
                  className={`px-3 py-2 rounded transition ${
                    location.pathname === '/settings' 
                      ? 'bg-slate-700 text-white font-medium border-l-4 border-indigo-500 pl-2' 
                      : 'hover:bg-slate-700'
                  }`}
                >
                  Company Settings
                </Link>
              </>
            )}
          </nav>
          <button
            onClick={logout}
            className="mt-auto w-full py-2 px-3 bg-red-800/80 hover:bg-red-800 text-white rounded text-left transition text-sm font-medium"
          >
            Logout
          </button>
        </aside>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
