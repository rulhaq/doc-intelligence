import { ReactNode } from 'react'

interface AnimatedCardProps {
  children: ReactNode
  className?: string
  hover?: boolean
  delay?: number
}

export default function AnimatedCard({ 
  children, 
  className = '', 
  hover = true,
  delay = 0 
}: AnimatedCardProps) {
  return (
    <div 
      className={`
        bg-white rounded-xl shadow-md border border-gray-200
        transform transition-all duration-300 ease-in-out
        animate-fadeIn
        ${hover ? 'hover:shadow-xl hover:-translate-y-1 hover:border-primary-300' : ''}
        ${className}
      `}
      style={{ animationDelay: `${delay}ms` }}
    >
      {children}
    </div>
  )
}

