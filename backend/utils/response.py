"""
Unified response format utilities with i18n support
"""
from flask import jsonify
from flask_babel import gettext as _
from typing import Any, Dict, Optional
from .i18n import get_error_message, get_success_message


def success_response(data: Any = None, message_key: str = None, status_code: int = 200, **kwargs):
    """
    Generate a successful response with i18n support

    Args:
        data: Response data
        message_key: Success message key for i18n
        status_code: HTTP status code
        **kwargs: Parameters for message interpolation

    Returns:
        Flask response with JSON format
    """
    if message_key:
        message = get_success_message(message_key, **kwargs)
    else:
        message = _("Success")

    response = {
        "success": True,
        "message": message
    }

    if data is not None:
        response["data"] = data

    return jsonify(response), status_code


def error_response(error_code: str, message_key: str = None, status_code: int = 400, **kwargs):
    """
    Generate an error response with i18n support

    Args:
        error_code: Error code identifier
        message_key: Error message key for i18n
        status_code: HTTP status code
        **kwargs: Parameters for message interpolation

    Returns:
        Flask response with JSON format
    """
    if message_key:
        message = get_error_message(message_key, **kwargs)
    else:
        message = _("An error occurred")

    return jsonify({
        "success": False,
        "error": {
            "code": error_code,
            "message": message
        }
    }), status_code


# Common error responses with i18n
def bad_request(message_key: str = "validation_failed", **kwargs):
    return error_response("INVALID_REQUEST", message_key, 400, **kwargs)


def not_found(resource: str = "Resource"):
    return error_response(f"{resource.upper()}_NOT_FOUND", f"{resource.lower()}_not_found", 404)


def invalid_status(message_key: str = "validation_failed", **kwargs):
    return error_response("INVALID_PROJECT_STATUS", message_key, 400, **kwargs)


def ai_service_error(message_key: str = "ai_service_unavailable", **kwargs):
    return error_response("AI_SERVICE_ERROR", message_key, 503, **kwargs)


def rate_limit_error(message_key: str = "unknown_error", **kwargs):
    return error_response("RATE_LIMIT_EXCEEDED", message_key, 429, **kwargs)


def unauthorized(message_key: str = "unauthorized_access", **kwargs):
    return error_response("UNAUTHORIZED", message_key, 401, **kwargs)


def forbidden(message_key: str = "access_denied", **kwargs):
    return error_response("FORBIDDEN", message_key, 403, **kwargs)


def server_error(message_key: str = "server_error", **kwargs):
    return error_response("SERVER_ERROR", message_key, 500, **kwargs)

