from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class SiteSetting(db.Model, TimestampMixin):
    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)

    @classmethod
    def get(cls, key: str, default: str = "") -> str:
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default

    @classmethod
    def set(cls, key: str, value: str) -> None:
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            db.session.add(cls(key=key, value=value))

    @classmethod
    def as_dict(cls) -> dict[str, str]:
        return {setting.key: setting.value for setting in cls.query.all()}

    @classmethod
    def seed_defaults(cls) -> None:
        defaults = {
            "announcement": "Free shipping on seed orders over $40 — grow something new today!",
            "hero_headline": "Cultivate your best season yet",
            "hero_subheadline": "Premium, lab-tested seeds, seasonal starter kits, and step-by-step guidance for thriving gardens.",
            "hero_primary_label": "Shop Featured Seeds",
            "hero_primary_url": "/products?filter=featured",
            "hero_secondary_label": "Browse Starter Kits",
            "hero_secondary_url": "/products?category=Starter%20Kits",
            "about_title": "Rooted in sustainable growing",
            "about_body": (
                "Growe partners with regenerative farms and horticulturists to curate seeds with exceptional germination rates. "
                "Our educational resources make it simple to plan, plant, and harvest regardless of experience."
            ),
            "newsletter_description": (
                "Join 25,000+ growers for planting guides, seasonal reminders, and exclusive seed drops delivered weekly."
            ),
            "contact_email": "hello@growe.com",
        }
        for key, value in defaults.items():
            db.session.add(cls(key=key, value=value))


@dataclass
class InventorySummary:
    total_products: int
    total_seeds_available: int
    low_stock_items: int


class Product(db.Model, TimestampMixin):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    germination_days = db.Column(db.Integer, default=7, nullable=False)
    sun_exposure = db.Column(db.String(40), default="Full Sun", nullable=False)
    difficulty = db.Column(db.String(40), default="Beginner", nullable=False)

    @classmethod
    def find_by_slug(cls, slug: str) -> "Product | None":
        return cls.query.filter_by(slug=slug).first()

    @classmethod
    def categories(cls) -> list[str]:
        return [row[0] for row in db.session.query(cls.category).distinct().order_by(cls.category)]

    @classmethod
    def inventory_summary(cls) -> InventorySummary:
        total_products = cls.query.count()
        total_seeds_available = db.session.query(func.sum(cls.stock)).scalar() or 0
        low_stock_items = cls.query.filter(cls.stock <= 10).count()
        return InventorySummary(total_products, total_seeds_available, low_stock_items)

    def to_dict(self) -> dict[str, str | int | float | bool]:
        """Serialize the product for API responses."""
        return {
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "price": float(self.price),
            "image_url": self.image_url,
            "category": self.category,
            "stock": self.stock,
            "is_featured": self.is_featured,
            "germination_days": self.germination_days,
            "sun_exposure": self.sun_exposure,
            "difficulty": self.difficulty,
        }

    @classmethod
    def seed_defaults(cls) -> None:
        products = [
            {
                "name": "Heirloom Cherry Tomato",
                "slug": "heirloom-cherry-tomato",
                "description": "Sweet, prolific vines ideal for patios and raised beds. Includes trellising tips and organic feeding schedule.",
                "price": 4.99,
                "image_url": "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?auto=format&fit=crop&w=800&q=80",
                "category": "Vegetables",
                "stock": 120,
                "is_featured": True,
                "germination_days": 7,
                "sun_exposure": "Full Sun",
                "difficulty": "Intermediate",
            },
            {
                "name": "Buttercrunch Lettuce",
                "slug": "buttercrunch-lettuce",
                "description": "Tender leaves with high bolt resistance. Packet includes succession planting calendar and soil prep checklist.",
                "price": 3.49,
                "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=800&q=80",
                "category": "Vegetables",
                "stock": 200,
                "is_featured": True,
                "germination_days": 6,
                "sun_exposure": "Partial Shade",
                "difficulty": "Beginner",
            },
            {
                "name": "Echinacea Purpurea",
                "slug": "echinacea-purpurea",
                "description": "Pollinator magnet with medicinal roots. Includes cold stratification guide for maximum germination.",
                "price": 5.99,
                "image_url": "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=800&q=80",
                "category": "Flowers",
                "stock": 80,
                "is_featured": True,
                "germination_days": 14,
                "sun_exposure": "Full Sun",
                "difficulty": "Intermediate",
            },
            {
                "name": "Bee-Friendly Wildflower Mix",
                "slug": "bee-friendly-wildflower-mix",
                "description": "18-species blend curated to support native pollinators all season long. Comes with bloom schedule poster.",
                "price": 8.99,
                "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=800&q=80",
                "category": "Flowers",
                "stock": 65,
                "is_featured": False,
                "germination_days": 10,
                "sun_exposure": "Full Sun",
                "difficulty": "Beginner",
            },
            {
                "name": "Basil Genovese",
                "slug": "basil-genovese",
                "description": "Classic Italian basil with high essential oil content. Includes pruning tutorial and pest prevention tips.",
                "price": 2.99,
                "image_url": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=800&q=80",
                "category": "Herbs",
                "stock": 150,
                "is_featured": False,
                "germination_days": 5,
                "sun_exposure": "Full Sun",
                "difficulty": "Beginner",
            },
            {
                "name": "Medicinal Herb Starter Kit",
                "slug": "medicinal-herb-starter-kit",
                "description": "Curated bundle of chamomile, lemon balm, and calendula with step-by-step drying and storage guide.",
                "price": 29.99,
                "image_url": "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=800&q=80",
                "category": "Starter Kits",
                "stock": 40,
                "is_featured": False,
                "germination_days": 12,
                "sun_exposure": "Partial Shade",
                "difficulty": "Beginner",
            },
        ]
        for product in products:
            db.session.add(cls(**product))


class Subscriber(db.Model, TimestampMixin):
    __tablename__ = "subscribers"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)

    @classmethod
    def recent(cls, limit: int = 5) -> list["Subscriber"]:
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()

    def __repr__(self) -> str:  # pragma: no cover - repr for debugging only
        return f"<Subscriber email={self.email!r}>"


__all__ = ["SiteSetting", "Product", "InventorySummary", "Subscriber"]
