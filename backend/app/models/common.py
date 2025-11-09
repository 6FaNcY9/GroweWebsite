from typing import List, Optional

from pydantic import BaseModel


class Item(BaseModel):
    id: str
    name: str
    icon: Optional[str] = None


class EmblemSetup(BaseModel):
    tree: str
    talents: List[str]


class Spell(BaseModel):
    id: str
    name: str
    icon: Optional[str] = None
