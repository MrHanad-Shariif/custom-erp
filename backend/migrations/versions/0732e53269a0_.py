"""empty message

Revision ID: 0732e53269a0
Revises: 
Create Date: 2026-02-11 02:21:07.018179

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0732e53269a0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create in dependency order; break customers/leads/projects cycle by adding FKs after leads exists.
    op.create_table('organizations',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('code', sa.String(length=64), nullable=False),
    sa.Column('timezone', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_organizations_code'), ['code'], unique=True)

    op.create_table('permissions',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('module', sa.String(length=64), nullable=False),
    sa.Column('action', sa.String(length=64), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('organization_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_organization_id'), ['organization_id'], unique=False)

    op.create_table('roles',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('organization_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('description', sa.String(length=512), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_roles_organization_id'), ['organization_id'], unique=False)

    op.create_table('role_permissions',
    sa.Column('role_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('permission_id', sa.String(length=64), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    op.create_table('user_roles',
    sa.Column('user_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('role_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    op.create_table('employees',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('organization_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('user_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('employee_code', sa.String(length=64), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('job_title', sa.String(length=128), nullable=False),
    sa.Column('department', sa.String(length=128), nullable=False),
    sa.Column('base_salary_monthly', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('hire_date', sa.Date(), nullable=True),
    sa.Column('termination_date', sa.Date(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'employee_code', name='uq_employee_org_code')
    )
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_employees_employee_code'), ['employee_code'], unique=False)
        batch_op.create_index(batch_op.f('ix_employees_organization_id'), ['organization_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_employees_user_id'), ['user_id'], unique=True)

    op.create_table('customers',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('organization_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('code', sa.String(length=64), nullable=False),
    sa.Column('tax_id', sa.String(length=64), nullable=False),
    sa.Column('billing_address', sa.Text(), nullable=False),
    sa.Column('shipping_address', sa.Text(), nullable=False),
    sa.Column('source_lead_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'code', name='uq_customer_org_code')
    )
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_customers_code'), ['code'], unique=False)
        batch_op.create_index(batch_op.f('ix_customers_organization_id'), ['organization_id'], unique=False)

    op.create_table('projects',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('organization_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('customer_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('source_lead_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('code', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('project_manager_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('budget_hours', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['project_manager_id'], ['employees.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'code', name='uq_project_org_code')
    )
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_projects_code'), ['code'], unique=False)
        batch_op.create_index(batch_op.f('ix_projects_customer_id'), ['customer_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_projects_organization_id'), ['organization_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_projects_project_manager_id'), ['project_manager_id'], unique=False)

    op.create_table('leads',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('organization_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('assigned_to_user_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('company_name', sa.String(length=255), nullable=False),
    sa.Column('contact_name', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=64), nullable=False),
    sa.Column('stage', sa.String(length=64), nullable=False),
    sa.Column('value', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('converted_customer_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('converted_project_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['assigned_to_user_id'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['converted_customer_id'], ['customers.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['converted_project_id'], ['projects.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_leads_assigned_to_user_id'), ['assigned_to_user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_leads_organization_id'), ['organization_id'], unique=False)

    op.create_foreign_key('fk_customers_source_lead_id', 'customers', 'leads', ['source_lead_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_projects_source_lead_id', 'projects', 'leads', ['source_lead_id'], ['id'], ondelete='SET NULL')

    op.create_table('customer_contacts',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('customer_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=64), nullable=False),
    sa.Column('role', sa.String(length=128), nullable=False),
    sa.Column('is_primary', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('customer_contacts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_customer_contacts_customer_id'), ['customer_id'], unique=False)

    op.create_table('invoices',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('organization_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('customer_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('project_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('number', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('paid_at', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'number', name='uq_invoice_org_number')
    )
    with op.batch_alter_table('invoices', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_invoices_customer_id'), ['customer_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_invoices_number'), ['number'], unique=False)
        batch_op.create_index(batch_op.f('ix_invoices_organization_id'), ['organization_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_invoices_project_id'), ['project_id'], unique=False)

    op.create_table('milestones',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('project_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('target_date', sa.Date(), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('milestones', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_milestones_project_id'), ['project_id'], unique=False)

    op.create_table('payroll_runs',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('organization_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('period', sa.String(length=32), nullable=False),
    sa.Column('period_start', sa.Date(), nullable=False),
    sa.Column('period_end', sa.Date(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('payroll_runs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_payroll_runs_organization_id'), ['organization_id'], unique=False)

    op.create_table('skus',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('organization_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('code', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('unit', sa.String(length=32), nullable=False),
    sa.Column('reorder_point', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('reorder_quantity', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'code', name='uq_sku_org_code')
    )
    with op.batch_alter_table('skus', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_skus_code'), ['code'], unique=False)
        batch_op.create_index(batch_op.f('ix_skus_organization_id'), ['organization_id'], unique=False)

    op.create_table('warehouses',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('organization_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('code', sa.String(length=64), nullable=False),
    sa.Column('address', sa.Text(), nullable=False),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'code', name='uq_warehouse_org_code')
    )
    with op.batch_alter_table('warehouses', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_warehouses_code'), ['code'], unique=False)
        batch_op.create_index(batch_op.f('ix_warehouses_organization_id'), ['organization_id'], unique=False)

    op.create_table('purchase_orders',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('organization_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('warehouse_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('number', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('order_date', sa.Date(), nullable=True),
    sa.Column('expected_date', sa.Date(), nullable=True),
    sa.Column('created_by_user_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'number', name='uq_po_org_number')
    )
    with op.batch_alter_table('purchase_orders', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_purchase_orders_number'), ['number'], unique=False)
        batch_op.create_index(batch_op.f('ix_purchase_orders_organization_id'), ['organization_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_purchase_orders_warehouse_id'), ['warehouse_id'], unique=False)

    op.create_table('stock_levels',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('warehouse_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('sku_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('reserved_quantity', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('reorder_point', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['sku_id'], ['skus.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('warehouse_id', 'sku_id', name='uq_stock_warehouse_sku')
    )
    with op.batch_alter_table('stock_levels', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_stock_levels_sku_id'), ['sku_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_stock_levels_warehouse_id'), ['warehouse_id'], unique=False)

    op.create_table('tasks',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('milestone_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('estimated_hours', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['milestone_id'], ['milestones.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_tasks_milestone_id'), ['milestone_id'], unique=False)

    op.create_table('employee_availability',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('employee_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('type', sa.String(length=32), nullable=False),
    sa.Column('reason', sa.String(length=255), nullable=False),
    sa.Column('hours_available', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('employee_availability', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_employee_availability_employee_id'), ['employee_id'], unique=False)

    op.create_table('payroll_items',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('payroll_run_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('employee_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('base_amount', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('timesheet_amount', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('total_amount', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['payroll_run_id'], ['payroll_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('payroll_items', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_payroll_items_employee_id'), ['employee_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_payroll_items_payroll_run_id'), ['payroll_run_id'], unique=False)

    op.create_table('project_requisitions',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('project_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('task_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('sku_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('warehouse_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('quantity_reserved', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('quantity_issued', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sku_id'], ['skus.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('project_requisitions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_project_requisitions_project_id'), ['project_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_project_requisitions_sku_id'), ['sku_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_project_requisitions_task_id'), ['task_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_project_requisitions_warehouse_id'), ['warehouse_id'], unique=False)

    op.create_table('purchase_order_lines',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('purchase_order_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('sku_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('quantity_ordered', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('quantity_received', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sku_id'], ['skus.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('purchase_order_lines', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_purchase_order_lines_purchase_order_id'), ['purchase_order_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_purchase_order_lines_sku_id'), ['sku_id'], unique=False)

    op.create_table('task_assignments',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('task_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('employee_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('role', sa.String(length=64), nullable=False),
    sa.Column('allocation_pct', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('task_id', 'employee_id', name='uq_task_assignment')
    )
    with op.batch_alter_table('task_assignments', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_task_assignments_employee_id'), ['employee_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_task_assignments_task_id'), ['task_id'], unique=False)

    op.create_table('task_materials',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('task_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('sku_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('quantity_required', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('quantity_consumed', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['sku_id'], ['skus.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('task_id', 'sku_id', name='uq_task_material')
    )
    with op.batch_alter_table('task_materials', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_task_materials_sku_id'), ['sku_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_task_materials_task_id'), ['task_id'], unique=False)

    op.create_table('timesheets',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('organization_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('employee_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('task_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('work_date', sa.Date(), nullable=False),
    sa.Column('hours', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('notes', sa.Text(), nullable=False),
    sa.Column('approved_by_user_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['approved_by_user_id'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('timesheets', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_timesheets_employee_id'), ['employee_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_timesheets_organization_id'), ['organization_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_timesheets_task_id'), ['task_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('timesheets', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_timesheets_task_id'))
        batch_op.drop_index(batch_op.f('ix_timesheets_organization_id'))
        batch_op.drop_index(batch_op.f('ix_timesheets_employee_id'))

    op.drop_table('timesheets')
    with op.batch_alter_table('task_materials', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_task_materials_task_id'))
        batch_op.drop_index(batch_op.f('ix_task_materials_sku_id'))

    op.drop_table('task_materials')
    with op.batch_alter_table('task_assignments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_task_assignments_task_id'))
        batch_op.drop_index(batch_op.f('ix_task_assignments_employee_id'))

    op.drop_table('task_assignments')
    with op.batch_alter_table('purchase_order_lines', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_purchase_order_lines_sku_id'))
        batch_op.drop_index(batch_op.f('ix_purchase_order_lines_purchase_order_id'))

    op.drop_table('purchase_order_lines')
    with op.batch_alter_table('project_requisitions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_project_requisitions_warehouse_id'))
        batch_op.drop_index(batch_op.f('ix_project_requisitions_task_id'))
        batch_op.drop_index(batch_op.f('ix_project_requisitions_sku_id'))
        batch_op.drop_index(batch_op.f('ix_project_requisitions_project_id'))

    op.drop_table('project_requisitions')
    with op.batch_alter_table('payroll_items', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_payroll_items_payroll_run_id'))
        batch_op.drop_index(batch_op.f('ix_payroll_items_employee_id'))

    op.drop_table('payroll_items')
    with op.batch_alter_table('employee_availability', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_employee_availability_employee_id'))

    op.drop_table('employee_availability')
    op.drop_table('user_roles')
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_tasks_milestone_id'))

    op.drop_table('tasks')
    with op.batch_alter_table('stock_levels', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_stock_levels_warehouse_id'))
        batch_op.drop_index(batch_op.f('ix_stock_levels_sku_id'))

    op.drop_table('stock_levels')
    op.drop_table('role_permissions')
    with op.batch_alter_table('purchase_orders', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_purchase_orders_warehouse_id'))
        batch_op.drop_index(batch_op.f('ix_purchase_orders_organization_id'))
        batch_op.drop_index(batch_op.f('ix_purchase_orders_number'))

    op.drop_table('purchase_orders')
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_employees_user_id'))
        batch_op.drop_index(batch_op.f('ix_employees_organization_id'))
        batch_op.drop_index(batch_op.f('ix_employees_employee_code'))

    op.drop_table('employees')
    with op.batch_alter_table('warehouses', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_warehouses_organization_id'))
        batch_op.drop_index(batch_op.f('ix_warehouses_code'))

    op.drop_table('warehouses')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_organization_id'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    with op.batch_alter_table('skus', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_skus_organization_id'))
        batch_op.drop_index(batch_op.f('ix_skus_code'))

    op.drop_table('skus')
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_roles_organization_id'))

    op.drop_table('roles')
    with op.batch_alter_table('payroll_runs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_payroll_runs_organization_id'))

    op.drop_table('payroll_runs')
    with op.batch_alter_table('milestones', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_milestones_project_id'))

    op.drop_table('milestones')
    with op.batch_alter_table('invoices', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_invoices_project_id'))
        batch_op.drop_index(batch_op.f('ix_invoices_organization_id'))
        batch_op.drop_index(batch_op.f('ix_invoices_number'))
        batch_op.drop_index(batch_op.f('ix_invoices_customer_id'))

    op.drop_table('invoices')
    with op.batch_alter_table('customer_contacts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_customer_contacts_customer_id'))

    op.drop_table('customer_contacts')
    op.drop_constraint('fk_projects_source_lead_id', 'projects', type_='foreignkey')
    op.drop_constraint('fk_customers_source_lead_id', 'customers', type_='foreignkey')
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_projects_project_manager_id'))
        batch_op.drop_index(batch_op.f('ix_projects_organization_id'))
        batch_op.drop_index(batch_op.f('ix_projects_customer_id'))
        batch_op.drop_index(batch_op.f('ix_projects_code'))

    op.drop_table('projects')
    op.drop_table('permissions')
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_organizations_code'))

    op.drop_table('organizations')
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_leads_organization_id'))
        batch_op.drop_index(batch_op.f('ix_leads_assigned_to_user_id'))

    op.drop_table('leads')
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_customers_organization_id'))
        batch_op.drop_index(batch_op.f('ix_customers_code'))

    op.drop_table('customers')
    # ### end Alembic commands ###
