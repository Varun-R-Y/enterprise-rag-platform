import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Layers } from 'lucide-react';
import Button from './Button';
import Container from './Container';

export default function Navbar() {
  const { isAuthenticated, currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';
  const isAppPage = location.pathname === '/dashboard' || location.pathname === '/documents' || location.pathname === '/chat';

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-slate-200 h-16 flex items-center w-full">
      <Container className="flex items-center justify-between">
        {/* Brand/Logo */}
        <div className="flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2 hover:opacity-90 transition">
            <Layers className="text-indigo-600" size={24} />
            <span className="font-bold text-lg text-slate-900 tracking-wide">Enterprise RAG</span>
          </Link>
        </div>
        
        {/* Middle Navigation Links */}
        <nav className="hidden md:flex items-center gap-8">
          {isAppPage ? (
            <>
              <Link 
                to="/" 
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition"
              >
                Home
              </Link>
              <Link 
                to="/dashboard" 
                className={`text-sm font-medium transition ${
                  location.pathname === '/dashboard' ? 'text-indigo-600 font-semibold' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Dashboard
              </Link>
              <Link 
                to="/documents" 
                className={`text-sm font-medium transition ${
                  location.pathname === '/documents' ? 'text-indigo-600 font-semibold' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Documents
              </Link>
              <Link 
                to="/chat" 
                className={`text-sm font-medium transition ${
                  location.pathname === '/chat' ? 'text-indigo-600 font-semibold' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Chat
              </Link>
              {currentUser?.role === 'SUPER_ADMIN' && (
                <Link 
                  to="/super-admin" 
                  className={`text-sm font-medium transition ${
                    location.pathname === '/super-admin' ? 'text-indigo-600 font-semibold' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Super Admin
                </Link>
              )}
              {currentUser?.role === 'ADMIN' && (
                <>
                  <Link 
                    to="/users" 
                    className={`text-sm font-medium transition ${
                      location.pathname === '/users' ? 'text-indigo-600 font-semibold' : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    Users
                  </Link>
                  <Link 
                    to="/settings" 
                    className={`text-sm font-medium transition ${
                      location.pathname === '/settings' ? 'text-indigo-600 font-semibold' : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    Settings
                  </Link>
                </>
              )}
            </>
          ) : (
            <>
              <a href="/#" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Home</a>
              <a href="/#features" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Features</a>
              <a href="/#pipeline" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Pipeline</a>
              <a href="/#techstack" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Tech Stack</a>
              <a href="/#architecture" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Architecture</a>
            </>
          )}
        </nav>

        {/* Right Authentication Actions */}
        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <div className="flex items-center gap-4">
              {currentUser && !isAuthPage && (
                <span className="hidden lg:inline text-xs text-slate-500 font-medium bg-slate-100 py-1 px-2.5 rounded-full">
                  {currentUser.full_name} ({currentUser.email})
                </span>
              )}
              {!isAppPage ? (
                <Button onClick={() => navigate('/dashboard')} variant="primary" className="h-10 px-4 text-sm py-1.5">
                  Dashboard
                </Button>
              ) : (
                <Button 
                  onClick={() => {
                    logout();
                    navigate('/');
                  }} 
                  variant="secondary" 
                  className="h-10 px-4 text-sm py-1.5 border border-slate-200 text-slate-600 hover:text-slate-900"
                >
                  Logout
                </Button>
              )}
            </div>
          ) : (
            <>
              <Button 
                onClick={() => navigate('/login')} 
                variant="primary" 
                className="h-10 px-4 text-sm py-1.5"
              >
                Sign In
              </Button>
            </>
          )}
        </div>
      </Container>
    </header>
  );
}
