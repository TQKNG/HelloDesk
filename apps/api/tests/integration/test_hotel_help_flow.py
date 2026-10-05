from uuid import uuid4


def staff_headers(client) -> dict[str, str]:
    sign_in = client.post("/api/v1/staff/sessions", json={"username": "admin", "password": "admin"})
    assert sign_in.status_code == 201
    return {"Authorization": f"Bearer {sign_in.json()['sessionToken']}"}


def test_help_request_is_confirmed_then_guest_owned_and_staff_acknowledged(client) -> None:
    session = client.post("/api/v1/guest/sessions", json={"language": "en"})
    headers = {"Authorization": f"Bearer {session.json()['sessionToken']}"}
    prepared = client.post(
        "/api/v1/guest/actions",
        json={"kind": "staff_help", "details": {"summary": "Please bring towels."}},
        headers=headers,
    )
    assert prepared.status_code == 201
    outcome = client.post(
        f"/api/v1/guest/actions/{prepared.json()['actionId']}/confirm",
        json={"confirmed": True},
        headers={**headers, "Idempotency-Key": str(uuid4())},
    )
    request_id = outcome.json()["result"]["helpRequestId"]
    assert client.get(f"/api/v1/guest/help-requests/{request_id}", headers=headers).status_code == 200
    assert client.put(f"/api/v1/staff/help-requests/{request_id}/acknowledgement", headers=staff_headers(client)).status_code == 200


def test_hotel_question_returns_localized_fact_or_staff_help_fallback(client) -> None:
    session = client.post("/api/v1/guest/sessions", json={"language": "vi"})
    headers = {"Authorization": f"Bearer {session.json()['sessionToken']}"}
    known = client.post("/api/v1/guest/hotel-questions", json={"question": "breakfast"}, headers=headers)
    unknown = client.post("/api/v1/guest/hotel-questions", json={"question": "Where is the pool?"}, headers=headers)

    assert known.status_code == 200
    assert known.json() == {"answer": "Bữa sáng được phục vụ từ 7 giờ đến 10 giờ sáng.", "needsStaffHelp": False}
    assert unknown.json() == {"answer": None, "needsStaffHelp": True}
