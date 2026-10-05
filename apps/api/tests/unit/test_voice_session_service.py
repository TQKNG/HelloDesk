import json
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from pydantic import SecretStr

from app.core.settings import Settings
from app.models.guest_session import GuestSessionRecord, Language
from app.services.voice_session_service import AzureVoiceSessionService


@pytest.mark.asyncio
async def test_gpt_live_session_uses_server_credentials_and_returns_only_sdp_answer() -> None:
    now = datetime(2026, 10, 4, tzinfo=UTC)
    session = GuestSessionRecord(
        token_hash="token-hash",
        language=Language.VIETNAMESE,
        created_at=now,
        expires_at=now + timedelta(minutes=15),
    )
    observed: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed["url"] = str(request.url)
        observed["authorization"] = request.headers.get("Authorization")
        observed["body"] = json.loads(request.content)
        return httpx.Response(200, json={"session": {"id": "provider-id"}, "transport": {"sdp": "v=0\r\na=answer\r\n"}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        service = AzureVoiceSessionService(
            Settings(
                azure_openai_endpoint="https://example.openai.azure.com",
                azure_openai_api_key=SecretStr("server-secret"),
                azure_openai_deployment="gpt-live-1",
            ),
            client=client,
        )
        answer = await service.negotiate(session, "v=0\r\no=guest-offer\r\n")

    assert answer == "v=0\r\na=answer\r\n"
    assert observed["url"] == "https://example.openai.azure.com/openai/v1/live/sessions"
    assert observed["authorization"] == "Bearer server-secret"
    request_body = observed["body"]
    assert isinstance(request_body, dict)
    assert request_body["transport"] == {"type": "webrtc", "sdp": "v=0\r\no=guest-offer\r\n"}
    assert request_body["session"]["model"] == "gpt-live-1"
    assert "tiếng Việt" in request_body["session"]["instructions"]
