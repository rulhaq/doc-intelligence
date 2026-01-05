import { useState, useEffect } from 'react'
import { SparklesIcon, DocumentTextIcon, QuestionMarkCircleIcon, LightBulbIcon } from '@heroicons/react/24/outline'

interface Props {
  onSelectQuestion: (question: string) => void
  hasDocuments?: boolean
}

export default function SuggestedQuestions({ onSelectQuestion, hasDocuments }: Props) {
  const [questions, setQuestions] = useState<{ text: string; icon: any; color: string }[]>([])

  useEffect(() => {
    // Generate contextual questions based on whether documents are uploaded
    if (hasDocuments) {
      setQuestions([
        {
          text: 'What are the main topics in these documents?',
          icon: DocumentTextIcon,
          color: 'from-blue-500 to-blue-600'
        },
        {
          text: 'Can you summarize the key points?',
          icon: SparklesIcon,
          color: 'from-purple-500 to-purple-600'
        },
        {
          text: 'What specific details are mentioned about...?',
          icon: QuestionMarkCircleIcon,
          color: 'from-green-500 to-green-600'
        },
        {
          text: 'Compare the information across documents',
          icon: LightBulbIcon,
          color: 'from-orange-500 to-orange-600'
        },
      ])
    } else {
      setQuestions([
        {
          text: 'How does this system work?',
          icon: QuestionMarkCircleIcon,
          color: 'from-blue-500 to-blue-600'
        },
        {
          text: 'What can you help me with?',
          icon: SparklesIcon,
          color: 'from-purple-500 to-purple-600'
        },
        {
          text: 'Tell me about the features available',
          icon: LightBulbIcon,
          color: 'from-green-500 to-green-600'
        },
      ])
    }
  }, [hasDocuments])

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <SparklesIcon className="w-5 h-5 text-primary-600" />
        <h3 className="text-sm font-semibold text-gray-900">
          {hasDocuments ? 'Ask about your documents' : 'Suggested questions'}
        </h3>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {questions.map((q, index) => (
          <button
            key={index}
            onClick={() => onSelectQuestion(q.text)}
            className="group relative overflow-hidden rounded-lg p-4 text-left transition-all duration-300 hover:scale-105 hover:shadow-lg"
          >
            {/* Gradient background */}
            <div className={`absolute inset-0 bg-gradient-to-br ${q.color} opacity-10 group-hover:opacity-20 transition-opacity`} />
            
            {/* Content */}
            <div className="relative flex items-start gap-3">
              <q.icon className={`w-5 h-5 text-transparent bg-gradient-to-br ${q.color} bg-clip-text flex-shrink-0 mt-0.5`} />
              <span className="text-sm text-gray-700 group-hover:text-gray-900 transition-colors">
                {q.text}
              </span>
            </div>

            {/* Hover effect */}
            <div className="absolute inset-0 border-2 border-transparent group-hover:border-primary-200 rounded-lg transition-colors" />
          </button>
        ))}
      </div>

      {hasDocuments && (
        <div className="mt-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start gap-2">
            <LightBulbIcon className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-blue-800">
              <span className="font-semibold">Pro tip:</span> Ask specific questions about names, dates, or topics mentioned in your documents for best results.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

