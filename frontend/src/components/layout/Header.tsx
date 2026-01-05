import { Link } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import Logo from '../common/Logo'
import { UserCircleIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline'

export default function Header() {
  const { user, logout } = useAuthStore()
  
  // Check for admin role (case insensitive)
  const isAdmin = user?.role?.toUpperCase() === 'ADMIN'

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Logo and Navigation */}
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center hover:opacity-80 transition-opacity">
              <Logo size="sm" />
            </Link>
            
            <nav className="flex space-x-1">
              <Link
                to="/"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                💬 Chat
              </Link>
              {isAdmin && (
                <>
                  <Link
                    to="/admin"
                    className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                  >
                    📄 Upload Document
                  </Link>
                  <Link
                    to="/admin/console"
                    className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                  >
                    ⚙️ Console
                  </Link>
                </>
              )}
            </nav>
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 px-3 py-2 bg-gray-50 rounded-lg">
              <UserCircleIcon className="w-5 h-5 text-gray-600" />
              <div className="text-sm">
                <div className="font-medium text-gray-900">{user?.username}</div>
                <div className="text-xs text-gray-500 capitalize">{user?.role?.toLowerCase()}</div>
              </div>
            </div>
            
            <button
              onClick={logout}
              className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Logout"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

