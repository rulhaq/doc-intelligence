import api from '../lib/api'

interface SearchRequest {
  query: string
  limit?: number
  score_threshold?: number
  filters?: any
}

interface SearchResult {
  doc_id: string
  chunk_id: string
  score: number
  text: string
  page?: number
  source?: string
  metadata?: any
}

interface SearchResponse {
  query: string
  results: SearchResult[]
  total: number
  search_time_ms: number
}

export const searchService = {
  async search(data: SearchRequest): Promise<SearchResponse> {
    const response = await api.post('/search', data)
    return response.data
  },
}

