"""
Authentication middleware and decorators - 认证中间件和装饰器
"""
from functools import wraps
from flask import request, jsonify, g
from typing import Callable, Optional
from services.auth_service import auth_service
from models import User


def get_token_from_header() -> Optional[str]:
    """
    从请求头获取token

    Returns:
        token字符串，如果不存在返回None
    """
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]  # 移除 'Bearer ' 前缀
    return None


def get_current_user() -> Optional[User]:
    """
    获取当前认证用户

    Returns:
        用户对象，如果未认证返回None
    """
    if hasattr(g, 'current_user'):
        return g.current_user

    token = get_token_from_header()
    if not token:
        return None

    payload = auth_service.verify_access_token(token)
    if not payload:
        return None

    user = User.query.get(payload['user_id'])
    if user and user.is_active:
        g.current_user = user
        return user

    return None


def token_required(f: Callable) -> Callable:
    """
    需要认证的装饰器

    Args:
        f: 被装饰的函数

    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'AUTHENTICATION_REQUIRED',
                    'message': 'Authentication token is required'
                }
            }), 401

        payload = auth_service.verify_access_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': 'Invalid or expired token'
                }
            }), 401

        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found or inactive'
                }
            }), 401

        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def optional_auth(f: Callable) -> Callable:
    """
    可选认证的装饰器（用于支持游客模式）

    Args:
        f: 被装饰的函数

    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 尝试获取用户，但不强制要求
        token = get_token_from_header()
        if token:
            payload = auth_service.verify_access_token(token)
            if payload:
                user = User.query.get(payload['user_id'])
                if user and user.is_active:
                    g.current_user = user

        return f(*args, **kwargs)

    return decorated_function


def require_email_verified(f: Callable) -> Callable:
    """
    需要邮箱验证的装饰器

    Args:
        f: 被装饰的函数

    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'AUTHENTICATION_REQUIRED',
                    'message': 'Authentication token is required'
                }
            }), 401

        user = g.current_user
        if not user.email_verified:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'EMAIL_NOT_VERIFIED',
                    'message': 'Email verification is required'
                }
            }), 403

        return f(*args, **kwargs)

    return decorated_function


class AuthMiddleware:
    """认证中间件类"""

    @staticmethod
    def before_request():
        """在每个请求前执行"""
        # 对于不需要认证的路径，跳过token验证
        skip_paths = [
            '/api/auth/register',
            '/api/auth/login',
            '/api/auth/oauth',
            '/api/auth/refresh',
            '/health',
            '/',
            '/api/i18n/languages',
            '/api/i18n/current'
        ]

        if request.path.startswith('/api/auth/oauth/') or request.path in skip_paths:
            return

        # 尝试设置当前用户
        token = get_token_from_header()
        if token:
            payload = auth_service.verify_access_token(token)
            if payload:
                user = User.query.get(payload['user_id'])
                if user and user.is_active:
                    g.current_user = user