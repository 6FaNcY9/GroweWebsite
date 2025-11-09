from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_tierlist_returns_expected_structure():
    response = client.get("/api/tierlist", params={"role": "Marksman", "lane": "Gold"})
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "Marksman"
    assert data["lane"] == "Gold"
    assert data["tiers"]
    tier_names = {group["tier"] for group in data["tiers"]}
    assert "S" in tier_names


def test_unknown_role_returns_404():
    response = client.get("/api/tierlist", params={"role": "Unknown", "lane": "Gold"})
    assert response.status_code == 404
