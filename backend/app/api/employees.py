"""HRM Employees API."""
from datetime import date
from decimal import Decimal

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.decorators import get_current_user, require_permission
from app.extensions import db
from app.models import Employee, User
from app.utils.auth_utils import hash_password
from app.utils.response import api_success, api_error

employees_bp = Blueprint("employees", __name__)


def _parse_date(v):
    if v is None or v == "":
        return None
    if isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v).split("T")[0])
    except Exception:
        return None


@employees_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("hrm.view")
def list_employees():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    employees = Employee.query.filter_by(organization_id=user.organization_id).order_by(Employee.full_name).all()
    return api_success(data=[e.to_dict() for e in employees])


@employees_bp.route("/<employee_id>", methods=["GET"])
@jwt_required()
@require_permission("hrm.view")
def get_employee(employee_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    e = db.session.get(Employee, employee_id)
    if not e or e.organization_id != user.organization_id:
        return api_error("Employee not found", status_code=404)
    return api_success(data=e.to_dict())


@employees_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("hrm.edit")
def create_employee():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    full_name = (data.get("full_name") or data.get("fullName") or "").strip()
    if not full_name:
        return api_error("full_name is required", status_code=400)
    code = (data.get("employee_code") or data.get("employeeCode") or "").strip()
    if not code:
        code = f"EMP-{Employee.query.filter_by(organization_id=user.organization_id).count() + 1:04d}"
    if Employee.query.filter_by(organization_id=user.organization_id, employee_code=code).first():
        return api_error("Employee code already exists", status_code=400)
    e = Employee(
        organization_id=user.organization_id,
        employee_code=code,
        full_name=full_name,
        job_title=(data.get("job_title") or "").strip(),
        department=(data.get("department") or "").strip(),
        base_salary_monthly=Decimal(str(data.get("base_salary_monthly") or data.get("base_salary") or 0)),
        hire_date=_parse_date(data.get("hire_date") or data.get("hireDate")),
        is_active=data.get("is_active", True),
    )
    if data.get("create_user_login") and data.get("email"):
        u = User(
            organization_id=user.organization_id,
            email=data["email"].strip().lower(),
            password_hash=hash_password(data.get("password") or "changeme"),
            full_name=full_name,
            is_active=True,
        )
        db.session.add(u)
        db.session.flush()
        e.user_id = u.id
    db.session.add(e)
    db.session.commit()
    return api_success(data=e.to_dict(), message="Employee created", status_code=201)


@employees_bp.route("/<employee_id>", methods=["PUT"])
@jwt_required()
@require_permission("hrm.edit")
def update_employee(employee_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    e = db.session.get(Employee, employee_id)
    if not e or e.organization_id != user.organization_id:
        return api_error("Employee not found", status_code=404)
    data = request.get_json() or {}
    for key in ("full_name", "job_title", "department", "employee_code"):
        if key in data and data[key] is not None:
            setattr(e, key, str(data[key]).strip())
    if "base_salary_monthly" in data:
        e.base_salary_monthly = Decimal(str(data["base_salary_monthly"]))
    if "hire_date" in data:
        e.hire_date = _parse_date(data["hire_date"])
    if "termination_date" in data:
        e.termination_date = _parse_date(data["termination_date"])
    if "is_active" in data:
        e.is_active = bool(data["is_active"])
    db.session.commit()
    return api_success(data=e.to_dict())
