import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useChatStore } from '../../store/chatStore'
import { useAuthStore } from '../../store/authStore'
import { conversationService } from '../../services/conversationService'
import { PlusIcon, ChatBubbleLeftIcon, TrashIcon } from '@heroicons/react/24/outline'
import AnimatedCard from '../common/AnimatedCard'
import toast from 'react-hot-toast'

export default function Sidebar() {
  const navigate = useNavigate()
  const { conversations, setConversations, currentConversation, setCurrentConversation } = useChatStore()
  const { user } = useAuthStore()
  const [isCreating, setIsCreating] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const isAdmin = user?.role === 'ADMIN'

  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const convs = await conversationService.getConversations()
      setConversations(convs)
    } catch (error) {
      toast.error('Failed to load conversations')
    }
  }

  const handleNewConversation = async () => {
    setIsCreating(true)
    try {
      const conv = await conversationService.createConversation({
        title: 'New Conversation',
      })
      await loadConversations()
      navigate(`/conversations/${conv.id}`)
      toast.success('New chat created! 💬')
    } catch (error) {
      toast.error('Failed to create conversation')
    } finally {
      setIsCreating(false)
    }
  }

  const handleDeleteConversation = async (e: React.MouseEvent, conversationId: string) => {
    e.preventDefault()
    e.stopPropagation()

    if (!isAdmin) {
      toast.error('Only admins can delete conversations')
      return
    }

    if (!window.confirm('Are you sure you want to delete this conversation? This action cannot be undone.')) {
      return
    }

    setDeletingId(conversationId)
    try {
      await conversationService.deleteConversation(conversationId)
      
      // If we're deleting the current conversation, navigate to home
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null)
        navigate('/')
      }
      
      await loadConversations()
      toast.success('Chat deleted successfully')
    } catch (error) {
      toast.error('Failed to delete conversation')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="w-72 bg-gradient-to-b from-gray-50 to-white border-r border-gray-200 flex flex-col shadow-lg">
      {/* Logo Header */}
      <div className="p-4 border-b border-gray-200 bg-white animate-fadeIn">
        
        <button
          onClick={handleNewConversation}
          disabled={isCreating}
          className="btn btn-primary w-full flex items-center justify-center space-x-2 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 animate-slideInLeft"
          style={{ animationDelay: '100ms' }}
        >
          {isCreating ? (
            <>
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Creating...</span>
            </>
          ) : (
            <>
              <PlusIcon className="w-5 h-5" />
              <span>New Chat</span>
            </>
          )}
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-2">
        {conversations.length === 0 ? (
          <div className="text-center py-12 text-gray-400 animate-fadeIn">
            <ChatBubbleLeftIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs mt-1">Start a new chat to begin!</p>
          </div>
        ) : (
          conversations.map((conv, index) => (
            <AnimatedCard
              key={conv.id}
              hover={true}
              delay={index * 50}
              className="p-0 overflow-hidden"
            >
              <div className="relative group">
                <Link
                  to={`/conversations/${conv.id}`}
                  className={`block p-4 transition-all duration-200 ${
                    currentConversation?.id === conv.id
                      ? 'bg-gradient-to-r from-primary-50 to-blue-50 border-l-4 border-primary-500'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${
                      currentConversation?.id === conv.id
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 text-gray-400'
                    }`}>
                      <ChatBubbleLeftIcon className="w-5 h-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium truncate ${
                        currentConversation?.id === conv.id ? 'text-primary-900' : 'text-gray-900'
                      }`}>
                        {conv.title}
                      </p>
                      <div className="flex items-center justify-between mt-1">
                        <p className="text-xs text-gray-500">
                          {new Date(conv.updated_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                </Link>
                
                {/* Delete button - admin only */}
                {isAdmin && (
                  <button
                    onClick={(e) => handleDeleteConversation(e, conv.id)}
                    disabled={deletingId === conv.id}
                    className="absolute top-2 right-2 p-2 rounded-lg bg-white shadow-md opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-50 hover:text-red-600 disabled:opacity-50"
                    title="Delete conversation (Admin only)"
                  >
                    {deletingId === conv.id ? (
                      <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    ) : (
                      <TrashIcon className="w-4 h-4" />
                    )}
                  </button>
                )}
              </div>
            </AnimatedCard>
          ))
        )}
      </div>

      {/* Footer Stats */}
      <div className="p-4 border-t border-gray-200 bg-white animate-fadeIn" style={{ animationDelay: '300ms' }}>
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3.293 1.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L7.586 10 5.293 7.707a1 1 0 010-1.414zM11 12a1 1 0 100 2h3a1 1 0 100-2h-3z" />
            </svg>
            {conversations.length} conversations
          </span>
          <span className="text-primary-600 font-medium">v1.0.0</span>
        </div>
      </div>
    </div>
  )
}
