"""CRM models: Lead, Customer, CustomerContact, Invoice."""
from datetime import date
from decimal import Decimal

from sqlalchemy import String, ForeignKey, Numeric, Date, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class Lead(db.Model, TimestampMixin):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assigned_to_user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(255), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(64), default="prospect")  # prospect, qualified, proposal, negotiation, closed_won, closed_lost
    stage: Mapped[str] = mapped_column(String(64), default="")
    value: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    converted_customer_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True
    )
    converted_project_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )

    organization = relationship("Organization", back_populates="leads")
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id])
    converted_customer = relationship("Customer", foreign_keys=[converted_customer_id])
    converted_project = relationship("Project", foreign_keys=[converted_project_id])

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "assigned_to_user_id": self.assigned_to_user_id,
            "company_name": self.company_name,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone": self.phone,
            "status": self.status,
            "stage": self.stage,
            "value": float(self.value) if self.value is not None else 0,
            "converted_customer_id": self.converted_customer_id,
            "converted_project_id": self.converted_project_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Customer(db.Model, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tax_id: Mapped[str] = mapped_column(String(64), default="")
    billing_address: Mapped[str] = mapped_column(Text, default="")
    shipping_address: Mapped[str] = mapped_column(Text, default="")
    source_lead_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )

    organization = relationship("Organization", back_populates="customers")
    contacts = relationship("CustomerContact", back_populates="customer", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="customer", lazy="dynamic")
    invoices = relationship("Invoice", back_populates="customer", lazy="dynamic")

    __table_args__ = (db.UniqueConstraint("organization_id", "code", name="uq_customer_org_code"),)

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "name": self.name,
            "code": self.code,
            "tax_id": self.tax_id,
            "billing_address": self.billing_address,
            "shipping_address": self.shipping_address,
            "source_lead_id": self.source_lead_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CustomerContact(db.Model, TimestampMixin):
    __tablename__ = "customer_contacts"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(64), default="")
    role: Mapped[str] = mapped_column(String(128), default="")
    is_primary: Mapped[bool] = mapped_column(db.Boolean, default=False)

    customer = relationship("Customer", back_populates="contacts")

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_primary": self.is_primary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Invoice(db.Model, TimestampMixin):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    project_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")  # draft, sent, paid, overdue
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    due_date: Mapped[date] = mapped_column(Date, nullable=True)
    paid_at: Mapped[date] = mapped_column(Date, nullable=True)

    organization = relationship("Organization", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    project = relationship("Project", back_populates="invoices")

    __table_args__ = (db.UniqueConstraint("organization_id", "number", name="uq_invoice_org_number"),)

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "customer_id": self.customer_id,
            "project_id": self.project_id,
            "number": self.number,
            "status": self.status,
            "amount": float(self.amount) if self.amount is not None else 0,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
