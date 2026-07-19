import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import tenantService from '../../services/tenantService';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Alert from '../../components/ui/Alert';
import Spinner from '../../components/ui/Spinner';
import { Building, Settings, MapPin, Globe } from 'lucide-react';

export default function CompanySettings() {
  const { currentUser, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!authLoading && currentUser && currentUser.role !== 'ADMIN') {
      navigate('/dashboard');
    }
  }, [currentUser, authLoading, navigate]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [alert, setAlert] = useState(null);
  
  const [companyDetails, setCompanyDetails] = useState({
    name: '',
    slug: '',
    description: '',
    logo_url: '',
    timezone: 'UTC'
  });

  useEffect(() => {
    fetchCompanySettings();
  }, []);

  const fetchCompanySettings = async () => {
    setLoading(true);
    try {
      const data = await tenantService.getMyCompanySettings();
      setCompanyDetails({
        name: data.name,
        slug: data.slug,
        description: data.description || '',
        logo_url: data.logo_url || '',
        timezone: data.timezone || 'UTC'
      });
    } catch (err) {
      setAlert({ type: 'error', message: 'Failed to retrieve company settings.' });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await tenantService.updateMyCompanySettings({
        description: companyDetails.description,
        logo_url: companyDetails.logo_url,
        timezone: companyDetails.timezone
      });
      setAlert({ type: 'success', message: 'Company settings successfully updated.' });
    } catch (err) {
      setAlert({ type: 'error', message: err.response?.data?.detail || 'Failed to update settings.' });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <Spinner size="lg" className="text-indigo-600" />
        <p className="text-slate-500 text-sm mt-3 font-medium">Retrieving company configuration...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">Company Settings</h1>
        <p className="text-slate-500 text-sm mt-1 leading-relaxed">
          Configure organization settings, descriptions, corporate brand assets, and local timezone properties.
        </p>
      </div>

      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
        />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Side: General Profile Card */}
        <div className="lg:col-span-1">
          <Card className="text-center p-5 space-y-4">
            <div className="mx-auto w-16 h-16 bg-slate-50 border border-slate-100 rounded-2xl flex items-center justify-center text-indigo-600 shadow-xs">
              {companyDetails.logo_url ? (
                <img 
                  src={companyDetails.logo_url} 
                  alt="Company Logo" 
                  className="w-12 h-12 object-contain"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
              ) : null}
              <Building size={32} style={{ display: companyDetails.logo_url ? 'none' : 'block' }} />
            </div>

            <div>
              <h3 className="font-bold text-slate-900 text-base">{companyDetails.name}</h3>
              <p className="text-xs text-slate-400 font-mono">/{companyDetails.slug}</p>
            </div>

            <div className="pt-3 border-t border-slate-100 flex flex-col gap-2 text-xs text-slate-500 text-left">
              <div className="flex items-center gap-2">
                <Globe size={14} className="text-slate-400" />
                <span>Slug: <span className="font-mono text-slate-700 font-medium">/{companyDetails.slug}</span></span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin size={14} className="text-slate-400" />
                <span>Timezone: <span className="text-slate-700 font-medium">{companyDetails.timezone}</span></span>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Side: Edit Form */}
        <div className="lg:col-span-2">
          <Card className="p-6">
            <h2 className="text-base font-bold text-slate-900 pb-3 border-b border-slate-100 mb-4 flex items-center gap-2">
              <Settings size={18} className="text-indigo-500" />
              Settings Configuration
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">Company Description</label>
                <textarea
                  rows={4}
                  className="w-full text-slate-900 bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Provide details about your organization..."
                  value={companyDetails.description}
                  onChange={(e) => setCompanyDetails(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Logo Image URL</label>
                  <input
                    type="text"
                    className="w-full text-slate-900 bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="https://example.com/logo.png"
                    value={companyDetails.logo_url}
                    onChange={(e) => setCompanyDetails(prev => ({ ...prev, logo_url: e.target.value }))}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Timezone</label>
                  <input
                    type="text"
                    className="w-full text-slate-900 bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="e.g. UTC, PST, Europe/London"
                    value={companyDetails.timezone}
                    onChange={(e) => setCompanyDetails(prev => ({ ...prev, timezone: e.target.value }))}
                  />
                </div>
              </div>

              <div className="flex justify-end pt-3 border-t border-slate-100">
                <Button
                  type="submit"
                  variant="primary"
                  disabled={submitting}
                  className="text-xs h-9 font-semibold px-4 cursor-pointer"
                >
                  {submitting ? 'Saving Changes...' : 'Save Settings'}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
}
