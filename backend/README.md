# Custom ERP — Flask Backend

RESTful API with JWT auth, RBAC, and PostgreSQL.

## Setup

1. Create a PostgreSQL database, e.g. `erp_db`.
2. Copy `.env.example` to `.env` and set `DATABASE_URL` and secrets.
3. Create virtualenv and install deps:

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

4. Create tables and seed permissions (run from `backend` folder):

   **PowerShell:**
   ```powershell
   $env:FLASK_APP="run.py"
   flask db init
   flask db migrate -m "Initial schema"
   flask db upgrade
   ```

   **Cmd:**
   ```cmd
   set FLASK_APP=run.py
   flask db init
   flask db migrate -m "Initial schema"
   flask db upgrade
   ```

5. Run the server:

   ```bash
   python run.py
   ```

API base: `http://localhost:5000`. Health: `GET /api/health`.

## Auth

- **POST /api/auth/register** — Body: `organization_name`, `organization_code`, `email`, `password`, `full_name`
- **POST /api/auth/login** — Body: `email`, `password` → returns `access_token`, `refresh_token`
- **GET /api/auth/me** — Header: `Authorization: Bearer <access_token>` → user, organization, permissions (for dynamic sidebar)
- **POST /api/auth/refresh** — Header: `Authorization: Bearer <refresh_token>` → new access_token

All other routes require `Authorization: Bearer <access_token>` and the appropriate permission (e.g. `crm.view`, `inventory.edit`).

## Response format

All responses: `{ "status": "success"|"error", "data": { ... }, "message": "" }`
