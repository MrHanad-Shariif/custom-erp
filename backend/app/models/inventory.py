"""Inventory models: Warehouse, Sku, StockLevel, PurchaseOrder, PurchaseOrderLine, ProjectRequisition."""
from datetime import date
from decimal import Decimal

from sqlalchemy import String, ForeignKey, Numeric, Date, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class Warehouse(db.Model, TimestampMixin):
    __tablename__ = "warehouses"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    address: Mapped[str] = mapped_column(Text, default="")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    organization = relationship("Organization", back_populates="warehouses")
    stock_levels = relationship("StockLevel", back_populates="warehouse", cascade="all, delete-orphan")
    purchase_orders = relationship("PurchaseOrder", back_populates="warehouse", lazy="dynamic")
    project_requisitions = relationship("ProjectRequisition", back_populates="warehouse", lazy="dynamic")

    __table_args__ = (db.UniqueConstraint("organization_id", "code", name="uq_warehouse_org_code"),)

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "name": self.name,
            "code": self.code,
            "address": self.address,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Sku(db.Model, TimestampMixin):
    __tablename__ = "skus"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), default="unit")
    reorder_point: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    reorder_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    organization = relationship("Organization", back_populates="skus")
    stock_levels = relationship("StockLevel", back_populates="sku", cascade="all, delete-orphan")
    purchase_order_lines = relationship("PurchaseOrderLine", back_populates="sku", lazy="dynamic")
    project_requisitions = relationship("ProjectRequisition", back_populates="sku", lazy="dynamic")
    task_materials = relationship("TaskMaterial", back_populates="sku", lazy="dynamic")

    __table_args__ = (db.UniqueConstraint("organization_id", "code", name="uq_sku_org_code"),)

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "code": self.code,
            "name": self.name,
            "unit": self.unit,
            "reorder_point": float(self.reorder_point) if self.reorder_point is not None else 0,
            "reorder_quantity": float(self.reorder_quantity) if self.reorder_quantity is not None else 0,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class StockLevel(db.Model, TimestampMixin):
    __tablename__ = "stock_levels"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    warehouse_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sku_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("skus.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    reserved_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    reorder_point: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)

    warehouse = relationship("Warehouse", back_populates="stock_levels")
    sku = relationship("Sku", back_populates="stock_levels")

    __table_args__ = (db.UniqueConstraint("warehouse_id", "sku_id", name="uq_stock_warehouse_sku"),)

    @property
    def available_quantity(self):
        return (self.quantity or 0) - (self.reserved_quantity or 0)

    def to_dict(self):
        return {
            "id": self.id,
            "warehouse_id": self.warehouse_id,
            "sku_id": self.sku_id,
            "quantity": float(self.quantity) if self.quantity is not None else 0,
            "reserved_quantity": float(self.reserved_quantity) if self.reserved_quantity is not None else 0,
            "reorder_point": float(self.reorder_point) if self.reorder_point is not None else 0,
            "available_quantity": float(self.available_quantity),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PurchaseOrder(db.Model, TimestampMixin):
    __tablename__ = "purchase_orders"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    warehouse_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")  # draft, submitted, received, cancelled
    order_date: Mapped[date] = mapped_column(Date, nullable=True)
    expected_date: Mapped[date] = mapped_column(Date, nullable=True)
    created_by_user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    organization = relationship("Organization", back_populates="purchase_orders")
    warehouse = relationship("Warehouse", back_populates="purchase_orders")
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    lines = relationship("PurchaseOrderLine", back_populates="purchase_order", cascade="all, delete-orphan")

    __table_args__ = (db.UniqueConstraint("organization_id", "number", name="uq_po_org_number"),)

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "warehouse_id": self.warehouse_id,
            "number": self.number,
            "status": self.status,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "expected_date": self.expected_date.isoformat() if self.expected_date else None,
            "created_by_user_id": self.created_by_user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PurchaseOrderLine(db.Model, TimestampMixin):
    __tablename__ = "purchase_order_lines"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    purchase_order_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sku_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("skus.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity_ordered: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    quantity_received: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)

    purchase_order = relationship("PurchaseOrder", back_populates="lines")
    sku = relationship("Sku", back_populates="purchase_order_lines")

    def to_dict(self):
        return {
            "id": self.id,
            "purchase_order_id": self.purchase_order_id,
            "sku_id": self.sku_id,
            "quantity_ordered": float(self.quantity_ordered) if self.quantity_ordered is not None else 0,
            "quantity_received": float(self.quantity_received) if self.quantity_received is not None else 0,
            "unit_price": float(self.unit_price) if self.unit_price is not None else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProjectRequisition(db.Model, TimestampMixin):
    __tablename__ = "project_requisitions"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True
    )
    sku_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("skus.id", ondelete="CASCADE"), nullable=False, index=True
    )
    warehouse_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity_reserved: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    quantity_issued: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    status: Mapped[str] = mapped_column(String(32), default="reserved")  # reserved, partial, issued, cancelled

    project = relationship("Project", back_populates="project_requisitions")
    task = relationship("Task", back_populates="project_requisitions")
    sku = relationship("Sku", back_populates="project_requisitions")
    warehouse = relationship("Warehouse", back_populates="project_requisitions")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "task_id": self.task_id,
            "sku_id": self.sku_id,
            "warehouse_id": self.warehouse_id,
            "quantity_reserved": float(self.quantity_reserved) if self.quantity_reserved is not None else 0,
            "quantity_issued": float(self.quantity_issued) if self.quantity_issued is not None else 0,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
