"""Project Management models: Project, Milestone, Task, TaskAssignment, TaskMaterial, Timesheet."""
from datetime import date
from decimal import Decimal

from sqlalchemy import String, ForeignKey, Numeric, Date, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class Project(db.Model, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    source_lead_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="active")  # draft, active, on_hold, completed, cancelled
    start_date: Mapped[date] = mapped_column(Date, nullable=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    project_manager_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True
    )
    budget_hours: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    organization = relationship("Organization", back_populates="projects")
    customer = relationship("Customer", back_populates="projects")
    project_manager = relationship("Employee", foreign_keys=[project_manager_id])
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan", order_by="Milestone.sort_order")
    project_requisitions = relationship("ProjectRequisition", back_populates="project", lazy="dynamic")
    invoices = relationship("Invoice", back_populates="project", lazy="dynamic")

    __table_args__ = (db.UniqueConstraint("organization_id", "code", name="uq_project_org_code"),)

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "customer_id": self.customer_id,
            "source_lead_id": self.source_lead_id,
            "name": self.name,
            "code": self.code,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "project_manager_id": self.project_manager_id,
            "budget_hours": float(self.budget_hours) if self.budget_hours is not None else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Milestone(db.Model, TimestampMixin):
    __tablename__ = "milestones"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    target_date: Mapped[date] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    project = relationship("Project", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone", cascade="all, delete-orphan", order_by="Task.sort_order")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "status": self.status,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Task(db.Model, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    milestone_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, in_progress, completed, cancelled
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    start_date: Mapped[date] = mapped_column(Date, nullable=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    estimated_hours: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    milestone = relationship("Milestone", back_populates="tasks")
    task_assignments = relationship("TaskAssignment", back_populates="task", cascade="all, delete-orphan")
    task_materials = relationship("TaskMaterial", back_populates="task", cascade="all, delete-orphan")
    timesheets = relationship("Timesheet", back_populates="task", lazy="dynamic")
    project_requisitions = relationship("ProjectRequisition", back_populates="task", lazy="dynamic")

    @property
    def project_id(self):
        return self.milestone.project_id if self.milestone else None

    def to_dict(self):
        return {
            "id": self.id,
            "milestone_id": self.milestone_id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "sort_order": self.sort_order,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "estimated_hours": float(self.estimated_hours) if self.estimated_hours is not None else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TaskAssignment(db.Model, TimestampMixin):
    __tablename__ = "task_assignments"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(64), default="")
    allocation_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=100)

    task = relationship("Task", back_populates="task_assignments")
    employee = relationship("Employee", back_populates="task_assignments")

    __table_args__ = (db.UniqueConstraint("task_id", "employee_id", name="uq_task_assignment"),)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "employee_id": self.employee_id,
            "role": self.role,
            "allocation_pct": float(self.allocation_pct) if self.allocation_pct is not None else 100,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TaskMaterial(db.Model, TimestampMixin):
    __tablename__ = "task_materials"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sku_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("skus.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity_required: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    quantity_consumed: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)

    task = relationship("Task", back_populates="task_materials")
    sku = relationship("Sku", back_populates="task_materials")

    __table_args__ = (db.UniqueConstraint("task_id", "sku_id", name="uq_task_material"),)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "sku_id": self.sku_id,
            "quantity_required": float(self.quantity_required) if self.quantity_required is not None else 0,
            "quantity_consumed": float(self.quantity_consumed) if self.quantity_consumed is not None else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Timesheet(db.Model, TimestampMixin):
    __tablename__ = "timesheets"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0)
    status: Mapped[str] = mapped_column(String(32), default="draft")  # draft, submitted, approved
    notes: Mapped[str] = mapped_column(Text, default="")
    approved_by_user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    organization = relationship("Organization", back_populates="timesheets")
    employee = relationship("Employee", back_populates="timesheets")
    task = relationship("Task", back_populates="timesheets")
    approved_by = relationship("User", foreign_keys=[approved_by_user_id])

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "employee_id": self.employee_id,
            "task_id": self.task_id,
            "work_date": self.work_date.isoformat() if self.work_date else None,
            "hours": float(self.hours) if self.hours is not None else 0,
            "status": self.status,
            "notes": self.notes,
            "approved_by_user_id": self.approved_by_user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
