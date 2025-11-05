"""Admin blueprint providing dashboard and catalog management."""
from __future__ import annotations

from functools import wraps
from typing import Any

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from ..extensions import db
from ..forms import AdminLoginForm, ProductForm, SiteSettingsForm
from ..models import Product, SiteSetting, Subscriber
from ..utils import slugify


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def login_required(view):
    """Ensure an administrator session is active before accessing a view."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            flash("Please sign in to manage the store.", "warning")
            return redirect(url_for("admin.login", next=request.url))
        return view(*args, **kwargs)

    return wrapped


@admin_bp.app_template_global()
def admin_url_for(endpoint: str, **values: Any) -> str:
    """Convenience helper to generate URLs for admin endpoints in templates."""
    return url_for(f"admin.{endpoint}", **values)


@admin_bp.route("/login", methods=["GET", "POST"])
def login() -> str:
    if session.get("admin_authenticated"):
        return redirect(url_for("admin.dashboard"))

    form = AdminLoginForm()
    if form.validate_on_submit():
        if check_password_hash(
            current_app.config["ADMIN_PASSWORD_HASH"], form.password.data
        ):
            session["admin_authenticated"] = True
            flash("Welcome back!", "success")
            return redirect(request.args.get("next") or url_for("admin.dashboard"))
        flash("Incorrect password. Please try again.", "danger")
    return render_template("admin/login.html", form=form)


@admin_bp.route("/logout")
@login_required
def logout() -> str:
    session.clear()
    flash("Signed out of the admin dashboard.", "info")
    return redirect(url_for("storefront.home"))


@admin_bp.route("/")
@login_required
def dashboard() -> str:
    settings = SiteSetting.as_dict()
    settings_form = SiteSettingsForm(data=settings)
    product_form = ProductForm()
    products = Product.query.order_by(Product.updated_at.desc()).all()
    subscribers = Subscriber.recent()
    return render_template(
        "admin/dashboard.html",
        settings_form=settings_form,
        product_form=product_form,
        products=products,
        subscriber_count=Subscriber.query.count(),
        recent_subscribers=subscribers,
    )


@admin_bp.route("/settings", methods=["POST"])
@login_required
def update_settings() -> str:
    form = SiteSettingsForm()
    if form.validate_on_submit():
        for field_name, value in form.data.items():
            if field_name in form._fields and field_name != "submit":  # noqa: WPS437
                SiteSetting.set(
                    field_name, value.strip() if isinstance(value, str) else value
                )
        db.session.commit()
        flash("Site settings updated.", "success")
    else:
        _flash_errors(form)
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/products", methods=["POST"])
@login_required
def create_product() -> str:
    form = ProductForm()
    if form.validate_on_submit():
        normalized_slug = form.slug.data or slugify(form.name.data)
        product = Product(
            name=form.name.data.strip(),
            slug=normalized_slug,
            description=form.description.data.strip(),
            price=form.price.data,
            image_url=form.image_url.data.strip(),
            category=form.category.data.strip(),
            stock=form.stock.data,
            is_featured=form.is_featured.data,
            germination_days=form.germination_days.data,
            sun_exposure=form.sun_exposure.data,
            difficulty=form.difficulty.data,
        )
        db.session.add(product)
        db.session.commit()
        flash(f"{product.name} added to the catalog.", "success")
    else:
        _flash_errors(form)
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/products/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit_product(slug: str) -> str:
    product = Product.find_by_slug(slug)
    if not product:
        abort(404)

    form = ProductForm(obj=product)
    form.product_id.data = product.id
    if form.validate_on_submit():
        product.name = form.name.data.strip()
        product.slug = form.slug.data or slugify(form.name.data)
        product.description = form.description.data.strip()
        product.price = form.price.data
        product.image_url = form.image_url.data.strip()
        product.category = form.category.data.strip()
        product.stock = form.stock.data
        product.is_featured = form.is_featured.data
        product.germination_days = form.germination_days.data
        product.sun_exposure = form.sun_exposure.data
        product.difficulty = form.difficulty.data
        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/edit_product.html", form=form, product=product)


@admin_bp.route("/products/<slug>/delete", methods=["POST"])
@login_required
def delete_product(slug: str) -> str:
    product = Product.find_by_slug(slug)
    if not product:
        abort(404)
    db.session.delete(product)
    db.session.commit()
    flash("Product removed from catalog.", "info")
    return redirect(url_for("admin.dashboard"))


def _flash_errors(form) -> None:
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{form._fields[field].label.text}: {error}", "danger")
