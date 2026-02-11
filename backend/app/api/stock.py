"""Inventory Stock levels API."""
from decimal import Decimal
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.decorators import get_current_user, require_permission
from app.extensions import db
from app.models import StockLevel, Warehouse, Sku
from app.utils.response import api_success, api_error

stock_bp = Blueprint("stock", __name__)


@stock_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("inventory.view")
def list_stock():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    warehouse_id = request.args.get("warehouse_id")
    q = db.session.query(StockLevel).join(Warehouse).filter(Warehouse.organization_id == user.organization_id)
    if warehouse_id:
        q = q.filter(StockLevel.warehouse_id == warehouse_id)
    levels = q.all()
    return api_success(data=[l.to_dict() for l in levels])


@stock_bp.route("/<stock_level_id>", methods=["GET"])
@jwt_required()
@require_permission("inventory.view")
def get_stock(stock_level_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    sl = db.session.get(StockLevel, stock_level_id)
    if not sl:
        return api_error("Stock level not found", status_code=404)
    if sl.warehouse.organization_id != user.organization_id:
        return api_error("Stock level not found", status_code=404)
    return api_success(data=sl.to_dict())


@stock_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("inventory.edit")
def create_or_update_stock():
    """Set or update stock level for a warehouse+sku. Creates record if not exists."""
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    warehouse_id = data.get("warehouse_id")
    sku_id = data.get("sku_id")
    quantity = data.get("quantity")
    reorder_point = data.get("reorder_point")
    if not warehouse_id or not sku_id:
        return api_error("warehouse_id and sku_id are required", status_code=400)
    wh = db.session.get(Warehouse, warehouse_id)
    sku = db.session.get(Sku, sku_id)
    if not wh or wh.organization_id != user.organization_id:
        return api_error("Warehouse not found", status_code=404)
    if not sku or sku.organization_id != user.organization_id:
        return api_error("SKU not found", status_code=404)
    sl = StockLevel.query.filter_by(warehouse_id=warehouse_id, sku_id=sku_id).first()
    if not sl:
        sl = StockLevel(warehouse_id=warehouse_id, sku_id=sku_id, quantity=Decimal(0), reserved_quantity=Decimal(0), reorder_point=Decimal(0))
        db.session.add(sl)
        db.session.flush()
    if quantity is not None:
        sl.quantity = Decimal(str(quantity))
    if reorder_point is not None:
        sl.reorder_point = Decimal(str(reorder_point))
    db.session.commit()
    return api_success(data=sl.to_dict())
