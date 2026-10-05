def test_failed_reservation_lookups_are_limited_per_guest_session(client) -> None:
    created = client.post("/api/v1/guest/sessions", json={"language": "en"})
    headers = {"Authorization": f"Bearer {created.json()['sessionToken']}"}

    for attempt in range(5):
        response = client.post(
            "/api/v1/guest/reservation-lookups",
            json={"reservationCode": f"UNKNOWN-{attempt}"},
            headers=headers,
        )
        assert response.status_code == 404

    limited = client.post(
        "/api/v1/guest/reservation-lookups",
        json={"reservationCode": "DEMO-EN-1001"},
        headers=headers,
    )
    assert limited.status_code == 429


def test_lookup_limit_isolated_between_guest_sessions(client) -> None:
    first = client.post("/api/v1/guest/sessions", json={"language": "en"})
    second = client.post("/api/v1/guest/sessions", json={"language": "en"})
    first_headers = {"Authorization": f"Bearer {first.json()['sessionToken']}"}
    second_headers = {"Authorization": f"Bearer {second.json()['sessionToken']}"}
    for attempt in range(5):
        client.post("/api/v1/guest/reservation-lookups", json={"reservationCode": f"UNKNOWN-{attempt}"}, headers=first_headers)

    allowed = client.post(
        "/api/v1/guest/reservation-lookups",
        json={"reservationCode": "DEMO-EN-1001"},
        headers=second_headers,
    )
    assert allowed.status_code == 200
