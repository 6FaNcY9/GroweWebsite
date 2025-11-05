"""Application configuration objects."""
from __future__ import annotations

from pathlib import Path
import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TAILWIND_CDN_VERSION = os.environ.get("TAILWIND_CDN_VERSION", "3.4.3")
    GROWE_COMPANY_NAME = os.environ.get("GROWE_COMPANY_NAME", "Growe Seed Co.")

    @staticmethod
    def database_uri(default_path: Path) -> str:
        return os.environ.get("DATABASE_URL", f"sqlite:///{default_path}")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True

    @staticmethod
    def database_uri(default_path: Path) -> str:  # pragma: no cover - helper for factory
        return "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "https")


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def resolve_config(env: str) -> type[BaseConfig]:
    return CONFIG_MAP.get(env, DevelopmentConfig)
