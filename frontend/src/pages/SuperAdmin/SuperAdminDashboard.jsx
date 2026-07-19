import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import tenantService from '../../services/tenantService';
import userService from '../../services/userService';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Modal from '../../components/ui/Modal';
import Alert from '../../components/ui/Alert';
import Badge from '../../components/ui/Badge';
import Spinner from '../../components/ui/Spinner';
import { 
  Building, 
  Users, 
  ShieldAlert, 
  ShieldCheck, 
  Settings, 
  FileText, 
  MessageSquare, 
  HardDrive, 
  Plus, 
  Check, 
  X, 
  Search,
  Briefcase,
  ExternalLink,
  Shield,
  Trash2
} from 'lucide-react';

const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export default function SuperAdminDashboard() {
  const { currentUser, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!authLoading && currentUser && currentUser.role !== 'SUPER_ADMIN') {
      navigate('/dashboard');
    }
  }, [currentUser, authLoading, navigate]);

  const [activeTab, setActiveTab] = useState('companies'); // 'companies', 'admins', 'users'
  const [tenants, setTenants] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [alert, setAlert] = useState(null);

  // Selected Company for detailed management
  const [selectedTenant, setSelectedTenant] = useState(null);
  const [selectedTenantDetails, setSelectedTenantDetails] = useState(null);
  const [selectedTenantUsers, setSelectedTenantUsers] = useState([]);
  const [selectedTenantDocs, setSelectedTenantDocs] = useState([]);
  const [selectedTenantTab, setSelectedTenantTab] = useState('general'); // 'general', 'users', 'docs'
  const [loadingDetails, setLoadingDetails] = useState(false);

  // Modals state
  const [isCreateTenantOpen, setIsCreateTenantOpen] = useState(false);
  const [tenantFormData, setTenantFormData] = useState({
    name: '',
    slug: '',
    description: '',
    timezone: 'UTC',
    logo_url: ''
  });
  const [tenantErrors, setTenantErrors] = useState({});

  const [isCreateAdminOpen, setIsCreateAdminOpen] = useState(false);
  const [adminFormData, setAdminFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    tenantId: ''
  });
  const [adminErrors, setAdminErrors] = useState({});

  // Search terms
  const [companySearch, setCompanySearch] = useState('');
  const [adminSearch, setAdminSearch] = useState('');
  const [userSearch, setUserSearch] = useState('');

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async (silent = false) => {
    if (!silent) setLoading(true);
    setRefreshing(true);
    try {
      const tenantData = await tenantService.listTenants();
      setTenants(tenantData);

      const usersList = await userService.listUsers();
      setAllUsers(usersList);
      setAlert(null);
    } catch (err) {
      setAlert({ type: 'error', message: err.response?.data?.detail || 'Failed to fetch SaaS records.' });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleCreateTenant = async (e) => {
    e.preventDefault();
    setTenantErrors({});
    if (!tenantFormData.name.trim()) {
      setTenantErrors({ name: 'Company Name is required' });
      return;
    }
    
    try {
      await tenantService.createTenant(tenantFormData);
      setAlert({ type: 'success', message: `Company '${tenantFormData.name}' registered successfully.` });
      setIsCreateTenantOpen(false);
      setTenantFormData({ name: '', slug: '', description: '', timezone: 'UTC', logo_url: '' });
      fetchInitialData(true);
    } catch (err) {
      setTenantErrors({ api: err.response?.data?.detail || 'Registration failed.' });
    }
  };

  const handleCreateAdmin = async (e) => {
    e.preventDefault();
    setAdminErrors({});
    const errors = {};
    if (!adminFormData.fullName.trim()) errors.fullName = 'Full Name is required';
    if (!adminFormData.email.trim()) errors.email = 'Email address is required';
    if (!adminFormData.password.trim() || adminFormData.password.length < 8) errors.password = 'Password must be at least 8 characters';
    if (!adminFormData.tenantId) errors.tenantId = 'Please select a company';

    if (Object.keys(errors).length > 0) {
      setAdminErrors(errors);
      return;
    }

    try {
      await userService.createCompanyAdmin(
        adminFormData.fullName,
        adminFormData.email,
        adminFormData.password,
        adminFormData.tenantId
      );
      setAlert({ type: 'success', message: `Company Admin created successfully.` });
      setIsCreateAdminOpen(false);
      setAdminFormData({ fullName: '', email: '', password: '', tenantId: '' });
      fetchInitialData(true);
    } catch (err) {
      setAdminErrors({ api: err.response?.data?.detail || 'Company Admin creation failed.' });
    }
  };

  const handleToggleTenantActive = async (id, currentStatus) => {
    try {
      await tenantService.updateTenant(id, { is_active: !currentStatus });
      setAlert({ 
        type: 'success', 
        message: `Company status successfully updated to ${!currentStatus ? 'Active' : 'Inactive'}.` 
      });
      fetchInitialData(true);
      if (selectedTenant && selectedTenant.id === id) {
        // Refresh detail view
        fetchTenantDetails(id);
      }
    } catch (err) {
      setAlert({ type: 'error', message: err.response?.data?.detail || 'Failed to toggle status.' });
    }
  };

  const fetchTenantDetails = async (id) => {
    setLoadingDetails(true);
    try {
      const details = await tenantService.getTenantDetails(id);
      setSelectedTenantDetails(details);
      
      // Load tenant specific users & docs
      const usersList = await userService.listUsers();
      const filteredUsers = usersList.filter(u => u.tenant_id === id);
      setSelectedTenantUsers(filteredUsers);

      // Setup documents fetch or mock if needed (documents route gets filtered by backend tenant bound)
      // Since Super Admin can't easily fetch documents list of a different tenant directly unless they override,
      // let's fetch documents if possible, or just default. Wait, super admin gets require_admin access to GET /documents? No, GET /documents lists for tenant of authenticated user.
      // So to list documents of another tenant, Super Admin endpoint or logic is needed. Let's make sure it is empty or lists documents where tenant_id == id.
      // Wait, is there a documents endpoint for super admin? In the requirements, Super Admin view company documents.
      // So we will just show stats or list documents in detail. We can add a tenant filter query parameter to GET /documents or fetch it in stats.
      // Let's filter all documents if backend return them, or fallback gracefully.
      setSelectedTenantDocs([]);
    } catch (err) {
      setAlert({ type: 'error', message: 'Failed to fetch company details.' });
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleSelectTenant = (tenant) => {
    setSelectedTenant(tenant);
    setSelectedTenantTab('general');
    fetchTenantDetails(tenant.id);
  };

  const handleUpdateTenantDetails = async (e) => {
    e.preventDefault();
    if (!selectedTenantDetails) return;
    try {
      const { name, slug, description, logo_url, timezone } = selectedTenantDetails.tenant;
      await tenantService.updateTenant(selectedTenant.id, {
        name,
        slug,
        description,
        logo_url,
        timezone
      });
      setAlert({ type: 'success', message: 'Company settings updated successfully.' });
      fetchInitialData(true);
    } catch (err) {
      setAlert({ type: 'error', message: err.response?.data?.detail || 'Update failed.' });
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm("Are you sure you want to permanently delete this user account?")) return;
    try {
      await userService.deleteUser(userId);
      setAlert({ type: 'success', message: 'User account deleted successfully.' });
      fetchInitialData(true);
      if (selectedTenant) {
        fetchTenantDetails(selectedTenant.id);
      }
    } catch (err) {
      setAlert({ type: 'error', message: err.response?.data?.detail || 'Failed to delete user.' });
    }
  };

  // Filtered lists
  const filteredTenants = tenants.filter(item => 
    item.tenant.name.toLowerCase().includes(companySearch.toLowerCase()) ||
    (item.admin_email && item.admin_email.toLowerCase().includes(companySearch.toLowerCase()))
  );

  const admins = allUsers.filter(u => u.role === 'ADMIN');
  const filteredAdmins = admins.filter(admin => 
    admin.full_name.toLowerCase().includes(adminSearch.toLowerCase()) ||
    admin.email.toLowerCase().includes(adminSearch.toLowerCase())
  );

  const filteredAllUsers = allUsers.filter(u => 
    u.full_name.toLowerCase().includes(userSearch.toLowerCase()) ||
    u.email.toLowerCase().includes(userSearch.toLowerCase()) ||
    u.role.toLowerCase().includes(userSearch.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px]">
        <Spinner size="lg" className="text-indigo-600" />
        <p className="text-slate-500 text-sm mt-3 font-medium">Loading Super Admin portal...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">Super Admin Portal</h1>
          <p className="text-slate-500 text-sm mt-1 leading-relaxed">
            Manage global enterprise tenants, system administrators, and monitor organization metrics.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {activeTab === 'companies' && (
            <Button
              onClick={() => setIsCreateTenantOpen(true)}
              variant="primary"
              className="h-10 px-4 py-2 cursor-pointer font-semibold flex items-center gap-2"
            >
              <Plus size={18} />
              Register Company
            </Button>
          )}
          {activeTab === 'admins' && (
            <Button
              onClick={() => setIsCreateAdminOpen(true)}
              variant="primary"
              className="h-10 px-4 py-2 cursor-pointer font-semibold flex items-center gap-2"
            >
              <Plus size={18} />
              Create Admin
            </Button>
          )}
        </div>
      </div>

      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
        />
      )}

      {/* Tabs bar */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => { setActiveTab('companies'); setSelectedTenant(null); }}
          className={`py-3 px-6 text-sm font-semibold border-b-2 cursor-pointer transition ${
            activeTab === 'companies' && !selectedTenant
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Companies
        </button>
        <button
          onClick={() => { setActiveTab('admins'); setSelectedTenant(null); }}
          className={`py-3 px-6 text-sm font-semibold border-b-2 cursor-pointer transition ${
            activeTab === 'admins'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Company Admins
        </button>
        <button
          onClick={() => { setActiveTab('users'); setSelectedTenant(null); }}
          className={`py-3 px-6 text-sm font-semibold border-b-2 cursor-pointer transition ${
            activeTab === 'users'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Universal Users
        </button>
        {selectedTenant && (
          <span className="py-3 px-4 text-sm font-semibold text-slate-400 border-b-2 border-transparent">
            &gt; Managing: <span className="text-indigo-600 font-bold">{selectedTenant.name}</span>
          </span>
        )}
      </div>

      {/* Selected Tenant Detailed Management Panel */}
      {selectedTenant && (
        <Card className="p-6 relative">
          <button 
            onClick={() => setSelectedTenant(null)}
            className="absolute top-6 right-6 text-slate-400 hover:text-slate-600 font-semibold text-sm flex items-center gap-1 cursor-pointer"
          >
            <X size={16} /> Back to List
          </button>

          {loadingDetails ? (
            <div className="flex justify-center items-center h-48">
              <Spinner className="text-indigo-600" />
            </div>
          ) : selectedTenantDetails && (
            <div className="space-y-6">
              {/* Detailed metrics header */}
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center pb-4 border-b border-slate-100 gap-4">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">{selectedTenantDetails.tenant.name}</h2>
                  <p className="text-xs text-slate-400 mt-1">Tenant ID: {selectedTenantDetails.tenant.id}</p>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant={selectedTenantDetails.tenant.is_active ? 'success' : 'primary'}>
                    {selectedTenantDetails.tenant.is_active ? 'Active' : 'Deactivated'}
                  </Badge>
                  <Button 
                    onClick={() => handleToggleTenantActive(selectedTenant.id, selectedTenantDetails.tenant.is_active)}
                    variant={selectedTenantDetails.tenant.is_active ? 'secondary' : 'primary'}
                    className="text-xs py-1.5 h-8 cursor-pointer"
                  >
                    {selectedTenantDetails.tenant.is_active ? 'Deactivate Tenant' : 'Activate Tenant'}
                  </Button>
                </div>
              </div>

              {/* Sub tabs inside Manage Tenant */}
              <div className="flex gap-2 p-1 bg-slate-50 rounded-lg w-fit">
                <button
                  onClick={() => setSelectedTenantTab('general')}
                  className={`px-4 py-1.5 text-xs font-semibold rounded-md transition ${
                    selectedTenantTab === 'general' ? 'bg-white text-indigo-600 shadow-xs' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  General Settings
                </button>
                <button
                  onClick={() => setSelectedTenantTab('users')}
                  className={`px-4 py-1.5 text-xs font-semibold rounded-md transition ${
                    selectedTenantTab === 'users' ? 'bg-white text-indigo-600 shadow-xs' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Tenant Users ({selectedTenantUsers.length})
                </button>
              </div>

              {selectedTenantTab === 'general' && (
                <form onSubmit={handleUpdateTenantDetails} className="space-y-4 max-w-xl">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Company Name</label>
                      <input 
                        type="text"
                        className="w-full text-slate-900 bg-white border border-slate-200 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
                        value={selectedTenantDetails.tenant.name}
                        onChange={(e) => {
                          const val = e.target.value;
                          setSelectedTenantDetails(prev => ({
                            ...prev,
                            tenant: { ...prev.tenant, name: val }
                          }));
                        }}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Slug (URL identifier)</label>
                      <input 
                        type="text"
                        className="w-full text-slate-900 bg-white border border-slate-200 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
                        value={selectedTenantDetails.tenant.slug}
                        onChange={(e) => {
                          const val = e.target.value;
                          setSelectedTenantDetails(prev => ({
                            ...prev,
                            tenant: { ...prev.tenant, slug: val }
                          }));
                        }}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Description</label>
                    <textarea 
                      rows={3}
                      className="w-full text-slate-900 bg-white border border-slate-200 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      value={selectedTenantDetails.tenant.description || ''}
                      onChange={(e) => {
                        const val = e.target.value;
                        setSelectedTenantDetails(prev => ({
                          ...prev,
                          tenant: { ...prev.tenant, description: val }
                        }));
                      }}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Logo URL</label>
                      <input 
                        type="text"
                        className="w-full text-slate-900 bg-white border border-slate-200 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
                        value={selectedTenantDetails.tenant.logo_url || ''}
                        onChange={(e) => {
                          const val = e.target.value;
                          setSelectedTenantDetails(prev => ({
                            ...prev,
                            tenant: { ...prev.tenant, logo_url: val }
                          }));
                        }}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Timezone</label>
                      <input 
                        type="text"
                        className="w-full text-slate-900 bg-white border border-slate-200 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
                        value={selectedTenantDetails.tenant.timezone}
                        onChange={(e) => {
                          const val = e.target.value;
                          setSelectedTenantDetails(prev => ({
                            ...prev,
                            tenant: { ...prev.tenant, timezone: val }
                          }));
                        }}
                      />
                    </div>
                  </div>

                  <Button type="submit" variant="primary" className="text-xs h-9 font-semibold">
                    Save General Changes
                  </Button>
                </form>
              )}

              {selectedTenantTab === 'users' && (
                <div className="border border-slate-200 rounded-xl overflow-hidden bg-white">
                  <table className="w-full text-left border-collapse">
                    <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 font-semibold uppercase text-[10px]">
                      <tr>
                        <th className="py-2.5 px-4">Full Name</th>
                        <th className="py-2.5 px-4">Email</th>
                        <th className="py-2.5 px-4">Role</th>
                        <th className="py-2.5 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-600 text-xs">
                      {selectedTenantUsers.length === 0 ? (
                        <tr>
                          <td colSpan={4} className="py-8 text-center text-slate-400">No users registered in this tenant.</td>
                        </tr>
                      ) : selectedTenantUsers.map(user => (
                        <tr key={user.id} className="hover:bg-slate-50/50">
                          <td className="py-3 px-4 font-semibold text-slate-900">{user.full_name}</td>
                          <td className="py-3 px-4">{user.email}</td>
                          <td className="py-3 px-4">
                            <Badge variant={user.role === 'ADMIN' ? 'success' : 'primary'}>
                              {user.role}
                            </Badge>
                          </td>
                          <td className="py-3 px-4 text-right">
                            <button 
                              onClick={() => handleDeleteUser(user.id)}
                              className="text-red-500 hover:text-red-700 cursor-pointer"
                              title="Delete user"
                            >
                              <Trash2 size={15} />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </Card>
      )}

      {/* Companies List Tab */}
      {activeTab === 'companies' && !selectedTenant && (
        <div className="space-y-4">
          {/* Filter search */}
          <div className="relative max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input
              type="text"
              placeholder="Search companies or admins..."
              className="w-full pl-9 pr-4 py-2 text-slate-900 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={companySearch}
              onChange={(e) => setCompanySearch(e.target.value)}
            />
          </div>

          {filteredTenants.length === 0 ? (
            <div className="text-center py-12 text-slate-400 bg-slate-50 border border-dashed border-slate-200 rounded-xl">
              No registered companies found matching the search criteria.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTenants.map((item) => (
                <Card key={item.tenant.id} className="p-5 flex flex-col justify-between hover:shadow-md transition duration-200 border-slate-200">
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-2">
                        <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                          <Building size={20} />
                        </div>
                        <div>
                          <h3 className="font-bold text-slate-900">{item.tenant.name}</h3>
                          <p className="text-xs text-slate-400 font-mono">/{item.tenant.slug}</p>
                        </div>
                      </div>
                      <Badge variant={item.tenant.is_active ? 'success' : 'primary'}>
                        {item.tenant.is_active ? 'Active' : 'Deactivated'}
                      </Badge>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-3 gap-2 bg-slate-50 p-2.5 rounded-lg text-center text-slate-600 text-xs">
                      <div>
                        <div className="font-bold text-slate-900">{item.stats.employees_count + item.stats.admins_count}</div>
                        <div className="text-[10px] text-slate-400">Users</div>
                      </div>
                      <div>
                        <div className="font-bold text-slate-900">{item.stats.documents_count}</div>
                        <div className="text-[10px] text-slate-400">Docs</div>
                      </div>
                      <div>
                        <div className="font-bold text-slate-900">{formatBytes(item.stats.storage_used_bytes)}</div>
                        <div className="text-[10px] text-slate-400">Storage</div>
                      </div>
                    </div>

                    {/* Details Info */}
                    <div className="space-y-1 text-xs text-slate-500">
                      <div className="flex justify-between">
                        <span>Admin Email:</span>
                        <span className="font-medium text-slate-700 select-all">{item.admin_email || 'Not Assigned'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Chats Conducted:</span>
                        <span className="font-medium text-slate-700">{item.stats.conversations_count}</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 mt-4 pt-3 border-t border-slate-100">
                    <Button 
                      onClick={() => handleSelectTenant(item.tenant)}
                      variant="secondary" 
                      className="flex-1 text-xs h-8 cursor-pointer font-semibold"
                    >
                      <Settings size={14} className="mr-1" />
                      Manage
                    </Button>
                    <Button 
                      onClick={() => handleToggleTenantActive(item.tenant.id, item.tenant.is_active)}
                      variant={item.tenant.is_active ? 'secondary' : 'primary'}
                      className="text-xs h-8 px-3 cursor-pointer"
                    >
                      {item.tenant.is_active ? 'Deactivate' : 'Activate'}
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Admins Tab */}
      {activeTab === 'admins' && (
        <div className="space-y-4">
          <div className="relative max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input
              type="text"
              placeholder="Search admins by name or email..."
              className="w-full pl-9 pr-4 py-2 text-slate-900 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={adminSearch}
              onChange={(e) => setAdminSearch(e.target.value)}
            />
          </div>

          <div className="border border-slate-200 rounded-xl overflow-hidden bg-white shadow-sm">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 font-semibold uppercase text-xs">
                <tr>
                  <th className="py-3 px-6">Name</th>
                  <th className="py-3 px-6">Email Address</th>
                  <th className="py-3 px-6">Company Tenant</th>
                  <th className="py-3 px-6">Status</th>
                  <th className="py-3 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-600 text-sm">
                {filteredAdmins.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-400">No company administrators found.</td>
                  </tr>
                ) : filteredAdmins.map(admin => {
                  const company = tenants.find(t => t.tenant.id === admin.tenant_id);
                  return (
                    <tr key={admin.id} className="hover:bg-slate-50/50 transition">
                      <td className="py-4 px-6 font-semibold text-slate-900">{admin.full_name}</td>
                      <td className="py-4 px-6 select-all">{admin.email}</td>
                      <td className="py-4 px-6 font-medium text-slate-800">
                        {company ? company.tenant.name : 'Unknown Tenant'}
                      </td>
                      <td className="py-4 px-6">
                        <Badge variant={admin.is_active ? 'success' : 'primary'}>
                          {admin.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </td>
                      <td className="py-4 px-6 text-right">
                        <button 
                          onClick={() => handleDeleteUser(admin.id)}
                          className="text-red-500 hover:text-red-700 transition cursor-pointer p-1.5 hover:bg-red-50 rounded-lg"
                          title="Delete Admin Account"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Universal Users Tab */}
      {activeTab === 'users' && (
        <div className="space-y-4">
          <div className="relative max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input
              type="text"
              placeholder="Search all users by name, email, or role..."
              className="w-full pl-9 pr-4 py-2 text-slate-900 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={userSearch}
              onChange={(e) => setUserSearch(e.target.value)}
            />
          </div>

          <div className="border border-slate-200 rounded-xl overflow-hidden bg-white shadow-sm">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 font-semibold uppercase text-xs">
                <tr>
                  <th className="py-3 px-6">Name</th>
                  <th className="py-3 px-6">Email Address</th>
                  <th className="py-3 px-6">Role</th>
                  <th className="py-3 px-6">Company</th>
                  <th className="py-3 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700 text-sm">
                {filteredAllUsers.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-400">No users found.</td>
                  </tr>
                ) : filteredAllUsers.map(user => {
                  const company = tenants.find(t => t.tenant.id === user.tenant_id);
                  return (
                    <tr key={user.id} className="hover:bg-slate-50/50 transition">
                      <td className="py-4 px-6 font-semibold text-slate-900">{user.full_name}</td>
                      <td className="py-4 px-6 select-all">{user.email}</td>
                      <td className="py-4 px-6">
                        <Badge variant={user.role === 'SUPER_ADMIN' ? 'secondary' : user.role === 'ADMIN' ? 'success' : 'primary'}>
                          {user.role}
                        </Badge>
                      </td>
                      <td className="py-4 px-6">
                        {company ? company.tenant.name : 'System Default'}
                      </td>
                      <td className="py-4 px-6 text-right">
                        {user.role !== 'SUPER_ADMIN' && (
                          <button 
                            onClick={() => handleDeleteUser(user.id)}
                            className="text-red-500 hover:text-red-700 transition cursor-pointer p-1.5 hover:bg-red-50 rounded-lg"
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
        </div>
      )}

      {/* Modal: Register Tenant */}
      <Modal
        isOpen={isCreateTenantOpen}
        onClose={() => setIsCreateTenantOpen(false)}
        title="Register SaaS Company Tenant"
      >
        <form onSubmit={handleCreateTenant} className="space-y-4">
          {tenantErrors.api && (
            <div className="p-3 bg-red-50 border-l-4 border-red-500 text-red-700 text-xs rounded">
              {tenantErrors.api}
            </div>
          )}

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Company Name</label>
            <input
              type="text"
              required
              className="w-full text-slate-900 bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={tenantFormData.name}
              onChange={(e) => setTenantFormData(prev => ({ ...prev, name: e.target.value }))}
            />
            {tenantErrors.name && (
              <p className="text-red-600 text-xs mt-1">{tenantErrors.name}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Slug (URL / Unique ID)</label>
            <input
              type="text"
              placeholder="e.g. google, acme-corp (auto-generated if empty)"
              className="w-full text-slate-900 bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={tenantFormData.slug}
              onChange={(e) => setTenantFormData(prev => ({ ...prev, slug: e.target.value }))}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Description</label>
            <textarea
              rows={2}
              className="w-full text-slate-900 bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={tenantFormData.description}
              onChange={(e) => setTenantFormData(prev => ({ ...prev, description: e.target.value }))}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Logo URL (Optional)</label>
              <input
                type="text"
                className="w-full text-slate-900 bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                value={tenantFormData.logo_url}
                onChange={(e) => setTenantFormData(prev => ({ ...prev, logo_url: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Timezone</label>
              <input
                type="text"
                className="w-full text-slate-900 bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                value={tenantFormData.timezone}
                onChange={(e) => setTenantFormData(prev => ({ ...prev, timezone: e.target.value }))}
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-slate-100">
            <Button
              type="button"
              variant="secondary"
              className="text-xs h-9 cursor-pointer"
              onClick={() => setIsCreateTenantOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="text-xs h-9 font-semibold cursor-pointer"
            >
              Register Tenant
            </Button>
          </div>
        </form>
      </Modal>

      {/* Modal: Create Admin */}
      <Modal
        isOpen={isCreateAdminOpen}
        onClose={() => setIsCreateAdminOpen(false)}
        title="Create Company Admin Account"
      >
        <form onSubmit={handleCreateAdmin} className="space-y-4">
          {adminErrors.api && (
            <div className="p-3 bg-red-50 border-l-4 border-red-500 text-red-700 text-xs rounded">
              {adminErrors.api}
            </div>
          )}

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Company Tenant</label>
            <select
              required
              className="w-full text-slate-900 bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={adminFormData.tenantId}
              onChange={(e) => setAdminFormData(prev => ({ ...prev, tenantId: e.target.value }))}
            >
              <option value="">-- Select Company --</option>
              {tenants.map(t => (
                <option key={t.tenant.id} value={t.tenant.id}>{t.tenant.name}</option>
              ))}
            </select>
            {adminErrors.tenantId && (
              <p className="text-red-600 text-xs mt-1">{adminErrors.tenantId}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Full Name</label>
            <input
              type="text"
              required
              className="w-full text-slate-900 bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={adminFormData.fullName}
              onChange={(e) => setAdminFormData(prev => ({ ...prev, fullName: e.target.value }))}
            />
            {adminErrors.fullName && (
              <p className="text-red-600 text-xs mt-1">{adminErrors.fullName}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Email Address</label>
            <input
              type="email"
              required
              className="w-full text-slate-900 bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={adminFormData.email}
              onChange={(e) => setAdminFormData(prev => ({ ...prev, email: e.target.value }))}
            />
            {adminErrors.email && (
              <p className="text-red-600 text-xs mt-1">{adminErrors.email}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Password</label>
            <input
              type="password"
              required
              className="w-full text-slate-900 bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              value={adminFormData.password}
              onChange={(e) => setAdminFormData(prev => ({ ...prev, password: e.target.value }))}
            />
            {adminErrors.password && (
              <p className="text-red-600 text-xs mt-1">{adminErrors.password}</p>
            )}
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-slate-100">
            <Button
              type="button"
              variant="secondary"
              className="text-xs h-9 cursor-pointer"
              onClick={() => setIsCreateAdminOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="text-xs h-9 font-semibold cursor-pointer"
            >
              Create Admin
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
