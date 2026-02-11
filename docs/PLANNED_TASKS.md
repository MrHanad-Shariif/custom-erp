# Planned tasks & notes

## Google Sign-in (OAuth) — ✅ Implemented

- **Backend:** Authlib; routes `GET /api/auth/google` and `GET /api/auth/google/callback`; User has `google_id` and nullable `password_hash`.
- **Frontend:** “Sign in with Google” button and `/signin/callback` page to receive tokens.
- **Setup:** See `docs/GOOGLE_OAUTH_SETUP.md` for Google Cloud Console steps and env vars (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `FRONTEND_URL`).

---

*Add new items below as needed.*
