"""Timesheets API (feeds HRM payroll and billing)."""
from datetime import date
from decimal import Decimal

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.decorators import get_current_user, require_permission
from app.extensions import db
from app.models import Timesheet, Task, Employee
from app.utils.response import api_success, api_error

timesheets_bp = Blueprint("timesheets", __name__)


def _parse_date(v):
    if v is None or v == "":
        return None
    try:
        return date.fromisoformat(str(v).split("T")[0])
    except Exception:
        return None


@timesheets_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("pm.view")
def list_timesheets():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    employee_id = request.args.get("employee_id")
    task_id = request.args.get("task_id")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    q = Timesheet.query.filter_by(organization_id=user.organization_id)
    if employee_id:
        q = q.filter(Timesheet.employee_id == employee_id)
    if task_id:
        q = q.filter(Timesheet.task_id == task_id)
    if from_date:
        q = q.filter(Timesheet.work_date >= _parse_date(from_date))
    if to_date:
        q = q.filter(Timesheet.work_date <= _parse_date(to_date))
    q = q.order_by(Timesheet.work_date.desc())
    return api_success(data=[t.to_dict() for t in q.all()])


@timesheets_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("pm.edit")
def create_timesheet():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    employee_id = data.get("employee_id")
    task_id = data.get("task_id")
    work_date = _parse_date(data.get("work_date"))
    hours = Decimal(str(data.get("hours") or 0))
    if not employee_id or not task_id or not work_date:
        return api_error("employee_id, task_id, and work_date are required", status_code=400)
    emp = db.session.get(Employee, employee_id)
    task = db.session.get(Task, task_id)
    if not emp or emp.organization_id != user.organization_id:
        return api_error("Employee not found", status_code=404)
    if not task:
        return api_error("Task not found", status_code=404)
    if task.milestone.project.organization_id != user.organization_id:
        return api_error("Task not found", status_code=404)
    ts = Timesheet(
        organization_id=user.organization_id,
        employee_id=employee_id,
        task_id=task_id,
        work_date=work_date,
        hours=hours,
        status=data.get("status") or "draft",
        notes=(data.get("notes") or "").strip(),
    )
    db.session.add(ts)
    db.session.commit()
    return api_success(data=ts.to_dict(), message="Timesheet created", status_code=201)


@timesheets_bp.route("/<timesheet_id>/approve", methods=["POST"])
@jwt_required()
@require_permission("pm.edit")
def approve_timesheet(timesheet_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    ts = db.session.get(Timesheet, timesheet_id)
    if not ts or ts.organization_id != user.organization_id:
        return api_error("Timesheet not found", status_code=404)
    ts.status = "approved"
    ts.approved_by_user_id = user.id
    db.session.commit()
    return api_success(data=ts.to_dict(), message="Timesheet approved")
