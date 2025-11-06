"""API blueprint offering lightweight JSON endpoints for integrations."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..models import Product, SiteSetting


api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/products")
def product_listing():
    """Return a JSON payload of products, filtered by optional query params."""
    category = request.args.get("category")
    search = request.args.get("q")

    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(Product.name.ilike(like))

    products = [product.to_dict() for product in query.order_by(Product.name.asc()).all()]
    return jsonify({"products": products})


@api_bp.get("/site-settings")
def site_settings():
    """Expose a read-only view of site settings for static clients."""
    return jsonify(SiteSetting.as_dict())
