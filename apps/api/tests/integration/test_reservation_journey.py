from uuid import uuid4


def create_guest_session(client, language: str = "en") -> dict[str, str]:
    response = client.post("/api/v1/guest/sessions", json={"language": language})
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['sessionToken']}"}


def confirm_lookup(client, headers: dict[str, str], reservation_code: str) -> None:
    lookup = client.post(
        "/api/v1/guest/reservation-lookups",
        json={"reservationCode": reservation_code},
        headers=headers,
    )
    assert lookup.status_code == 200
    confirmed = client.post(
        f"/api/v1/guest/reservation-lookups/{lookup.json()['lookupId']}/confirm",
        headers=headers,
    )
    assert confirmed.status_code == 200


def test_check_in_requires_lookup_and_explicit_confirm_then_returns_room_details(client) -> None:
    headers = create_guest_session(client)
    denied = client.post("/api/v1/guest/actions", json={"kind": "check_in"}, headers=headers)
    assert denied.status_code == 201
    denied_confirmation = client.post(
        f"/api/v1/guest/actions/{denied.json()['actionId']}/confirm",
        json={"confirmed": True},
        headers={**headers, "Idempotency-Key": str(uuid4())},
    )
    assert denied_confirmation.status_code == 409

    confirm_lookup(client, headers, "DEMO-EN-1001")
    pending = client.post("/api/v1/guest/actions", json={"kind": "check_in"}, headers=headers)
    action_id = pending.json()["actionId"]
    outcome = client.post(
        f"/api/v1/guest/actions/{action_id}/confirm",
        json={"confirmed": True},
        headers={**headers, "Idempotency-Key": str(uuid4())},
    )

    assert outcome.status_code == 200
    assert outcome.json()["result"]["roomNumber"] == "101"
    assert outcome.json()["result"]["roomBarcodePayload"]


def test_bill_and_checkout_are_limited_to_scoped_checked_in_stay(client) -> None:
    headers = create_guest_session(client)
    assert client.get("/api/v1/guest/bill", headers=headers).status_code == 409
    confirm_lookup(client, headers, "DEMO-CHECKED-IN")

    bill = client.get("/api/v1/guest/bill", headers=headers)
    assert bill.status_code == 200
    assert bill.json()["totalAmountMinor"] == 12500
    pending = client.post("/api/v1/guest/actions", json={"kind": "check_out"}, headers=headers)
    outcome = client.post(
        f"/api/v1/guest/actions/{pending.json()['actionId']}/confirm",
        json={"confirmed": True},
        headers={**headers, "Idempotency-Key": str(uuid4())},
    )

    assert outcome.status_code == 200
    assert outcome.json()["message"] == "Checkout is complete."
    assert client.get("/api/v1/guest/bill", headers=headers).status_code == 409


def test_lookup_cannot_be_confirmed_by_a_different_guest_session(client) -> None:
    first_headers = create_guest_session(client)
    second_headers = create_guest_session(client)
    lookup = client.post(
        "/api/v1/guest/reservation-lookups",
        json={"reservationCode": "DEMO-EN-1001"},
        headers=first_headers,
    )

    response = client.post(
        f"/api/v1/guest/reservation-lookups/{lookup.json()['lookupId']}/confirm",
        headers=second_headers,
    )
    assert response.status_code == 404
