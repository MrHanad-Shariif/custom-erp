"""Project Management API."""
from datetime import date
from decimal import Decimal

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.decorators import get_current_user, require_permission
from app.extensions import db
from app.models import Project, Milestone, Task, TaskAssignment, TaskMaterial, Employee, Sku
from app.utils.response import api_success, api_error

projects_bp = Blueprint("projects", __name__)


def _parse_date(v):
    if v is None or v == "":
        return None
    try:
        return date.fromisoformat(str(v).split("T")[0])
    except Exception:
        return None


@projects_bp.route("", methods=["GET"])
@jwt_required()
@require_permission("pm.view")
def list_projects():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    projects = Project.query.filter_by(organization_id=user.organization_id).order_by(Project.created_at.desc()).all()
    return api_success(data=[p.to_dict() for p in projects])


@projects_bp.route("/<project_id>", methods=["GET"])
@jwt_required()
@require_permission("pm.view")
def get_project(project_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    p = db.session.get(Project, project_id)
    if not p or p.organization_id != user.organization_id:
        return api_error("Project not found", status_code=404)
    data = p.to_dict()
    data["milestones"] = [m.to_dict() for m in p.milestones]
    for m in data["milestones"]:
        milestone_obj = next(x for x in p.milestones if x.id == m["id"])
        m["tasks"] = [t.to_dict() for t in milestone_obj.tasks]
    return api_success(data=data)


@projects_bp.route("", methods=["POST"])
@jwt_required()
@require_permission("pm.edit")
def create_project():
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return api_error("name is required", status_code=400)
    code = (data.get("code") or "").strip() or f"PRJ-{Project.query.filter_by(organization_id=user.organization_id).count() + 1:04d}"
    if Project.query.filter_by(organization_id=user.organization_id, code=code).first():
        return api_error("Project code already exists", status_code=400)
    p = Project(
        organization_id=user.organization_id,
        customer_id=data.get("customer_id") or None,
        name=name,
        code=code,
        status=data.get("status") or "active",
        start_date=_parse_date(data.get("start_date")),
        end_date=_parse_date(data.get("end_date")),
        project_manager_id=data.get("project_manager_id") or None,
        budget_hours=Decimal(str(data.get("budget_hours") or 0)),
    )
    db.session.add(p)
    db.session.commit()
    return api_success(data=p.to_dict(), message="Project created", status_code=201)


@projects_bp.route("/<project_id>", methods=["PUT"])
@jwt_required()
@require_permission("pm.edit")
def update_project(project_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    p = db.session.get(Project, project_id)
    if not p or p.organization_id != user.organization_id:
        return api_error("Project not found", status_code=404)
    data = request.get_json() or {}
    for key in ("name", "code", "status", "customer_id", "project_manager_id"):
        if key in data and data[key] is not None:
            setattr(p, key, data[key])
    if "start_date" in data:
        p.start_date = _parse_date(data["start_date"])
    if "end_date" in data:
        p.end_date = _parse_date(data["end_date"])
    if "budget_hours" in data:
        p.budget_hours = Decimal(str(data["budget_hours"]))
    db.session.commit()
    return api_success(data=p.to_dict())


@projects_bp.route("/<project_id>/milestones", methods=["POST"])
@jwt_required()
@require_permission("pm.edit")
def create_milestone(project_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    p = db.session.get(Project, project_id)
    if not p or p.organization_id != user.organization_id:
        return api_error("Project not found", status_code=404)
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return api_error("name is required", status_code=400)
    m = Milestone(
        project_id=p.id,
        name=name,
        description=(data.get("description") or "").strip(),
        target_date=_parse_date(data.get("target_date")),
        status=data.get("status") or "pending",
        sort_order=int(data.get("sort_order") or 0),
    )
    db.session.add(m)
    db.session.commit()
    return api_success(data=m.to_dict(), message="Milestone created", status_code=201)


@projects_bp.route("/<project_id>/milestones/<milestone_id>/tasks", methods=["POST"])
@jwt_required()
@require_permission("pm.edit")
def create_task(project_id, milestone_id):
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    m = db.session.get(Milestone, milestone_id)
    if not m or m.project_id != project_id or m.project.organization_id != user.organization_id:
        return api_error("Milestone not found", status_code=404)
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return api_error("name is required", status_code=400)
    t = Task(
        milestone_id=m.id,
        name=name,
        description=(data.get("description") or "").strip(),
        status=data.get("status") or "pending",
        sort_order=int(data.get("sort_order") or 0),
        start_date=_parse_date(data.get("start_date")),
        end_date=_parse_date(data.get("end_date")),
        estimated_hours=Decimal(str(data.get("estimated_hours") or 0)),
    )
    db.session.add(t)
    db.session.flush()
    for emp in data.get("assignments") or []:
        emp_id = emp.get("employee_id") if isinstance(emp, dict) else emp
        if emp_id:
            pct = Decimal(str(emp.get("allocation_pct", 100) if isinstance(emp, dict) else 100))
            db.session.add(TaskAssignment(task_id=t.id, employee_id=emp_id, allocation_pct=pct))
    for mat in data.get("materials") or []:
        sku_id = mat.get("sku_id") if isinstance(mat, dict) else mat
        qty = Decimal(str(mat.get("quantity_required", 1) if isinstance(mat, dict) else 1))
        if sku_id:
            db.session.add(TaskMaterial(task_id=t.id, sku_id=sku_id, quantity_required=qty, quantity_consumed=Decimal(0)))
    db.session.commit()
    out = t.to_dict()
    out["assignments"] = [a.to_dict() for a in t.task_assignments]
    out["materials"] = [x.to_dict() for x in t.task_materials]
    return api_success(data=out, message="Task created", status_code=201)
