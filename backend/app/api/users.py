"""Users API (org-scoped)."""
from flask import Blueprint, request

from flask_jwt_extended import jwt_required
from app.api.decorators import get_current_user, require_permission
from app.extensions import db
from app.models import User, UserRole, Role
from app.utils.response import api_success, api_error
from app.utils.auth_utils import hash_password

users_bp = Blueprint("users", __name__)


def _user_to_dict(u):
    d = u.to_dict()
    d["role_ids"] = [ur.role_id for ur in u.user_roles]
    return d


@users_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("auth.view")
def list_users():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    org_id = user.organization_id
    users = User.query.filter_by(organization_id=org_id).all()
    return api_success(data=[_user_to_dict(u) for u in users])


@users_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
@require_permission("auth.view")
def get_user(user_id):
    current = get_current_user()
    if not current:
        return api_error("Unauthorized", status_code=401)
    u = db.session.get(User, user_id)
    if not u or u.organization_id != current.organization_id:
        return api_error("User not found", status_code=404)
    return api_success(data=_user_to_dict(u))


@users_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("auth.edit")
def create_user():
    current = get_current_user()
    if not current:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    full_name = (data.get("full_name") or data.get("fullName") or "").strip()
    password = data.get("password")
    role_ids = data.get("role_ids") or []

    if not email:
        return api_error("Email is required", status_code=400)
    if not full_name:
        return api_error("Full name is required", status_code=400)
    if not password:
        return api_error("Password is required for new user", status_code=400)
    if User.query.filter_by(email=email).first():
        return api_error("Email already registered", status_code=400)

    u = User(
        organization_id=current.organization_id,
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        is_active=data.get("is_active", True),
    )
    db.session.add(u)
    db.session.flush()
    for role_id in role_ids:
        r = db.session.get(Role, role_id)
        if r and r.organization_id == current.organization_id:
            db.session.add(UserRole(user_id=u.id, role_id=role_id))
    db.session.commit()
    return api_success(data=_user_to_dict(u), message="User created", status_code=201)


@users_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
@require_permission("auth.edit")
def update_user(user_id):
    current = get_current_user()
    if not current:
        return api_error("Unauthorized", status_code=401)
    u = db.session.get(User, user_id)
    if not u or u.organization_id != current.organization_id:
        return api_error("User not found", status_code=404)
    data = request.get_json() or {}
    full_name = (data.get("full_name") or data.get("fullName") or "").strip()
    if full_name:
        u.full_name = full_name
    if "is_active" in data:
        u.is_active = bool(data["is_active"])
    password = data.get("password")
    if password:
        u.password_hash = hash_password(password)
    role_ids = data.get("role_ids")
    if role_ids is not None:
        UserRole.query.filter_by(user_id=u.id).delete()
        for role_id in role_ids:
            r = db.session.get(Role, role_id)
            if r and r.organization_id == current.organization_id:
                db.session.add(UserRole(user_id=u.id, role_id=role_id))
    db.session.commit()
    return api_success(data=_user_to_dict(u), message="User updated")


@users_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
@require_permission("auth.edit")
def delete_user(user_id):
    current = get_current_user()
    if not current:
        return api_error("Unauthorized", status_code=401)
    if user_id == current.id:
        return api_error("Cannot delete your own account", status_code=400)
    u = db.session.get(User, user_id)
    if not u or u.organization_id != current.organization_id:
        return api_error("User not found", status_code=404)
    db.session.delete(u)
    db.session.commit()
    return api_success(message="User deleted")


@users_bp.route("/<user_id>/roles", methods=["PUT"])
@jwt_required()
@require_permission("auth.edit")
def set_user_roles(user_id):
    current = get_current_user()
    if not current:
        return api_error("Unauthorized", status_code=401)
    u = db.session.get(User, user_id)
    if not u or u.organization_id != current.organization_id:
        return api_error("User not found", status_code=404)
    data = request.get_json() or {}
    role_ids = data.get("role_ids") or []
    UserRole.query.filter_by(user_id=u.id).delete()
    for role_id in role_ids:
        r = db.session.get(Role, role_id)
        if r and r.organization_id == current.organization_id:
            db.session.add(UserRole(user_id=u.id, role_id=role_id))
    db.session.commit()
    return api_success(data=_user_to_dict(u), message="Roles updated")
