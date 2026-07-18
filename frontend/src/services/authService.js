import api from '../api/axios';

const authService = {
  /**
   * Log in user using OAuth2 username/password form data.
   * Matches username (email) and password.
   * @param {string} email 
   * @param {string} password 
   * @returns {Promise<{access_token: string, token_type: string}>}
   */
  login: async (email, password) => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);

    const response = await api.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  /**
   * Register a new user under the default tenant ID from the environment.
   * @param {string} fullName 
   * @param {string} email 
   * @param {string} password 
   * @returns {Promise<{id: string, email: string, full_name: string, tenant_id: string}>}
   */
  register: async (fullName, email, password) => {
    const tenantId = import.meta.env.VITE_DEFAULT_TENANT_ID;
    if (!tenantId) {
      throw new Error('VITE_DEFAULT_TENANT_ID is not configured in the environment.');
    }

    const payload = {
      full_name: fullName,
      email: email,
      password: password,
      tenant_id: tenantId,
    };

    const response = await api.post('/auth/register', payload);
    return response.data;
  },

  /**
   * Retrieve currently authenticated user's profile info.
   * @returns {Promise<{id: string, email: string, full_name: string, role: string, tenant_id: string, is_active: boolean}>}
   */
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export default authService;
