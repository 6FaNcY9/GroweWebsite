"""Storefront blueprint powering the customer-facing experience."""
from __future__ import annotations

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy import or_

from ..extensions import db
from ..forms import NewsletterForm
from ..models import InventorySummary, Product, Subscriber


storefront_bp = Blueprint("storefront", __name__)

@storefront_bp.route("/")
def home() -> str:
    featured_products = (
        Product.query.filter_by(is_featured=True).order_by(Product.name).all()
    )
    categories = Product.categories()
    summary: InventorySummary = Product.inventory_summary()
    return render_template(
        "home.html",
        featured_products=featured_products,
        categories=categories,
        summary=summary,
    )


@storefront_bp.route("/products")
def products() -> str:
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    price_min = request.args.get("min_price", type=float)
    price_max = request.args.get("max_price", type=float)
    sort = request.args.get("sort", "name")

    query = Product.query

    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            or_(
                db.func.lower(Product.name).like(like),
                db.func.lower(Product.description).like(like),
            )
        )

    if category:
        query = query.filter_by(category=category)

    if price_min is not None:
        query = query.filter(Product.price >= price_min)
    if price_max is not None:
        query = query.filter(Product.price <= price_max)

    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "stock":
        query = query.order_by(Product.stock.desc())
    else:
        query = query.order_by(Product.name.asc())

    products = query.all()

    return render_template(
        "products.html",
        products=products,
        selected_category=category,
        search=search,
        price_min=price_min,
        price_max=price_max,
        sort=sort,
        categories=Product.categories(),
        summary=Product.inventory_summary(),
    )


@storefront_bp.route("/products/<slug>")
def product_detail(slug: str) -> str:
    product = Product.find_by_slug(slug)
    if not product:
        abort(404)

    related_products = (
        Product.query.filter(
            Product.category == product.category,
            Product.id != product.id,
        )
        .order_by(Product.is_featured.desc(), Product.name.asc())
        .limit(4)
        .all()
    )

    return render_template(
        "product_detail.html",
        product=product,
        related_products=related_products,
    )


@storefront_bp.route("/newsletter", methods=["POST"])
def subscribe_newsletter() -> str:
    form = NewsletterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        existing = Subscriber.query.filter_by(email=email).first()
        brand = current_app.config.get("GROWE_COMPANY_NAME", "Growe Seed Co.")
        short_brand = brand.split()[0] if brand else "Growe"
        if existing:
            flash(f"You're already subscribed to the {short_brand} newsletter!", "info")
        else:
            subscriber = Subscriber(email=email)
            db.session.add(subscriber)
            db.session.commit()
            flash(f"Thanks for joining the {brand} growing community!", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{form._fields[field].label.text}: {error}", "danger")
    return redirect(request.referrer or url_for("storefront.home"))
