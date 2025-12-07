import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Mail, Lock, User, ArrowLeft, Github, Chrome, Eye, EyeOff } from 'lucide-react';
import { Button, useToast } from '@/components/shared';
import { useAuthStore } from '@/store/useAuthStore';
import { login, register, getOAuthAuthorizationUrl, handleOAuthCallback } from '@/api/auth';

type AuthMode = 'login' | 'register';

export const Auth: React.FC = () => {
  const { t } = useTranslation(['common', 'auth', 'errors']);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { show, ToastContainer } = useToast();
  const { login: loginStore } = useAuthStore();

  const [mode, setMode] = useState<AuthMode>('login');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // 表单数据
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
  });

  // 处理 OAuth 回调
  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const provider = searchParams.get('provider') as 'google' | 'github' | null;

    if (code && state && provider) {
      handleOAuthCallbackFlow(provider, code, state);
    }
  }, [searchParams]);

  const handleOAuthCallbackFlow = async (
    provider: 'google' | 'github',
    code: string,
    state: string
  ) => {
    setIsLoading(true);
    try {
      const response = await handleOAuthCallback(provider, code, state);
      if (response.success && response.data) {
        const { user, tokens } = response.data;
        const authTokens = {
          access_token: tokens.access_token,
          refresh_token: tokens.refresh_token,
          expires_at: Math.floor(Date.now() / 1000) + tokens.expires_in,
        };
        loginStore(user, authTokens);
        show({ message: t('auth:login_success'), type: 'success' });
        navigate('/');
      }
    } catch (error: any) {
      console.error('OAuth callback error:', error);
      show({
        message: error?.response?.data?.error?.message || t('auth:oauth_error'),
        type: 'error',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.email || !formData.password) {
      show({ message: t('errors:validation_error'), type: 'error' });
      return;
    }

    if (mode === 'register' && !formData.username) {
      show({ message: t('errors:validation_error'), type: 'error' });
      return;
    }

    setIsLoading(true);
    try {
      let response;
      if (mode === 'login') {
        response = await login({
          email: formData.email,
          password: formData.password,
        });
      } else {
        response = await register({
          email: formData.email,
          password: formData.password,
          username: formData.username,
        });
      }

      if (response.success && response.data) {
        const { user, tokens } = response.data;
        const authTokens = {
          access_token: tokens.access_token,
          refresh_token: tokens.refresh_token,
          expires_at: Math.floor(Date.now() / 1000) + tokens.expires_in,
        };
        loginStore(user, authTokens);
        show({
          message: mode === 'login' ? t('auth:login_success') : t('auth:register_success'),
          type: 'success',
        });
        navigate('/');
      }
    } catch (error: any) {
      console.error('Auth error:', error);
      show({
        message:
          error?.response?.data?.error?.message ||
          (mode === 'login' ? t('auth:login_error') : t('auth:register_error')),
        type: 'error',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOAuthLogin = async (provider: 'google' | 'github') => {
    try {
      const response = await getOAuthAuthorizationUrl(provider);
      if (response.success && response.data.authorization_url) {
        // 重定向到 OAuth 授权页面
        window.location.href = response.data.authorization_url;
      }
    } catch (error: any) {
      console.error('OAuth error:', error);
      show({
        message: error?.response?.data?.error?.message || t('auth:oauth_error'),
        type: 'error',
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-orange-50/30 to-pink-50/50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4 transition-colors duration-300">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-banana-500/10 dark:bg-banana-500/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-orange-400/10 dark:bg-orange-400/5 rounded-full blur-3xl animate-pulse"></div>
      </div>

      <div className="relative w-full max-w-md">
        {/* 返回按钮 */}
        <button
          onClick={() => navigate('/')}
          className="mb-6 flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
        >
          <ArrowLeft size={20} />
          <span>{t('buttons.back')}</span>
        </button>

        {/* 登录/注册卡片 */}
        <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-gray-100 dark:border-gray-700">
          {/* Logo 和标题 */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-banana-500 to-orange-500 rounded-2xl mb-4">
              <img
                src="/logo.jpg"
                alt="Logo"
                className="w-12 h-12 rounded-xl object-cover"
              />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              {mode === 'login' ? t('auth:login') : t('auth:register')}
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {mode === 'login'
                ? t('auth:login_subtitle')
                : t('auth:register_subtitle')}
            </p>
          </div>

          {/* OAuth 登录按钮 */}
          <div className="space-y-3 mb-6">
            <button
              onClick={() => handleOAuthLogin('google')}
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
            >
              <Chrome size={20} />
              <span>{t('auth:continue_with_google')}</span>
            </button>

            <button
              onClick={() => handleOAuthLogin('github')}
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-gray-900 dark:bg-gray-700 border border-gray-800 dark:border-gray-600 rounded-lg text-white hover:bg-gray-800 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
            >
              <Github size={20} />
              <span>{t('auth:continue_with_github')}</span>
            </button>
          </div>

          {/* 分隔线 */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300 dark:border-gray-600"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">
                {t('auth:or_continue_with_email')}
              </span>
            </div>
          </div>

          {/* 邮箱登录表单 */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('auth:username')}
                </label>
                <div className="relative">
                  <User
                    size={20}
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                  />
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) =>
                      setFormData({ ...formData, username: e.target.value })
                    }
                    className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-banana-500 focus:border-transparent text-gray-900 dark:text-gray-100 transition-colors"
                    placeholder={t('auth:username_placeholder')}
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('auth:email')}
              </label>
              <div className="relative">
                <Mail
                  size={20}
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-banana-500 focus:border-transparent text-gray-900 dark:text-gray-100 transition-colors"
                  placeholder={t('auth:email_placeholder')}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('auth:password')}
              </label>
              <div className="relative">
                <Lock
                  size={20}
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) =>
                    setFormData({ ...formData, password: e.target.value })
                  }
                  className="w-full pl-10 pr-12 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-banana-500 focus:border-transparent text-gray-900 dark:text-gray-100 transition-colors"
                  placeholder={t('auth:password_placeholder')}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              loading={isLoading}
              className="w-full bg-gradient-to-r from-banana-500 to-orange-500 hover:from-banana-600 hover:to-orange-600 text-black font-semibold py-3"
            >
              {mode === 'login' ? t('auth:login') : t('auth:register')}
            </Button>
          </form>

          {/* 切换登录/注册 */}
          <div className="mt-6 text-center text-sm">
            <span className="text-gray-600 dark:text-gray-400">
              {mode === 'login'
                ? t('auth:no_account')
                : t('auth:already_have_account')}
            </span>
            <button
              onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
              className="ml-2 text-banana-600 dark:text-banana-400 hover:underline font-medium"
            >
              {mode === 'login' ? t('auth:register') : t('auth:login')}
            </button>
          </div>

          {/* 提示：可选登录 */}
          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <p className="text-xs text-blue-800 dark:text-blue-300 text-center">
              💡 {t('auth:optional_login_hint')}
            </p>
          </div>
        </div>
      </div>

      <ToastContainer />
    </div>
  );
};