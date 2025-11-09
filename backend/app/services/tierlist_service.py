from fastapi import HTTPException, status

from ..models.tierlist import TierListResponse, TierListIndex
from .providers import TierListDataProvider


class TierListService:
    def __init__(self, provider: TierListDataProvider):
        self._provider = provider

    def get_index(self) -> TierListIndex:
        roles = self._provider.list_roles()
        lanes = self._provider.list_lanes()
        lookup = {
            role: {lane: self._provider.get_tier_groups(role, lane) for lane in lanes}
            for role in roles
        }
        return TierListIndex(roles=roles, lanes=lanes, lookup=lookup)

    def get_for_role_lane(self, role: str, lane: str) -> TierListResponse:
        if role not in self._provider.list_roles():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown role '{role}'")
        if lane not in self._provider.list_lanes():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown lane '{lane}'")
        tiers = self._provider.get_tier_groups(role, lane)
        return TierListResponse(role=role, lane=lane, tiers=tiers)
