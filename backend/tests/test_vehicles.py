import pytest


@pytest.mark.asyncio
async def test_create_and_list_vehicle(client):
    r = await client.post(
        "/api/v1/vehicles/",
        json={"plate": "ABC-123", "vehicle_type": "van", "capacity_kg": 1500.0},
    )
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "available"

    lst = await client.get("/api/v1/vehicles/")
    assert len(lst.json()) == 1


@pytest.mark.asyncio
async def test_maintenance_alert_severities(client):
    await client.post(
        "/api/v1/vehicles/",
        json={
            "plate": "OK-1",
            "odometer_km": 5000,
            "last_service_odometer_km": 0,
        },
    )
    await client.post(
        "/api/v1/vehicles/",
        json={
            "plate": "SOON-2",
            "odometer_km": 9500,
            "last_service_odometer_km": 0,
        },
    )
    await client.post(
        "/api/v1/vehicles/",
        json={
            "plate": "OVER-3",
            "odometer_km": 12000,
            "last_service_odometer_km": 0,
        },
    )
    alerts = (await client.get("/api/v1/vehicles/maintenance/alerts")).json()
    by_plate = {a["plate"]: a for a in alerts}
    assert by_plate["OK-1"]["severity"] == "ok"
    assert by_plate["SOON-2"]["severity"] == "due_soon"
    assert by_plate["OVER-3"]["severity"] == "overdue"


@pytest.mark.asyncio
async def test_auto_assign_picks_highest_capacity(client):
    await client.post(
        "/api/v1/vehicles/",
        json={"plate": "SMALL", "capacity_kg": 500.0},
    )
    await client.post(
        "/api/v1/vehicles/",
        json={"plate": "BIG", "capacity_kg": 2500.0},
    )
    r = await client.post("/api/v1/routes/", json={"name": "R"})
    route_id = r.json()["id"]

    res = await client.post(f"/api/v1/vehicles/auto-assign/{route_id}")
    assert res.status_code == 200, res.text
    assert res.json()["plate"] == "BIG"

    r2 = await client.get(f"/api/v1/routes/{route_id}")
    assert r2.json()["vehicle_id"] is not None


@pytest.mark.asyncio
async def test_auto_assign_skips_busy_vehicles(client):
    v = await client.post(
        "/api/v1/vehicles/",
        json={"plate": "ONLY-ONE", "capacity_kg": 1000.0},
    )
    r1 = await client.post("/api/v1/routes/", json={"name": "R1"})
    await client.post(f"/api/v1/vehicles/auto-assign/{r1.json()['id']}")

    r2 = await client.post("/api/v1/routes/", json={"name": "R2"})
    res = await client.post(f"/api/v1/vehicles/auto-assign/{r2.json()['id']}")
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_sync_stub(client):
    await client.post("/api/v1/vehicles/", json={"plate": "S-1"})
    r = await client.post("/api/v1/vehicles/sync")
    assert r.status_code == 200
    assert r.json()["pulled"] == 1
