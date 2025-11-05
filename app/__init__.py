from pathlib import Path
import os

from flask import Flask
from werkzeug.security import generate_password_hash

from .blueprints.admin import admin_bp
from .blueprints.api import api_bp
from .blueprints.storefront import storefront_bp
from .cli import register_cli
from .config import resolve_config
from .extensions import csrf, db


def _configure_admin_password(app: Flask) -> None:
    admin_password_hash = os.environ.get("ADMIN_PASSWORD_HASH")
    if admin_password_hash:
        app.config["ADMIN_PASSWORD_HASH"] = admin_password_hash
        return

    fallback_password = os.environ.get("ADMIN_PASSWORD", "growe-admin")
    app.config["ADMIN_PASSWORD_HASH"] = generate_password_hash(fallback_password)


def create_app(test_config: dict | None = None) -> Flask:
    """Application factory for the Growe seed store."""
    app = Flask(__name__, instance_relative_config=True)

    env = os.environ.get("GROWE_ENV", "development")
    config_cls = resolve_config(env)
    default_db_path = Path(app.instance_path) / "growe.sqlite3"
    app.config.from_object(config_cls)
    app.config.setdefault(
        "SQLALCHEMY_DATABASE_URI", config_cls.database_uri(default_db_path)
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    _configure_admin_password(app)

    db.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(storefront_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    register_cli(app)

    @app.context_processor
    def inject_global_context() -> dict[str, object]:
        from datetime import datetime

        from .forms import NewsletterForm
        from .models import SiteSetting

        settings = SiteSetting.as_dict()
        return {
            "company_name": app.config.get("GROWE_COMPANY_NAME", "Growe Seed Co."),
            "tailwind_cdn_version": app.config.get("TAILWIND_CDN_VERSION", "3.4.3"),
            "site_settings": settings,
            "announcement": settings.get("announcement"),
            "current_year": datetime.utcnow().year,
            "newsletter_form": NewsletterForm(),
        }

    with app.app_context():
        from . import models

        db.create_all()

        if models.SiteSetting.query.count() == 0:
            models.SiteSetting.seed_defaults()
            db.session.commit()

        if models.Product.query.count() == 0:
            models.Product.seed_defaults()
            db.session.commit()

    return app
