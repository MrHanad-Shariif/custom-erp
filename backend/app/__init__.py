"""Flask application factory."""
import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from app.config import config_by_name
from app.extensions import db
from app.utils.response import api_success


def create_app(config_name=None):
    """Create and configure the Flask app."""
    app = Flask(__name__)
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    # CORS: allow localhost in dev and FRONTEND_URL in production
    _cors_origins = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    _frontend_url = app.config.get("FRONTEND_URL")
    if _frontend_url:
        _cors_origins.append(_frontend_url.rstrip("/"))
    CORS(app, supports_credentials=True, origins=_cors_origins)

    # Ensure models are registered
    from app import models  # noqa: F401

    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.organizations import org_bp
    from app.api.users import users_bp
    from app.api.roles import roles_bp
    from app.api.leads import leads_bp
    from app.api.customers import customers_bp
    from app.api.employees import employees_bp
    from app.api.warehouses import warehouses_bp
    from app.api.skus import skus_bp
    from app.api.stock import stock_bp
    from app.api.purchase_orders import purchase_orders_bp
    from app.api.projects import projects_bp
    from app.api.timesheets import timesheets_bp
    from app.api.payroll import payroll_bp
    from app.api.invoices import invoices_bp
    from app.api.dashboard import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(org_bp, url_prefix="/api/organizations")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(roles_bp, url_prefix="/api/roles")
    app.register_blueprint(leads_bp, url_prefix="/api/crm/leads")
    app.register_blueprint(customers_bp, url_prefix="/api/crm/customers")
    app.register_blueprint(employees_bp, url_prefix="/api/hrm/employees")
    app.register_blueprint(warehouses_bp, url_prefix="/api/inventory/warehouses")
    app.register_blueprint(skus_bp, url_prefix="/api/inventory/skus")
    app.register_blueprint(stock_bp, url_prefix="/api/inventory/stock")
    app.register_blueprint(purchase_orders_bp, url_prefix="/api/inventory/purchase-orders")
    app.register_blueprint(projects_bp, url_prefix="/api/pm/projects")
    app.register_blueprint(timesheets_bp, url_prefix="/api/pm/timesheets")
    app.register_blueprint(payroll_bp, url_prefix="/api/hrm/payroll")
    app.register_blueprint(invoices_bp, url_prefix="/api/finance/invoices")

    @app.route("/api/health")
    def health():
        return api_success({"status": "ok"})

    with app.app_context():
        from app.seed_permissions import seed_permissions
        seed_permissions()

    return app
