import base64
import pytest


@pytest.mark.asyncio
async def test_default_templates_auto_seeded(client):
    r = await client.get("/api/v1/notifications/templates")
    assert r.status_code == 200
    kinds = {t["kind"] for t in r.json()}
    assert {"on_the_way", "fifteen_minute_warning", "delivered"} <= kinds


@pytest.mark.asyncio
async def test_status_change_to_completed_sends_delivered(client):
    s = await client.post(
        "/api/v1/stops/",
        json={
            "name": "Alex",
            "address": "1 Main",
            "lat": 1.0,
            "lng": 1.0,
            "customer_email": "alex@example.com",
        },
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    delivery_id = r.json()["deliveries"][0]["id"]

    await client.patch(
        f"/api/v1/deliveries/{delivery_id}", json={"status": "completed"}
    )

    events = (await client.get(f"/api/v1/notifications/events?delivery_id={delivery_id}")).json()
    assert len(events) == 1
    assert events[0]["kind"] == "delivered"
    assert events[0]["channel"] == "email"
    assert events[0]["recipient"] == "alex@example.com"
    assert "Alex" in events[0]["body"]
    assert "1 Main" in events[0]["body"]


@pytest.mark.asyncio
async def test_status_change_to_in_progress_sends_on_the_way(client):
    s = await client.post(
        "/api/v1/stops/",
        json={
            "name": "Bea",
            "address": "2 Oak",
            "lat": 1.0,
            "lng": 1.0,
            "customer_phone": "+15551234567",
        },
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    delivery_id = r.json()["deliveries"][0]["id"]

    await client.patch(
        f"/api/v1/deliveries/{delivery_id}", json={"status": "in_progress"}
    )

    events = (await client.get(f"/api/v1/notifications/events?delivery_id={delivery_id}")).json()
    assert len(events) == 1
    assert events[0]["kind"] == "on_the_way"
    assert events[0]["channel"] == "sms"


@pytest.mark.asyncio
async def test_no_notification_when_no_customer_contact(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "Cy", "address": "3 Pine", "lat": 1.0, "lng": 1.0},
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    delivery_id = r.json()["deliveries"][0]["id"]
    await client.patch(
        f"/api/v1/deliveries/{delivery_id}", json={"status": "completed"}
    )
    events = (await client.get(f"/api/v1/notifications/events?delivery_id={delivery_id}")).json()
    assert events == []


@pytest.mark.asyncio
async def test_proof_completion_also_notifies(client):
    s = await client.post(
        "/api/v1/stops/",
        json={
            "name": "Dee",
            "address": "4 Elm",
            "lat": 1.0,
            "lng": 1.0,
            "customer_email": "dee@example.com",
        },
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    delivery_id = r.json()["deliveries"][0]["id"]
    photo = base64.b64encode(b"x" * 2048).decode()
    await client.post(
        f"/api/v1/deliveries/{delivery_id}/complete",
        json={"photo_b64": photo, "barcode": "X"},
    )
    events = (await client.get(f"/api/v1/notifications/events?delivery_id={delivery_id}")).json()
    assert any(e["kind"] == "delivered" for e in events)


@pytest.mark.asyncio
async def test_manual_send_with_custom_template(client):
    # Create a custom template, then send it manually.
    s = await client.post(
        "/api/v1/stops/",
        json={
            "name": "Eve",
            "address": "5 Ash",
            "lat": 1.0,
            "lng": 1.0,
            "customer_email": "eve@example.com",
        },
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    delivery_id = r.json()["deliveries"][0]["id"]

    await client.post(
        "/api/v1/notifications/templates",
        json={"kind": "rescheduled", "subject": "Rescheduled", "body": "Hi {customer_name}, rescheduled."},
    )
    res = await client.post(
        "/api/v1/notifications/send",
        json={"delivery_id": delivery_id, "kind": "rescheduled"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["subject"] == "Rescheduled"
    assert "Eve" in res.json()["body"]


@pytest.mark.asyncio
async def test_update_template(client):
    templates = (await client.get("/api/v1/notifications/templates")).json()
    delivered = next(t for t in templates if t["kind"] == "delivered")
    r = await client.patch(
        f"/api/v1/notifications/templates/{delivered['id']}",
        json={"subject": "Package delivered"},
    )
    assert r.json()["subject"] == "Package delivered"
