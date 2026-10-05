"""Guest action prepare, confirm, and cancellation endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from app.core.errors import InvalidInputError
from app.models.guest_session import GuestSessionRecord
from app.models.pending_action import ActionOutcome, ConfirmActionRequest, PendingActionResponse, PrepareActionRequest
from app.routes.dependencies import get_confirmation_service, require_guest_session
from app.services.confirmation_service import ConfirmationService

router = APIRouter(prefix="/actions", tags=["guest-actions"])


@router.post("", response_model=PendingActionResponse, status_code=status.HTTP_201_CREATED)
async def prepare_guest_action(
    request: PrepareActionRequest,
    session: Annotated[GuestSessionRecord, Depends(require_guest_session)],
    confirmation_service: Annotated[ConfirmationService, Depends(get_confirmation_service)],
) -> PendingActionResponse:
    return await confirmation_service.prepare(session, request)


@router.post("/{action_id}/confirm", response_model=ActionOutcome)
async def confirm_guest_action(
    action_id: UUID,
    request: ConfirmActionRequest,
    idempotency_key: Annotated[UUID | None, Header(alias="Idempotency-Key")] = None,
    session: GuestSessionRecord = Depends(require_guest_session),
    confirmation_service: ConfirmationService = Depends(get_confirmation_service),
) -> ActionOutcome:
    if idempotency_key is None:
        raise InvalidInputError("An Idempotency-Key header is required.")
    return await confirmation_service.confirm(session, action_id, idempotency_key, request.confirmed)


@router.post("/{action_id}/cancel", response_model=PendingActionResponse)
async def cancel_guest_action(
    action_id: UUID,
    session: Annotated[GuestSessionRecord, Depends(require_guest_session)],
    confirmation_service: Annotated[ConfirmationService, Depends(get_confirmation_service)],
) -> PendingActionResponse:
    return await confirmation_service.cancel(session, action_id)
