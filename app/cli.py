"""Custom Flask CLI commands for operations teams."""
from __future__ import annotations

import click
from flask import current_app
from werkzeug.security import generate_password_hash

from .extensions import db
from .models import Product, SiteSetting


def register_cli(app) -> None:
    """Register reusable CLI commands on the provided Flask app."""

    @app.cli.command("seed-data")
    def seed_data() -> None:
        """Populate the database with default site settings and catalog data."""
        if SiteSetting.query.count() == 0:
            SiteSetting.seed_defaults()
            click.echo("Seeded default site settings.")
        else:
            click.echo("Site settings already populated.")

        if Product.query.count() == 0:
            Product.seed_defaults()
            click.echo("Seeded default products.")
        else:
            click.echo("Products already populated.")
        db.session.commit()

    @app.cli.command("hash-password")
    @click.argument("password")
    def hash_password(password: str) -> None:
        """Generate a password hash suitable for the ADMIN_PASSWORD_HASH env var."""
        click.echo(generate_password_hash(password))

    @app.cli.command("show-config")
    def show_config() -> None:
        """Display key runtime configuration values without secrets."""
        keys = [
            "SQLALCHEMY_DATABASE_URI",
            "GROWE_COMPANY_NAME",
            "TAILWIND_CDN_VERSION",
            "TESTING",
            "DEBUG",
        ]
        for key in keys:
            click.echo(f"{key}={current_app.config.get(key)}")
