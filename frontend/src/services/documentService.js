import api from '../api/axios';

const documentService = {
  /**
   * Get all documents for the current tenant.
   * @returns {Promise<Array<{id: string, original_filename: string, status: string, uploaded_at: string, chunk_count: number}>>}
   */
  getDocuments: async () => {
    const response = await api.get('/documents');
    return response.data;
  },

  /**
   * Upload a PDF file with progress tracking.
   * @param {File} file 
   * @param {function(number): void} onProgress 
   * @returns {Promise<{document_id: string, message: string}>}
   */
  uploadDocument: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });
    return response.data;
  },

  /**
   * Delete a document by its ID.
   * @param {string} documentId 
   * @returns {Promise<void>}
   */
  deleteDocument: async (documentId) => {
    await api.delete(`/documents/${documentId}`);
  },
};

export default documentService;
