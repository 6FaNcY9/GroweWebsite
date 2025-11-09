from typing import List

from pydantic import BaseModel

from .builds import CategorisedBuilds


class HeroSummary(BaseModel):
    id: str
    name: str
    primary_role: str
    secondary_roles: List[str]
    recommended_lanes: List[str]
    portrait: str | None = None


class HeroDetail(BaseModel):
    id: str
    name: str
    title: str | None = None
    description: str | None = None
    primary_role: str
    secondary_roles: List[str]
    recommended_lanes: List[str]
    difficulty: str | None = None
    builds: CategorisedBuilds
    portrait: str | None = None
    icon: str | None = None
