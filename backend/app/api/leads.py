"""CRM Leads API."""
from decimal import Decimal
from flask import Blueprint, request

from flask_jwt_extended import jwt_required
from app.api.decorators import get_current_user, require_permission
from app.extensions import db
from app.models import Lead, Customer, Project
from app.utils.response import api_success, api_error

leads_bp = Blueprint("leads", __name__)


def _lead_from_json(data):
    return {
        "company_name": (data.get("company_name") or "").strip() or None,
        "contact_name": (data.get("contact_name") or "").strip(),
        "email": (data.get("email") or "").strip(),
        "phone": (data.get("phone") or "").strip(),
        "status": (data.get("status") or "prospect").strip(),
        "stage": (data.get("stage") or "").strip(),
        "value": data.get("value"),
    }


@leads_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("crm.view")
def list_leads():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    leads = Lead.query.filter_by(organization_id=user.organization_id).order_by(Lead.created_at.desc()).all()
    return api_success(data=[l.to_dict() for l in leads])


@leads_bp.route("/<lead_id>", methods=["GET"])
@jwt_required()
@require_permission("crm.view")
def get_lead(lead_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    lead = db.session.get(Lead, lead_id)
    if not lead or lead.organization_id != user.organization_id:
        return api_error("Lead not found", status_code=404)
    return api_success(data=lead.to_dict())


@leads_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("crm.lead.create")
def create_lead():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    if not data.get("company_name"):
        return api_error("company_name is required", status_code=400)
    lead = Lead(
        organization_id=user.organization_id,
        assigned_to_user_id=user.id,
        company_name=data["company_name"].strip(),
        contact_name=(data.get("contact_name") or "").strip(),
        email=(data.get("email") or "").strip(),
        phone=(data.get("phone") or "").strip(),
        status=(data.get("status") or "prospect").strip(),
        stage=(data.get("stage") or "").strip(),
        value=Decimal(str(data.get("value") or 0)),
    )
    db.session.add(lead)
    db.session.commit()
    return api_success(data=lead.to_dict(), message="Lead created", status_code=201)


@leads_bp.route("/<lead_id>", methods=["PUT"])
@jwt_required()
@require_permission("crm.edit")
def update_lead(lead_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    lead = db.session.get(Lead, lead_id)
    if not lead or lead.organization_id != user.organization_id:
        return api_error("Lead not found", status_code=404)
    data = request.get_json() or {}
    for k, v in _lead_from_json(data).items():
        if v is not None:
            setattr(lead, k, v)
    if "value" in data:
        lead.value = Decimal(str(data["value"]))
    db.session.commit()
    return api_success(data=lead.to_dict())


@leads_bp.route("/<lead_id>/convert", methods=["POST"])
@jwt_required()
@require_permission("crm.lead.convert")
def convert_lead(lead_id):
    """Convert Closed-Won lead to Customer and Project."""
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    lead = db.session.get(Lead, lead_id)
    if not lead or lead.organization_id != user.organization_id:
        return api_error("Lead not found", status_code=404)
    if lead.status == "closed_won" and lead.converted_customer_id:
        return api_error("Lead already converted", status_code=400)
    if lead.status != "closed_won":
        lead.status = "closed_won"

    code_base = (lead.company_name[:4] or "C").upper().replace(" ", "")
    existing = Customer.query.filter_by(organization_id=user.organization_id).count()
    customer_code = f"{code_base}{existing + 1:04d}"
    customer = Customer(
        organization_id=user.organization_id,
        name=lead.company_name,
        code=customer_code,
        billing_address="",
        shipping_address="",
        source_lead_id=lead.id,
    )
    db.session.add(customer)
    db.session.flush()

    proj_count = Project.query.filter_by(organization_id=user.organization_id).count()
    project_code = f"PRJ-{proj_count + 1:04d}"
    project = Project(
        organization_id=user.organization_id,
        customer_id=customer.id,
        source_lead_id=lead.id,
        name=f"Project: {lead.company_name}",
        code=project_code,
        status="active",
    )
    db.session.add(project)
    db.session.flush()

    lead.converted_customer_id = customer.id
    lead.converted_project_id = project.id
    db.session.commit()
    return api_success(
        data={
            "lead": lead.to_dict(),
            "customer": customer.to_dict(),
            "project": project.to_dict(),
        },
        message="Lead converted to customer and project",
    )
