"""Inventory SKUs API."""
from decimal import Decimal
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.decorators import get_current_user, require_permission
from app.extensions import db
from app.models import Sku
from app.utils.response import api_success, api_error

skus_bp = Blueprint("skus", __name__)


@skus_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("inventory.view")
def list_skus():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    items = Sku.query.filter_by(organization_id=user.organization_id).order_by(Sku.code).all()
    return api_success(data=[s.to_dict() for s in items])


@skus_bp.route("/<sku_id>", methods=["GET"])
@jwt_required()
@require_permission("inventory.view")
def get_sku(sku_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    s = db.session.get(Sku, sku_id)
    if not s or s.organization_id != user.organization_id:
        return api_error("SKU not found", status_code=404)
    return api_success(data=s.to_dict())


@skus_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("inventory.edit")
def create_sku():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    code = (data.get("code") or "").strip()
    if not name:
        return api_error("name is required", status_code=400)
    if not code:
        code = f"SKU-{Sku.query.filter_by(organization_id=user.organization_id).count() + 1:04d}"
    if Sku.query.filter_by(organization_id=user.organization_id, code=code).first():
        return api_error("SKU code already exists", status_code=400)
    s = Sku(
        organization_id=user.organization_id,
        name=name,
        code=code,
        unit=(data.get("unit") or "unit").strip(),
        reorder_point=Decimal(str(data.get("reorder_point") or 0)),
        reorder_quantity=Decimal(str(data.get("reorder_quantity") or 0)),
        is_active=data.get("is_active", True),
    )
    db.session.add(s)
    db.session.commit()
    return api_success(data=s.to_dict(), message="SKU created", status_code=201)


@skus_bp.route("/<sku_id>", methods=["PUT"])
@jwt_required()
@require_permission("inventory.edit")
def update_sku(sku_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    s = db.session.get(Sku, sku_id)
    if not s or s.organization_id != user.organization_id:
        return api_error("SKU not found", status_code=404)
    data = request.get_json() or {}
    for key in ("name", "code", "unit"):
        if key in data and data[key] is not None:
            setattr(s, key, str(data[key]).strip())
    if "reorder_point" in data:
        s.reorder_point = Decimal(str(data["reorder_point"]))
    if "reorder_quantity" in data:
        s.reorder_quantity = Decimal(str(data["reorder_quantity"]))
    if "is_active" in data:
        s.is_active = bool(data["is_active"])
    db.session.commit()
    return api_success(data=s.to_dict())
