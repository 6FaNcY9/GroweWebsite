"""Utility helpers for the Growe application."""

from __future__ import annotations

import re

_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def slugify(value: str, fallback: str = "item") -> str:
    """Normalize arbitrary text into a URL-safe slug."""

    slug = _SLUG_PATTERN.sub("-", (value or "").lower()).strip("-")
    return slug or fallback
