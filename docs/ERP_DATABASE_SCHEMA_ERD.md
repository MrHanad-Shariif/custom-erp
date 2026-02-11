# Custom Integrated ERP — Relational Database Schema (ERD)

This document defines the **centralized relational database schema** for the ERP. All modules share a single PostgreSQL database with consistent references to **Organizations** and **Users**. No application code is written until this schema is approved.

---

## 1. High-Level Module Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         CUSTOM INTEGRATED ERP                                     │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────────┤
│   AUTH      │    CRM      │    HRM      │  INVENTORY  │   PROJECT MANAGEMENT    │
│ (Gatekeeper)│ Lead→Contract│ Talent & Pay│ Supply Chain│ Tasks, Timesheets, Resources│
├─────────────┴─────────────┴─────────────┴─────────────┴─────────────────────────┤
│  SHARED: organizations, users, roles, permissions, user_roles, role_permissions   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Entity-Relationship Diagram (Mermaid)

```mermaid
erDiagram
    %% ========== SHARED / AUTH ==========
    organizations ||--o{ users : "has"
    organizations ||--o{ employees : "employs"
    organizations ||--o{ customers : "has"
    organizations ||--o{ warehouses : "owns"
    organizations ||--o{ roles : "defines"
    
    roles ||--o{ role_permissions : "has"
    permissions ||--o{ role_permissions : "in"
    users ||--o{ user_roles : "has"
    roles ||--o{ user_roles : "assigned_to"
    
    users ||--o| employees : "is"
    users {
        uuid id PK
        uuid organization_id FK
        string email UK
        string password_hash
        string full_name
        boolean is_active
        timestamps
    }
    
    organizations {
        uuid id PK
        string name
        string code UK
        string timezone
        timestamps
    }
    
    roles {
        uuid id PK
        uuid organization_id FK
        string name UK
        string description
        timestamps
    }
    
    permissions {
        string id PK
        string module
        string action
        string description
    }
    
    role_permissions {
        uuid role_id FK
        string permission_id FK
        PK(role_id, permission_id)
    }
    
    user_roles {
        uuid user_id FK
        uuid role_id FK
        timestamps
        PK(user_id, role_id)
    }
    
    %% ========== CRM ==========
    customers ||--o{ customer_contacts : "has"
    customers ||--o{ projects : "owns"
    customers ||--o{ invoices : "billed_to"
    leads ||--o| customers : "converts_to"
    leads ||--o| projects : "converts_to"
    
    leads {
        uuid id PK
        uuid organization_id FK
        uuid assigned_to_user_id FK
        string company_name
        string contact_name
        string email
        string phone
        string status
        string stage
        decimal value
        uuid converted_customer_id FK
        uuid converted_project_id FK
        timestamps
    }
    
    customers {
        uuid id PK
        uuid organization_id FK
        string name
        string code UK
        string tax_id
        string billing_address
        string shipping_address
        uuid source_lead_id FK
        timestamps
    }
    
    customer_contacts {
        uuid id PK
        uuid customer_id FK
        string name
        string email
        string phone
        string role
        boolean is_primary
        timestamps
    }
    
    invoices {
        uuid id PK
        uuid organization_id FK
        uuid customer_id FK
        uuid project_id FK
        string number UK
        string status
        decimal amount
        date due_date
        date paid_at
        timestamps
    }
    
    %% ========== HRM ==========
    employees ||--o{ employee_availability : "has"
    employees ||--o{ timesheets : "logs"
    employees ||--o{ task_assignments : "assigned"
    employees ||--o{ payroll_items : "has"
    payroll_runs ||--o{ payroll_items : "contains"
    
    employees {
        uuid id PK
        uuid organization_id FK
        uuid user_id FK UK
        string employee_code UK
        string full_name
        string job_title
        string department
        decimal base_salary_monthly
        date hire_date
        date termination_date
        boolean is_active
        timestamps
    }
    
    employee_availability {
        uuid id PK
        uuid employee_id FK
        date date
        string type
        string reason
        decimal hours_available
        timestamps
    }
    
    payroll_runs {
        uuid id PK
        uuid organization_id FK
        string period
        date period_start
        date period_end
        string status
        timestamps
    }
    
    payroll_items {
        uuid id PK
        uuid payroll_run_id FK
        uuid employee_id FK
        decimal base_amount
        decimal timesheet_amount
        decimal total_amount
        string status
        timestamps
    }
    
    %% ========== INVENTORY ==========
    warehouses ||--o{ stock_levels : "holds"
    skus ||--o{ stock_levels : "at"
    skus ||--o{ purchase_order_lines : "ordered"
    skus ||--o{ project_requisitions : "reserved"
    purchase_orders ||--o{ purchase_order_lines : "has"
    projects ||--o{ project_requisitions : "requests"
    
    warehouses {
        uuid id PK
        uuid organization_id FK
        string name
        string code UK
        string address
        boolean is_default
        timestamps
    }
    
    skus {
        uuid id PK
        uuid organization_id FK
        string code UK
        string name
        string unit
        decimal reorder_point
        decimal reorder_quantity
        boolean is_active
        timestamps
    }
    
    stock_levels {
        uuid id PK
        uuid warehouse_id FK
        uuid sku_id FK
        decimal quantity
        decimal reserved_quantity
        decimal reorder_point
        timestamps
        UK(warehouse_id, sku_id)
    }
    
    purchase_orders {
        uuid id PK
        uuid organization_id FK
        uuid warehouse_id FK
        string number UK
        string status
        date order_date
        date expected_date
        uuid created_by_user_id FK
        timestamps
    }
    
    purchase_order_lines {
        uuid id PK
        uuid purchase_order_id FK
        uuid sku_id FK
        decimal quantity_ordered
        decimal quantity_received
        decimal unit_price
        timestamps
    }
    
    project_requisitions {
        uuid id PK
        uuid project_id FK
        uuid task_id FK
        uuid sku_id FK
        uuid warehouse_id FK
        decimal quantity_reserved
        decimal quantity_issued
        string status
        timestamps
    }
    
    %% ========== PROJECT MANAGEMENT ==========
    projects ||--o{ milestones : "has"
    milestones ||--o{ tasks : "has"
    tasks ||--o{ task_assignments : "has"
    tasks ||--o{ task_materials : "has"
    tasks ||--o{ timesheets : "against"
    tasks ||--o{ project_requisitions : "has"
    
    projects {
        uuid id PK
        uuid organization_id FK
        uuid customer_id FK
        uuid source_lead_id FK
        string name
        string code UK
        string status
        date start_date
        date end_date
        uuid project_manager_id FK
        decimal budget_hours
        timestamps
    }
    
    milestones {
        uuid id PK
        uuid project_id FK
        string name
        string description
        date target_date
        string status
        integer sort_order
        timestamps
    }
    
    tasks {
        uuid id PK
        uuid milestone_id FK
        string name
        string description
        string status
        integer sort_order
        date start_date
        date end_date
        decimal estimated_hours
        timestamps
    }
    
    task_assignments {
        uuid id PK
        uuid task_id FK
        uuid employee_id FK
        string role
        decimal allocation_pct
        timestamps
        UK(task_id, employee_id)
    }
    
    task_materials {
        uuid id PK
        uuid task_id FK
        uuid sku_id FK
        decimal quantity_required
        decimal quantity_consumed
        timestamps
        UK(task_id, sku_id)
    }
    
    timesheets {
        uuid id PK
        uuid organization_id FK
        uuid employee_id FK
        uuid task_id FK
        date work_date
        decimal hours
        string status
        string notes
        uuid approved_by_user_id FK
        timestamps
    }
```

---

## 3. Table Definitions (Logical Schema)

### 3.1 Shared / Authentication

| Table | Purpose | Key FKs |
|-------|---------|--------|
| **organizations** | Tenant root. All data is scoped by `organization_id`. | — |
| **users** | System login. Linked to **employees** for staff; used for JWT and RBAC. | organization_id |
| **roles** | Organization-level roles (e.g. "Project Manager", "Finance Admin"). | organization_id |
| **permissions** | Global list of granular permissions (e.g. `inventory.view`, `finance.edit`, `crm.lead.create`). | — |
| **role_permissions** | Many-to-many: which permissions each role has. | role_id, permission_id |
| **user_roles** | Many-to-many: which roles each user has. | user_id, role_id |

- **ERP:** Sidebar and menu items are driven by user permissions (e.g. show "Inventory" only if user has any `inventory.*` permission).

---

### 3.2 CRM (Lead-to-Contract)

| Table | Purpose | Key FKs |
|-------|---------|--------|
| **leads** | Lead pipeline: Prospect → Qualified → Proposal → Negotiation → Closed-Won/Closed-Lost. | organization_id, assigned_to_user_id, converted_customer_id, converted_project_id |
| **customers** | Customer master. Created when a lead is converted to Closed-Won. | organization_id, source_lead_id |
| **customer_contacts** | Contacts per customer (for Customer 360 and communications). | customer_id |
| **invoices** | Invoices for billing (owned by Finance; linked here for Customer 360 view). | organization_id, customer_id, project_id |

- **Conversion:** When a lead moves to Closed-Won, the app creates one **customers** row and one **projects** row, and sets `leads.converted_customer_id`, `leads.converted_project_id`, and `customers.source_lead_id`, `projects.source_lead_id`.
- **Customer 360:** Single view = customer + its **projects** + its **invoices** (filter `invoices.status != 'paid'` for unpaid).

---

### 3.3 HRM (Talent & Utilization)

| Table | Purpose | Key FKs |
|-------|---------|--------|
| **employees** | Employee master. One-to-one with **users** for system access. | organization_id, user_id |
| **employee_availability** | Calendar of availability, leave, or reduced hours (for utilization and over-allocation checks). | employee_id |
| **payroll_runs** | Monthly (or period) payroll batch. | organization_id |
| **payroll_items** | Per-employee line in a payroll run: base salary + timesheet-based amount. | payroll_run_id, employee_id |

- **New hire:** Creating an **employees** record can trigger creation of a **users** record (and optional default role).
- **Payroll:** `payroll_items.timesheet_amount` is computed from **timesheets** (PM) for that employee and period; `total_amount = base_amount + timesheet_amount` (or your formula).
- **Availability vs PM:** Project Management checks **employee_availability** and **task_assignments** + **timesheets** to prevent over-allocation.

---

### 3.4 Inventory (Supply Chain)

| Table | Purpose | Key FKs |
|-------|---------|--------|
| **warehouses** | Warehouse/location master. | organization_id |
| **skus** | Product/SKU master; includes `reorder_point` and `reorder_quantity`. | organization_id |
| **stock_levels** | Per-warehouse, per-SKU: `quantity`, `reserved_quantity`, optional override `reorder_point`. | warehouse_id, sku_id |
| **purchase_orders** | PO header. Can be system-generated when stock falls below reorder point. | organization_id, warehouse_id, created_by_user_id |
| **purchase_order_lines** | PO lines: SKU, quantity, received quantity, unit price. | purchase_order_id, sku_id |
| **project_requisitions** | Project (and task) reserves/requisitions inventory. | project_id, task_id, sku_id, warehouse_id |

- **Reorder:** When `stock_levels.quantity - reserved_quantity < reorder_point`, the system can create a **purchase_orders** + **purchase_order_lines**.
- **Project requisition:** PM reserves stock via **project_requisitions**; **stock_levels.reserved_quantity** is updated so available = quantity - reserved. Issue flow can decrease `reserved_quantity` and `quantity` when materials are issued.

---

### 3.5 Project Management (Engine)

| Table | Purpose | Key FKs |
|-------|---------|--------|
| **projects** | Project workspace. Created from CRM (Closed-Won) or manually; linked to **customers**. | organization_id, customer_id, source_lead_id, project_manager_id |
| **milestones** | Project phases or milestones. | project_id |
| **tasks** | Tasks under a milestone. | milestone_id |
| **task_assignments** | Which employees are assigned to which task (and allocation %). | task_id, employee_id |
| **task_materials** | Which SKUs (and quantities) a task needs. | task_id, sku_id |
| **timesheets** | Hours logged by employee on a task. Used for payroll (HRM) and client billing (CRM/Finance). | organization_id, employee_id, task_id, approved_by_user_id |

- **Assign task:** When assigning a task, the system can check **task_materials** and **stock_levels** (and **project_requisitions**) to ensure materials are available or reserved.
- **Log hours:** **Timesheets** feed into **payroll_items** (HRM) and into invoicing (Finance/CRM via project → customer).

---

## 4. Cross-Module Integration Points (Schema Support)

| Trigger | Source Module | Tables / FKs Involved | Impacted Module |
|---------|----------------|------------------------|-----------------|
| Close Deal (Closed-Won) | CRM | leads → customers, projects (converted_*_id, source_lead_id) | Project Management (new project), Customer 360 |
| Log Hours | Project Mgmt | timesheets (employee_id, task_id, hours, status) | HRM (payroll_items.timesheet_amount), CRM/Finance (billing) |
| Assign Task | Project Mgmt | task_assignments, task_materials, stock_levels, project_requisitions | Inventory (reserve/check stock) |
| New Hire | HRM | employees.user_id → users | Authentication (create user, assign role) |
| Stock below reorder | Inventory | stock_levels.quantity, reorder_point → purchase_orders | Procurement (create PO) |
| Reserve for project | Project Mgmt / Inventory | project_requisitions, stock_levels.reserved_quantity | Inventory (availability) |

---

## 5. Standard Conventions

- **Primary keys:** UUID for all main entities (good for distributed and merging).
- **Multi-tenancy:** All business data tables carry `organization_id` where applicable; APIs and ORM scope by organization.
- **Soft delete:** Optional `deleted_at` on critical entities (e.g. users, customers, employees) can be added later without changing the ERD.
- **Timestamps:** `created_at`, `updated_at` on all tables.
- **Unique keys:** Documented in the ERD (e.g. `(organization_id, code)` for customers, `(warehouse_id, sku_id)` for stock_levels).

---

## 6. API Response Standard (Reference)

All Flask routes will return:

```json
{
  "status": "success",
  "data": { ... },
  "message": ""
}
```

Error responses will use the same structure with `status: "error"` and optional `message` and `errors` (validation). This is noted here for alignment with the schema; implementation comes after approval.

---

## 7. Next Steps After Approval

1. **Base:** Flask backend + PostgreSQL connection + Auth (JWT, RBAC, ERP dynamic sidebar).
2. **Core:** HRM and CRM (people and customer data).
3. **Flow:** Inventory and Project Management (work and materials).

If you approve this schema (or specify changes), the next step is to implement it in SQLAlchemy models and then build the APIs and ERP Vue front end accordingly.
