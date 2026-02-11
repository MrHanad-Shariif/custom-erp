"""Dashboard overview API: counts and chart data for the ERP home page."""
from decimal import Decimal

from flask import Blueprint
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.api.decorators import get_current_user
from app.extensions import db
from app.models import (
    Customer,
    Employee,
    Lead,
    Invoice,
    PurchaseOrder,
    Project,
    Warehouse,
    StockLevel,
)
from app.utils.response import api_success, api_error

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("", methods=["GET"])
@jwt_required()
def get_dashboard():
    """Return overview counts and chart data for the current organization."""
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    org_id = user.organization_id

    # Counts
    customers_count = Customer.query.filter_by(organization_id=org_id).count()
    employees_count = Employee.query.filter_by(organization_id=org_id).count()
    purchase_orders_count = PurchaseOrder.query.filter_by(organization_id=org_id).count()
    projects_count = Project.query.filter_by(organization_id=org_id).count()
    invoices_count = Invoice.query.filter_by(organization_id=org_id).count()
    leads_count = Lead.query.filter_by(organization_id=org_id).count()

    # Leads by status (for chart)
    leads_by_status = (
        db.session.query(Lead.status, func.count(Lead.id))
        .filter(Lead.organization_id == org_id)
        .group_by(Lead.status)
        .all()
    )
    leads_by_status_list = [{"status": s or "unknown", "count": c} for s, c in leads_by_status]

    # Stock by warehouse: sum quantity per warehouse
    stock_by_warehouse = (
        db.session.query(Warehouse.name, func.coalesce(func.sum(StockLevel.quantity), 0))
        .outerjoin(StockLevel, Warehouse.id == StockLevel.warehouse_id)
        .filter(Warehouse.organization_id == org_id)
        .group_by(Warehouse.id, Warehouse.name)
        .order_by(func.coalesce(func.sum(StockLevel.quantity), 0).desc())
        .limit(10)
        .all()
    )
    stock_by_warehouse_list = [
        {"warehouse_name": name, "total_quantity": float(q) if isinstance(q, Decimal) else q}
        for name, q in stock_by_warehouse
    ]

    data = {
        "customers_count": customers_count,
        "employees_count": employees_count,
        "purchase_orders_count": purchase_orders_count,
        "projects_count": projects_count,
        "invoices_count": invoices_count,
        "leads_count": leads_count,
        "leads_by_status": leads_by_status_list,
        "stock_by_warehouse": stock_by_warehouse_list,
    }
    return api_success(data=data)
