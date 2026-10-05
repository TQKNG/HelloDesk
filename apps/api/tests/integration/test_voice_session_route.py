from app.core.settings import Settings
from app.main import create_app


class MockVoiceBroker:
    async def negotiate(self, session, offer_sdp: str) -> str:
        assert session.id
        assert offer_sdp == "v=0\r\n"
        return "v=0\r\na=answer\r\n"


def test_voice_sdp_requires_guest_session_and_uses_server_broker() -> None:
    from fastapi.testclient import TestClient

    with TestClient(create_app(Settings(), MockVoiceBroker())) as client:
        created = client.post("/api/v1/guest/sessions", json={"language": "en"})
        token = created.json()["sessionToken"]
        response = client.post(
            "/api/v1/guest/voice/sdp",
            content="v=0\r\n",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/sdp"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/sdp")
    assert response.text == "v=0\r\na=answer\r\n"
