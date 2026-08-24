import { apiClient } from './client'

export interface AuthCredentials {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserResponse {
  id: string
  email: string
}

export async function registerUser(credentials: AuthCredentials): Promise<UserResponse> {
  const { data } = await apiClient.post<UserResponse>('/auth/register', credentials)
  return data
}

export async function loginUser(credentials: AuthCredentials): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', credentials)
  return data
}

export async function fetchCurrentUser(): Promise<UserResponse> {
  const { data } = await apiClient.get<UserResponse>('/auth/me')
  return data
}
