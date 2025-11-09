from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .models.hero import HeroDetail
from .services.build_aggregator import BuildAggregator
from .services.hero_service import HeroService
from .services.providers import (
    MobileLegendsApiHeroProvider,
    MockBuildDataProvider,
    MockHeroDataProvider,
    MockTierListDataProvider,
)
from .services.tierlist_service import TierListService

app = FastAPI(title="Mobile Legends Helper")
settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent

data_dir = settings.data_dir
hero_provider = (
    MobileLegendsApiHeroProvider() if settings.hero_provider == "mapi" else MockHeroDataProvider(data_dir)
)
build_providers = [MockBuildDataProvider(data_dir)]
hero_service = HeroService(hero_provider, BuildAggregator(build_providers))
tierlist_service = TierListService(MockTierListDataProvider(data_dir))

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/heroes", response_class=HTMLResponse)
def hero_roster(request: Request):
    heroes = hero_service.list_heroes()
    roles = sorted({hero.primary_role for hero in heroes})
    lanes = sorted({lane for hero in heroes for lane in hero.recommended_lanes})
    return templates.TemplateResponse(
        "heroes.html",
        {
            "request": request,
            "heroes": heroes,
            "roles": roles,
            "lanes": lanes,
        },
    )


@app.get("/heroes/{hero_id}", response_class=HTMLResponse)
def hero_detail_page(request: Request, hero_id: str):
    hero = hero_service.get_hero_detail(hero_id)
    return templates.TemplateResponse("hero_detail.html", {"request": request, "hero": hero})


@app.get("/tier-list", response_class=HTMLResponse)
def tier_list_page(request: Request):
    index = tierlist_service.get_index()
    return templates.TemplateResponse("tier_list.html", {"request": request, "index": index})


@app.get("/api/heroes")
def list_heroes():
    return hero_service.list_heroes()


@app.get("/api/heroes/{hero_id}")
def get_hero(hero_id: str) -> HeroDetail:
    return hero_service.get_hero_detail(hero_id)


@app.get("/api/tierlist")
def get_tier_list(role: str, lane: str):
    return tierlist_service.get_for_role_lane(role, lane)
