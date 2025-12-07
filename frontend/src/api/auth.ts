import axios from 'axios';
import type { User, AuthTokens } from '@/store/useAuthStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const authApi = axios.create({
  baseURL: `${API_BASE_URL}/api/auth`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface RegisterData {
  email: string;
  password: string;
  username: string;
  preferred_language?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  data: {
    user: User;
    tokens: {
      access_token: string;
      refresh_token: string;
      expires_in: number;
    };
  };
  message?: string;
}

// 注册
export const register = async (data: RegisterData): Promise<AuthResponse> => {
  const response = await authApi.post<AuthResponse>('/register', data);
  return response.data;
};

// 登录
export const login = async (data: LoginData): Promise<AuthResponse> => {
  const response = await authApi.post<AuthResponse>('/login', data);
  return response.data;
};

// 登出
export const logout = async (accessToken: string): Promise<void> => {
  await authApi.post('/logout', {}, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
};

// 刷新令牌
export const refreshToken = async (refreshToken: string): Promise<AuthResponse> => {
  const response = await authApi.post<AuthResponse>('/refresh', {
    refresh_token: refreshToken,
  });
  return response.data;
};

// 获取当前用户信息
export const getCurrentUser = async (accessToken: string): Promise<{ success: boolean; data: { user: User } }> => {
  const response = await authApi.get('/me', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  return response.data;
};

// 更新用户资料
export const updateProfile = async (
  accessToken: string,
  data: Partial<User>
): Promise<{ success: boolean; data: { user: User } }> => {
  const response = await authApi.put('/me', data, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  return response.data;
};

// OAuth 相关
export interface OAuthProvider {
  name: string;
  display_name: string;
  configured: boolean;
}

// 获取 OAuth 授权 URL
export const getOAuthAuthorizationUrl = async (
  provider: 'google' | 'github'
): Promise<{ success: boolean; data: { authorization_url: string; state: string } }> => {
  const response = await authApi.get(`/oauth/${provider}/authorize`);
  return response.data;
};

// 处理 OAuth 回调
export const handleOAuthCallback = async (
  provider: 'google' | 'github',
  code: string,
  state: string
): Promise<AuthResponse> => {
  const response = await authApi.post<AuthResponse>(`/oauth/${provider}/callback`, {
    code,
    state,
  });
  return response.data;
};

// 获取支持的 OAuth 提供商
export const getOAuthProviders = async (): Promise<{
  success: boolean;
  data: { providers: OAuthProvider[] };
}> => {
  const response = await authApi.get('/oauth/providers');
  return response.data;
};