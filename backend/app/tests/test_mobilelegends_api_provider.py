import httpx
from httpx import Response

from app.services.providers import MobileLegendsApiHeroProvider


LIST_PAYLOAD = {
    "code": 2000,
    "message": "SUCCESS",
    "data": [
        {
            "heroid": "32",
            "name": "Martis",
            "key": "//assets.mobilelegends.com/martis.png",
        }
    ],
}

DETAIL_PAYLOAD = {
    "code": 2000,
    "message": "SUCCESS",
    "data": {
        "name": "Martis",
        "type": "Fighter",
        "des": "A resilient fighter",
        "diff": "45",
        "cover_picture": "//assets.mobilelegends.com/martis-cover.png",
        "gallery_picture": "//assets.mobilelegends.com/martis-icon.png",
        "gear": {
            "out_pack": [
                {
                    "equipment_id": 3201,
                    "equip": {
                        "name": "Warrior Boots",
                        "icon": "//assets.mobilelegends.com/items/warrior-boots.png",
                    },
                },
                {
                    "equipment_id": 3202,
                    "equip": {
                        "name": "Bloodlust Axe",
                        "icon": "//assets.mobilelegends.com/items/bloodlust-axe.png",
                    },
                },
            ],
            "out_pack_tips": "Core fighter items",
            "verysix": [
                {
                    "equipment_id": 3301,
                    "equip": {
                        "name": "Immortality",
                        "icon": "//assets.mobilelegends.com/items/immortality.png",
                    },
                }
            ],
        },
    },
}


def _mock_transport(request: httpx.Request) -> Response:
    if request.url.path == "/hero/list":
        return Response(200, json=LIST_PAYLOAD)
    if request.url.path == "/hero/detail":
        assert request.url.params.get("id") == "32"
        return Response(200, json=DETAIL_PAYLOAD)
    raise AssertionError(f"Unexpected URL {request.url!r}")


def _build_provider() -> MobileLegendsApiHeroProvider:
    transport = httpx.MockTransport(_mock_transport)
    client = httpx.Client(transport=transport, base_url="https://mapi.mobilelegends.com")
    return MobileLegendsApiHeroProvider(client=client)


def test_list_heroes_uses_fallback_metadata():
    provider = _build_provider()
    heroes = provider.list_heroes()
    assert len(heroes) == 1

    martis = heroes[0]
    assert martis.id == "martis"
    assert martis.primary_role == "Fighter"
    assert "EXP" in martis.recommended_lanes
    assert martis.portrait == "https://assets.mobilelegends.com/martis.png"


def test_detail_includes_official_builds_and_defaults():
    provider = _build_provider()
    detail = provider.get_hero_detail("martis")

    assert detail.primary_role == "Fighter"
    assert detail.portrait == "https://assets.mobilelegends.com/martis-cover.png"
    assert detail.icon == "https://assets.mobilelegends.com/martis-icon.png"

    meta_builds = detail.builds.meta_builds
    assert meta_builds, "Expected at least one build from the official API"

    build = meta_builds[0]
    assert build.name == "Official Recommended Build"
    assert [item.name for item in build.items][:2] == ["Warrior Boots", "Bloodlust Axe"]
    assert build.emblem.tree == "Assassin"
    assert build.spell.name == "Flicker"

    situational = detail.builds.situational_builds
    assert situational and situational[0].items[0].name == "Immortality"
