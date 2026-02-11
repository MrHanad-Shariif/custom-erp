# Google Sign-in (OAuth) – What You Need to Do

The app supports **Sign in with Google**. To enable it, you need to create OAuth credentials in Google Cloud and add them to your backend.

---

## 1. What to create in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a **project**.
3. **OAuth consent screen**
   - APIs & Services → **OAuth consent screen**
   - User type: **External** (so any Google user can sign in; use Internal only if you use Google Workspace and want to limit to your org).
   - Fill App name, User support email, Developer contact. Add scopes: **email**, **profile**, **openid** (these are usually added by default when you add the Google OAuth client).
   - If the app is in **Testing**: add your own email (and any test users) under **Test users**. Only these accounts can sign in until you publish.
   - When ready for everyone: click **Publish app** so the app is **In production** (no need to add each user’s email).
4. **Credentials**
   - APIs & Services → **Credentials** → **Create credentials** → **OAuth client ID**
   - Application type: **Web application**
   - **Authorized JavaScript origins** (your frontend):
     - Local: `http://localhost:5173`
     - Production: `https://your-frontend-domain.com`
   - **Authorized redirect URIs** (your **backend** callback, not the frontend):
     - Local: `http://localhost:5000/api/auth/google/callback`
     - Production: `https://your-api-domain.com/api/auth/google/callback`
   - Create → copy the **Client ID** and **Client secret**.

---

## 2. What to share with the code / environment

You only need to put these in your **backend** `.env` (never commit the real file; use `.env.example` as a template without real values):

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLIENT_ID` | OAuth 2.0 Client ID from Google | `123...abc.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0 Client secret from Google | `GOCSPX-...` |
| `FRONTEND_URL` | Base URL of your frontend (used to validate redirect) | `http://localhost:5173` or `https://your-app.com` |

- **Local:** e.g. `FRONTEND_URL=http://localhost:5173`
- **Production:** set `FRONTEND_URL` to your real frontend origin (e.g. `https://your-erp.onrender.com`).

No need to add each user’s email in Google Console: in **Testing** only test users can sign in; in **Production** any Google account can.

---

## 3. Behaviour in the app

- **Sign in with Google** is only for **existing** users: the backend looks up the user by Google ID or by email. If no user exists for that Google email, the user sees: *“No account with this Google email. Please sign up first.”*
- Users who signed up with email/password can later use **Sign in with Google** if their email matches; the backend will link their account to Google.
- After a successful Google sign-in, the user is redirected to the frontend with tokens and is logged in like a normal sign-in.

---

## 4. Quick checklist

- [ ] Google Cloud project created
- [ ] OAuth consent screen configured (External or Internal), scopes email, profile, openid
- [ ] OAuth 2.0 Web client created
- [ ] Authorized JavaScript origins = your frontend URL(s)
- [ ] Authorized redirect URIs = your **backend** URL(s) ending with `/api/auth/google/callback`
- [ ] `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `FRONTEND_URL` set in backend `.env`
- [ ] Backend and frontend running; test “Sign in with Google” with an existing user’s email
