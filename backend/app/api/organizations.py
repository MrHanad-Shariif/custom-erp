"""Organizations API (current org only for now)."""
from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.api.decorators import get_current_user
from app.utils.response import api_success, api_error

org_bp = Blueprint("organizations", __name__)


@org_bp.route("/current", methods=["GET"])
@jwt_required()
def current():
    """Return current user's organization."""
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", status_code=401)
    return api_success(data=user.organization.to_dict())
