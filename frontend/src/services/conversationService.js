import api from '../api/axios';

const conversationService = {
  /**
   * Get paginated conversations list.
   * @param {number} [page=1] 
   * @param {number} [limit=20] 
   * @returns {Promise<Array<{id: string, title: string, created_at: string, updated_at: string, message_count: number}>>}
   */
  getConversations: async (page = 1, limit = 20) => {
    const response = await api.get('/conversations', {
      params: { page, limit },
    });
    return response.data;
  },

  /**
   * Create a new conversation session.
   * @param {string} [title="New Chat"] 
   * @returns {Promise<{id: string, title: string, created_at: string, updated_at: string, message_count: number}>}
   */
  createConversation: async (title = 'New Chat') => {
    const response = await api.post('/conversations', { title });
    return response.data;
  },

  /**
   * Get metadata for a specific conversation.
   * @param {string} id 
   * @returns {Promise<{id: string, title: string, created_at: string, updated_at: string, message_count: number}>}
   */
  getConversation: async (id) => {
    const response = await api.get(`/conversations/${id}`);
    return response.data;
  },

  /**
   * Rename a conversation title.
   * @param {string} id 
   * @param {string} title 
   * @returns {Promise<{id: string, title: string, created_at: string, updated_at: string, message_count: number}>}
   */
  updateConversation: async (id, title) => {
    const response = await api.patch(`/conversations/${id}`, { title });
    return response.data;
  },

  /**
   * Delete a conversation and all associated messages.
   * @param {string} id 
   * @returns {Promise<void>}
   */
  deleteConversation: async (id) => {
    await api.delete(`/conversations/${id}`);
  },

  /**
   * Get all messages for a specific conversation, ordered ASC.
   * @param {string} id 
   * @returns {Promise<Array<{id: string, role: string, content: string, citations: any, created_at: string}>>}
   */
  getConversationMessages: async (id) => {
    const response = await api.get(`/conversations/${id}/messages`);
    return response.data;
  },
};

export default conversationService;
