import pytest


@pytest.mark.asyncio
async def test_create_and_list_av(client):
    r = await client.post(
        "/api/v1/av/",
        json={
            "vendor": "Waymo",
            "model": "Driver-X",
            "autopilot_level": 5,
            "capacity_kg": 1200.0,
        },
    )
    assert r.status_code == 201, r.text
    lst = await client.get("/api/v1/av/")
    assert len(lst.json()) == 1
    assert lst.json()[0]["status"] == "available"


@pytest.mark.asyncio
async def test_dispatch_picks_highest_autopilot_level(client):
    await client.post(
        "/api/v1/av/",
        json={"vendor": "Vendor A", "model": "L3", "autopilot_level": 3},
    )
    await client.post(
        "/api/v1/av/",
        json={"vendor": "Vendor B", "model": "L5", "autopilot_level": 5},
    )
    route = await client.post("/api/v1/routes/", json={"name": "AV-route"})

    res = await client.post(
        "/api/v1/av/dispatch",
        json={"route_id": route.json()["id"], "min_autopilot_level": 3},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["autopilot_level"] == 5
    assert body["vendor"] == "Vendor B"


@pytest.mark.asyncio
async def test_dispatch_filters_by_min_level(client):
    await client.post(
        "/api/v1/av/",
        json={"vendor": "Low", "model": "L2", "autopilot_level": 2},
    )
    route = await client.post("/api/v1/routes/", json={"name": "R"})
    res = await client.post(
        "/api/v1/av/dispatch",
        json={"route_id": route.json()["id"], "min_autopilot_level": 4},
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_dispatch_marks_busy_and_recall_frees(client):
    av = await client.post(
        "/api/v1/av/",
        json={"vendor": "V", "model": "M", "autopilot_level": 4},
    )
    route = await client.post("/api/v1/routes/", json={"name": "R"})
    await client.post(
        "/api/v1/av/dispatch", json={"route_id": route.json()["id"]}
    )

    avs = (await client.get("/api/v1/av/")).json()
    assert avs[0]["status"] == "dispatched"
    assert avs[0]["current_route_id"] == route.json()["id"]

    # Second dispatch fails — none left.
    route2 = await client.post("/api/v1/routes/", json={"name": "R2"})
    second = await client.post(
        "/api/v1/av/dispatch", json={"route_id": route2.json()["id"]}
    )
    assert second.status_code == 400

    # Recall frees it.
    recalled = await client.post(f"/api/v1/av/recall/{av.json()['id']}")
    assert recalled.json()["status"] == "available"


@pytest.mark.asyncio
async def test_dispatch_404_missing_route(client):
    await client.post(
        "/api/v1/av/", json={"vendor": "V", "model": "M", "autopilot_level": 4}
    )
    r = await client.post(
        "/api/v1/av/dispatch",
        json={"route_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_recall_404(client):
    r = await client.post(
        "/api/v1/av/recall/00000000-0000-0000-0000-000000000000"
    )
    assert r.status_code == 404
