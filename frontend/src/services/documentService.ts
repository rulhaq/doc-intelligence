import api from '../lib/api'

interface Document {
  id: string
  filename: string
  original_filename: string
  file_size: number
  mime_type: string
  status: string
  title?: string
  source?: string
  tags?: string[]
  total_pages?: number
  created_at: string
  updated_at: string
}

interface DocumentUploadResponse {
  document_id: string
  filename: string
  file_size: number
  status: string
}

interface PagePreview {
  page_number: number
  image_url: string
  ocr_text?: string
  ocr_blocks?: any[]
  ocr_confidence?: number
  corrected_text?: string
  corrections?: any[]
  edited_text?: string
  is_edited: boolean
}

interface DocumentPreview {
  document_id: string
  filename: string
  total_pages: number
  status: string
  pages: PagePreview[]
}

export const documentService = {
  async uploadDocument(file: File): Promise<DocumentUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/admin/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async processOCR(documentId: string): Promise<void> {
    await api.post(`/admin/documents/${documentId}/process-ocr`)
  },

  async getDocumentPreview(documentId: string): Promise<DocumentPreview> {
    const response = await api.get(`/admin/documents/${documentId}/preview`)
    return response.data
  },

  async updateDocumentPreview(documentId: string, edits: any[]): Promise<void> {
    await api.put(`/admin/documents/${documentId}/preview`, edits)
  },

  async commitDocument(documentId: string): Promise<void> {
    await api.post(`/admin/documents/${documentId}/commit`)
  },

  async getDocumentStatus(documentId: string): Promise<any> {
    const response = await api.get(`/admin/documents/${documentId}/status`)
    return response.data
  },

  async getDocuments(page: number = 1, pageSize: number = 50): Promise<{
    documents: Document[]
    total: number
    page: number
    page_size: number
  }> {
    const response = await api.get('/admin/documents', {
      params: { page, page_size: pageSize },
    })
    return response.data
  },

  async deleteDocument(documentId: string): Promise<void> {
    await api.delete(`/admin/documents/${documentId}`)
  },
}

