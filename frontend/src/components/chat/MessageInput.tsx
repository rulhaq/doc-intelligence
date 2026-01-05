import { useState } from 'react'
import { PaperAirplaneIcon } from '@heroicons/react/24/solid'

interface Props {
  onSend: (text: string) => void
  disabled?: boolean
}

export default function MessageInput({ onSend, disabled }: Props) {
  const [text, setText] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (text.trim() && !disabled) {
      onSend(text.trim())
      setText('')
    }
  }

  return (
    <div className="border-t border-gray-200 p-4 bg-white">
      <form onSubmit={handleSubmit} className="flex space-x-4">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Ask a question about your documents..."
          disabled={disabled}
          className="input flex-1"
        />
        <button
          type="submit"
          disabled={disabled || !text.trim()}
          className="btn btn-primary px-4 py-2 flex items-center space-x-2"
        >
          <PaperAirplaneIcon className="w-5 h-5" />
          <span>Send</span>
        </button>
      </form>
    </div>
  )
}

