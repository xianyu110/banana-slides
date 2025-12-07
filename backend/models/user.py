"""
User Model - 用户模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from models import db
import uuid


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # OAuth用户可为空
    username = Column(String(80), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    auth_provider = Column(String(20), default='email')  # 'email', 'google', 'github'
    provider_id = Column(String(100), nullable=True)  # OAuth提供商的用户ID
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    # 用户偏好设置
    preferred_language = Column(String(10), default='zh-CN')

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self, include_sensitive=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'avatar_url': self.avatar_url,
            'auth_provider': self.auth_provider,
            'email_verified': self.email_verified,
            'is_active': self.is_active,
            'preferred_language': self.preferred_language,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_sensitive:
            data['provider_id'] = self.provider_id

        return data

    @staticmethod
    def find_by_email(email):
        """根据邮箱查找用户"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def find_by_oauth_provider(provider, provider_id):
        """根据OAuth提供商和ID查找用户"""
        return User.query.filter_by(
            auth_provider=provider,
            provider_id=provider_id
        ).first()

    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login_at = datetime.utcnow()
        db.session.commit()


class UserSession(db.Model):
    """用户会话模型（用于JWT刷新token管理）"""
    __tablename__ = 'user_sessions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    refresh_token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # 关系
    user = db.relationship('User', backref=db.backref('sessions', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<UserSession {self.user_id}>'

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

    @staticmethod
    def find_by_refresh_token(refresh_token):
        """根据refresh token查找会话"""
        return UserSession.query.filter_by(
            refresh_token=refresh_token,
            is_active=True
        ).first()

    @staticmethod
    def cleanup_expired_sessions():
        """清理过期的会话"""
        UserSession.query.filter(
            UserSession.expires_at < datetime.utcnow()
        ).delete()
        db.session.commit()