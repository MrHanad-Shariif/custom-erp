"""RBAC and auth decorators."""
from functools import wraps

from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

from app.extensions import db
from app.models import User
from app.utils.response import api_error


def require_permission(permission_id):
    """Decorator: require JWT and that the user has the given permission."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            if not user_id:
                return api_error("Invalid token", status_code=401)
            user = db.session.get(User, user_id)
            if not user or not user.is_active:
                return api_error("User not found or inactive", status_code=401)
            if permission_id and permission_id not in user.get_permission_ids():
                return api_error("Insufficient permissions", status_code=403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(*permission_ids):
    """Decorator: require JWT and that the user has at least one of the given permissions."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            if not user_id:
                return api_error("Invalid token", status_code=401)
            user = db.session.get(User, user_id)
            if not user or not user.is_active:
                return api_error("User not found or inactive", status_code=401)
            if permission_ids:
                user_perms = user.get_permission_ids()
                if not any(p in user_perms for p in permission_ids):
                    return api_error("Insufficient permissions", status_code=403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user():
    """After verify_jwt_in_request(), return the current User or None."""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return None
        return db.session.get(User, user_id)
    except Exception:
        return None
