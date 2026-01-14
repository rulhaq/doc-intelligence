type AppConfig = {
  apiUrl?: string
  wsUrl?: string
  grafanaUrl?: string
  qdrantUrl?: string
  prometheusUrl?: string
}

const runtimeConfig = (globalThis as typeof globalThis & { __APP_CONFIG__?: AppConfig }).__APP_CONFIG__ || {}

const buildConfig: AppConfig = {
  apiUrl: import.meta.env.VITE_API_URL,
  wsUrl: import.meta.env.VITE_WS_URL,
  grafanaUrl: import.meta.env.VITE_GRAFANA_URL,
  qdrantUrl: import.meta.env.VITE_QDRANT_URL,
  prometheusUrl: import.meta.env.VITE_PROMETHEUS_URL,
}

const mergedConfig: AppConfig = { ...buildConfig, ...runtimeConfig }

const requireValue = (name: string, value?: string): string => {
  if (!value || value.trim().length === 0) {
    throw new Error(`${name} is required`)
  }
  return value
}

export const API_URL = requireValue('VITE_API_URL', mergedConfig.apiUrl)
export const WS_URL = requireValue('VITE_WS_URL', mergedConfig.wsUrl)

export const DASHBOARD_URLS = {
  grafana: mergedConfig.grafanaUrl,
  qdrant: mergedConfig.qdrantUrl,
  prometheus: mergedConfig.prometheusUrl,
}
