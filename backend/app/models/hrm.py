"""HRM models: Employee, EmployeeAvailability, PayrollRun, PayrollItem."""
from datetime import date
from decimal import Decimal

from sqlalchemy import String, ForeignKey, Numeric, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class Employee(db.Model, TimestampMixin):
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True, index=True
    )
    employee_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str] = mapped_column(String(128), default="")
    department: Mapped[str] = mapped_column(String(128), default="")
    base_salary_monthly: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    hire_date: Mapped[date] = mapped_column(Date, nullable=True)
    termination_date: Mapped[date] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    organization = relationship("Organization", back_populates="employees")
    user = relationship("User", back_populates="employee")
    availability = relationship("EmployeeAvailability", back_populates="employee", cascade="all, delete-orphan")
    payroll_items = relationship("PayrollItem", back_populates="employee", lazy="dynamic")
    task_assignments = relationship("TaskAssignment", back_populates="employee", lazy="dynamic")
    timesheets = relationship("Timesheet", back_populates="employee", lazy="dynamic")

    __table_args__ = (db.UniqueConstraint("organization_id", "employee_code", name="uq_employee_org_code"),)

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "user_id": self.user_id,
            "employee_code": self.employee_code,
            "full_name": self.full_name,
            "job_title": self.job_title,
            "department": self.department,
            "base_salary_monthly": float(self.base_salary_monthly) if self.base_salary_monthly is not None else 0,
            "hire_date": self.hire_date.isoformat() if self.hire_date else None,
            "termination_date": self.termination_date.isoformat() if self.termination_date else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class EmployeeAvailability(db.Model, TimestampMixin):
    __tablename__ = "employee_availability"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    employee_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    type: Mapped[str] = mapped_column(String(32), default="available")  # available, leave, reduced
    reason: Mapped[str] = mapped_column(String(255), default="")
    hours_available: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=8)

    employee = relationship("Employee", back_populates="availability")

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "date": self.date.isoformat() if self.date else None,
            "type": self.type,
            "reason": self.reason,
            "hours_available": float(self.hours_available) if self.hours_available is not None else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PayrollRun(db.Model, TimestampMixin):
    __tablename__ = "payroll_runs"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period: Mapped[str] = mapped_column(String(32), nullable=False)  # e.g. "2025-02"
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft")  # draft, calculated, approved, paid

    organization = relationship("Organization", back_populates="payroll_runs")
    items = relationship("PayrollItem", back_populates="payroll_run", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "period": self.period,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PayrollItem(db.Model, TimestampMixin):
    __tablename__ = "payroll_items"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    payroll_run_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("payroll_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    base_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    timesheet_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    status: Mapped[str] = mapped_column(String(32), default="pending")

    payroll_run = relationship("PayrollRun", back_populates="items")
    employee = relationship("Employee", back_populates="payroll_items")

    def to_dict(self):
        return {
            "id": self.id,
            "payroll_run_id": self.payroll_run_id,
            "employee_id": self.employee_id,
            "base_amount": float(self.base_amount) if self.base_amount is not None else 0,
            "timesheet_amount": float(self.timesheet_amount) if self.timesheet_amount is not None else 0,
            "total_amount": float(self.total_amount) if self.total_amount is not None else 0,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
