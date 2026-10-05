"""Authenticated SDP negotiation endpoint for the browser voice client."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Response

from app.models.guest_session import GuestSessionRecord
from app.routes.dependencies import get_voice_session_broker, require_guest_session
from app.services.voice_session_service import VoiceSessionBroker

router = APIRouter(prefix="/guest/voice", tags=["voice"])


@router.post("/sdp", response_class=Response, responses={502: {"description": "Voice provider unavailable"}})
async def negotiate_voice_session(
    offer_sdp: Annotated[str, Body(media_type="application/sdp")],
    session: Annotated[GuestSessionRecord, Depends(require_guest_session)],
    voice_session_broker: Annotated[VoiceSessionBroker, Depends(get_voice_session_broker)],
) -> Response:
    answer_sdp = await voice_session_broker.negotiate(session, offer_sdp)
    return Response(content=answer_sdp, media_type="application/sdp")
