# Growe Seed Co. Platform

A production-ready Flask web application for managing an online seed catalog with an admin dashboard, Tailwind CSS styling, and editable marketing content.

## Features

- **Dynamic storefront** with Tailwind-powered landing and catalog pages that read from a relational database.
- **Searchable product catalog** including category, price range, and stock-based sorting to help customers find the perfect seeds or starter kits.
- **Admin dashboard** secured by password hashes with live previews for homepage messaging and full CRUD management for products.
- **Inventory and subscriber insights** summarizing stock levels, low-inventory thresholds, and newsletter growth trends.
- **Product storytelling** with dedicated detail pages that highlight horticulture data, planting timelines, and related varieties.
- **Configurable layout** pulling company name and Tailwind CDN version from environment variables for consistent branding across templates.
- **Read-only JSON API** exposing products and site settings for marketing automations or headless storefront experiments.
- **SQLite persistence** via SQLAlchemy plus defaults that seed the database with sample content for local development.
- **Operations-friendly CLI** commands for reseeding data, generating admin password hashes, and inspecting runtime configuration.

## Getting started

1. Create and activate a Python 3.11 virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Set environment variables for production deployment:
   ```bash
   export SECRET_KEY="replace-with-strong-secret"
   export ADMIN_PASSWORD="choose-a-secure-password"            # fallback if hash is not provided
   export ADMIN_PASSWORD_HASH="pbkdf2:sha256:..."               # preferred: generate via `python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"`
   export DATABASE_URL="sqlite:///growe.sqlite3"  # or your preferred database
   export GROWE_COMPANY_NAME="Growe Seed Collective"
   export TAILWIND_CDN_VERSION="3.4.3"
   export GROWE_ENV="production"
   ```
4. Run the development server:
   ```bash
   flask --app run:app --debug run
   ```
5. Visit `http://127.0.0.1:5000/` for the storefront and `http://127.0.0.1:5000/admin` for the dashboard. The default password is `growe-admin`, which is hashed automatically for development.

### Helpful CLI commands

The app registers a few `flask` commands once dependencies are installed:

```bash
flask --app run:app seed-data        # populate default settings and products if missing
flask --app run:app hash-password <secret>  # output a PBKDF2 hash for ADMIN_PASSWORD_HASH
flask --app run:app show-config      # print non-sensitive runtime configuration values
```

## Database

The application uses SQLite by default. Tables are created automatically on first launch, and starter data is inserted the first time the database is empty. Replace the `DATABASE_URL` environment variable to use PostgreSQL, MySQL, or another SQLAlchemy-compatible backend in production.

To reseed data in an existing environment, run `flask --app run:app seed-data`.

## Tests

No automated tests are included yet. Run `flask shell` to experiment with the data models.
