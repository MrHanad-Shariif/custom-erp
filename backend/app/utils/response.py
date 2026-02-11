"""Standard API response helpers."""
from flask import jsonify


def api_success(data=None, message="", status_code=200):
    """Return standard success JSON: { status, data, message }."""
    return jsonify({
        "status": "success",
        "data": data if data is not None else {},
        "message": message,
    }), status_code


def api_error(message="An error occurred", errors=None, status_code=400):
    """Return standard error JSON: { status, message, errors? }."""
    payload = {
        "status": "error",
        "data": {},
        "message": message,
    }
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status_code
