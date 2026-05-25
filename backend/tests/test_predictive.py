import pytest

from app.services.predictive import set_weather_factor, traffic_factor


@pytest.fixture(autouse=True)
def _reset_weather():
    set_weather_factor(1.0)
    yield
    set_weather_factor(1.0)


def test_traffic_factor_rush_hour():
    assert traffic_factor(8) == 1.5
    assert traffic_factor(17) == 1.5


def test_traffic_factor_late_night():
    assert traffic_factor(2) == 0.85
    assert traffic_factor(23) == 0.85


def test_traffic_factor_normal():
    assert traffic_factor(6) == 1.0
    assert traffic_factor(20) == 1.0


@pytest.mark.asyncio
async def test_get_and_set_weather(client):
    g = await client.get("/api/v1/predictive/weather")
    assert g.json()["factor"] == 1.0

    p = await client.post("/api/v1/predictive/weather", json={"factor": 1.3})
    assert p.status_code == 200
    assert p.json()["factor"] == 1.3


@pytest.mark.asyncio
async def test_set_weather_rejects_invalid(client):
    r = await client.post("/api/v1/predictive/weather", json={"factor": -1.0})
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_route_forecast_applies_factors(client):
    r = await client.post(
        "/api/v1/routes/",
        json={"name": "R", "estimated_minutes": 100},
    )
    route_id = r.json()["id"]

    # Force adverse weather to make the test deterministic.
    await client.post("/api/v1/predictive/weather", json={"factor": 1.2})

    f = await client.get(f"/api/v1/predictive/routes/{route_id}/forecast")
    assert f.status_code == 200, f.text
    body = f.json()
    assert body["baseline_minutes"] == 100
    assert body["weather_factor"] == 1.2
    expected = int(100 * body["combined_factor"])
    assert body["adjusted_minutes"] == expected


@pytest.mark.asyncio
async def test_route_forecast_404(client):
    r = await client.get(
        "/api/v1/predictive/routes/00000000-0000-0000-0000-000000000000/forecast"
    )
    assert r.status_code == 404
