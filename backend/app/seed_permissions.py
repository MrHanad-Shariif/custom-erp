"""Seed default permissions for RBAC. Run once or from migration."""
from app.extensions import db
from app.models import Permission

DEFAULT_PERMISSIONS = [
    ("auth.view", "auth", "view", "View auth"),
    ("auth.edit", "auth", "edit", "Edit auth"),
    ("crm.view", "crm", "view", "View CRM"),
    ("crm.edit", "crm", "edit", "Edit CRM"),
    ("crm.lead.create", "crm", "lead.create", "Create leads"),
    ("crm.lead.convert", "crm", "lead.convert", "Convert lead to project"),
    ("hrm.view", "hrm", "view", "View HRM"),
    ("hrm.edit", "hrm", "edit", "Edit HRM"),
    ("inventory.view", "inventory", "view", "View inventory"),
    ("inventory.edit", "inventory", "edit", "Edit inventory"),
    ("finance.view", "finance", "view", "View finance"),
    ("finance.edit", "finance", "edit", "Edit finance"),
    ("pm.view", "pm", "view", "View projects"),
    ("pm.edit", "pm", "edit", "Edit projects"),
]


def seed_permissions():
    """Insert default permissions if not present. No-op if tables do not exist yet."""
    try:
        for perm_id, module, action, description in DEFAULT_PERMISSIONS:
            if db.session.get(Permission, perm_id) is None:
                db.session.add(Permission(id=perm_id, module=module, action=action, description=description))
        db.session.commit()
    except Exception:
        db.session.rollback()
