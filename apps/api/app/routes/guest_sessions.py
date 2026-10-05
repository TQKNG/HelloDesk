"""Guest session creation endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.models.guest_session import CreateGuestSessionRequest, GuestSessionResponse
from app.routes.dependencies import get_guest_session_service
from app.services.guest_session_service import GuestSessionService

router = APIRouter(prefix="/guest/sessions", tags=["guest-sessions"])


@router.post("", response_model=GuestSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_guest_session(
    request: CreateGuestSessionRequest,
    service: Annotated[GuestSessionService, Depends(get_guest_session_service)],
) -> GuestSessionResponse:
    return await service.create(request)
