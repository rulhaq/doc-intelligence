import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import TypingText from './TypingText'

interface DocumentSource {
  document_id: string
  document_title: string
  chunk_id?: string
  page_number?: number
  similarity?: number
}

interface Message {
  id: string
  role: string
  text: string
  cards?: any[]
  sources?: DocumentSource[]
  created_at: string
}

interface Props {
  messages: Message[]
  isLoading: boolean
}

export default function MessageList({ messages, isLoading }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({})
  const [lastAssistantMessageId, setLastAssistantMessageId] = useState<string | null>(null)
  const [typingComplete, setTypingComplete] = useState<Record<string, boolean>>({})

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Track the last assistant message for typing animation
  useEffect(() => {
    const lastMessage = messages[messages.length - 1]
    if (lastMessage && lastMessage.role === 'assistant' && lastMessage.id !== lastAssistantMessageId) {
      setLastAssistantMessageId(lastMessage.id)
      setTypingComplete(prev => ({ ...prev, [lastMessage.id]: false }))
    }
  }, [messages, lastAssistantMessageId])

  const toggleSources = (messageId: string) => {
    setExpandedSources(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }))
  }

  const handleOpenDocument = async (documentId: string) => {
    // Open document in admin panel
    window.open(`/admin?document=${documentId}`, '_blank')
  }

  // Detect if text contains RTL characters (Arabic, Hebrew, etc.)
  const isRTL = (text: string) => /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/.test(text)

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {messages.map((message) => {
        const messageIsRTL = isRTL(message.text)
        
        return (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className="max-w-3xl w-full">
              <div
                className={`rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
                dir={messageIsRTL ? 'rtl' : 'ltr'}
              >
                {message.role === 'assistant' ? (
                  message.id === lastAssistantMessageId && !typingComplete[message.id] ? (
                    <TypingText
                      text={message.text}
                      speed={50}
                      isRTL={messageIsRTL}
                      onComplete={() => setTypingComplete(prev => ({ ...prev, [message.id]: true }))}
                    />
                  ) : (
                    <ReactMarkdown 
                      className={`prose prose-sm max-w-none ${messageIsRTL ? 'text-right' : 'text-left'}`}
                      components={{
                        p: ({node, ...props}) => <p className={messageIsRTL ? 'text-right' : 'text-left'} {...props} />
                      }}
                    >
                      {message.text}
                    </ReactMarkdown>
                  )
                ) : (
                  <p className={`text-sm ${messageIsRTL ? 'text-right' : 'text-left'}`}>
                    {message.text}
                  </p>
                )}
              </div>

              {/* Document Sources */}
              {message.sources && message.sources.length > 0 && message.role === 'assistant' && (
                <div className="mt-2 ml-2">
                  <button
                    onClick={() => toggleSources(message.id)}
                    className="flex items-center gap-1 text-xs text-gray-600 hover:text-gray-900"
                  >
                    <svg 
                      className={`w-3 h-3 transition-transform ${expandedSources[message.id] ? 'rotate-90' : ''}`} 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                    <span>
                      {message.sources.length} source{message.sources.length > 1 ? 's' : ''}
                    </span>
                  </button>

                  {expandedSources[message.id] && (
                    <div className="mt-2 space-y-1">
                      {message.sources.map((source, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded border border-gray-200 text-xs"
                        >
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-gray-900 truncate">
                              {source.document_title}
                            </div>
                            <div className="text-gray-500 flex items-center gap-2 mt-0.5">
                              {source.page_number && (
                                <span>Page {source.page_number}</span>
                              )}
                              {source.similarity && (
                                <span className="text-green-600">
                                  {(source.similarity * 100).toFixed(0)}% match
                                </span>
                              )}
                            </div>
                          </div>
                          <button
                            onClick={() => handleOpenDocument(source.document_id)}
                            className="ml-2 px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 whitespace-nowrap"
                          >
                            View Doc
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )
      })}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-100 rounded-lg px-4 py-3">
            <div className="flex space-x-2">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  )
}
