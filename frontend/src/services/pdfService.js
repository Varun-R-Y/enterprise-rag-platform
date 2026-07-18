import api from '../api/axios';

const pdfService = {
  /**
   * Retrieves the original uploaded PDF as a Blob.
   * @param {string} documentId 
   * @returns {Promise<Blob>}
   */
  getDocumentFile: async (documentId) => {
    const response = await api.get(`/documents/${documentId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  }
};

export default pdfService;
