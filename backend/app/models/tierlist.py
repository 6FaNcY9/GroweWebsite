from typing import Dict, List

from pydantic import BaseModel


class TierEntry(BaseModel):
    hero_id: str
    hero_name: str
    primary_role: str
    lane: str
    icon: str | None = None


class TierGroup(BaseModel):
    tier: str
    heroes: List[TierEntry]


class TierListResponse(BaseModel):
    role: str
    lane: str
    tiers: List[TierGroup]


class TierListIndex(BaseModel):
    roles: List[str]
    lanes: List[str]
    lookup: Dict[str, Dict[str, List[TierGroup]]]
