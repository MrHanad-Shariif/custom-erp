# Custom Integrated ERP

Unified ERP with **Flask (Python)** backend and **Vue.js 3 (ERP)** frontend, and **PostgreSQL**.

## Modules

- **Auth** — JWT, RBAC (granular permissions), dynamic sidebar by role
- **CRM** — Leads, Customers, Customer 360, Lead → Project conversion
- **HRM** — Employees, availability, payroll (from timesheets)
- **Inventory** — Warehouses, SKUs, stock, purchase orders, project requisitions
- **Project Management** — Projects, milestones, tasks, timesheets
- **Finance** — Invoices (Customer 360)

## Quick start

### 1. Database

Create a PostgreSQL database, e.g. `erp_db`.

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
copy .env.example .env   # set DATABASE_URL, SECRET_KEY
set FLASK_APP=run.py
flask db init
flask db migrate -m "Initial"
flask db upgrade
python run.py
```

API: `http://localhost:5000`. See `backend/README.md` for auth and endpoints.

### 3. Frontend

```bash
cd frontend/ERP-vuejs-1.0.0
copy .env.example .env   # VITE_API_URL=http://localhost:5000
npm install
npm run dev
```

Open `http://localhost:5173`. Sign up (creates org + admin user), then sign in.

## Schema

See `docs/ERP_DATABASE_SCHEMA_ERD.md` for the full relational schema and integration points.

## Docs

- **Deployment (e.g. Render):** `docs/DEPLOYMENT.md` — how backend and frontend run as two services and work together.
- **Render step-by-step:** `docs/RENDER_DEPLOYMENT.md` — connect Git, create PostgreSQL + Web Service + Static Site, env vars.
- **Planned tasks:** `docs/PLANNED_TASKS.md` — e.g. Google Sign-in (OAuth).
