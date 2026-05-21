import pytest


@pytest.mark.asyncio
async def test_create_and_list_driver(client):
    r = await client.post(
        "/api/v1/drivers/",
        json={"name": "Alice", "email": "alice@example.com", "vehicle_type": "van"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "active"

    r2 = await client.get("/api/v1/drivers/")
    assert r2.status_code == 200
    assert len(r2.json()) == 1


@pytest.mark.asyncio
async def test_update_driver_status(client):
    r = await client.post(
        "/api/v1/drivers/",
        json={"name": "Bob", "email": "bob@example.com"},
    )
    driver_id = r.json()["id"]

    r2 = await client.patch(f"/api/v1/drivers/{driver_id}", json={"status": "on_route"})
    assert r2.status_code == 200
    assert r2.json()["status"] == "on_route"
