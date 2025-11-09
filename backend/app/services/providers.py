from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Protocol

import httpx

from ..config import get_settings
from ..models.builds import Build, CategorisedBuilds
from ..models.common import EmblemSetup, Item, Spell
from ..models.hero import HeroDetail, HeroSummary
from ..models.tierlist import TierGroup


class HeroDataProvider(Protocol):
    def list_heroes(self) -> List[HeroSummary]:
        ...

    def get_hero(self, hero_id: str) -> HeroSummary:
        ...

    def get_hero_detail(self, hero_id: str) -> HeroDetail:
        ...


class TierListDataProvider(Protocol):
    def list_roles(self) -> List[str]:
        ...

    def list_lanes(self) -> List[str]:
        ...

    def get_tier_groups(self, role: str, lane: str) -> List[TierGroup]:
        ...


class BuildDataProvider(Protocol):
    def get_builds_for_hero(self, hero_id: str) -> List[Build]:
        ...


@dataclass
class _JsonDataLoader:
    path: Path

    def load(self) -> dict:
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


class MockHeroDataProvider(HeroDataProvider):
    def __init__(self, data_dir: Path):
        self._data_dir = data_dir

    @property
    @lru_cache
    def _heroes(self) -> dict:
        loader = _JsonDataLoader(self._data_dir / "heroes.json")
        return loader.load()

    def list_heroes(self) -> List[HeroSummary]:
        return [HeroSummary(**hero) for hero in self._heroes.values()]

    def get_hero(self, hero_id: str) -> HeroSummary:
        try:
            return HeroSummary(**self._heroes[hero_id])
        except KeyError as exc:
            raise KeyError(f"Hero '{hero_id}' not found in mock data") from exc

    def get_hero_detail(self, hero_id: str) -> HeroDetail:
        hero_data = self._heroes.get(hero_id)
        if hero_data is None:
            raise KeyError(f"Hero '{hero_id}' not found in mock data")

        base_kwargs = {k: v for k, v in hero_data.items() if k != "builds"}
        return HeroDetail(**base_kwargs, builds=_empty_builds())


class MockTierListDataProvider(TierListDataProvider):
    def __init__(self, data_dir: Path):
        self._data_dir = data_dir

    @property
    @lru_cache
    def _tierlist(self) -> dict:
        loader = _JsonDataLoader(self._data_dir / "tierlist.json")
        return loader.load()

    def list_roles(self) -> List[str]:
        return list(self._tierlist.keys())

    def list_lanes(self) -> List[str]:
        lanes: set[str] = set()
        for lane_map in self._tierlist.values():
            lanes.update(lane_map.keys())
        return sorted(lanes)

    def get_tier_groups(self, role: str, lane: str) -> List[TierGroup]:
        role_data = self._tierlist.get(role, {})
        lane_data = role_data.get(lane, [])
        return [TierGroup(**entry) for entry in lane_data]


class MockBuildDataProvider(BuildDataProvider):
    def __init__(self, data_dir: Path):
        self._data_dir = data_dir

    @property
    @lru_cache
    def _builds(self) -> List[dict]:
        loader = _JsonDataLoader(self._data_dir / "builds.json")
        return loader.load()

    def get_builds_for_hero(self, hero_id: str) -> List[Build]:
        return [Build(**build) for build in self._builds if build["hero_id"] == hero_id]


def _normalise_asset(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    if url.startswith("//"):
        return f"https:{url}"
    return url


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "hero"


def _coalesce_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _default_emblem() -> EmblemSetup:
    return EmblemSetup(tree="Unknown", talents=[])


def _default_spell() -> Spell:
    return Spell(id="unknown", name="Unknown")


class MobileLegendsApiHeroProvider(HeroDataProvider):
    """Fetch hero data from the official Mobile Legends public API."""

    BASE_URL = "https://mapi.mobilelegends.com"
    HERO_LIST_PATH = "/hero/list"
    HERO_DETAIL_PATH = "/hero/detail"

    def __init__(
        self,
        client: Optional[httpx.Client] = None,
        fallback_data_dir: Optional[Path] = None,
    ) -> None:
        settings = get_settings()
        self._client = client or httpx.Client(
            base_url=self.BASE_URL,
            timeout=settings.http_timeout_seconds,
            headers={
                "User-Agent": "GroweMLHelper/1.0 (+https://github.com/mobaguides/mobile-legends-api)",
                "Accept": "application/json",
            },
        )

        data_dir = fallback_data_dir or settings.data_dir
        self._fallback_provider = MockHeroDataProvider(data_dir)
        self._fallback_build_provider = MockBuildDataProvider(data_dir)
        self._fallback_index: Dict[str, HeroSummary] = {
            hero.name.lower(): hero for hero in self._fallback_provider.list_heroes()
        }

        self._slug_to_remote_id: Dict[str, str] = {}
        self._summary_cache: Optional[List[HeroSummary]] = None
        self._detail_cache: Dict[str, HeroDetail] = {}

    def list_heroes(self) -> List[HeroSummary]:
        self._ensure_index_loaded()
        assert self._summary_cache is not None
        return list(self._summary_cache)

    def get_hero(self, hero_id: str) -> HeroSummary:
        self._ensure_index_loaded()
        if self._summary_cache is None:
            raise KeyError(hero_id)
        for summary in self._summary_cache:
            if summary.id == hero_id:
                return summary
        raise KeyError(f"Hero '{hero_id}' not found")

    def get_hero_detail(self, hero_id: str) -> HeroDetail:
        self._ensure_index_loaded()
        if hero_id in self._detail_cache:
            return self._detail_cache[hero_id]

        remote_id = self._slug_to_remote_id.get(hero_id)
        if remote_id is None:
            raise KeyError(f"Hero '{hero_id}' is not indexed from the API")

        response = self._client.get(self.HERO_DETAIL_PATH, params={"id": remote_id})
        response.raise_for_status()
        payload: dict = response.json().get("data", {})

        name = payload.get("name") or hero_id.replace("-", " ").title()
        fallback_summary = self._fallback_index.get(name.lower())
        primary_role = _coalesce_text(payload.get("type")) or (
            fallback_summary.primary_role if fallback_summary else "Unknown"
        )
        lanes = list(fallback_summary.recommended_lanes) if fallback_summary else []
        secondary_roles = (
            list(fallback_summary.secondary_roles) if fallback_summary else []
        )

        builds = self._builds_from_payload(
            hero_slug=hero_id,
            primary_role=primary_role,
            lanes=lanes,
            fallback_summary=fallback_summary,
            payload=payload,
        )

        detail = HeroDetail(
            id=hero_id,
            name=name,
            title=None,
            description=_coalesce_text(payload.get("des")),
            primary_role=primary_role,
            secondary_roles=secondary_roles,
            recommended_lanes=lanes,
            difficulty=_coalesce_text(payload.get("diff")),
            builds=builds,
            portrait=_normalise_asset(payload.get("cover_picture")),
            icon=_normalise_asset(payload.get("gallery_picture")),
        )
        self._detail_cache[hero_id] = detail
        return detail

    def _ensure_index_loaded(self) -> None:
        if self._summary_cache is not None:
            return

        response = self._client.get(self.HERO_LIST_PATH)
        response.raise_for_status()
        payload = response.json()
        heroes: Iterable[dict] = payload.get("data", [])

        summaries: List[HeroSummary] = []
        for entry in heroes:
            remote_id = str(entry.get("heroid") or entry.get("hero_id") or "").strip()
            name = entry.get("name") or f"Hero {remote_id or '?'}"
            fallback_summary = self._fallback_index.get(name.lower())
            slug = (
                fallback_summary.id
                if fallback_summary is not None
                else _slugify(name)
            )

            summary = HeroSummary(
                id=slug,
                name=name,
                primary_role=(
                    fallback_summary.primary_role
                    if fallback_summary is not None
                    else "Unknown"
                ),
                secondary_roles=(
                    list(fallback_summary.secondary_roles)
                    if fallback_summary is not None
                    else []
                ),
                recommended_lanes=(
                    list(fallback_summary.recommended_lanes)
                    if fallback_summary is not None
                    else []
                ),
                portrait=_normalise_asset(entry.get("key")),
            )

            if remote_id:
                self._slug_to_remote_id[slug] = remote_id

            summaries.append(summary)

        self._summary_cache = summaries

    def _builds_from_payload(
        self,
        hero_slug: str,
        primary_role: str,
        lanes: List[str],
        fallback_summary: Optional[HeroSummary],
        payload: dict,
    ) -> CategorisedBuilds:
        gear: dict = payload.get("gear") or {}
        out_pack: List[dict] = gear.get("out_pack") or []
        situational_pack: List[dict] = gear.get("verysix") or []

        emblem, spell = self._derive_defaults(fallback_summary)

        meta_builds: List[Build] = []
        if out_pack:
            meta_builds.append(
                Build(
                    id=f"{hero_slug}-official-meta",
                    hero_id=hero_slug,
                    name="Official Recommended Build",
                    role=primary_role,
                    lane=lanes[0] if lanes else "Unknown",
                    items=self._convert_items(out_pack),
                    emblem=emblem,
                    spell=spell,
                    source_name="Mobile Legends Official",
                    source_url="https://m.mobilelegends.com/",
                    is_meta=True,
                    category="meta",
                    notes=_coalesce_text(gear.get("out_pack_tips")),
                )
            )

        situational_builds: List[Build] = []
        if situational_pack:
            situational_builds.append(
                Build(
                    id=f"{hero_slug}-official-situational",
                    hero_id=hero_slug,
                    name="Situational Items",
                    role=primary_role,
                    lane=lanes[0] if lanes else "Unknown",
                    items=self._convert_items(situational_pack),
                    emblem=emblem,
                    spell=spell,
                    source_name="Mobile Legends Official",
                    source_url="https://m.mobilelegends.com/",
                    is_meta=False,
                    category="situational",
                    notes=None,
                )
            )

        return CategorisedBuilds(
            meta_builds=meta_builds,
            off_meta_builds=[],
            situational_builds=situational_builds,
        )

    def _convert_items(self, entries: List[dict]) -> List[Item]:
        items: List[Item] = []
        for entry in entries:
            equip = entry.get("equip") or {}
            name = equip.get("name") or "Unknown Item"
            item_id = _slugify(name)
            items.append(
                Item(
                    id=item_id,
                    name=name,
                    icon=_normalise_asset(equip.get("icon")),
                )
            )
        return items

    def _derive_defaults(
        self, fallback_summary: Optional[HeroSummary]
    ) -> tuple[EmblemSetup, Spell]:
        if fallback_summary is None:
            return _default_emblem(), _default_spell()

        builds = self._fallback_build_provider.get_builds_for_hero(
            fallback_summary.id
        )
        for build in builds:
            if build.is_meta:
                return build.emblem, build.spell

        if builds:
            first = builds[0]
            return first.emblem, first.spell

        return _default_emblem(), _default_spell()


def _empty_builds() -> CategorisedBuilds:
    return CategorisedBuilds(meta_builds=[], off_meta_builds=[], situational_builds=[])
