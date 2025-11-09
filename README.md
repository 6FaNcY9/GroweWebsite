# Mobile Legends Helper Web App

This repository hosts a mobile-first web companion for **Mobile Legends: Bang Bang**. The goal is to provide tier lists, hero information, and curated build recommendations through a Python backend and lightweight server-rendered frontend.

## Stack Choices

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) with Uvicorn. FastAPI delivers type-safe routing, automatic docs, and native Pydantic model support, which fits the structured hero/build schemas.
- **Frontend:** Jinja2 templates with progressive enhancement. A template-driven UI keeps the stack simple and avoids a separate build pipeline while still letting us sprinkle in JavaScript for filtering and tier switching.
- **Data Providers:** Pluggable provider interfaces power the hero, tier list, and build layers. The default implementation reads from local JSON mocks, but a production-ready provider integrates the official Mobile Legends endpoints at `https://mapi.mobilelegends.com`.
- **Testing:** `pytest` paired with FastAPI's `TestClient` for API verification.

All tooling lives in Python to respect the "no Android/Java" constraint.

## Project Structure

```
backend/
  app/
    api/                # (reserved for future API sub-routers)
    data/               # helpers for data access
    models/             # Pydantic schemas (heroes, builds, tier lists)
    services/           # Provider interfaces, build aggregator, domain services
    static/             # CSS assets
    templates/          # Jinja2 templates for the UI
    tests/              # pytest test suite
    main.py             # FastAPI application entrypoint
backend/requirements.txt
data/
  heroes.json           # Mock hero roster metadata
  builds.json           # Mock builds grouped by hero
  tierlist.json         # Mock tier lists grouped by role/lane
```

## Getting Started

This project targets **Python 3.11+**. The commands below assume a Unix-like shell.

```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Running the Development Server

```bash
uvicorn app.main:app --reload --app-dir backend
```

Open http://127.0.0.1:8000 in a mobile browser or desktop responsive view to explore the app.

FastAPI automatically exposes JSON docs at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Publishing Your Local Changes

If you forked this repository on GitHub and do not see the FastAPI project files yet, push the local `main` branch:

```bash
git remote add origin <your-github-url>
git push -u origin main
```

After the first push the repository will show the latest commits (including the FastAPI app) so you can pull them onto any other machine for the initial run.

### Troubleshooting: GitHub Shows Old Code

If the GitHub UI still displays the original placeholder commit, make sure your local branch is named `main` before pushing:

```bash
git status           # verify you're on branch main
git branch -M main   # rename the current branch to main if needed
git push -u origin main
```

GitHub uses `main` as the default branch for new repositories, so publishing to a differently named branch (for example `work`) will not update what you see on the repo homepage until you either change the default branch in GitHub's settings or push the latest commits to `main`.

### Running Tests

```bash
pytest backend/app/tests --maxfail=1 -q
```

## Data Providers & Real API Integration

The service layer defines provider protocols (`HeroDataProvider`, `TierListDataProvider`, `BuildDataProvider`) so data sources can be swapped without touching the presentation layer.

- `MockHeroDataProvider`, `MockTierListDataProvider`, and `MockBuildDataProvider` read JSON from the `data/` folder. These mocks load into memory once at startup for quick iteration.
- `MobileLegendsApiHeroProvider` consumes the official Mobile Legends endpoints (`https://mapi.mobilelegends.com/hero/list` and `.../hero/detail`). After surveying the community-operated APIs, the official service proved the most up-to-date and reliably maintained, so the provider normalises its payloads, enriches them with the mock metadata (roles, lanes), and surfaces the in-game recommended builds straight from Moonton. Set the environment variable `ML_HERO_PROVIDER=mapi` to enable it.

Future providers—such as scrapers or community APIs—can implement the same protocol to slot into the `BuildAggregator` or tier list service.

## Extending the App

- **Real-time data:** Implement additional provider classes (e.g. `ApiTierListDataProvider`) that fetch from third-party sources and register them in `app/main.py`.
- **Caching:** Wrap provider calls with caching or persistence layers (Redis, SQLite) before enabling heavy scraping.
- **Authentication:** If you expose personalised features, layer FastAPI dependencies for auth.
- **Frontend polish:** Replace the template UI with a dedicated SPA if you need offline support or more complex state handling.

## Mock Data Overview

The mock JSON files illustrate the shape expected from real providers:

- `heroes.json`: dictionary keyed by hero slug with summary metadata.
- `builds.json`: list of builds referencing heroes by slug. Each build records category (`meta`, `off_meta`, `situational`).
- `tierlist.json`: nested `role -> lane -> [tier groups]` structure used by the tier list UI.

These formats mirror the Pydantic models so you can plug new providers straight into the services.

## Switching to the Official API

1. Ensure outbound HTTPS access to `https://mapi.mobilelegends.com`.
2. Set the environment variable before starting Uvicorn:
   ```bash
   export ML_HERO_PROVIDER=mapi
   uvicorn app.main:app --reload --app-dir backend
   ```
3. The hero roster and detail endpoints will now pull live data. Build/tier providers remain mock-based until you implement their remote counterparts.

If the official API is unreachable, the application falls back to the mock provider so the UI continues to function.
