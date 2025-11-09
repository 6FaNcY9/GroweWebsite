from fastapi import HTTPException, status

from ..models.hero import HeroDetail, HeroSummary
from .build_aggregator import BuildAggregator
from .providers import HeroDataProvider


class HeroService:
    def __init__(self, hero_provider: HeroDataProvider, build_aggregator: BuildAggregator):
        self._hero_provider = hero_provider
        self._build_aggregator = build_aggregator

    def list_heroes(self) -> list[HeroSummary]:
        try:
            return self._hero_provider.list_heroes()
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    def get_hero(self, hero_id: str) -> HeroSummary:
        try:
            return self._hero_provider.get_hero(hero_id)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    def get_hero_detail(self, hero_id: str) -> HeroDetail:
        try:
            hero_detail = self._hero_provider.get_hero_detail(hero_id)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        # merge builds from aggregator unless provider already filled them in
        if not hero_detail.builds.meta_builds and not hero_detail.builds.off_meta_builds and not hero_detail.builds.situational_builds:
            hero_detail.builds = self._build_aggregator.get_builds_for_hero(hero_id)
        return hero_detail
