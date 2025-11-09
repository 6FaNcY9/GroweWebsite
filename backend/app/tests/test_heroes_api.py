from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_heroes_returns_mock_data():
    response = client.get("/api/heroes")
    assert response.status_code == 200
    heroes = response.json()
    hero_ids = {hero["id"] for hero in heroes}
    assert "martis" in hero_ids
    assert "brody" in hero_ids


def test_get_hero_detail_contains_build_groups():
    response = client.get("/api/heroes/martis")
    assert response.status_code == 200
    hero = response.json()
    assert hero["id"] == "martis"
    assert hero["builds"]["meta_builds"]
    assert hero["builds"]["off_meta_builds"]
