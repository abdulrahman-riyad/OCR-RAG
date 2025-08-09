import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
})

// Upload functions
export const uploadFiles = async (files: File[]) => {
  const formData = new FormData()
  files.forEach(file => {
    formData.append('files', file)
  })
  
  const response = await apiClient.post('/api/v1/upload/batch', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data.results
}

// Process functions
export const processDocument = async (documentId: string) => {
  const response = await apiClient.post(`/api/v1/process/${documentId}`)
  return response.data
}

export const getProcessingStatus = async (documentId: string) => {
  const response = await apiClient.get(`/api/v1/process/${documentId}/status`)
  return response.data
}

// Document functions
export const getDocuments = async () => {
  const response = await apiClient.get('/api/v1/documents')
  return response.data
}

export const getDocument = async (documentId: string) => {
  const response = await apiClient.get(`/api/v1/documents/${documentId}`)
  return response.data
}

export const deleteDocument = async (documentId: string) => {
  const response = await apiClient.delete(`/api/v1/documents/${documentId}`)
  return response.data
}

// Search functions
export const searchDocuments = async (query: string) => {
  const response = await apiClient.post('/api/v1/search', {
    query,
    limit: 20,
  })
  return response.data
}

export const getSearchSuggestions = async (query: string) => {
  const response = await apiClient.get('/api/v1/search/suggestions', {
    params: { q: query }
  })
  return response.data.suggestions
}

// Chat functions (for future use)
export const sendChatMessage = async (message: string, documentId?: string) => {
  const response = await apiClient.post('/api/v1/chat', {
    message,
    document_id: documentId
  })
  return response.data
}