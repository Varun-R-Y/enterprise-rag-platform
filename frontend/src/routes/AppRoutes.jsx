import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import AnonymousRoute from './AnonymousRoute';
import AppLayout from '../layouts/AppLayout';

// Pages
import Landing from '../pages/Landing/Landing';
import Login from '../pages/Login/Login';
import Dashboard from '../pages/Dashboard/Dashboard';
import Documents from '../pages/Documents/Documents';
import Chat from '../pages/Chat/Chat';
import UserManagement from '../pages/UserManagement/UserManagement';
import SuperAdminDashboard from '../pages/SuperAdmin/SuperAdminDashboard';
import CompanySettings from '../pages/CompanySettings/CompanySettings';
import NotFound from '../pages/NotFound/NotFound';

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public Landing Page */}
      <Route path="/" element={<Landing />} />

      {/* Public Routes for guest users only (redirects to dashboard if already logged in) */}
      <Route element={<AnonymousRoute />}>
        <Route path="/login" element={<Login />} />
      </Route>

      {/* Protected Routes inside AppLayout */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/users" element={<UserManagement />} />
          <Route path="/super-admin" element={<SuperAdminDashboard />} />
          <Route path="/settings" element={<CompanySettings />} />
        </Route>
      </Route>

      {/* Catch-all Route */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
