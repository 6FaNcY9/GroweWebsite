from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    data_dir: Path = Path(__file__).resolve().parents[2] / "data"
    hero_provider: Literal["mock", "mapi"] = "mock"
    http_timeout_seconds: float = 10.0

    class Config:
        env_prefix = "ml_"


@lru_cache
def get_settings() -> Settings:
    return Settings()
