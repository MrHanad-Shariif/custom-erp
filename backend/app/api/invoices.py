"""Invoices API (Finance / Customer 360)."""
from datetime import date
from decimal import Decimal

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.decorators import get_current_user, require_permission
from app.extensions import db
from app.models import Invoice, Customer, Project
from app.utils.response import api_success, api_error

invoices_bp = Blueprint("invoices", __name__)


def _parse_date(v):
    if v is None or v == "":
        return None
    try:
        return date.fromisoformat(str(v).split("T")[0])
    except Exception:
        return None


@invoices_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("finance.view")
def list_invoices():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    customer_id = request.args.get("customer_id")
    status = request.args.get("status")
    q = Invoice.query.filter_by(organization_id=user.organization_id)
    if customer_id:
        q = q.filter(Invoice.customer_id == customer_id)
    if status:
        q = q.filter(Invoice.status == status)
    q = q.order_by(Invoice.created_at.desc())
    return api_success(data=[i.to_dict() for i in q.all()])


@invoices_bp.route("/<invoice_id>", methods=["GET"])
@jwt_required()
@require_permission("finance.view")
def get_invoice(invoice_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    inv = db.session.get(Invoice, invoice_id)
    if not inv or inv.organization_id != user.organization_id:
        return api_error("Invoice not found", status_code=404)
    return api_success(data=inv.to_dict())


@invoices_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("finance.edit")
def create_invoice():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    customer_id = data.get("customer_id")
    if not customer_id:
        return api_error("customer_id is required", status_code=400)
    c = db.session.get(Customer, customer_id)
    if not c or c.organization_id != user.organization_id:
        return api_error("Customer not found", status_code=404)
    n = Invoice.query.filter_by(organization_id=user.organization_id).count() + 1
    number = data.get("number") or f"INV-{n:05d}"
    inv = Invoice(
        organization_id=user.organization_id,
        customer_id=customer_id,
        project_id=data.get("project_id"),
        number=number,
        status=data.get("status") or "draft",
        amount=Decimal(str(data.get("amount") or 0)),
        due_date=_parse_date(data.get("due_date")),
    )
    db.session.add(inv)
    db.session.commit()
    return api_success(data=inv.to_dict(), message="Invoice created", status_code=201)


@invoices_bp.route("/<invoice_id>", methods=["PUT"])
@jwt_required()
@require_permission("finance.edit")
def update_invoice(invoice_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    inv = db.session.get(Invoice, invoice_id)
    if not inv or inv.organization_id != user.organization_id:
        return api_error("Invoice not found", status_code=404)
    data = request.get_json() or {}
    if "status" in data:
        inv.status = data["status"]
    if "amount" in data:
        inv.amount = Decimal(str(data["amount"]))
    if "due_date" in data:
        inv.due_date = _parse_date(data["due_date"])
    if data.get("status") == "paid":
        inv.paid_at = date.today()
    db.session.commit()
    return api_success(data=inv.to_dict())
