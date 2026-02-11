"""Authentication: login, register, me, refresh, Google OAuth."""
import base64
import re
import urllib.parse

from flask import Blueprint, request, redirect, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)

from authlib.integrations.requests_client import OAuth2Session

from app.extensions import db
from app.models import User, Organization, Role, RolePermission, Permission, UserRole
from app.utils.response import api_success, api_error
from app.utils.auth_utils import hash_password, check_password

auth_bp = Blueprint("auth", __name__)

# Google OAuth endpoints
GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new organization and admin user."""
    data = request.get_json() or {}
    org_name = data.get("organization_name") or data.get("organizationName")
    org_code = data.get("organization_code") or data.get("organizationCode")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name") or data.get("fullName")

    if not all([org_name, org_code, email, password, full_name]):
        return api_error("Missing required fields: organization_name, organization_code, email, password, full_name", status_code=400)

    if User.query.filter_by(email=email).first():
        return api_error("Email already registered", status_code=400)
    if Organization.query.filter_by(code=org_code).first():
        return api_error("Organization code already taken", status_code=400)

    org = Organization(name=org_name, code=org_code.strip().upper())
    db.session.add(org)
    db.session.flush()

    user = User(
        organization_id=org.id,
        email=email.strip().lower(),
        password_hash=hash_password(password),
        full_name=full_name.strip(),
        is_active=True,
    )
    db.session.add(user)
    db.session.flush()

    # Assign default admin role if exists
    admin_role = Role.query.filter_by(organization_id=org.id, name="Admin").first()
    if not admin_role:
        admin_role = Role(organization_id=org.id, name="Admin", description="Full access")
        db.session.add(admin_role)
        db.session.flush()
        for perm in Permission.query.all():
            db.session.add(RolePermission(role_id=admin_role.id, permission_id=perm.id))
    db.session.add(UserRole(user_id=user.id, role_id=admin_role.id))
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return api_success(
        data={
            "user": user.to_dict(),
            "organization": org.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
        message="Registration successful",
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login and return JWT tokens."""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return api_error("Email and password required", status_code=400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.password_hash or not check_password(password, user.password_hash):
        return api_error("Invalid email or password", status_code=401)
    if not user.is_active:
        return api_error("Account is disabled", status_code=401)

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return api_success(
        data={
            "user": user.to_dict(),
            "organization": user.organization.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Return current user, organization, and permissions (for dynamic sidebar)."""
    from app.api.decorators import get_current_user
    user = get_current_user()
    if not user:
        return api_error("User not found", status_code=401)
    return api_success(
        data={
            "user": user.to_dict(),
            "organization": user.organization.to_dict(),
            "permissions": list(user.get_permission_ids()),
        },
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user or not user.is_active:
        return api_error("User not found or inactive", status_code=401)
    access_token = create_access_token(identity=user.id)
    return api_success(data={"access_token": access_token})


def _allowed_redirect_uri(redirect_uri: str) -> bool:
    """Allow only frontend origin to prevent open redirect."""
    frontend = (current_app.config.get("FRONTEND_URL") or "").rstrip("/")
    if not frontend:
        return True
    return redirect_uri.rstrip("/").startswith(frontend) or redirect_uri == frontend


@auth_bp.route("/google", methods=["GET"])
def google_start():
    """Redirect user to Google consent page. Query: redirect_uri (where to send user after login)."""
    client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    client_secret = current_app.config.get("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        return api_error("Google sign-in is not configured", status_code=503)

    redirect_uri = request.args.get("redirect_uri") or ""
    redirect_uri = urllib.parse.unquote(redirect_uri)
    if not redirect_uri:
        return api_error("redirect_uri is required", status_code=400)
    if not _allowed_redirect_uri(redirect_uri):
        return api_error("redirect_uri not allowed", status_code=400)

    callback_url = request.url_root.rstrip("/") + "/api/auth/google/callback"
    state = base64.urlsafe_b64encode(redirect_uri.encode("utf-8")).decode("ascii")

    session = OAuth2Session(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=callback_url,
        scope="openid email profile",
    )
    url, _ = session.create_authorization_url(
        GOOGLE_AUTHORIZE_URL,
        state=state,
        prompt="select_account",
    )
    return redirect(url)


@auth_bp.route("/google/callback", methods=["GET"])
def google_callback():
    """Exchange code for tokens, get user info, find/create user, redirect to frontend with JWT."""
    client_id = current_app.config.get("GOOGLE_CLIENT_ID")
    client_secret = current_app.config.get("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        return redirect(_frontend_error_redirect("oauth_not_configured", "Google sign-in is not configured"))

    state = request.args.get("state") or ""
    try:
        redirect_uri = base64.urlsafe_b64decode(state.encode("ascii")).decode("utf-8")
    except Exception:
        redirect_uri = (current_app.config.get("FRONTEND_URL") or "http://localhost:5173").rstrip("/") + "/signin/callback"
    if not _allowed_redirect_uri(redirect_uri):
        redirect_uri = (current_app.config.get("FRONTEND_URL") or "http://localhost:5173").rstrip("/") + "/signin/callback"

    code = request.args.get("code")
    if not code:
        error = request.args.get("error", "unknown")
        return redirect(_frontend_error_redirect("google_denied", error))

    callback_url = request.url_root.rstrip("/") + "/api/auth/google/callback"
    session = OAuth2Session(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=callback_url,
    )
    try:
        token = session.fetch_token(
            GOOGLE_TOKEN_URL,
            code=code,
            authorization_response=request.url,
        )
    except Exception as e:
        current_app.logger.warning("Google token exchange failed: %s", e)
        return redirect(_frontend_error_redirect("token_failed", "Could not sign in with Google"))

    access_token_google = token.get("access_token")
    if not access_token_google:
        return redirect(_frontend_error_redirect("token_failed", "No access token from Google"))

    # Session already has the token from fetch_token; no need to pass token= to get()
    resp = session.get(GOOGLE_USERINFO_URL)
    if resp.status_code != 200:
        return redirect(_frontend_error_redirect("userinfo_failed", "Could not get profile from Google"))
    info = resp.json()
    google_id = info.get("sub")
    email = (info.get("email") or "").strip().lower()
    name = (info.get("name") or email or "User").strip()

    if not email:
        return redirect(_frontend_error_redirect("no_email", "Google did not provide an email"))

    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_id = google_id
            db.session.commit()
        else:
            # Sign up with Google: create new organization and user (same as register flow)
            org_code = _unique_org_code_for_google(email, google_id)
            org = Organization(name=f"Personal ({name})", code=org_code)
            db.session.add(org)
            db.session.flush()

            user = User(
                organization_id=org.id,
                email=email,
                password_hash=None,
                google_id=google_id,
                full_name=name,
                is_active=True,
            )
            db.session.add(user)
            db.session.flush()

            admin_role = Role.query.filter_by(organization_id=org.id, name="Admin").first()
            if not admin_role:
                admin_role = Role(organization_id=org.id, name="Admin", description="Full access")
                db.session.add(admin_role)
                db.session.flush()
                for perm in Permission.query.all():
                    db.session.add(RolePermission(role_id=admin_role.id, permission_id=perm.id))
            db.session.add(UserRole(user_id=user.id, role_id=admin_role.id))
            db.session.commit()

    if not user.is_active:
        return redirect(_frontend_error_redirect("account_disabled", "Account is disabled"))

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    target = f"{redirect_uri}#access_token={urllib.parse.quote(access_token)}&refresh_token={urllib.parse.quote(refresh_token)}"
    return redirect(target)


def _frontend_error_redirect(error_code: str, message: str) -> str:
    base = (current_app.config.get("FRONTEND_URL") or "http://localhost:5173").rstrip("/") + "/signin/callback"
    return f"{base}?error={urllib.parse.quote(error_code)}&message={urllib.parse.quote(message)}"


def _unique_org_code_for_google(email: str, google_id: str) -> str:
    """Generate a unique organization code for Google sign-up (e.g. PERSONAL_ABC12)."""
    safe = re.sub(r"[^a-z0-9]", "", email.split("@")[0].lower())[:8] or "user"
    suffix = (google_id[:6] if google_id else "") or "0"
    base_code = f"PERSONAL_{safe.upper()}{suffix.upper()}"
    code = base_code
    n = 0
    while Organization.query.filter_by(code=code).first():
        n += 1
        code = f"{base_code}{n}"
    return code
