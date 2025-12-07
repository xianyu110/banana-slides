"""
OAuth Controller - OAuth认证控制器
"""
from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from services.oauth_service import oauth_service, google_oauth_service, github_oauth_service
from utils.response import success_response, bad_request, server_error
import secrets

oauth_bp = Blueprint('oauth', __name__, url_prefix='/api/auth/oauth')


@oauth_bp.route('/<provider>/authorize', methods=['GET'])
def get_authorization_url(provider: str):
    """
    GET /api/auth/oauth/<provider>/authorize - 获取OAuth授权URL

    Args:
        provider: OAuth提供商 ('google' 或 'github')

    Query params:
    - redirect_uri: 登录成功后的重定向URL（可选）

    Returns:
        {
            "authorization_url": "https://...",
            "state": "state_value"
        }
    """
    try:
        if provider not in ['google', 'github']:
            return bad_request('validation_failed',
                             message='Unsupported OAuth provider')

        # 生成状态参数，用于防止CSRF攻击
        state = secrets.token_urlsafe(32)

        # 获取授权URL
        if provider == 'google':
            result = google_oauth_service.get_authorization_url(state)
        else:
            result = github_oauth_service.get_authorization_url(state)

        return success_response({
            'authorization_url': result['authorization_url'],
            'state': result['state'],
            'provider': provider
        }, 'authorization_url_generated')

    except ValueError as e:
        return bad_request('validation_failed', message=str(e))
    except Exception as e:
        return server_error('unknown_error')


@oauth_bp.route('/<provider>/callback', methods=['POST'])
def handle_oauth_callback(provider: str):
    """
    POST /api/auth/oauth/<provider>/callback - 处理OAuth回调

    Args:
        provider: OAuth提供商 ('google' 或 'github')

    Request body:
    {
        "code": "authorization_code",
        "state": "state_value"
    }
    """
    try:
        if provider not in ['google', 'github']:
            return bad_request('validation_failed',
                             message='Unsupported OAuth provider')

        data = request.get_json()
        if not data:
            return bad_request('validation_failed')

        code = data.get('code')
        state = data.get('state')

        if not code:
            return bad_request('validation_failed',
                             message='Authorization code is required')

        # 处理OAuth回调
        if provider == 'google':
            result = google_oauth_service.handle_callback(code, state)
        else:
            result = github_oauth_service.handle_callback(code, state)

        return success_response({
            'user': result['user'],
            'tokens': result['tokens'],
            'provider': provider
        }, 'oauth_login_successful')

    except ValueError as e:
        return bad_request('oauth_failed', message=str(e))
    except Exception as e:
        return server_error('unknown_error')


@oauth_bp.route('/<provider>/config', methods=['GET'])
def get_oauth_config(provider: str):
    """
    GET /api/auth/oauth/<provider>/config - 获取OAuth配置信息

    Args:
        provider: OAuth提供商 ('google' 或 'github')

    Returns:
        OAuth配置信息（不包括敏感信息）
    """
    try:
        if provider not in ['google', 'github']:
            return bad_request('validation_failed',
                             message='Unsupported OAuth provider')

        configs = oauth_service.configs
        config = configs.get(provider, {})

        # 只返回非敏感信息
        public_config = {
            'configured': bool(config.get('client_id') and config.get('client_secret')),
            'redirect_uri': config.get('redirect_uri'),
            'scope': config.get('scope')
        }

        return success_response({
            'provider': provider,
            'config': public_config
        }, 'config_retrieved')

    except Exception as e:
        return server_error('unknown_error')


@oauth_bp.route('/providers', methods=['GET'])
def list_oauth_providers():
    """
    GET /api/auth/oauth/providers - 获取支持的OAuth提供商列表

    Returns:
        支持的OAuth提供商列表及其配置状态
    """
    try:
        providers = []
        for provider_name, config in oauth_service.configs.items():
            providers.append({
                'name': provider_name,
                'display_name': 'Google' if provider_name == 'google' else 'GitHub',
                'configured': bool(config.get('client_id') and config.get('client_secret')),
                'redirect_uri': config.get('redirect_uri')
            })

        return success_response({
            'providers': providers
        }, 'providers_retrieved')

    except Exception as e:
        return server_error('unknown_error')


# Webhook/redirect端点（用于前端直接跳转）
@oauth_bp.route('/<provider>/redirect', methods=['GET'])
def oauth_redirect(provider: str):
    """
    GET /api/auth/oauth/<provider>/redirect - OAuth重定向端点

    这个端点主要用于Web应用的重定向流程。
    对于单页应用，建议使用 /authorize 端点获取URL后在前端处理。

    Args:
        provider: OAuth提供商 ('google' 或 'github')
    """
    try:
        if provider not in ['google', 'github']:
            return jsonify({
                'success': False,
                'error': 'Unsupported OAuth provider'
            }), 400

        # 生成状态参数
        state = secrets.token_urlsafe(32)

        # 获取授权URL
        if provider == 'google':
            result = google_oauth_service.get_authorization_url(state)
        else:
            result = github_oauth_service.get_authorization_url(state)

        # 重定向到OAuth授权页面
        return redirect(result['authorization_url'])

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500