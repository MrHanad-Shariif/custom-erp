"""Payroll runs and items (timesheet amounts from PM)."""
from datetime import date
from decimal import Decimal

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.decorators import get_current_user, require_permission
from sqlalchemy import func
from app.extensions import db
from app.models import PayrollRun, PayrollItem, Employee, Timesheet
from app.utils.response import api_success, api_error

payroll_bp = Blueprint("payroll", __name__)


def _parse_date(v):
    if v is None or v == "":
        return None
    try:
        return date.fromisoformat(str(v).split("T")[0])
    except Exception:
        return None


@payroll_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("hrm.view")
def list_payroll_runs():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    runs = PayrollRun.query.filter_by(organization_id=user.organization_id).order_by(PayrollRun.period_start.desc()).all()
    return api_success(data=[r.to_dict() for r in runs])


@payroll_bp.route("/<run_id>", methods=["GET"])
@jwt_required()
@require_permission("hrm.view")
def get_payroll_run(run_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    r = db.session.get(PayrollRun, run_id)
    if not r or r.organization_id != user.organization_id:
        return api_error("Payroll run not found", status_code=404)
    data = r.to_dict()
    data["items"] = [i.to_dict() for i in r.items]
    return api_success(data=data)


@payroll_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("hrm.edit")
def create_payroll_run():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    period_start = _parse_date(data.get("period_start"))
    period_end = _parse_date(data.get("period_end"))
    period = data.get("period") or (period_start.strftime("%Y-%m") if period_start else "")
    if not period_start or not period_end:
        return api_error("period_start and period_end are required", status_code=400)
    r = PayrollRun(
        organization_id=user.organization_id,
        period=period,
        period_start=period_start,
        period_end=period_end,
        status="draft",
    )
    db.session.add(r)
    db.session.flush()
    employees = Employee.query.filter_by(organization_id=user.organization_id, is_active=True).all()
    for emp in employees:
        base = emp.base_salary_monthly or Decimal(0)
        ts_total = db.session.query(func.coalesce(func.sum(Timesheet.hours), 0)).filter(
            Timesheet.employee_id == emp.id,
            Timesheet.work_date >= period_start,
            Timesheet.work_date <= period_end,
            Timesheet.status == "approved",
        ).scalar() or 0
        # Simple: timesheet amount = hours * rate (you can add hourly_rate to Employee later)
        timesheet_amount = Decimal(str(ts_total)) * Decimal("0")  # placeholder: no hourly rate in schema
        item = PayrollItem(
            payroll_run_id=r.id,
            employee_id=emp.id,
            base_amount=base,
            timesheet_amount=timesheet_amount,
            total_amount=base + timesheet_amount,
            status="pending",
        )
        db.session.add(item)
    db.session.commit()
    data = r.to_dict()
    data["items"] = [i.to_dict() for i in r.items]
    return api_success(data=data, message="Payroll run created", status_code=201)
