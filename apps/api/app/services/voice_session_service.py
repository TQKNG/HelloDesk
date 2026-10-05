"""Azure GPT-Live WebRTC session brokerage with server-side credentials."""

import json
from typing import Protocol

import httpx

from app.core.errors import ProviderUnavailableError
from app.core.settings import Settings
from app.models.guest_session import GuestSessionRecord


class VoiceSessionBroker(Protocol):
    async def negotiate(self, session: GuestSessionRecord, offer_sdp: str) -> str: ...


class AzureVoiceSessionService:
    """Creates a GPT-Live session and returns only its WebRTC SDP answer."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._client = client

    async def negotiate(self, session: GuestSessionRecord, offer_sdp: str) -> str:
        endpoint = self._settings.azure_voice_sdp_endpoint
        if not offer_sdp.strip() or not endpoint or not self._settings.azure_openai_api_key:
            raise ProviderUnavailableError()
        instructions = (
            "You are a concise, warm hotel receptionist. "
            "Speak only English and keep using English for this guest session. "
            "Help with check-in, checkout, hotel information, staff help, and demo rides. "
            "Never claim that an action was completed. Ask the guest to review and explicitly confirm "
            "all action details on the kiosk before anything is changed."
            if session.language.value == "en"
            else "Bạn là lễ tân khách sạn thân thiện, trả lời ngắn gọn. "
            "Chỉ nói tiếng Việt trong suốt phiên của khách. Hỗ trợ nhận phòng, trả phòng, "
            "thông tin khách sạn, yêu cầu nhân viên trợ giúp và chuyến xe thử nghiệm. "
            "Không bao giờ nói rằng một hành động đã hoàn tất. Hãy yêu cầu khách xem lại và "
            "xác nhận rõ ràng mọi chi tiết trên màn hình kiosk trước khi thay đổi bất kỳ thông tin nào."
        )
        request_body = {
            "session": {
                "model": self._settings.azure_openai_deployment or "gpt-live-1",
                "instructions": instructions,
                "delegation": {"type": "client"},
            },
            "transport": {"type": "webrtc", "sdp": offer_sdp},
        }
        headers = {
            "Authorization": f"Bearer {self._settings.azure_openai_api_key.get_secret_value()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        try:
            if self._client is not None:
                response = await self._client.post(endpoint, json=request_body, headers=headers)
            else:
                async with httpx.AsyncClient(timeout=20) as client:
                    response = await client.post(endpoint, json=request_body, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError() from exc
        try:
            sdp_answer = response.json()["transport"]["sdp"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ProviderUnavailableError()
        if not isinstance(sdp_answer, str) or not sdp_answer.strip():
            raise ProviderUnavailableError()
        return sdp_answer
