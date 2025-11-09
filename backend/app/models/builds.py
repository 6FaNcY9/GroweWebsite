from typing import List, Optional

from pydantic import BaseModel

from .common import EmblemSetup, Item, Spell


class Build(BaseModel):
    id: str
    hero_id: str
    name: str
    role: str
    lane: str
    items: List[Item]
    emblem: EmblemSetup
    spell: Spell
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    is_meta: bool = True
    category: str = "meta"
    notes: Optional[str] = None


class CategorisedBuilds(BaseModel):
    meta_builds: List[Build]
    off_meta_builds: List[Build]
    situational_builds: List[Build]
