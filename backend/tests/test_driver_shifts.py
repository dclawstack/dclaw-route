from datetime import timedelta
import pytest

from app.core.utils import utc_now


@pytest.mark.asyncio
async def test_create_and_list_shift(client):
    d = await client.post(
        "/api/v1/drivers/", json={"name": "Sam", "email": "sam@example.com"}
    )
    driver_id = d.json()["id"]
    start = (utc_now() - timedelta(hours=8)).isoformat()
    end = utc_now().isoformat()
    r = await client.post(
        "/api/v1/shifts/",
        json={
            "driver_id": driver_id,
            "start_at": start,
            "end_at": end,
            "hours_worked": 8.0,
            "status": "completed",
        },
    )
    assert r.status_code == 201, r.text

    rl = await client.get(f"/api/v1/shifts/?driver_id={driver_id}")
    assert rl.status_code == 200
    assert len(rl.json()) == 1


@pytest.mark.asyncio
async def test_fatigue_alert_ok(client):
    d = await client.post(
        "/api/v1/drivers/", json={"name": "Tom", "email": "tom@example.com"}
    )
    driver_id = d.json()["id"]
    # 30 hours over the last 5 days
    for i in range(5):
        start = (utc_now() - timedelta(days=i)).isoformat()
        await client.post(
            "/api/v1/shifts/",
            json={
                "driver_id": driver_id,
                "start_at": start,
                "hours_worked": 6.0,
                "status": "completed",
            },
        )
    r = await client.get(f"/api/v1/shifts/fatigue/alerts/{driver_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["hours_last_7_days"] == 30.0
    assert body["severity"] == "ok"


@pytest.mark.asyncio
async def test_fatigue_alert_critical(client):
    d = await client.post(
        "/api/v1/drivers/", json={"name": "Joe", "email": "joe@example.com"}
    )
    driver_id = d.json()["id"]
    # 65 hours in last 5 days → above the 60h limit
    for i in range(5):
        start = (utc_now() - timedelta(days=i)).isoformat()
        await client.post(
            "/api/v1/shifts/",
            json={
                "driver_id": driver_id,
                "start_at": start,
                "hours_worked": 13.0,
                "status": "completed",
            },
        )
    r = await client.get(f"/api/v1/shifts/fatigue/alerts/{driver_id}")
    body = r.json()
    assert body["hours_last_7_days"] == 65.0
    assert body["severity"] == "critical"
    assert body["remaining_hours"] == 0.0


@pytest.mark.asyncio
async def test_fatigue_excludes_old_shifts(client):
    d = await client.post(
        "/api/v1/drivers/", json={"name": "Ann", "email": "ann@example.com"}
    )
    driver_id = d.json()["id"]
    # Old shift (10 days ago) shouldn't count toward 7-day window
    old = (utc_now() - timedelta(days=10)).isoformat()
    await client.post(
        "/api/v1/shifts/",
        json={
            "driver_id": driver_id,
            "start_at": old,
            "hours_worked": 40.0,
            "status": "completed",
        },
    )
    r = await client.get(f"/api/v1/shifts/fatigue/alerts/{driver_id}")
    assert r.json()["hours_last_7_days"] == 0.0


@pytest.mark.asyncio
async def test_fatigue_alerts_list(client):
    await client.post(
        "/api/v1/drivers/", json={"name": "Ben", "email": "ben@example.com"}
    )
    r = await client.get("/api/v1/shifts/fatigue/alerts")
    assert r.status_code == 200
    assert len(r.json()) == 1
