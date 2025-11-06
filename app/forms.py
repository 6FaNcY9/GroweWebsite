from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    HiddenField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, NumberRange, Optional, URL, ValidationError

from .utils import slugify


class SiteSettingsForm(FlaskForm):
    announcement = StringField("Announcement Banner", validators=[Optional()])
    hero_headline = StringField("Hero Headline", validators=[DataRequired()])
    hero_subheadline = TextAreaField("Hero Subheadline", validators=[DataRequired()])
    hero_primary_label = StringField("Primary Button Label", validators=[Optional()])
    hero_primary_url = StringField("Primary Button URL", validators=[Optional(), URL(require_tld=False, message="Enter a valid URL or relative path.")])
    hero_secondary_label = StringField("Secondary Button Label", validators=[Optional()])
    hero_secondary_url = StringField("Secondary Button URL", validators=[Optional(), URL(require_tld=False, message="Enter a valid URL or relative path.")])
    about_title = StringField("About Section Title", validators=[DataRequired()])
    about_body = TextAreaField("About Section Copy", validators=[DataRequired()])
    newsletter_description = TextAreaField("Newsletter Description", validators=[DataRequired()])
    contact_email = StringField("Support Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Save Site Settings")


class ProductForm(FlaskForm):
    product_id = HiddenField()
    name = StringField("Name", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired(), NumberRange(min=0)])
    image_url = StringField("Image URL", validators=[DataRequired(), URL()])
    category = StringField("Category", validators=[DataRequired()])
    stock = IntegerField("Units In Stock", validators=[DataRequired(), NumberRange(min=0)])
    is_featured = BooleanField("Featured Product")
    germination_days = IntegerField(
        "Germination Days", validators=[DataRequired(), NumberRange(min=1, max=60)]
    )
    sun_exposure = SelectField(
        "Sun Exposure",
        choices=[
            ("Full Sun", "Full Sun"),
            ("Partial Shade", "Partial Shade"),
            ("Full Shade", "Full Shade"),
        ],
        validators=[DataRequired()],
    )
    difficulty = SelectField(
        "Difficulty",
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Save Product")

    def validate_slug(self, field) -> None:  # noqa: D401
        """Ensure the slug is unique across products."""

        from .models import Product  # Imported lazily to avoid circular import

        slug = slugify(field.data, fallback="")
        field.data = slug
        if not slug:
            raise ValidationError("Please enter a slug for this product.")

        existing = Product.query.filter_by(slug=slug).first()
        if existing:
            if not self.product_id.data or str(existing.id) != str(self.product_id.data):
                raise ValidationError("This slug is already in use. Choose another.")


class AdminLoginForm(FlaskForm):
    password = PasswordField("Admin Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class NewsletterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Join newsletter")
