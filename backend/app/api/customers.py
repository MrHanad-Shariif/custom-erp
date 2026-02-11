"""CRM Customers API + Customer 360."""
from flask import Blueprint, request

from flask_jwt_extended import jwt_required
from app.api.decorators import get_current_user, require_permission
from app.extensions import db
from app.models import Customer, CustomerContact, Project, Invoice
from app.utils.response import api_success, api_error

customers_bp = Blueprint("customers", __name__)


@customers_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("crm.view")
def list_customers():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    customers = Customer.query.filter_by(organization_id=user.organization_id).order_by(Customer.name).all()
    return api_success(data=[c.to_dict() for c in customers])


@customers_bp.route("/<customer_id>", methods=["GET"])
@jwt_required()
@require_permission("crm.view")
def get_customer(customer_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    c = db.session.get(Customer, customer_id)
    if not c or c.organization_id != user.organization_id:
        return api_error("Customer not found", status_code=404)
    return api_success(data=c.to_dict())


@customers_bp.route("/<customer_id>/360", methods=["GET"])
@jwt_required()
@require_permission("crm.view")
def customer_360(customer_id):
    """Single view: customer + projects + unpaid invoices."""
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    c = db.session.get(Customer, customer_id)
    if not c or c.organization_id != user.organization_id:
        return api_error("Customer not found", status_code=404)
    projects = Project.query.filter_by(customer_id=c.id).all()
    unpaid_invoices = Invoice.query.filter_by(customer_id=c.id).filter(Invoice.status != "paid").all()
    return api_success(
        data={
            "customer": c.to_dict(),
            "contacts": [x.to_dict() for x in c.contacts],
            "projects": [p.to_dict() for p in projects],
            "unpaid_invoices": [i.to_dict() for i in unpaid_invoices],
        }
    )


@customers_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("crm.edit")
def create_customer():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    code = (data.get("code") or "").strip()
    if not name:
        return api_error("name is required", status_code=400)
    if not code:
        code = f"CUST-{Customer.query.filter_by(organization_id=user.organization_id).count() + 1:04d}"
    if Customer.query.filter_by(organization_id=user.organization_id, code=code).first():
        return api_error("Customer code already exists", status_code=400)
    c = Customer(
        organization_id=user.organization_id,
        name=name,
        code=code,
        tax_id=(data.get("tax_id") or "").strip(),
        billing_address=(data.get("billing_address") or "").strip(),
        shipping_address=(data.get("shipping_address") or "").strip(),
    )
    db.session.add(c)
    db.session.commit()
    return api_success(data=c.to_dict(), message="Customer created", status_code=201)


@customers_bp.route("/<customer_id>", methods=["PUT"])
@jwt_required()
@require_permission("crm.edit")
def update_customer(customer_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    c = db.session.get(Customer, customer_id)
    if not c or c.organization_id != user.organization_id:
        return api_error("Customer not found", status_code=404)
    data = request.get_json() or {}
    for key in ("name", "code", "tax_id", "billing_address", "shipping_address"):
        if key in data and data[key] is not None:
            setattr(c, key, str(data[key]).strip())
    db.session.commit()
    return api_success(data=c.to_dict())
