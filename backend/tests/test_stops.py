import pytest


@pytest.mark.asyncio
async def test_create_and_list_stop(client):
    payload = {"name": "Warehouse A", "address": "1 Main St", "lat": 40.7, "lng": -74.0}
    r = await client.post("/api/v1/stops/", json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["name"] == "Warehouse A"
    assert "id" in body

    r2 = await client.get("/api/v1/stops/")
    assert r2.status_code == 200
    assert len(r2.json()) == 1


@pytest.mark.asyncio
async def test_get_update_delete_stop(client):
    r = await client.post(
        "/api/v1/stops/",
        json={"name": "S1", "address": "A", "lat": 1.0, "lng": 2.0},
    )
    stop_id = r.json()["id"]

    r2 = await client.get(f"/api/v1/stops/{stop_id}")
    assert r2.status_code == 200

    r3 = await client.patch(f"/api/v1/stops/{stop_id}", json={"name": "S1-updated"})
    assert r3.status_code == 200
    assert r3.json()["name"] == "S1-updated"

    r4 = await client.delete(f"/api/v1/stops/{stop_id}")
    assert r4.status_code == 204

    r5 = await client.get(f"/api/v1/stops/{stop_id}")
    assert r5.status_code == 404


@pytest.mark.asyncio
async def test_get_missing_stop(client):
    r = await client.get("/api/v1/stops/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
