"""Import all models so they are registered with SQLAlchemy. Order matters for FKs."""
from app.models.base import TimestampMixin, generate_uuid
from app.models.organization import Organization
from app.models.user import User, Role, Permission, RolePermission, UserRole
from app.models.hrm import Employee, EmployeeAvailability, PayrollRun, PayrollItem
from app.models.crm import Customer, CustomerContact
from app.models.project import Project, Milestone, Task, TaskAssignment, TaskMaterial, Timesheet
from app.models.inventory import Warehouse, Sku, StockLevel, PurchaseOrder, PurchaseOrderLine, ProjectRequisition
from app.models.crm import Lead, Invoice  # after Project (Lead/Invoice reference Project)

__all__ = [
    "TimestampMixin",
    "generate_uuid",
    "Organization",
    "User",
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    "Employee",
    "EmployeeAvailability",
    "PayrollRun",
    "PayrollItem",
    "Customer",
    "CustomerContact",
    "Lead",
    "Invoice",
    "Warehouse",
    "Sku",
    "StockLevel",
    "PurchaseOrder",
    "PurchaseOrderLine",
    "ProjectRequisition",
    "Project",
    "Milestone",
    "Task",
    "TaskAssignment",
    "TaskMaterial",
    "Timesheet",
]
