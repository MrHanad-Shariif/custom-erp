"""Roles API (org-scoped)."""
from flask import Blueprint, request

from flask_jwt_extended import jwt_required
from app.api.decorators import get_current_user, require_permission
from app.extensions import db
from app.models import Role, Permission, RolePermission, UserRole
from app.utils.response import api_success, api_error

roles_bp = Blueprint("roles", __name__)


@roles_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("auth.view")
def list_roles():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    roles = Role.query.filter_by(organization_id=user.organization_id).all()
    data = []
    for r in roles:
        d = r.to_dict()
        d["permission_ids"] = [rp.permission_id for rp in r.role_permissions]
        data.append(d)
    return api_success(data=data)


@roles_bp.route("/permissions", methods=["GET"])
@jwt_required()
@require_permission("auth.view")
def list_permissions():
    perms = Permission.query.all()
    return api_success(data=[p.to_dict() for p in perms])


@roles_bp.route("/<role_id>", methods=["GET"])
@jwt_required()
@require_permission("auth.view")
def get_role(role_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    r = db.session.get(Role, role_id)
    if not r or r.organization_id != user.organization_id:
        return api_error("Role not found", status_code=404)
    perm_ids = [rp.permission_id for rp in r.role_permissions]
    data = r.to_dict()
    data["permission_ids"] = perm_ids
    return api_success(data=data)


@roles_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("auth.edit")
def create_role():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip()
    permission_ids = data.get("permission_ids") or []
    if not name:
        return api_error("Role name is required", status_code=400)
    if Role.query.filter_by(organization_id=user.organization_id, name=name).first():
        return api_error("Role with this name already exists", status_code=400)
    r = Role(organization_id=user.organization_id, name=name, description=description)
    db.session.add(r)
    db.session.flush()
    for pid in permission_ids:
        if Permission.query.get(pid):
            db.session.add(RolePermission(role_id=r.id, permission_id=pid))
    db.session.commit()
    data_out = r.to_dict()
    data_out["permission_ids"] = [rp.permission_id for rp in r.role_permissions]
    return api_success(data=data_out, message="Role created", status_code=201)


@roles_bp.route("/<role_id>", methods=["PUT"])
@jwt_required()
@require_permission("auth.edit")
def update_role(role_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    r = db.session.get(Role, role_id)
    if not r or r.organization_id != user.organization_id:
        return api_error("Role not found", status_code=404)
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if name:
        r.name = name
    if "description" in data:
        r.description = (data.get("description") or "").strip()
    permission_ids = data.get("permission_ids")
    if permission_ids is not None:
        RolePermission.query.filter_by(role_id=r.id).delete()
        for pid in permission_ids:
            if Permission.query.get(pid):
                db.session.add(RolePermission(role_id=r.id, permission_id=pid))
    db.session.commit()
    data_out = r.to_dict()
    data_out["permission_ids"] = [rp.permission_id for rp in r.role_permissions]
    return api_success(data=data_out, message="Role updated")


@roles_bp.route("/<role_id>", methods=["DELETE"])
@jwt_required()
@require_permission("auth.edit")
def delete_role(role_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    r = db.session.get(Role, role_id)
    if not r or r.organization_id != user.organization_id:
        return api_error("Role not found", status_code=404)
    db.session.delete(r)
    db.session.commit()
    return api_success(message="Role deleted")
