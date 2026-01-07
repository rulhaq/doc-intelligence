import { useState, useEffect } from 'react'
import {
  ChartBarIcon,
  CircleStackIcon,
  ServerIcon,
  CpuChipIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'
import api from '../../lib/api'
import toast from 'react-hot-toast'
import { DASHBOARD_URLS } from '../../lib/config'

type Dashboard = {
  id: string
  name: string
  icon: typeof ChartBarIcon
  url: string
  description: string
  color: string
}

const dashboards: Dashboard[] = [
  {
    id: 'grafana',
    name: 'Grafana Metrics',
    icon: ChartBarIcon,
    url: DASHBOARD_URLS.grafana || '',
    description: 'System metrics, performance, and analytics',
    color: 'orange',
  },
  {
    id: 'qdrant',
    name: 'Qdrant Console',
    icon: CircleStackIcon,
    url: DASHBOARD_URLS.qdrant || '',
    description: 'Vector database administration',
    color: 'purple',
  },
  {
    id: 'prometheus',
    name: 'Prometheus',
    icon: CpuChipIcon,
    url: DASHBOARD_URLS.prometheus || '',
    description: 'Metrics collection and alerting',
    color: 'blue',
  },
].filter((dashboard) => dashboard.url)

interface SystemStats {
  total_users: number
  total_documents: number
  total_conversations: number
  total_vectors: number
  storage_used_bytes: number
  vllm_status: string
  qdrant_status: string
}

export default function MonitoringDashboards() {
  const [selectedDashboard, setSelectedDashboard] = useState<Dashboard | null>(dashboards[0] || null)
  const [iframeKey, setIframeKey] = useState(0)
  const [iframeLoading, setIframeLoading] = useState(true)
  const [iframeError, setIframeError] = useState(false)
  const [stats, setStats] = useState<SystemStats>({
    total_users: 0,
    total_documents: 0,
    total_conversations: 0,
    total_vectors: 0,
    storage_used_bytes: 0,
    vllm_status: 'unknown',
    qdrant_status: 'unknown',
  })
  const [loadingStats, setLoadingStats] = useState(true)

  useEffect(() => {
    loadStats()
    const interval = setInterval(loadStats, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      const response = await api.get('/admin/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load stats:', error)
      toast.error('Failed to load system statistics')
    } finally {
      setLoadingStats(false)
    }
  }

  const handleRefresh = () => {
    setIframeKey(prev => prev + 1)
    setIframeLoading(true)
    setIframeError(false)
    loadStats()
  }

  const handleDashboardChange = (dashboard: Dashboard) => {
    setSelectedDashboard(dashboard)
    setIframeLoading(true)
    setIframeError(false)
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      setIframeLoading(false)
    }, 3000)
    return () => clearTimeout(timer)
  }, [iframeKey, selectedDashboard])

  return (
    <div className="h-full flex flex-col space-y-4">
      {dashboards.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {dashboards.map((dashboard) => (
            <button
              key={dashboard.id}
              onClick={() => handleDashboardChange(dashboard)}
              className={`relative group overflow-hidden rounded-lg p-4 transition-all duration-200 ${
                selectedDashboard?.id === dashboard.id
                  ? 'bg-gradient-to-br from-primary-50 to-primary-100 border-2 border-primary-500 shadow-lg'
                  : 'bg-white border border-gray-200 hover:border-primary-300 hover:shadow-md'
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`p-2 rounded-lg ${
                    selectedDashboard?.id === dashboard.id
                      ? `bg-${dashboard.color}-500 text-white`
                      : `bg-${dashboard.color}-100 text-${dashboard.color}-600`
                  }`}
                >
                  <dashboard.icon className="w-6 h-6" />
                </div>
                <div className="text-left flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate">
                    {dashboard.name}
                  </h3>
                  <p className="text-xs text-gray-600 truncate">
                    {dashboard.description}
                  </p>
                </div>
              </div>

              {selectedDashboard?.id === dashboard.id && (
                <div className="absolute top-2 right-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                </div>
              )}
            </button>
          ))}
        </div>
      )}

      {selectedDashboard && (
        <div className="flex-1 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center gap-3">
              <selectedDashboard.icon className="w-5 h-5 text-gray-600" />
              <div>
                <h3 className="font-semibold text-gray-900">{selectedDashboard.name}</h3>
                <p className="text-xs text-gray-600">{selectedDashboard.url}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleRefresh}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="Refresh"
              >
                <ArrowPathIcon className="w-5 h-5" />
              </button>
              <a
                href={selectedDashboard.url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 text-sm font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors"
              >
                Open in New Tab
              </a>
            </div>
          </div>

          <div className="relative h-full">
            <iframe
              key={iframeKey}
              src={selectedDashboard.url}
              className="w-full h-full"
              title={selectedDashboard.name}
              onLoad={() => {
                setIframeLoading(false)
                setIframeError(false)
              }}
              onError={() => {
                console.error(`Failed to load ${selectedDashboard.name}`)
                setIframeLoading(false)
                setIframeError(true)
              }}
            />

            {iframeLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                  <p className="text-sm text-gray-600">Loading {selectedDashboard.name}...</p>
                </div>
              </div>
            )}

            {iframeError && !iframeLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
                <div className="text-center max-w-md">
                  <svg className="mx-auto h-16 w-16 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Dashboard Not Available</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Unable to load {selectedDashboard.name} in the embedded view.
                    This may be due to CORS restrictions or the service not running.
                  </p>
                  <a
                    href={selectedDashboard.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    Open in New Tab
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {dashboards.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-sm text-gray-600">
          No dashboard URLs configured. Set the dashboard URLs in environment variables to enable embeds.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-600">Total Users</p>
              {loadingStats ? (
                <div className="h-8 w-16 bg-gray-200 animate-pulse rounded mt-1"></div>
              ) : (
                <p className="text-2xl font-bold text-gray-900">{stats.total_users}</p>
              )}
            </div>
            <div className="p-2 bg-green-100 rounded-lg">
              <ChartBarIcon className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-600">Total Vectors</p>
              {loadingStats ? (
                <div className="h-8 w-16 bg-gray-200 animate-pulse rounded mt-1"></div>
              ) : (
                <p className="text-2xl font-bold text-gray-900">{stats.total_vectors}</p>
              )}
            </div>
            <div className={`p-2 rounded-lg ${
              stats.qdrant_status === 'healthy' ? 'bg-purple-100' : 'bg-red-100'
            }`}>
              <CircleStackIcon className={`w-6 h-6 ${
                stats.qdrant_status === 'healthy' ? 'text-purple-600' : 'text-red-600'
              }`} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-600">Documents</p>
              {loadingStats ? (
                <div className="h-8 w-16 bg-gray-200 animate-pulse rounded mt-1"></div>
              ) : (
                <p className="text-2xl font-bold text-gray-900">{stats.total_documents}</p>
              )}
            </div>
            <div className="p-2 bg-orange-100 rounded-lg">
              <ServerIcon className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-600">Conversations</p>
              {loadingStats ? (
                <div className="h-8 w-16 bg-gray-200 animate-pulse rounded mt-1"></div>
              ) : (
                <p className="text-2xl font-bold text-gray-900">{stats.total_conversations}</p>
              )}
            </div>
            <div className={`p-2 rounded-lg ${
              stats.vllm_status === 'healthy' ? 'bg-blue-100' : 'bg-red-100'
            }`}>
              <CpuChipIcon className={`w-6 h-6 ${
                stats.vllm_status === 'healthy' ? 'text-blue-600' : 'text-red-600'
              }`} />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
          </div>
          <div className="flex-1">
            <h4 className="text-sm font-medium text-blue-900">External Dashboard Access</h4>
            <p className="text-xs text-blue-700 mt-1">
              If dashboards do not load in the iframe due to security restrictions, use "Open in New Tab".
              Ensure the dashboard URLs are set and reachable.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
