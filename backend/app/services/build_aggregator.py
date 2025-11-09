from collections import defaultdict
from typing import Iterable, List

from ..models.builds import Build, CategorisedBuilds
from .providers import BuildDataProvider


class BuildAggregator:
    """Aggregates builds from multiple data providers and groups them by category."""

    def __init__(self, providers: Iterable[BuildDataProvider]):
        self._providers = list(providers)

    def get_builds_for_hero(self, hero_id: str) -> CategorisedBuilds:
        grouped: dict[str, List[Build]] = defaultdict(list)
        seen_ids: set[str] = set()

        for provider in self._providers:
            for build in provider.get_builds_for_hero(hero_id):
                if build.id in seen_ids:
                    continue
                seen_ids.add(build.id)
                grouped[build.category].append(build)

        return CategorisedBuilds(
            meta_builds=grouped.get("meta", []),
            off_meta_builds=grouped.get("off_meta", []),
            situational_builds=grouped.get("situational", []),
        )
