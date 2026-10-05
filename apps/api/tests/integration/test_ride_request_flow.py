from uuid import uuid4


def create_guest_session(client) -> dict[str, str]:
    response = client.post("/api/v1/guest/sessions", json={"language": "en"})
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['sessionToken']}"}


def prepare_ride(client, headers: dict[str, str], destination_id: str = "demo-union-square") -> dict[str, object]:
    response = client.post(
        "/api/v1/guest/actions",
        json={"kind": "uber_ride", "details": {"destinationId": destination_id}},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_ride_is_not_created_until_the_guest_confirms(client) -> None:
    headers = create_guest_session(client)
    pending = prepare_ride(client, headers)

    assert client.app.state.ride_request_repository._requests == {}
    outcome = client.post(
        f"/api/v1/guest/actions/{pending['actionId']}/confirm",
        json={"confirmed": True},
        headers={**headers, "Idempotency-Key": str(uuid4())},
    )

    assert outcome.status_code == 200
    payload = outcome.json()
    assert payload["status"] == "simulated"
    assert payload["result"]["rideStatus"] == "simulated"
    assert "providerReference" not in payload["result"]
    assert len(client.app.state.ride_request_repository._requests) == 1


def test_ride_status_is_owned_by_the_creating_guest_session(client) -> None:
    first_headers = create_guest_session(client)
    pending = prepare_ride(client, first_headers)
    outcome = client.post(
        f"/api/v1/guest/actions/{pending['actionId']}/confirm",
        json={"confirmed": True},
        headers={**first_headers, "Idempotency-Key": str(uuid4())},
    )
    request_id = outcome.json()["result"]["rideRequestId"]

    owned = client.get(f"/api/v1/guest/ride-requests/{request_id}", headers=first_headers)
    other_headers = create_guest_session(client)
    unowned = client.get(f"/api/v1/guest/ride-requests/{request_id}", headers=other_headers)

    assert owned.status_code == 200
    assert owned.json()["status"] == "simulated"
    assert unowned.status_code == 404


def test_an_unknown_destination_never_creates_a_ride(client) -> None:
    headers = create_guest_session(client)
    pending = prepare_ride(client, headers, destination_id="unconfigured-place")

    outcome = client.post(
        f"/api/v1/guest/actions/{pending['actionId']}/confirm",
        json={"confirmed": True},
        headers={**headers, "Idempotency-Key": str(uuid4())},
    )

    assert outcome.status_code == 400
    assert client.app.state.ride_request_repository._requests == {}
