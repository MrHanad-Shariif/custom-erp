"""Purchase Orders API."""
from datetime import date
from decimal import Decimal

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.decorators import get_current_user, require_permission
from app.extensions import db
from app.models import PurchaseOrder, PurchaseOrderLine, Warehouse, Sku
from app.utils.response import api_success, api_error

purchase_orders_bp = Blueprint("purchase_orders", __name__)


def _parse_date(v):
    if v is None or v == "":
        return None
    try:
        return date.fromisoformat(str(v).split("T")[0])
    except Exception:
        return None


@purchase_orders_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("inventory.view")
def list_pos():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    pos = PurchaseOrder.query.filter_by(organization_id=user.organization_id).order_by(PurchaseOrder.created_at.desc()).all()
    return api_success(data=[p.to_dict() for p in pos])


@purchase_orders_bp.route("/<po_id>", methods=["GET"])
@jwt_required()
@require_permission("inventory.view")
def get_po(po_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    po = db.session.get(PurchaseOrder, po_id)
    if not po or po.organization_id != user.organization_id:
        return api_error("Purchase order not found", status_code=404)
    data = po.to_dict()
    data["lines"] = [l.to_dict() for l in po.lines]
    return api_success(data=data)


@purchase_orders_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("inventory.edit")
def create_po():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    warehouse_id = data.get("warehouse_id")
    if not warehouse_id:
        return api_error("warehouse_id is required", status_code=400)
    wh = db.session.get(Warehouse, warehouse_id)
    if not wh or wh.organization_id != user.organization_id:
        return api_error("Warehouse not found", status_code=404)
    n = PurchaseOrder.query.filter_by(organization_id=user.organization_id).count() + 1
    number = data.get("number") or f"PO-{n:05d}"
    po = PurchaseOrder(
        organization_id=user.organization_id,
        warehouse_id=warehouse_id,
        number=number,
        status=data.get("status") or "draft",
        order_date=_parse_date(data.get("order_date")),
        expected_date=_parse_date(data.get("expected_date")),
        created_by_user_id=user.id,
    )
    db.session.add(po)
    db.session.flush()
    for line in data.get("lines") or []:
        sku_id = line.get("sku_id")
        qty = Decimal(str(line.get("quantity_ordered") or line.get("quantity") or 0))
        if sku_id and qty > 0:
            db.session.add(PurchaseOrderLine(
                purchase_order_id=po.id,
                sku_id=sku_id,
                quantity_ordered=qty,
                quantity_received=Decimal(0),
                unit_price=Decimal(str(line.get("unit_price") or 0)),
            ))
    db.session.commit()
    data = po.to_dict()
    data["lines"] = [l.to_dict() for l in po.lines]
    return api_success(data=data, message="Purchase order created", status_code=201)
