"""
OAuth Service - OAuth认证服务
"""
import os
import json
from typing import Dict, Any, Optional
from authlib.integrations.base_client import OAuthError
from authlib.integrations.requests_client import OAuth2Session
from services.auth_service import auth_service
from utils.response import success_response, bad_request, server_error
import requests


class OAuthService:
    """OAuth服务基类"""

    def __init__(self):
        self.configs = self._load_oauth_configs()

    def _load_oauth_configs(self) -> Dict[str, Dict[str, str]]:
        """从环境变量加载OAuth配置"""
        return {
            'google': {
                'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID', ''),
                'client_secret': os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', ''),
                'authorize_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'userinfo_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
                'redirect_uri': os.getenv('GOOGLE_OAUTH_REDIRECT_URI', 'http://localhost:3000/auth/google/callback'),
                'scope': 'openid email profile'
            },
            'github': {
                'client_id': os.getenv('GITHUB_OAUTH_CLIENT_ID', ''),
                'client_secret': os.getenv('GITHUB_OAUTH_CLIENT_SECRET', ''),
                'authorize_url': 'https://github.com/login/oauth/authorize',
                'token_url': 'https://github.com/login/oauth/access_token',
                'userinfo_url': 'https://api.github.com/user',
                'redirect_uri': os.getenv('GITHUB_OAUTH_REDIRECT_URI', 'http://localhost:3000/auth/github/callback'),
                'scope': 'user:email'
            }
        }

    def get_authorization_url(self, provider: str, state: str = None) -> Dict[str, Any]:
        """
        获取OAuth授权URL

        Args:
            provider: OAuth提供商 ('google' 或 'github')
            state: 状态参数，用于防止CSRF攻击

        Returns:
            包含授权URL的字典
        """
        if provider not in self.configs:
            raise ValueError(f'Unsupported OAuth provider: {provider}')

        config = self.configs[provider]

        if not config['client_id'] or not config['client_secret']:
            raise ValueError(f'OAuth configuration missing for {provider}')

        session = OAuth2Session(
            client_id=config['client_id'],
            scope=config['scope'],
            redirect_uri=config['redirect_uri'],
            state=state
        )

        authorization_url, state = session.authorization_url(config['authorize_url'])

        return {
            'authorization_url': authorization_url,
            'state': state
        }

    def handle_callback(self, provider: str, code: str, state: str = None) -> Dict[str, Any]:
        """
        处理OAuth回调

        Args:
            provider: OAuth提供商
            code: 授权码
            state: 状态参数

        Returns:
            用户信息和令牌
        """
        if provider not in self.configs:
            raise ValueError(f'Unsupported OAuth provider: {provider}')

        config = self.configs[provider]

        try:
            # 使用授权码获取访问令牌
            session = OAuth2Session(
                client_id=config['client_id'],
                redirect_uri=config['redirect_uri']
            )

            token = session.fetch_token(
                token_url=config['token_url'],
                code=code,
                client_secret=config['client_secret'],
                include_client_id=True
            )

            # 获取用户信息
            user_info = self._get_user_info(provider, token['access_token'])

            # 创建或更新用户
            user = auth_service.create_or_update_oauth_user(
                provider=provider,
                provider_id=str(user_info['id']),
                email=user_info['email'],
                username=user_info.get('name', user_info['email'].split('@')[0]),
                avatar_url=user_info.get('avatar_url', user_info.get('picture'))
            )

            # 生成JWT令牌
            jwt_tokens = auth_service.generate_tokens(user)

            return {
                'user': user.to_dict(),
                'tokens': jwt_tokens
            }

        except OAuthError as e:
            raise ValueError(f'OAuth authentication failed: {str(e)}')
        except Exception as e:
            raise ValueError(f'Authentication failed: {str(e)}')

    def _get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """获取用户信息"""
        if provider == 'google':
            return self._get_google_user_info(access_token)
        elif provider == 'github':
            return self._get_github_user_info(access_token)
        else:
            raise ValueError(f'Unsupported provider: {provider}')

    def _get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """获取Google用户信息"""
        config = self.configs['google']
        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.get(config['userinfo_url'], headers=headers)
        response.raise_for_status()

        user_info = response.json()
        return {
            'id': user_info['id'],
            'email': user_info['email'],
            'name': user_info['name'],
            'avatar_url': user_info['picture'],
            'email_verified': user_info.get('verified_email', False)
        }

    def _get_github_user_info(self, access_token: str) -> Dict[str, Any]:
        """获取GitHub用户信息"""
        config = self.configs['github']
        headers = {'Authorization': f'token {access_token}'}

        # 获取基本信息
        response = requests.get(config['userinfo_url'], headers=headers)
        response.raise_for_status()

        user_info = response.json()

        # 获取邮箱信息（GitHub需要单独请求）
        email_response = requests.get('https://api.github.com/user/emails', headers=headers)
        email_response.raise_for_status()
        emails = email_response.json()

        # 找到主邮箱（verified为true的primary邮箱）
        primary_email = None
        for email_info in emails:
            if email_info.get('verified', False) and email_info.get('primary', False):
                primary_email = email_info['email']
                break

        # 如果没有verified的primary邮箱，使用第一个邮箱
        if not primary_email and emails:
            primary_email = emails[0]['email']

        return {
            'id': user_info['id'],
            'email': primary_email,
            'name': user_info['name'] or user_info['login'],
            'avatar_url': user_info['avatar_url'],
            'email_verified': True  # GitHub邮箱通过OAuth验证
        }


class GoogleOAuthService(OAuthService):
    """Google OAuth服务"""

    def get_authorization_url(self, state: str = None) -> Dict[str, Any]:
        """获取Google OAuth授权URL"""
        return super().get_authorization_url('google', state)

    def handle_callback(self, code: str, state: str = None) -> Dict[str, Any]:
        """处理Google OAuth回调"""
        return super().handle_callback('google', code, state)


class GitHubOAuthService(OAuthService):
    """GitHub OAuth服务"""

    def get_authorization_url(self, state: str = None) -> Dict[str, Any]:
        """获取GitHub OAuth授权URL"""
        return super().get_authorization_url('github', state)

    def handle_callback(self, code: str, state: str = None) -> Dict[str, Any]:
        """处理GitHub OAuth回调"""
        return super().handle_callback('github', code, state)


# 创建服务实例
oauth_service = OAuthService()
google_oauth_service = GoogleOAuthService()
github_oauth_service = GitHubOAuthService()