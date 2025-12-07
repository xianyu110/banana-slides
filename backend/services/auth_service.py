"""
Authentication Service - 认证服务
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, UserSession


class AuthService:
    """认证服务类"""

    def __init__(self, secret_key: str = None):
        """
        初始化认证服务

        Args:
            secret_key: JWT密钥，如果为None则从环境变量获取
        """
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.token_expiry = timedelta(minutes=15)  # Access Token 15分钟
        self.refresh_token_expiry = timedelta(days=7)  # Refresh Token 7天

    def hash_password(self, password: str) -> str:
        """
        密码哈希

        Args:
            password: 原始密码

        Returns:
            哈希后的密码
        """
        return generate_password_hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        验证密码

        Args:
            password: 原始密码
            hashed_password: 哈希后的密码

        Returns:
            是否匹配
        """
        return check_password_hash(hashed_password, password)

    def generate_tokens(self, user: User) -> Dict[str, str]:
        """
        生成访问令牌和刷新令牌

        Args:
            user: 用户对象

        Returns:
            包含access_token和refresh_token的字典
        """
        # 生成访问令牌
        access_token_payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow(),
            'type': 'access'
        }

        access_token = jwt.encode(
            access_token_payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        # 生成刷新令牌
        refresh_token = secrets.token_urlsafe(64)

        # 保存刷新令牌到数据库
        user_session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + self.refresh_token_expiry
        )
        db.session.add(user_session)
        db.session.commit()

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': int(self.token_expiry.total_seconds())
        }

    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证访问令牌

        Args:
            token: JWT访问令牌

        Returns:
            令牌载荷，验证失败返回None
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # 验证令牌类型
            if payload.get('type') != 'access':
                return None

            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def refresh_tokens(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        刷新访问令牌

        Args:
            refresh_token: 刷新令牌

        Returns:
            新的令牌字典，失败返回None
        """
        # 查找刷新令牌
        session = UserSession.find_by_refresh_token(refresh_token)
        if not session or not session.is_active or session.expires_at < datetime.utcnow():
            return None

        # 获取用户信息
        user = User.query.get(session.user_id)
        if not user or not user.is_active:
            return None

        # 生成新令牌
        tokens = self.generate_tokens(user)

        # 删除旧刷新令牌
        db.session.delete(session)
        db.session.commit()

        return tokens

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """
        撤销刷新令牌

        Args:
            refresh_token: 刷新令牌

        Returns:
            是否成功撤销
        """
        session = UserSession.find_by_refresh_token(refresh_token)
        if session:
            db.session.delete(session)
            db.session.commit()
            return True
        return False

    def revoke_all_user_tokens(self, user_id: str) -> int:
        """
        撤销用户的所有刷新令牌

        Args:
            user_id: 用户ID

        Returns:
            撤销的令牌数量
        """
        count = UserSession.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return count

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        邮箱密码认证

        Args:
            email: 邮箱
            password: 密码

        Returns:
            认证成功返回用户对象，失败返回None
        """
        user = User.find_by_email(email)
        if user and user.is_active and user.auth_provider == 'email':
            if self.verify_password(password, user.password_hash):
                return user
        return None

    def register_user(self, email: str, password: str, username: str) -> Optional[User]:
        """
        用户注册

        Args:
            email: 邮箱
            password: 密码
            username: 用户名

        Returns:
            注册成功返回用户对象，失败返回None
        """
        # 检查邮箱是否已存在
        if User.find_by_email(email):
            return None

        # 创建新用户
        user = User(
            email=email,
            password_hash=self.hash_password(password),
            username=username,
            auth_provider='email',
            email_verified=False
        )

        db.session.add(user)
        db.session.commit()

        return user

    def create_or_update_oauth_user(self, provider: str, provider_id: str,
                                    email: str, username: str = None,
                                    avatar_url: str = None) -> User:
        """
        创建或更新OAuth用户

        Args:
            provider: OAuth提供商 ('google' 或 'github')
            provider_id: 提供商用户ID
            email: 邮箱
            username: 用户名
            avatar_url: 头像URL

        Returns:
            用户对象
        """
        # 查找现有用户
        user = User.find_by_oauth_provider(provider, provider_id)

        if user:
            # 更新现有用户信息
            if email != user.email:
                # 检查新邮箱是否已被使用
                existing_user = User.find_by_email(email)
                if existing_user and existing_user.id != user.id:
                    raise ValueError(f"Email {email} is already in use")
                user.email = email

            user.username = username or user.username
            user.avatar_url = avatar_url or user.avatar_url
            user.email_verified = True  # OAuth用户邮箱视为已验证
            user.updated_at = datetime.utcnow()
        else:
            # 检查邮箱是否已被其他用户使用
            existing_user = User.find_by_email(email)
            if existing_user:
                # 如果邮箱已被使用，检查是否是同提供商
                if existing_user.auth_provider == provider and not existing_user.provider_id:
                    # 更新现有用户为OAuth用户
                    existing_user.provider_id = provider_id
                    existing_user.username = username or existing_user.username
                    existing_user.avatar_url = avatar_url or existing_user.avatar_url
                    existing_user.email_verified = True
                    existing_user.updated_at = datetime.utcnow()
                    user = existing_user
                else:
                    raise ValueError(f"Email {email} is already in use")
            else:
                # 创建新OAuth用户
                user = User(
                    email=email,
                    username=username or email.split('@')[0],
                    avatar_url=avatar_url,
                    auth_provider=provider,
                    provider_id=provider_id,
                    email_verified=True,
                    password_hash=None  # OAuth用户没有密码
                )
                db.session.add(user)

        db.session.commit()
        return user


# 全局认证服务实例
auth_service = AuthService()