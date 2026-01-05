import api from '../lib/api'

interface Conversation {
  id: string
  user_id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

interface Message {
  id: string
  conversation_id: string
  role: string
  text: string
  cards?: any[]
  sources?: any[]
  tokens_used?: number
  inference_time_ms?: number
  created_at: string
}

interface CreateConversationRequest {
  title: string
}

interface SendMessageRequest {
  role: string
  text: string
  context_filters?: any
}

export const conversationService = {
  async getConversations(): Promise<Conversation[]> {
    const response = await api.get('/conversations')
    return response.data
  },

  async getConversation(id: string): Promise<Conversation & { messages: Message[] }> {
    const response = await api.get(`/conversations/${id}`)
    return response.data
  },

  async createConversation(data: CreateConversationRequest): Promise<Conversation> {
    const response = await api.post('/conversations', data)
    return response.data
  },

  async sendMessage(conversationId: string, data: SendMessageRequest): Promise<Message> {
    const response = await api.post(`/conversations/${conversationId}/message`, data)
    return response.data
  },

  async deleteConversation(id: string): Promise<void> {
    await api.delete(`/conversations/${id}`)
  },
}

