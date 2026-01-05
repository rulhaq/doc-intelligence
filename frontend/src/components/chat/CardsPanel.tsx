import { DocumentTextIcon } from '@heroicons/react/24/outline'
import SuggestedQuestions from './SuggestedQuestions'

interface Props {
  messages: any[]
  selectedCard: any
  onSelectCard: (card: any) => void
  onSelectQuestion: (question: string) => void
  hasDocuments?: boolean
}

export default function CardsPanel({ messages, selectedCard, onSelectCard, onSelectQuestion, hasDocuments }: Props) {
  // Collect all cards from messages
  const allCards = messages.flatMap(m => m.cards || [])

  return (
    <div className="w-96 border-l border-gray-200 overflow-y-auto bg-gray-50">
      {/* Suggested Questions Section */}
      {messages.length === 0 && (
        <div className="border-b border-gray-200 bg-white">
          <SuggestedQuestions onSelectQuestion={onSelectQuestion} hasDocuments={hasDocuments} />
        </div>
      )}

      {/* Source Documents Section */}
      {allCards.length > 0 && (
        <div className="p-4 bg-white border-b border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <DocumentTextIcon className="w-5 h-5 text-gray-600" />
            <h3 className="text-sm font-semibold text-gray-900">Source Documents</h3>
          </div>
          <div className="space-y-3">
            {allCards.map((card, index) => (
              <div
                key={index}
                onClick={() => onSelectCard(card)}
                className={`card cursor-pointer hover:shadow-md transition-shadow bg-white ${
                  selectedCard === card ? 'ring-2 ring-primary-500' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-sm font-medium text-gray-900">
                    {card.title || 'Document'}
                  </h4>
                  {card.score && (
                    <span className="text-xs text-green-600 font-semibold">
                      {(card.score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                
                {card.snippet && (
                  <p className="text-xs text-gray-600 line-clamp-3">
                    {card.snippet}
                  </p>
                )}

                {card.metadata?.source && (
                  <div className="mt-2 text-xs text-gray-400">
                    Source: {card.metadata.source}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Tips */}
      {messages.length > 0 && (
        <div className="p-4">
          <SuggestedQuestions onSelectQuestion={onSelectQuestion} hasDocuments={hasDocuments} />
        </div>
      )}
    </div>
  )
}

