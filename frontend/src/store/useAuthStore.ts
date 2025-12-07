import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: string;
  email: string;
  username: string;
  avatar_url?: string;
  auth_provider: 'email' | 'google' | 'github';
  preferred_language?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_at: number;
}

interface AuthState {
  // 状态
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  login: (user: User, tokens: AuthTokens) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  setTokens: (tokens: AuthTokens) => void;
  setLoading: (loading: boolean) => void;

  // 辅助方法
  isTokenExpired: () => boolean;
  getAccessToken: () => string | null;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始状态
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,

      // 登录
      login: (user, tokens) => {
        set({
          user,
          tokens,
          isAuthenticated: true,
        });
      },

      // 登出
      logout: () => {
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
        });
        // 清除 localStorage 中的其他认证相关数据
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      },

      // 更新用户信息
      updateUser: (updates) => {
        const currentUser = get().user;
        if (currentUser) {
          set({
            user: { ...currentUser, ...updates },
          });
        }
      },

      // 更新 tokens
      setTokens: (tokens) => {
        set({ tokens });
      },

      // 设置加载状态
      setLoading: (loading) => {
        set({ isLoading: loading });
      },

      // 检查 token 是否过期
      isTokenExpired: () => {
        const { tokens } = get();
        if (!tokens) return true;

        const now = Date.now() / 1000; // 转换为秒
        return now >= tokens.expires_at;
      },

      // 获取访问令牌
      getAccessToken: () => {
        const { tokens, isTokenExpired } = get();
        if (!tokens || isTokenExpired()) {
          return null;
        }
        return tokens.access_token;
      },
    }),
    {
      name: 'auth-storage', // localStorage key
      partialize: (state) => ({
        // 只持久化这些字段
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);