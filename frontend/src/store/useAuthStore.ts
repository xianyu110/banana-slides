import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { isSupabaseConfigured } from '@/lib/supabase';
import {
  supabaseLogin,
  supabaseRegister,
  supabaseLogout,
  supabaseOAuthLogin,
  supabaseGetSession,
  onAuthStateChange,
} from '@/api/supabaseAuth';
import * as legacyAuth from '@/api/auth';

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
  authMode: 'supabase' | 'legacy'; // 当前使用的认证模式

  // Actions
  login: (user: User, tokens: AuthTokens) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  setTokens: (tokens: AuthTokens) => void;
  setLoading: (loading: boolean) => void;

  // Supabase 认证方法
  loginWithEmail: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  registerWithEmail: (email: string, password: string, username: string) => Promise<{ success: boolean; error?: string }>;
  loginWithOAuth: (provider: 'google' | 'github') => Promise<{ success: boolean; error?: string }>;
  initializeAuth: () => Promise<void>;

  // 辅助方法
  isTokenExpired: () => boolean;
  getAccessToken: () => string | null;
  isUsingSupabase: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始状态
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      authMode: isSupabaseConfigured() ? 'supabase' : 'legacy',

      // 检查是否使用 Supabase
      isUsingSupabase: () => {
        return isSupabaseConfigured();
      },

      // 登录（设置状态）
      login: (user, tokens) => {
        set({
          user,
          tokens,
          isAuthenticated: true,
        });
      },

      // 登出
      logout: async () => {
        const { authMode } = get();

        if (authMode === 'supabase' && isSupabaseConfigured()) {
          await supabaseLogout();
        }

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

      // 邮箱登录
      loginWithEmail: async (email, password) => {
        set({ isLoading: true });

        try {
          if (isSupabaseConfigured()) {
            // 使用 Supabase 登录
            const result = await supabaseLogin(email, password);

            if (result.success && result.data) {
              const { user, tokens } = result.data;
              const authTokens: AuthTokens = {
                access_token: tokens.access_token,
                refresh_token: tokens.refresh_token,
                expires_at: Math.floor(Date.now() / 1000) + tokens.expires_in,
              };
              set({
                user,
                tokens: authTokens,
                isAuthenticated: true,
                authMode: 'supabase',
              });
              return { success: true };
            }

            return { success: false, error: result.error };
          } else {
            // 使用原有后端登录
            const response = await legacyAuth.login({ email, password });

            if (response.success && response.data) {
              const { user, tokens } = response.data;
              const authTokens: AuthTokens = {
                access_token: tokens.access_token,
                refresh_token: tokens.refresh_token,
                expires_at: Math.floor(Date.now() / 1000) + tokens.expires_in,
              };
              set({
                user,
                tokens: authTokens,
                isAuthenticated: true,
                authMode: 'legacy',
              });
              return { success: true };
            }

            return { success: false, error: '登录失败' };
          }
        } catch (error: any) {
          return {
            success: false,
            error: error?.response?.data?.error?.message || error.message || '登录失败',
          };
        } finally {
          set({ isLoading: false });
        }
      },

      // 邮箱注册
      registerWithEmail: async (email, password, username) => {
        set({ isLoading: true });

        try {
          if (isSupabaseConfigured()) {
            // 使用 Supabase 注册
            const result = await supabaseRegister(email, password, username);

            if (result.success && result.data) {
              const { user, tokens } = result.data;
              const authTokens: AuthTokens = {
                access_token: tokens.access_token,
                refresh_token: tokens.refresh_token,
                expires_at: Math.floor(Date.now() / 1000) + tokens.expires_in,
              };
              set({
                user,
                tokens: authTokens,
                isAuthenticated: true,
                authMode: 'supabase',
              });
              return { success: true };
            }

            return { success: false, error: result.error };
          } else {
            // 使用原有后端注册
            const response = await legacyAuth.register({ email, password, username });

            if (response.success && response.data) {
              const { user, tokens } = response.data;
              const authTokens: AuthTokens = {
                access_token: tokens.access_token,
                refresh_token: tokens.refresh_token,
                expires_at: Math.floor(Date.now() / 1000) + tokens.expires_in,
              };
              set({
                user,
                tokens: authTokens,
                isAuthenticated: true,
                authMode: 'legacy',
              });
              return { success: true };
            }

            return { success: false, error: '注册失败' };
          }
        } catch (error: any) {
          return {
            success: false,
            error: error?.response?.data?.error?.message || error.message || '注册失败',
          };
        } finally {
          set({ isLoading: false });
        }
      },

      // OAuth 登录
      loginWithOAuth: async (provider) => {
        if (isSupabaseConfigured()) {
          const result = await supabaseOAuthLogin(provider);
          return result;
        } else {
          // 使用原有后端 OAuth
          try {
            const response = await legacyAuth.getOAuthAuthorizationUrl(provider);
            if (response.success && response.data.authorization_url) {
              window.location.href = response.data.authorization_url;
              return { success: true };
            }
            return { success: false, error: 'OAuth 初始化失败' };
          } catch (error: any) {
            return {
              success: false,
              error: error?.response?.data?.error?.message || error.message || 'OAuth 失败',
            };
          }
        }
      },

      // 初始化认证状态（应用启动时调用）
      initializeAuth: async () => {
        if (isSupabaseConfigured()) {
          // 检查 Supabase 会话
          const result = await supabaseGetSession();

          if (result.success && result.data) {
            const { user, tokens } = result.data;
            const authTokens: AuthTokens = {
              access_token: tokens.access_token,
              refresh_token: tokens.refresh_token,
              expires_at: Math.floor(Date.now() / 1000) + tokens.expires_in,
            };
            set({
              user,
              tokens: authTokens,
              isAuthenticated: true,
              authMode: 'supabase',
            });
          }

          // 监听认证状态变化
          onAuthStateChange((event, session) => {
            console.log('[Auth] State changed:', event);

            if (event === 'SIGNED_IN' && session?.user) {
              const user: User = {
                id: session.user.id,
                email: session.user.email || '',
                username: session.user.user_metadata?.username ||
                          session.user.user_metadata?.name ||
                          session.user.email?.split('@')[0] ||
                          'User',
                avatar_url: session.user.user_metadata?.avatar_url,
                auth_provider: (session.user.app_metadata?.provider as 'email' | 'google' | 'github') || 'email',
                preferred_language: session.user.user_metadata?.preferred_language,
              };
              const authTokens: AuthTokens = {
                access_token: session.access_token,
                refresh_token: session.refresh_token || '',
                expires_at: Math.floor(Date.now() / 1000) + (session.expires_in || 3600),
              };
              set({
                user,
                tokens: authTokens,
                isAuthenticated: true,
                authMode: 'supabase',
              });
            } else if (event === 'SIGNED_OUT') {
              set({
                user: null,
                tokens: null,
                isAuthenticated: false,
              });
            } else if (event === 'TOKEN_REFRESHED' && session) {
              set({
                tokens: {
                  access_token: session.access_token,
                  refresh_token: session.refresh_token || '',
                  expires_at: Math.floor(Date.now() / 1000) + (session.expires_in || 3600),
                },
              });
            }
          });
        }
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
        authMode: state.authMode,
      }),
    }
  )
);
