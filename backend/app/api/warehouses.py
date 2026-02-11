"""Inventory Warehouses API."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.decorators import get_current_user, require_permission
from app.extensions import db
from app.models import Warehouse
from app.utils.response import api_success, api_error

warehouses_bp = Blueprint("warehouses", __name__)


@warehouses_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("inventory.view")
def list_warehouses():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    items = Warehouse.query.filter_by(organization_id=user.organization_id).order_by(Warehouse.name).all()
    return api_success(data=[w.to_dict() for w in items])


@warehouses_bp.route("/<warehouse_id>", methods=["GET"])
@jwt_required()
@require_permission("inventory.view")
def get_warehouse(warehouse_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    w = db.session.get(Warehouse, warehouse_id)
    if not w or w.organization_id != user.organization_id:
        return api_error("Warehouse not found", status_code=404)
    return api_success(data=w.to_dict())


@warehouses_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("inventory.edit")
def create_warehouse():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    code = (data.get("code") or "").strip()
    if not name:
        return api_error("name is required", status_code=400)
    if not code:
        code = f"WH-{Warehouse.query.filter_by(organization_id=user.organization_id).count() + 1:04d}"
    if Warehouse.query.filter_by(organization_id=user.organization_id, code=code).first():
        return api_error("Warehouse code already exists", status_code=400)
    w = Warehouse(
        organization_id=user.organization_id,
        name=name,
        code=code,
        address=(data.get("address") or "").strip(),
        is_default=bool(data.get("is_default", False)),
    )
    db.session.add(w)
    db.session.commit()
    return api_success(data=w.to_dict(), message="Warehouse created", status_code=201)


@warehouses_bp.route("/<warehouse_id>", methods=["PUT"])
@jwt_required()
@require_permission("inventory.edit")
def update_warehouse(warehouse_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    w = db.session.get(Warehouse, warehouse_id)
    if not w or w.organization_id != user.organization_id:
        return api_error("Warehouse not found", status_code=404)
    data = request.get_json() or {}
    for key in ("name", "code", "address"):
        if key in data and data[key] is not None:
            setattr(w, key, str(data[key]).strip())
    if "is_default" in data:
        w.is_default = bool(data["is_default"])
    db.session.commit()
    return api_success(data=w.to_dict())
