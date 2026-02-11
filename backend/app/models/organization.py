"""Organization and tenant model."""
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class Organization(db.Model, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")

    users = relationship("User", back_populates="organization", lazy="dynamic")
    employees = relationship("Employee", back_populates="organization", lazy="dynamic")
    customers = relationship("Customer", back_populates="organization", lazy="dynamic")
    warehouses = relationship("Warehouse", back_populates="organization", lazy="dynamic")
    roles = relationship("Role", back_populates="organization", lazy="dynamic")
    leads = relationship("Lead", back_populates="organization", lazy="dynamic")
    projects = relationship("Project", back_populates="organization", lazy="dynamic")
    payroll_runs = relationship("PayrollRun", back_populates="organization", lazy="dynamic")
    timesheets = relationship("Timesheet", back_populates="organization", lazy="dynamic")
    skus = relationship("Sku", back_populates="organization", lazy="dynamic")
    purchase_orders = relationship("PurchaseOrder", back_populates="organization", lazy="dynamic")
    invoices = relationship("Invoice", back_populates="organization", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "timezone": self.timezone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
