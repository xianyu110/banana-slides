"""
Settings Controller - API configuration management
"""
import os
from flask import Blueprint, request, jsonify
from models import db
from models.settings import Settings

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


@settings_bp.route('/api-config', methods=['GET'])
def get_api_config():
    """Get current API configuration"""
    try:
        # Get from database or fall back to environment variables
        config = {
            'text_api_key': Settings.get_value('GOOGLE_API_KEY', os.getenv('GOOGLE_API_KEY', '')),
            'text_api_base': Settings.get_value('GOOGLE_API_BASE', os.getenv('GOOGLE_API_BASE', '')),
            'image_api_key': Settings.get_value('GOOGLE_IMAGE_API_KEY', os.getenv('GOOGLE_IMAGE_API_KEY', '')),
            'image_api_base': Settings.get_value('GOOGLE_IMAGE_API_BASE', os.getenv('GOOGLE_IMAGE_API_BASE', '')),
        }

        # Mask API keys for security (show only last 8 characters)
        if config['text_api_key']:
            config['text_api_key_masked'] = '***' + config['text_api_key'][-8:] if len(config['text_api_key']) > 8 else '***'
        if config['image_api_key']:
            config['image_api_key_masked'] = '***' + config['image_api_key'][-8:] if len(config['image_api_key']) > 8 else '***'

        return jsonify(config), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/api-config', methods=['PUT'])
def update_api_config():
    """Update API configuration"""
    try:
        data = request.json

        # Update settings in database
        if 'text_api_key' in data:
            Settings.set_value('GOOGLE_API_KEY', data['text_api_key'])
        if 'text_api_base' in data:
            Settings.set_value('GOOGLE_API_BASE', data['text_api_base'])
        if 'image_api_key' in data:
            Settings.set_value('GOOGLE_IMAGE_API_KEY', data['image_api_key'])
        if 'image_api_base' in data:
            Settings.set_value('GOOGLE_IMAGE_API_BASE', data['image_api_base'])

        return jsonify({'message': 'API configuration updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/api-presets', methods=['GET'])
def get_api_presets():
    """Get predefined API configuration presets"""
    # Import built-in defaults
    from default_config import DEFAULT_TEXT_API_KEY, DEFAULT_IMAGE_API_KEY

    # Get default keys from environment or use built-in defaults
    default_text_key = os.getenv('DEFAULT_TEXT_API_KEY', DEFAULT_TEXT_API_KEY)
    default_image_key = os.getenv('DEFAULT_IMAGE_API_KEY', DEFAULT_IMAGE_API_KEY)

    presets = [
        {
            'id': 'builtin',
            'name': '🎁 内置配置（推荐新手）',
            'description': '使用系统内置的API密钥，开箱即用',
            'config': {
                'text_api_base': 'https://generativelanguage.googleapis.com',
                'image_api_base': 'https://apipro.maynor1024.live',
                'requires_key': False,
                'text_api_key': default_text_key,
                'image_api_key': default_image_key,
            }
        },
        {
            'id': 'official',
            'name': '官方 Google API（全部）',
            'description': '使用官方 Google Gemini API，稳定可靠',
            'config': {
                'text_api_base': 'https://generativelanguage.googleapis.com',
                'image_api_base': 'https://generativelanguage.googleapis.com',
                'requires_key': True,
            }
        },
        {
            'id': 'hybrid_apipro',
            'name': '混合模式 - apipro.maynor1024.live',
            'description': '文本使用官方API，图片使用第三方代理',
            'config': {
                'text_api_base': 'https://generativelanguage.googleapis.com',
                'image_api_base': 'https://apipro.maynor1024.live',
                'requires_key': True,
                'image_key_format': 'sk-xxx'
            }
        },
        {
            'id': 'hybrid_nextai',
            'name': '混合模式 - api.nextaicore.com',
            'description': '文本使用官方API，图片使用第三方代理（可能不支持图片生成）',
            'config': {
                'text_api_base': 'https://generativelanguage.googleapis.com',
                'image_api_base': 'https://api.nextaicore.com',
                'requires_key': True,
                'image_key_format': 'sk-xxx',
                'warning': '此API可能不支持图片生成'
            }
        },
    ]

    return jsonify(presets), 200
