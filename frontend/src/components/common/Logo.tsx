interface LogoProps {
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export default function Logo({ className = '', size = 'md' }: LogoProps) {
  const sizes = {
    sm: 'h-8',
    md: 'h-12',
    lg: 'h-16'
  }

  return (
    <img 
      src="/assets/Scalovate_Logo_Black.png"
      alt="Scalovate" 
      className={`${sizes[size]} object-contain ${className}`}
    />
  )
}

