import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useChatStore } from '../store/chatStore'
import { conversationService } from '../services/conversationService'
import { documentService } from '../services/documentService'
import toast from 'react-hot-toast'
import MessageList from '../components/chat/MessageList'
import MessageInput from '../components/chat/MessageInput'
import CardsPanel from '../components/chat/CardsPanel'

export default function ChatPage() {
  const { id } = useParams()
  const { currentConversation, messages, setCurrentConversation, setMessages, addMessage } = useChatStore()
  const [isLoading, setIsLoading] = useState(false)
  const [selectedCard, setSelectedCard] = useState<any>(null)
  const [hasDocuments, setHasDocuments] = useState(false)

  useEffect(() => {
    if (id) {
      loadConversation(id)
    }
    checkForDocuments()
  }, [id])

  const checkForDocuments = async () => {
    try {
      const docs = await documentService.getDocuments(1, 1)
      setHasDocuments(docs.total > 0)
    } catch (error) {
      console.error('Failed to check documents:', error)
    }
  }

  const loadConversation = async (conversationId: string) => {
    try {
      const conversation = await conversationService.getConversation(conversationId)
      setCurrentConversation(conversation)
      setMessages(conversation.messages as any)
    } catch (error) {
      toast.error('Failed to load conversation')
    }
  }

  const handleSendMessage = async (text: string) => {
    if (!currentConversation) {
      // Create new conversation
      try {
        const newConv = await conversationService.createConversation({
          title: text.slice(0, 50),
        })
        setCurrentConversation(newConv)
        
        // Send message
        await sendMessage(newConv.id, text)
      } catch (error) {
        toast.error('Failed to create conversation')
      }
    } else {
      await sendMessage(currentConversation.id, text)
    }
  }

  const sendMessage = async (conversationId: string, text: string) => {
    setIsLoading(true)
    
    // Add user message optimistically
    addMessage({
      id: Date.now().toString(),
      role: 'user',
      text,
      created_at: new Date().toISOString(),
    } as any)

    try {
      const response = await conversationService.sendMessage(conversationId, {
        role: 'user',
        text,
      })
      
      // Add assistant response
      addMessage(response as any)
    } catch (error) {
      toast.error('Failed to send message')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectQuestion = (question: string) => {
    handleSendMessage(question)
  }

  return (
    <div className="flex h-full">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        <MessageList messages={messages} isLoading={isLoading} />
        <MessageInput onSend={handleSendMessage} disabled={isLoading} />
      </div>

      {/* Cards panel - always show */}
      <CardsPanel
        messages={messages}
        selectedCard={selectedCard}
        onSelectCard={setSelectedCard}
        onSelectQuestion={handleSelectQuestion}
        hasDocuments={hasDocuments}
      />
    </div>
  )
}

