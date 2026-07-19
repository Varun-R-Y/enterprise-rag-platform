import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Users, 
  UserPlus, 
  Trash2, 
  Search, 
  Shield, 
  Briefcase, 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle2, 
  X, 
  Plus 
} from 'lucide-react';

// UI Components
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Spinner from '../../components/ui/Spinner';
import Modal from '../../components/ui/Modal';
import Alert from '../../components/ui/Alert';

// Services
import userService from '../../services/userService';

export default function UserManagement() {
  const { currentUser, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!authLoading && currentUser && currentUser.role !== 'ADMIN') {
      navigate('/dashboard');
    }
  }, [currentUser, authLoading, navigate]);

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Create User Modal State
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [formData, setFormData] = useState({ fullName: '', email: '', password: '' });
  const [formErrors, setFormErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  
  // Deletion State
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Global Alert State
  const [alert, setAlert] = useState(null);

  const fetchUsers = async (isSilent = false) => {
    if (!isSilent) setLoading(true);
    else setRefreshing(true);
    
    try {
      const data = await userService.listUsers();
      setUsers(data || []);
    } catch (err) {
      console.error('Failed to load users:', err);
      let errorMsg = 'Could not retrieve users. Please verify backend connection.';
      if (err.response && err.response.data && err.response.data.detail) {
        errorMsg = typeof err.response.data.detail === 'string'
          ? err.response.data.detail
          : err.response.data.detail.map(e => e.msg).join(', ');
      }
      setAlert({ type: 'error', message: errorMsg });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchUsers(false);
  }, []);

  const validateForm = () => {
    const errors = {};
    if (!formData.fullName.trim()) errors.fullName = 'Full Name is required.';
    if (!formData.email.trim()) {
      errors.email = 'Email address is required.';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Invalid email address format.';
    }
    if (!formData.password) {
      errors.password = 'Password is required.';
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters.';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setSubmitting(true);
    try {
      await userService.createEmployee(formData.fullName, formData.email, formData.password);
      setAlert({ type: 'success', message: `Employee account created successfully for ${formData.email}.` });
      setIsCreateOpen(false);
      setFormData({ fullName: '', email: '', password: '' });
      setFormErrors({});
      fetchUsers(true);
    } catch (err) {
      console.error('Failed to create user:', err);
      let errorMsg = 'Failed to create user account.';
      if (err.response && err.response.data && err.response.data.detail) {
        errorMsg = typeof err.response.data.detail === 'string'
          ? err.response.data.detail
          : err.response.data.detail.map(e => e.msg).join(', ');
      }
      setFormErrors({ api: errorMsg });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    try {
      await userService.deleteUser(deleteTarget.id);
      setAlert({ type: 'success', message: `Successfully deleted user account ${deleteTarget.email}.` });
      setDeleteTarget(null);
      fetchUsers(true);
    } catch (err) {
      console.error('Failed to delete user:', err);
      let errorMsg = 'Failed to delete user.';
      if (err.response && err.response.data && err.response.data.detail) {
        errorMsg = typeof err.response.data.detail === 'string'
          ? err.response.data.detail
          : err.response.data.detail.map(e => e.msg).join(', ');
      }
      setAlert({ type: 'error', message: errorMsg });
    } finally {
      setIsDeleting(false);
    }
  };

  // Stats
  const totalCount = users.length;
  const adminCount = users.filter((u) => u.role === 'ADMIN').length;
  const employeeCount = users.filter((u) => u.role === 'EMPLOYEE').length;

  // Filtered Users
  const filteredUsers = users.filter((u) => {
    const term = searchTerm.toLowerCase();
    return (
      u.full_name?.toLowerCase().includes(term) ||
      u.email?.toLowerCase().includes(term) ||
      u.role?.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">User Management</h1>
          <p className="text-slate-500 text-sm mt-1">Manage employee accounts and roles under your enterprise tenant.</p>
        </div>
        <div className="flex items-center gap-2.5">
          <Button 
            onClick={() => fetchUsers(true)} 
            variant="secondary" 
            className="h-10 px-3 border border-slate-200 text-slate-600 hover:text-slate-900 shadow-sm"
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
          <Button 
            onClick={() => setIsCreateOpen(true)} 
            variant="primary" 
            className="h-10 px-4 text-sm py-1.5 flex items-center gap-2"
          >
            <UserPlus size={16} />
            <span>Add Employee</span>
          </Button>
        </div>
      </div>

      {/* Global Alerts */}
      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
        />
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="flex items-center gap-4 py-4 px-6">
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-lg">
            <Users size={24} />
          </div>
          <div>
            <span className="text-sm font-medium text-slate-500 block">Total Users</span>
            <span className="text-2xl font-bold text-slate-900 mt-0.5 block">{totalCount}</span>
          </div>
        </Card>

        <Card className="flex items-center gap-4 py-4 px-6">
          <div className="p-3 bg-violet-50 text-violet-600 rounded-lg">
            <Shield size={24} />
          </div>
          <div>
            <span className="text-sm font-medium text-slate-500 block">Administrators</span>
            <span className="text-2xl font-bold text-slate-900 mt-0.5 block">{adminCount}</span>
          </div>
        </Card>

        <Card className="flex items-center gap-4 py-4 px-6">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg">
            <Briefcase size={24} />
          </div>
          <div>
            <span className="text-sm font-medium text-slate-500 block">Employees</span>
            <span className="text-2xl font-bold text-slate-900 mt-0.5 block">{employeeCount}</span>
          </div>
        </Card>
      </div>

      {/* Search & Main Table */}
      <Card className="overflow-hidden border border-slate-200">
        <div className="p-4 border-b border-slate-100 flex items-center gap-3">
          <div className="relative flex-grow max-w-md">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input
              type="text"
              placeholder="Search by name, email, or role..."
              className="w-full pl-10 pr-4 h-10 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <Spinner size="lg" />
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="p-12 text-center">
            <Users className="mx-auto text-slate-300 mb-3" size={40} />
            <h3 className="font-semibold text-slate-800 text-base">No Users Found</h3>
            <p className="text-slate-400 text-sm mt-1">Try refining your search term or add a new employee.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left text-sm">
              <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 font-semibold uppercase text-xs">
                <tr>
                  <th className="py-3 px-6">Full Name</th>
                  <th className="py-3 px-6">Email Address</th>
                  <th className="py-3 px-6">Role</th>
                  <th className="py-3 px-6">Created By</th>
                  <th className="py-3 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {filteredUsers.map((user) => {
                  const isSelf = user.id === currentUser?.id;
                  const isAdminRole = user.role === 'ADMIN';
                  
                  return (
                    <tr key={user.id} className="hover:bg-slate-50/50 transition">
                      <td className="py-4 px-6 font-semibold text-slate-900">{user.full_name}</td>
                      <td className="py-4 px-6">{user.email}</td>
                      <td className="py-4 px-6">
                        <span className={`inline-flex items-center gap-1.5 py-1 px-2.5 rounded-full text-xs font-semibold ${
                          isAdminRole
                            ? 'bg-violet-50 text-violet-700 border border-violet-100'
                            : 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                        }`}>
                          {isAdminRole ? <Shield size={10} /> : <Briefcase size={10} />}
                          <span>{isAdminRole ? 'Admin' : 'Employee'}</span>
                        </span>
                      </td>
                      <td className="py-4 px-6 text-xs text-slate-400 font-mono">
                        {user.created_by ? user.created_by : 'System Seed'}
                      </td>
                      <td className="py-4 px-6 text-right">
                        {isSelf ? (
                          <span className="text-xs font-medium text-slate-400 italic mr-2 bg-slate-100 px-2 py-1 rounded">You</span>
                        ) : (
                          <button
                            onClick={() => setDeleteTarget(user)}
                            className="p-2 text-slate-400 hover:text-red-600 transition rounded-lg hover:bg-slate-100"
                            title="Delete User"
                          >
                            <Trash2 size={16} />
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Create Employee Modal */}
      {isCreateOpen && (
        <Modal 
          isOpen={isCreateOpen} 
          onClose={() => {
            setIsCreateOpen(false);
            setFormErrors({});
            setFormData({ fullName: '', email: '', password: '' });
          }}
          title="Add New Employee"
        >
          <form onSubmit={handleCreateSubmit} className="space-y-4">
            {formErrors.api && (
              <div className="p-3 bg-red-50 border-l-4 border-red-500 text-red-700 text-sm rounded">
                {formErrors.api}
              </div>
            )}

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">
                Full Name
              </label>
              <input
                type="text"
                disabled={submitting}
                className={`w-full border rounded-lg px-3 py-2 text-slate-900 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                  formErrors.fullName ? 'border-red-500' : 'border-slate-200'
                }`}
                value={formData.fullName}
                onChange={(e) => setFormData(prev => ({ ...prev, fullName: e.target.value }))}
              />
              {formErrors.fullName && (
                <p className="text-red-600 text-xs mt-1">{formErrors.fullName}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                disabled={submitting}
                className={`w-full border rounded-lg px-3 py-2 text-slate-900 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                  formErrors.email ? 'border-red-500' : 'border-slate-200'
                }`}
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              />
              {formErrors.email && (
                <p className="text-red-600 text-xs mt-1">{formErrors.email}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">
                Password
              </label>
              <input
                type="password"
                disabled={submitting}
                className={`w-full border rounded-lg px-3 py-2 text-slate-900 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                  formErrors.password ? 'border-red-500' : 'border-slate-200'
                }`}
                value={formData.password}
                onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              />
              {formErrors.password && (
                <p className="text-red-600 text-xs mt-1">{formErrors.password}</p>
              )}
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-slate-100">
              <Button
                type="button"
                variant="secondary"
                disabled={submitting}
                className="h-10 px-4 text-sm"
                onClick={() => {
                  setIsCreateOpen(false);
                  setFormErrors({});
                  setFormData({ fullName: '', email: '', password: '' });
                }}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={submitting}
                className="h-10 px-4 text-sm"
              >
                {submitting ? 'Creating...' : 'Create Employee'}
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Delete Confirmation Modal */}
      {deleteTarget && (
        <Modal
          isOpen={!!deleteTarget}
          onClose={() => setDeleteTarget(null)}
          title="Delete User Account"
        >
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-3 bg-amber-50 text-amber-800 rounded-lg text-sm border border-amber-200">
              <AlertTriangle className="text-amber-500 shrink-0 mt-0.5" size={16} />
              <p>
                Are you sure you want to delete the user account for <strong>{deleteTarget.full_name}</strong> ({deleteTarget.email})? 
                This action is permanent and will prevent them from logging in.
              </p>
            </div>
            <div className="flex justify-end gap-3 pt-3 border-t border-slate-100">
              <Button
                type="button"
                variant="secondary"
                disabled={isDeleting}
                className="h-10 px-4 text-sm"
                onClick={() => setDeleteTarget(null)}
              >
                Cancel
              </Button>
              <Button
                type="button"
                variant="primary"
                disabled={isDeleting}
                className="h-10 px-4 text-sm bg-red-600 hover:bg-red-500 active:bg-red-700"
                onClick={handleDeleteConfirm}
              >
                {isDeleting ? 'Deleting...' : 'Delete User'}
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
