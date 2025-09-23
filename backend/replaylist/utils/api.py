"""Standardized API response helpers."""

from datetime import datetime
from typing import Any, Dict, Optional


def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR", details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response: Dict[str, Any] = {
        "success": False,
        "error": {
            "message": message,
            "code": error_code,
            "timestamp": datetime.utcnow().isoformat(),
        },
    }
    if details:
        response["error"]["details"] = details
    return response


def create_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    response: Dict[str, Any] = {
        "success": True,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if data is not None:
        response["data"] = data
    return response


