import os
from flask import Flask, render_template
from config import config_map
from app.extensions import db, login_manager, bcrypt, csrf


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "default")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    register_blueprints(app)
    register_template_helpers(app)
    register_error_handlers(app)

    return app


def register_blueprints(app):
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.dashboard.routes import dashboard_bp
    from app.blueprints.sales.routes import sales_bp
    from app.blueprints.inventory.routes import inventory_bp
    from app.blueprints.customers.routes import customers_bp
    from app.blueprints.invoices.routes import invoices_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.api.routes import api_bp
    from app.blueprints.reports.routes import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(sales_bp, url_prefix="/sales")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(invoices_bp, url_prefix="/invoices")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/reports")


def register_template_helpers(app):
    @app.template_filter("currency")
    def currency_filter(value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0.0
        symbol = app.config.get("CURRENCY_SYMBOL", "$")
        return f"{symbol}{value:,.2f}"

    @app.template_filter("compact_number")
    def compact_number_filter(value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            return "0"
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        if value >= 1_000:
            return f"{value / 1_000:.1f}K"
        return f"{value:.0f}"

    @app.template_filter("compact_currency")
    def compact_currency_filter(value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0.0
        symbol = app.config.get("CURRENCY_SYMBOL", "$")
        if value >= 1_000_000:
            return f"{symbol}{value / 1_000_000:.1f}M"
        if value >= 1_000:
            return f"{symbol}{value / 1_000:.1f}K"
        return f"{symbol}{value:,.0f}"

    @app.context_processor
    def inject_globals():
        return {
            "app_name": app.config.get("APP_NAME"),
            "app_tagline": app.config.get("APP_TAGLINE"),
        }


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500
