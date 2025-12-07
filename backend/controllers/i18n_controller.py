"""
Internationalization Controller - 处理国际化相关的API
"""
from flask import Blueprint, request, jsonify, make_response
from flask_babel import gettext as _

i18n_bp = Blueprint('i18n', __name__, url_prefix='/api/i18n')


@i18n_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """
    GET /api/i18n/languages - 获取支持的语言列表

    Returns:
        支持的语言列表
    """
    languages = [
        {
            'code': 'zh-CN',
            'name': 'Chinese (Simplified)',
            'nativeName': '简体中文',
            'flag': '🇨🇳'
        },
        {
            'code': 'en-US',
            'name': 'English (US)',
            'nativeName': 'English',
            'flag': '🇺🇸'
        }
    ]

    return jsonify({
        'languages': languages,
        'default': 'zh-CN'
    })


@i18n_bp.route('/set-language', methods=['POST'])
def set_language():
    """
    POST /api/i18n/set-language - 设置用户语言偏好

    Request body:
    {
        "language": "zh-CN" | "en-US"
    }

    Returns:
        设置结果
    """
    try:
        data = request.get_json()

        if not data or 'language' not in data:
            return jsonify({
                'success': False,
                'error': _('Language is required')
            }), 400

        language = data['language']
        supported_languages = ['zh-CN', 'en-US']

        if language not in supported_languages:
            return jsonify({
                'success': False,
                'error': _('Unsupported language')
            }), 400

        # 设置Cookie
        response = make_response(jsonify({
            'success': True,
            'message': _('Language set successfully'),
            'language': language
        }))

        # 设置语言Cookie，有效期1年
        response.set_cookie(
            'language',
            language,
            max_age=365*24*60*60,  # 1年
            httponly=False,
            samesite='Lax'
        )

        return response

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@i18n_bp.route('/current', methods=['GET'])
def get_current_language():
    """
    GET /api/i18n/current - 获取当前语言设置

    Returns:
        当前语言信息
    """
    from flask import current_app
    from flask_babel import get_locale

    current_locale = get_locale()

    # 将locale转换为我们的语言代码
    language_map = {
        'zh': 'zh-CN',
        'en': 'en-US'
    }

    current_language = language_map.get(str(current_locale), 'zh-CN')

    return jsonify({
        'language': current_language,
        'locale': str(current_locale)
    })