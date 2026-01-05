import api from '../lib/api'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface LoginRequest {
  username: string
  password: string
}

interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

interface UserResponse {
  id: string
  email: string
  username: string
  full_name?: string
  role: string
  is_active: boolean
  auth_provider?: string
  created_at: string
  last_login?: string
}

export const authService = {
  async login(data: LoginRequest): Promise<{ tokens: LoginResponse; user: UserResponse }> {
    // Login endpoint doesn't need auth, use axios directly
    const response = await axios.post<LoginResponse>(
      `${API_URL}/api/v1/auth/local/login`,
      data
    )
    
    // Get user info with the token
    const userResponse = await axios.get<UserResponse>(
      `${API_URL}/api/v1/auth/me`,
      {
        headers: {
          Authorization: `Bearer ${response.data.access_token}`,
        },
      }
    )
    
    return {
      tokens: response.data,
      user: userResponse.data,
    }
  },

  async register(data: {
    email: string
    username: string
    password: string
    full_name?: string
  }): Promise<UserResponse> {
    const response = await axios.post<UserResponse>(
      `${API_URL}/api/v1/auth/local/register`,
      data
    )
    return response.data
  },

  async getCurrentUser(): Promise<UserResponse> {
    const response = await api.get<UserResponse>('/auth/me')
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<LoginResponse> {
    const response = await axios.post<LoginResponse>(
      `${API_URL}/api/v1/auth/refresh`,
      { refresh_token: refreshToken }
    )
    return response.data
  },
}

