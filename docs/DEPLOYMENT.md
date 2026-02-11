# Deploying Custom ERP on Render

## How backend and frontend work together

**They do not run on the same server.** On Render you deploy **two separate services**:

| Service   | What it is        | Runs on                    | Role |
|----------|-------------------|----------------------------|------|
| **Backend**  | Flask API (Python) | e.g. `https://your-erp-api.onrender.com`  | Serves REST API, auth, database, business logic. |
| **Frontend** | Vue.js SPA         | e.g. `https://your-erp.onrender.com`      | Serves HTML/JS/CSS; runs in the **user’s browser**. |

### Flow when a user uses the app

1. User opens the **frontend URL** in the browser → Render serves the built Vue app (static files).
2. The Vue app loads and runs in the **browser**.
3. When the app needs data (login, list leads, etc.), it sends **HTTP requests to the backend URL** (e.g. `https://your-erp-api.onrender.com/api/...`).
4. The **backend** (running on its own Render service) receives the request, talks to the database, and returns JSON.
5. The frontend receives the response and updates the UI.

So:

- **Two servers:** one for the API, one for the frontend static site.
- **One place the “app” runs:** the frontend code runs in the user’s browser; the backend runs on Render.
- **They “work together”** by the frontend knowing the backend’s URL (via env) and calling it for all API requests.

---

## What you need on Render

### 1. Backend (Web Service)

- **Type:** Web Service.
- **Build:** e.g. `pip install -r requirements.txt`, `flask db upgrade` if you run migrations in build.
- **Start:** e.g. `gunicorn run:app` (with correct bind/port for Render).
- **Env vars:** `DATABASE_URL` (Render PostgreSQL or external), `SECRET_KEY`, and any other your app needs (e.g. future OAuth `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`).
- **Result:** One URL like `https://your-erp-api.onrender.com`.

### 2. Frontend (Static Site or Web Service)

- **Option A – Static Site (recommended for Vue/Vite):**  
  Build command: `npm ci && npm run build`.  
  Publish directory: `dist`.  
  Render serves the `dist` files. Users get the frontend from a URL like `https://your-erp.onrender.com`.

- **Option B – Web Service:**  
  Serve the `dist` folder with a small static server (e.g. Node). Less common for a pure SPA.

### 3. Connect frontend to backend

- In the **frontend** project, set an env var that your app uses as the API base URL, e.g.:
  - **Name:** `VITE_API_URL` (or whatever your Vite app reads).
  - **Value:** `https://your-erp-api.onrender.com` (your real backend URL).
- Rebuild the frontend so the build bakes in this URL. Then all API calls from the browser go to the backend on Render.

### 4. CORS

- The backend must allow requests **from the frontend origin** (e.g. `https://your-erp.onrender.com`). In Flask, configure CORS so the frontend URL is an allowed origin (and in production don’t use `*` if you care about credentials).

### 5. Database

- Use a **PostgreSQL** instance (Render PostgreSQL or another provider). Set `DATABASE_URL` on the backend service. Run migrations as part of deploy or a separate step.

---

## Summary

| Question | Answer |
|----------|--------|
| Do backend and frontend run on the same server? | **No.** They are two separate Render services (two URLs). |
| Where does the Vue app run? | In the **user’s browser**. Render only serves the built files. |
| How do they work together? | The frontend is configured with the backend URL and calls it for all API requests. |
| What do you deploy? | (1) Backend Web Service, (2) Frontend Static Site (or Web Service), (3) PostgreSQL, (4) Env vars and CORS so the frontend can talk to the backend. |

Once this is set up, the project runs on Render with the API and the frontend working together as described above.
