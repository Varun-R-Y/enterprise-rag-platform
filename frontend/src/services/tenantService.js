import api from '../api/axios';

const tenantService = {
  listTenants: async () => {
    const response = await api.get('/tenants');
    return response.data;
  },

  getTenantDetails: async (id) => {
    const response = await api.get(`/tenants/${id}`);
    return response.data;
  },

  createTenant: async (tenantData) => {
    const response = await api.post('/tenants', tenantData);
    return response.data;
  },

  updateTenant: async (id, tenantData) => {
    const response = await api.patch(`/tenants/${id}`, tenantData);
    return response.data;
  },

  updateMyCompanySettings: async (settingsData) => {
    const response = await api.patch('/tenants/my-company/settings', settingsData);
    return response.data;
  },

  getMyCompanySettings: async () => {
    const response = await api.get('/tenants/my-company/settings');
    return response.data;
  }
};

export default tenantService;
