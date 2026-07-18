import api from '../api/axios';

const chatService = {
  /**
   * Submit a question to the Chat assistant.
   * @param {string} question 
   * @param {string} [conversationId=null]
   * @param {number} [topK=5]
   * @returns {Promise<{answer: string, sources: Array<{document: string, page: number, score: number}>}>}
   */
  askQuestion: async (question, conversationId = null, topK = 5) => {
    const payload = {
      question,
      top_k: topK,
      conversation_id: conversationId,
    };
    const response = await api.post('/chat', payload);
    return response.data;
  },
};

export default chatService;
