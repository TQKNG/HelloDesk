"""Cross-session authorization checks for guest-owned records."""

from uuid import uuid4


def _session(client) -> dict[str, str]:
    response = client.post("/api/v1/guest/sessions", json={"language": "en"})
    return {"Authorization": f"Bearer {response.json()['sessionToken']}"}


def test_guest_cannot_confirm_another_sessions_action(client) -> None:
    first = _session(client)
    second = _session(client)
    action = client.post(
        "/api/v1/guest/actions",
        json={"kind": "staff_help", "details": {"summary": "Please bring towels."}},
        headers=first,
    )

    response = client.post(
        f"/api/v1/guest/actions/{action.json()['actionId']}/confirm",
        json={"confirmed": True},
        headers={**second, "Idempotency-Key": str(uuid4())},
    )

    assert response.status_code == 404


def test_guest_cannot_read_another_sessions_help_request(client) -> None:
    first = _session(client)
    second = _session(client)
    action = client.post(
        "/api/v1/guest/actions",
        json={"kind": "staff_help", "details": {"summary": "Please bring towels."}},
        headers=first,
    )
    confirmed = client.post(
        f"/api/v1/guest/actions/{action.json()['actionId']}/confirm",
        json={"confirmed": True},
        headers={**first, "Idempotency-Key": str(uuid4())},
    )
    help_request_id = confirmed.json()["result"]["helpRequestId"]

    response = client.get(f"/api/v1/guest/help-requests/{help_request_id}", headers=second)

    assert response.status_code == 404
