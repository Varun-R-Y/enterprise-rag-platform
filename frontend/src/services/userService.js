import api from '../api/axios';

const userService = {
  /**
   * Admin-only endpoint to create employee accounts for their tenant.
   * @param {string} fullName 
   * @param {string} email 
   * @param {string} password 
   * @returns {Promise<{id: string, email: string, full_name: string, role: string, tenant_id: string, is_active: boolean, created_by: string}>}
   */
  createEmployee: async (fullName, email, password) => {
    const payload = {
      full_name: fullName,
      email: email,
      password: password,
    };
    const response = await api.post('/users', payload);
    return response.data;
  },

  /**
   * Admin-only endpoint to list all users of their tenant.
   * @returns {Promise<Array<{id: string, email: string, full_name: string, role: string, tenant_id: string, is_active: boolean, created_by: string}>>}
   */
  listUsers: async () => {
    const response = await api.get('/users');
    return response.data;
  },

  /**
   * Admin-only endpoint to delete a user.
   * @param {string} userId 
   */
  deleteUser: async (userId) => {
    const response = await api.delete(`/users/${userId}`);
    return response.data;
  },

  /**
   * Super-admin-only endpoint to create a Company Admin account.
   * @param {string} fullName 
   * @param {string} email 
   * @param {string} password 
   * @param {string} tenantId 
   * @returns {Promise<any>}
   */
  createCompanyAdmin: async (fullName, email, password, tenantId) => {
    const payload = {
      full_name: fullName,
      email: email,
      password: password,
      tenant_id: tenantId,
    };
    const response = await api.post('/users/company-admin', payload);
    return response.data;
  },
};

export default userService;
