"""
Authentication Controller - 用户认证控制器
"""
from flask import Blueprint, request, jsonify, g
from flask_babel import gettext as _
from services.auth_service import auth_service
from models import db, User
from utils.response import success_response, bad_request, unauthorized, server_error
from utils.validators import validate_email, validate_password
from utils.auth import get_current_user
import traceback
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    POST /api/auth/register - 用户注册

    Request body:
    {
        "email": "user@example.com",
        "password": "password123",
        "username": "username"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return bad_request('validation_failed')

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        username = data.get('username', '').strip()

        # 验证输入
        if not email or not password or not username:
            return bad_request('required_field_missing')

        # 验证邮箱格式
        if not validate_email(email):
            return bad_request('invalid_email')

        # 验证密码强度
        password_validation = validate_password(password)
        if password_validation:
            return bad_request(password_validation['code'], **password_validation)

        # 验证用户名
        if len(username) < 2 or len(username) > 50:
            return bad_request('invalid_format', field='username',
                             message=_('Username must be between 2 and 50 characters'))

        # 检查用户名格式
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fff]+$', username):
            return bad_request('invalid_format', field='username',
                             message=_('Username can only contain letters, numbers, underscores and Chinese characters'))

        # 注册用户
        user = auth_service.register_user(email, password, username)
        if not user:
            return bad_request('validation_failed',
                             message=_('Email already exists'))

        return success_response({
            'user': user.to_dict(),
            'message': _('User registered successfully. Please check your email for verification.')
        }, 'user_created', status_code=201)

    except Exception as e:
        db.session.rollback()
        return server_error('unknown_error')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/auth/login - 用户登录

    Request body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return bad_request('validation_failed')

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return bad_request('required_field_missing')

        # 认证用户
        user = auth_service.authenticate_user(email, password)
        if not user:
            return unauthorized('invalid_credentials')

        # 生成令牌
        tokens = auth_service.generate_tokens(user)

        # 更新最后登录时间
        user.update_last_login()

        return success_response({
            'user': user.to_dict(),
            'tokens': tokens
        }, 'login_successful')

    except Exception as e:
        return server_error('unknown_error')


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    POST /api/auth/refresh - 刷新访问令牌

    Request body:
    {
        "refresh_token": "refresh_token_here"
    }
    """
    try:
        data = request.get_json()

        if not data or 'refresh_token' not in data:
            return bad_request('validation_failed')

        refresh_token = data['refresh_token']
        tokens = auth_service.refresh_tokens(refresh_token)

        if not tokens:
            return unauthorized('invalid_credentials')

        return success_response({
            'tokens': tokens
        }, 'token_refreshed')

    except Exception as e:
        return server_error('unknown_error')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    POST /api/auth/logout - 用户登出

    Request body:
    {
        "refresh_token": "refresh_token_here"
    }
    """
    try:
        data = request.get_json()

        if data and 'refresh_token' in data:
            # 撤销指定的刷新令牌
            auth_service.revoke_refresh_token(data['refresh_token'])

        return success_response({
            'message': _('Logged out successfully')
        }, 'logout_successful')

    except Exception as e:
        return server_error('unknown_error')


@auth_bp.route('/logout-all', methods=['POST'])
def logout_all():
    """
    POST /api/auth/logout-all - 撤销用户所有会话
    """
    try:
        user = get_current_user()
        if not user:
            return unauthorized('unauthorized_access')

        # 撤销用户的所有刷新令牌
        count = auth_service.revoke_all_user_tokens(user.id)

        return success_response({
            'message': _('Logged out from all devices successfully'),
            'revoked_sessions': count
        }, 'logout_all_successful')

    except Exception as e:
        return server_error('unknown_error')


@auth_bp.route('/me', methods=['GET'])
def get_current_user_info():
    """
    GET /api/auth/me - 获取当前用户信息
    """
    try:
        user = get_current_user()
        if not user:
            return unauthorized('unauthorized_access')

        return success_response({
            'user': user.to_dict()
        })

    except Exception as e:
        return server_error('unknown_error')


@auth_bp.route('/me', methods=['PUT'])
def update_current_user():
    """
    PUT /api/auth/me - 更新当前用户信息

    Request body:
    {
        "username": "new_username",
        "preferred_language": "zh-CN"
    }
    """
    try:
        user = get_current_user()
        if not user:
            return unauthorized('unauthorized_access')

        data = request.get_json()
        if not data:
            return bad_request('validation_failed')

        # 更新用户名
        if 'username' in data:
            username = data['username'].strip()
            if len(username) < 2 or len(username) > 50:
                return bad_request('invalid_format', field='username',
                                 message=_('Username must be between 2 and 50 characters'))

            if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fff]+$', username):
                return bad_request('invalid_format', field='username',
                                 message=_('Username can only contain letters, numbers, underscores and Chinese characters'))

            # 检查用户名是否已被使用
            existing_user = User.query.filter(
                User.username == username,
                User.id != user.id
            ).first()
            if existing_user:
                return bad_request('validation_failed',
                                 message=_('Username already exists'))

            user.username = username

        # 更新语言偏好
        if 'preferred_language' in data:
            language = data['preferred_language']
            if language in ['zh-CN', 'en-US']:
                user.preferred_language = language

        db.session.commit()

        return success_response({
            'user': user.to_dict(),
            'message': _('Profile updated successfully')
        }, 'profile_updated')

    except Exception as e:
        db.session.rollback()
        return server_error('unknown_error')


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """
    POST /api/auth/change-password - 修改密码

    Request body:
    {
        "current_password": "current_password",
        "new_password": "new_password"
    }
    """
    try:
        user = get_current_user()
        if not user:
            return unauthorized('unauthorized_access')

        data = request.get_json()
        if not data:
            return bad_request('validation_failed')

        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')

        if not current_password or not new_password:
            return bad_request('required_field_missing')

        # 验证当前密码
        if user.auth_provider != 'email' or not user.password_hash:
            return bad_request('validation_failed',
                             message=_('OAuth users cannot change password'))

        if not auth_service.verify_password(current_password, user.password_hash):
            return bad_request('invalid_credentials',
                             message=_('Current password is incorrect'))

        # 验证新密码
        password_validation = validate_password(new_password)
        if password_validation:
            return bad_request(password_validation['code'], **password_validation)

        # 更新密码
        user.password_hash = auth_service.hash_password(new_password)
        db.session.commit()

        # 撤销所有现有令牌（强制重新登录）
        auth_service.revoke_all_user_tokens(user.id)

        return success_response({
            'message': _('Password changed successfully. Please login again.')
        }, 'password_changed')

    except Exception as e:
        db.session.rollback()
        return server_error('unknown_error')


@auth_bp.route('/verify-email', methods=['GET'])
def check_email_availability():
    """
    GET /api/auth/verify-email - 检查邮箱是否可用

    Query params:
    - email: 要检查的邮箱
    """
    try:
        email = request.args.get('email', '').strip().lower()
        if not email:
            return bad_request('required_field_missing')

        if not validate_email(email):
            return bad_request('invalid_email')

        existing_user = User.find_by_email(email)
        return success_response({
            'available': existing_user is None
        })

    except Exception as e:
        return server_error('unknown_error')


@auth_bp.route('/verify-username', methods=['GET'])
def check_username_availability():
    """
    GET /api/auth/verify-username - 检查用户名是否可用

    Query params:
    - username: 要检查的用户名
    """
    try:
        username = request.args.get('username', '').strip()
        if not username:
            return bad_request('required_field_missing')

        if len(username) < 2 or len(username) > 50:
            return bad_request('invalid_format', field='username',
                             message=_('Username must be between 2 and 50 characters'))

        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fff]+$', username):
            return bad_request('invalid_format', field='username',
                             message=_('Username can only contain letters, numbers, underscores and Chinese characters'))

        existing_user = User.query.filter_by(username=username).first()
        return success_response({
            'available': existing_user is None
        })

    except Exception as e:
        return server_error('unknown_error')