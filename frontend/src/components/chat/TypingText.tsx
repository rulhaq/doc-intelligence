import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'

interface Props {
  text: string
  speed?: number // characters per second
  onComplete?: () => void
  isRTL?: boolean
}

export default function TypingText({ text, speed = 50, onComplete, isRTL = false }: Props) {
  const [displayedText, setDisplayedText] = useState('')
  const [isTyping, setIsTyping] = useState(true)

  useEffect(() => {
    if (!text) return

    let currentIndex = 0
    const chars = text.split('')
    setIsTyping(true)
    setDisplayedText('')

    const interval = setInterval(() => {
      if (currentIndex < chars.length) {
        setDisplayedText(prev => prev + chars[currentIndex])
        currentIndex++
      } else {
        clearInterval(interval)
        setIsTyping(false)
        onComplete?.()
      }
    }, 1000 / speed)

    return () => clearInterval(interval)
  }, [text, speed, onComplete])

  return (
    <div className="relative">
      <ReactMarkdown 
        className={`prose prose-sm max-w-none ${isRTL ? 'text-right' : 'text-left'}`}
        components={{
          p: ({node, ...props}) => <p className={isRTL ? 'text-right' : 'text-left'} {...props} />
        }}
      >
        {displayedText}
      </ReactMarkdown>
      {isTyping && (
        <span className="inline-block w-0.5 h-4 bg-current ml-0.5 animate-pulse" />
      )}
    </div>
  )
}

