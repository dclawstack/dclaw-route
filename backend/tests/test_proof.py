import base64
import pytest

from app.services.proof_validator import validate_photo


def test_validate_photo_handles_none():
    assert validate_photo(None) is None
    assert validate_photo("") is None


def test_validate_photo_rejects_too_small():
    tiny = base64.b64encode(b"hi").decode()
    assert validate_photo(tiny) is False


def test_validate_photo_accepts_large_payload():
    big = base64.b64encode(b"x" * 2048).decode()
    assert validate_photo(big) is True


def test_validate_photo_strips_data_uri_prefix():
    big = base64.b64encode(b"x" * 2048).decode()
    assert validate_photo(f"data:image/jpeg;base64,{big}") is True


@pytest.mark.asyncio
async def test_complete_delivery_with_photo(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "X", "address": "X", "lat": 0.0, "lng": 0.0},
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    delivery_id = r.json()["deliveries"][0]["id"]

    photo = base64.b64encode(b"x" * 2048).decode()
    proof = await client.post(
        f"/api/v1/deliveries/{delivery_id}/complete",
        json={
            "photo_b64": photo,
            "barcode": "ABC123",
            "geotag_lat": 40.7,
            "geotag_lng": -74.0,
            "notes": "Left at front door",
        },
    )
    assert proof.status_code == 200, proof.text
    body = proof.json()
    assert body["status"] == "completed"
    assert body["completed_at"] is not None
    assert body["photo_validated"] is True
    assert body["barcode"] == "ABC123"
    assert body["notes"] == "Left at front door"


@pytest.mark.asyncio
async def test_complete_requires_some_proof(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "X", "address": "X", "lat": 0.0, "lng": 0.0},
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    delivery_id = r.json()["deliveries"][0]["id"]

    bad = await client.post(
        f"/api/v1/deliveries/{delivery_id}/complete", json={"notes": "just notes"}
    )
    assert bad.status_code == 400


@pytest.mark.asyncio
async def test_get_proof_after_completion(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "X", "address": "X", "lat": 0.0, "lng": 0.0},
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    delivery_id = r.json()["deliveries"][0]["id"]
    await client.post(
        f"/api/v1/deliveries/{delivery_id}/complete",
        json={"signature_b64": "data:image/png;base64,abc"},
    )

    proof = await client.get(f"/api/v1/deliveries/{delivery_id}/proof")
    assert proof.status_code == 200
    assert proof.json()["signature_b64"] == "data:image/png;base64,abc"
