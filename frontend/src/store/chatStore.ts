import { create } from 'zustand'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  text: string
  cards?: Card[]
  created_at: string
}

interface Card {
  type: string
  doc_id?: string
  title?: string
  snippet?: string
  score?: number
  metadata?: any
}

interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
}

interface ChatState {
  conversations: Conversation[]
  currentConversation: Conversation | null
  messages: Message[]
  isStreaming: boolean
  setConversations: (conversations: Conversation[]) => void
  setCurrentConversation: (conversation: Conversation | null) => void
  setMessages: (messages: Message[]) => void
  addMessage: (message: Message) => void
  updateLastMessage: (text: string) => void
  setIsStreaming: (isStreaming: boolean) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  conversations: [],
  currentConversation: null,
  messages: [],
  isStreaming: false,

  setConversations: (conversations) => set({ conversations }),
  
  setCurrentConversation: (conversation) => set({ currentConversation: conversation }),
  
  setMessages: (messages) => set({ messages }),
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message],
  })),
  
  updateLastMessage: (text) => set((state) => {
    const messages = [...state.messages]
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1]
      messages[messages.length - 1] = {
        ...lastMessage,
        text: lastMessage.text + text,
      }
    }
    return { messages }
  }),
  
  setIsStreaming: (isStreaming) => set({ isStreaming }),
  
  clearMessages: () => set({ messages: [] }),
}))

