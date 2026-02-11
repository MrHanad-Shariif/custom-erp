# Deploy Custom ERP to Render – Step by Step

You will create **three** things on Render: **PostgreSQL**, **Backend (Web Service)**, and **Frontend (Static Site)**. The backend and frontend must be deployed from your **Git repository**, so do Step 0 first.

---

## Step 0: Put your code on GitHub (or GitLab / Bitbucket)

Render deploys from Git. If your project is not in a repo yet:

1. Create a new repository on **GitHub** (e.g. `custom-erp`). Do **not** add a README (you already have code).
2. On your machine, in the **project root** (the folder that contains `backend`, `frontend`, `docs`):

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

3. Replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub username and repo name.

---

## Step 1: Create a PostgreSQL database on Render

1. In Render dashboard: **New +** → **PostgreSQL**.
2. Name it (e.g. `erp-db`), choose region, then **Create Database**.
3. After it’s created, open the database and copy the **Internal Database URL** (you’ll use it for the backend).  
   - You can use the **External** URL if your backend will run outside Render; for a Render Web Service use **Internal**.

---

## Step 2: Connect Git and create the Backend (Web Service)

1. In Render: **New +** → **Web Service**.
2. **Connect your Git provider** (e.g. GitHub) if you haven’t already. Authorize Render and select the repo that contains your project (the one with `backend/` and `frontend/`).
3. **Configure the Web Service:**
   - **Name:** e.g. `custom-erp-api`
   - **Region:** same as your database (or closest to you).
   - **Branch:** `main` (or your default branch).
   - **Root Directory:** `backend`  
     (so Render runs commands inside the `backend` folder).
   - **Runtime:** `Python 3`.
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && flask db upgrade
     ```
   - **Start Command:**
     ```bash
     gunicorn --bind 0.0.0.0:$PORT run:app
     ```
     (Render sets `PORT`; gunicorn will listen on it.)
4. **Environment variables** (Add Environment Variable):
   - `FLASK_ENV` = `production`
   - `DATABASE_URL` = paste the **Internal Database URL** from Step 1.
   - `SECRET_KEY` = a long random string (e.g. generate one at https://randomkeygen.com/).
   - `JWT_SECRET_KEY` = another long random string (or same as SECRET_KEY).
   - `FRONTEND_URL` = leave empty for now; after you create the frontend in Step 3, set this to your **frontend** URL (e.g. `https://custom-erp.onrender.com`).
   - If you use Google Sign-in: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` (and keep `FRONTEND_URL` set to the frontend URL).
5. Click **Create Web Service**. Wait for the first deploy to finish.
6. Copy your backend URL (e.g. `https://custom-erp-api.onrender.com`). You’ll need it for the frontend and for `FRONTEND_URL` / Google Console.

---

## Step 3: Create the Frontend (Static Site)

1. In Render: **New +** → **Static Site**.
2. Select the **same** GitHub repo as the backend.
3. **Configure the Static Site:**
   - **Name:** e.g. `custom-erp`
   - **Branch:** `main`.
   - **Root Directory:** `frontend/tailadmin-vuejs-1.0.0`  
     (the folder that contains `package.json` and `vite.config.ts`).
   - **Build Command:**
     ```bash
     npm ci && npm run build
     ```
   - **Publish Directory:** `dist`  
     (Vite outputs the built files here).
4. **Environment variable** (so the frontend calls your backend):
   - Key: `VITE_API_URL`  
   - Value: your **backend** URL from Step 2, e.g. `https://custom-erp-api.onrender.com`  
   (no trailing slash).
5. Click **Create Static Site**. Wait for the build to finish.
6. Copy your frontend URL (e.g. `https://custom-erp.onrender.com`).

---

## Step 4: Wire backend and frontend together

1. **Backend:** Open your Web Service → **Environment** → add or edit:
   - `FRONTEND_URL` = your **frontend** URL from Step 3 (e.g. `https://custom-erp.onrender.com`).  
   This is used for CORS and for Google OAuth redirect.
2. **Redeploy** the backend (Manual Deploy or push a commit) so it picks up `FRONTEND_URL`.
3. **Google OAuth (if you use it):** In Google Cloud Console, add:
   - **Authorized JavaScript origins:** your frontend URL (e.g. `https://custom-erp.onrender.com`).
   - **Authorized redirect URIs:** `https://custom-erp-api.onrender.com/api/auth/google/callback`  
   (your backend URL + `/api/auth/google/callback`).

---

## Summary

| Step | What you create      | Result |
|------|----------------------|--------|
| 0    | Push code to GitHub  | Repo Render can use |
| 1    | PostgreSQL           | Database URL |
| 2    | Web Service (backend)| Backend URL, Root: `backend` |
| 3    | Static Site (frontend)| Frontend URL, Root: `frontend/tailadmin-vuejs-1.0.0` |
| 4    | Set `FRONTEND_URL` on backend, update Google OAuth | App and Sign in with Google work |

**Useful:**  
- Backend health: `https://YOUR-BACKEND-URL/api/health`  
- Frontend: open the frontend URL in the browser; sign up or sign in; the app will call the backend automatically.
