import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authService } from '../services/authService'
import toast from 'react-hot-toast'
import Logo from '../components/common/Logo'
import AnimatedCard from '../components/common/AnimatedCard'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const { tokens, user } = await authService.login({ username, password })
      login(tokens.access_token, tokens.refresh_token, user)
      toast.success('Welcome back! 🎉')
      navigate('/')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-100 rounded-full opacity-20 animate-pulse-slow"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-100 rounded-full opacity-20 animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
      </div>

      <AnimatedCard className="max-w-md w-full p-8 relative z-10">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-6 animate-fadeIn">
            <Logo size="lg" />
          </div>
          
          <p className="mt-2 text-md text-gray-600 animate-fadeIn" style={{ animationDelay: '200ms' }}>
            Enterprise AI Chat & Document Intelligence
          </p>
        </div>
        
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div className="animate-slideInLeft" style={{ animationDelay: '300ms' }}>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Username or Email
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="input w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="animate-slideInRight" style={{ animationDelay: '400ms' }}>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="input w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="animate-fadeIn" style={{ animationDelay: '500ms' }}>
            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full py-3 px-4 h-auto rounded-lg font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </div>
        </form>

        <div className="mt-8 pt-6 border-t border-gray-200 animate-fadeIn" style={{ animationDelay: '600ms' }}>
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <p className="text-xs font-medium text-blue-900 mb-2">Demo Credentials</p>
            <div className="space-y-1 text-sm text-blue-700">
              <p className="font-mono bg-white px-3 py-1 rounded inline-block">admin / admin123</p>
              <p className="text-xs text-blue-600 mt-2">or</p>
              <p className="font-mono bg-white px-3 py-1 rounded inline-block">user / user123</p>
            </div>
          </div>
        </div>
      </AnimatedCard>
    </div>
  )
}

