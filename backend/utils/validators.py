"""
Data validation utilities
"""
import re
from typing import Set, Dict, Optional, Any

# Project status states
PROJECT_STATUSES = {
    'DRAFT',
    'OUTLINE_GENERATED',
    'DESCRIPTIONS_GENERATED',
    'GENERATING_IMAGES',
    'COMPLETED'
}

# Page status states
PAGE_STATUSES = {
    'DRAFT',
    'DESCRIPTION_GENERATED',
    'GENERATING',
    'COMPLETED',
    'FAILED'
}

# Task status states
TASK_STATUSES = {
    'PENDING',
    'PROCESSING',
    'COMPLETED',
    'FAILED'
}

# Task types
TASK_TYPES = {
    'GENERATE_DESCRIPTIONS',
    'GENERATE_IMAGES'
}


def validate_project_status(status: str) -> bool:
    """Validate project status"""
    return status in PROJECT_STATUSES


def validate_page_status(status: str) -> bool:
    """Validate page status"""
    return status in PAGE_STATUSES


def validate_task_status(status: str) -> bool:
    """Validate task status"""
    return status in TASK_STATUSES


def validate_task_type(task_type: str) -> bool:
    """Validate task type"""
    return task_type in TASK_TYPES


def allowed_file(filename: str, allowed_extensions: Set[str]) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


# User authentication validators
def validate_email(email: str) -> bool:
    """
    验证邮箱格式

    Args:
        email: 邮箱地址

    Returns:
        是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> Optional[Dict[str, Any]]:
    """
    验证密码强度

    Args:
        password: 密码

    Returns:
        验证失败返回错误信息，成功返回None
    """
    errors = []

    # 检查长度
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    elif len(password) > 128:
        errors.append("Password must be less than 128 characters long")

    # 检查是��包含字母
    if not re.search(r'[a-zA-Z]', password):
        errors.append("Password must contain at least one letter")

    # 检查是否包含数字
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")

    # 可选：检查特殊字符
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     errors.append("Password must contain at least one special character")

    if errors:
        return {
            'code': 'password_too_short',
            'message': '; '.join(errors)
        }

    return None


def validate_username(username: str) -> Optional[Dict[str, Any]]:
    """
    验证用户名

    Args:
        username: 用户名

    Returns:
        验证失败返回错误信息，成功返回None
    """
    if len(username) < 2:
        return {
            'code': 'username_too_short',
            'message': 'Username must be at least 2 characters long'
        }

    if len(username) > 50:
        return {
            'code': 'username_too_long',
            'message': 'Username must be less than 50 characters long'
        }

    # 允许字母、数字、下划线和中文字符
    if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fff]+$', username):
        return {
            'code': 'username_invalid_format',
            'message': 'Username can only contain letters, numbers, underscores and Chinese characters'
        }

    return None


def validate_project_name(name: str) -> Optional[Dict[str, Any]]:
    """
    验证项目名称

    Args:
        name: 项目名称

    Returns:
        验证失败返回错误信息，成功返回None
    """
    if not name or not name.strip():
        return {
            'code': 'project_name_required',
            'message': 'Project name is required'
        }

    name = name.strip()

    if len(name) < 1:
        return {
            'code': 'project_name_too_short',
            'message': 'Project name cannot be empty'
        }

    if len(name) > 100:
        return {
            'code': 'project_name_too_long',
            'message': 'Project name must be less than 100 characters long'
        }

    return None


def validate_idea_prompt(prompt: str) -> Optional[Dict[str, Any]]:
    """
    验证想法提示词

    Args:
        prompt: 想法提示词

    Returns:
        验证失败返回错误信息，成功返回None
    """
    if not prompt or not prompt.strip():
        return {
            'code': 'idea_prompt_required',
            'message': 'Idea prompt is required'
        }

    prompt = prompt.strip()

    if len(prompt) < 10:
        return {
            'code': 'idea_prompt_too_short',
            'message': 'Idea prompt must be at least 10 characters long'
        }

    if len(prompt) > 1000:
        return {
            'code': 'idea_prompt_too_long',
            'message': 'Idea prompt must be less than 1000 characters long'
        }

    return None


def validate_file_size(file_size: int, max_size_mb: int = 16) -> Optional[Dict[str, Any]]:
    """
    验证文件大小

    Args:
        file_size: 文件大小（字节）
        max_size_mb: 最大允许大小（MB）

    Returns:
        验证失败返回错误信息，成功返回None
    """
    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        return {
            'code': 'file_too_large',
            'message': f'File size must be less than {max_size_mb}MB'
        }

    return None


def validate_file_extension(filename: str, allowed_extensions: list) -> Optional[Dict[str, Any]]:
    """
    验证文件扩展名

    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名列表

    Returns:
        验证失败返回错误信息，成功返回None
    """
    if not filename:
        return {
            'code': 'filename_required',
            'message': 'Filename is required'
        }

    extension = filename.lower().split('.')[-1]
    if extension not in allowed_extensions:
        return {
            'code': 'invalid_file_type',
            'message': f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
        }

    return None

