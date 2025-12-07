"""
国际化工具模块
"""
from flask_babel import gettext as _
from typing import Dict, Any

def get_error_message(key: str, **kwargs) -> str:
    """
    获取本地化的错误消息

    Args:
        key: 错误消息键
        **kwargs: 插值参数

    Returns:
        本地化的错误消息
    """
    error_messages: Dict[str, str] = {
        # 项目相关错误
        'project_not_found': _('Project not found'),
        'project_creation_failed': _('Failed to create project'),
        'project_update_failed': _('Failed to update project'),
        'project_delete_failed': _('Failed to delete project'),

        # 页面相关错误
        'page_not_found': _('Page not found'),
        'page_creation_failed': _('Failed to create page'),
        'page_update_failed': _('Failed to update page'),
        'page_delete_failed': _('Failed to delete page'),

        # 任务相关错误
        'task_not_found': _('Task not found'),
        'task_creation_failed': _('Failed to create task'),
        'task_failed': _('Task execution failed'),

        # 文件相关错误
        'file_not_found': _('File not found'),
        'file_upload_failed': _('File upload failed'),
        'file_size_exceeded': _('File size exceeded'),
        'file_type_not_allowed': _('File type not allowed'),

        # AI服务相关错误
        'ai_service_unavailable': _('AI service temporarily unavailable'),
        'ai_generation_failed': _('AI generation failed'),
        'ai_model_not_available': _('AI model not available'),
        'ai_quota_exceeded': _('AI quota exceeded'),

        # 认证相关错误
        'unauthorized_access': _('Unauthorized access'),
        'invalid_credentials': _('Invalid credentials'),
        'session_expired': _('Session expired'),

        # 验证相关错误
        'validation_failed': _('Validation failed'),
        'required_field_missing': _('Required field missing'),
        'invalid_format': _('Invalid format'),

        # 系统相关错误
        'server_error': _('Internal server error'),
        'database_error': _('Database error'),
        'network_error': _('Network connection error'),
        'service_unavailable': _('Service temporarily unavailable'),

        # 通用错误
        'unknown_error': _('An unknown error occurred'),
        'operation_failed': _('Operation failed'),
        'access_denied': _('Access denied'),
    }

    message = error_messages.get(key, key)

    # 支持插值
    try:
        if kwargs:
            return message % kwargs
        return message
    except (KeyError, TypeError):
        # 如果插值失败，返回原始消息
        return message

def get_success_message(key: str, **kwargs) -> str:
    """
    获取本地化的成功消息

    Args:
        key: 成功消息键
        **kwargs: 插值参数

    Returns:
        本地化的成功消息
    """
    success_messages: Dict[str, str] = {
        'project_created': _('Project created successfully'),
        'project_updated': _('Project updated successfully'),
        'project_deleted': _('Project deleted successfully'),

        'page_created': _('Page created successfully'),
        'page_updated': _('Page updated successfully'),
        'page_deleted': _('Page deleted successfully'),

        'file_uploaded': _('File uploaded successfully'),
        'file_deleted': _('File deleted successfully'),

        'task_completed': _('Task completed successfully'),

        'settings_saved': _('Settings saved successfully'),

        'operation_completed': _('Operation completed successfully'),
    }

    message = success_messages.get(key, key)

    # 支持插值
    try:
        if kwargs:
            return message % kwargs
        return message
    except (KeyError, TypeError):
        # 如果插值失败，返回原始消息
        return message