"""Authenticated staff help-request routes."""

from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends
from app.models.help_request import HelpRequestResponse, HelpRequestStatus
from app.routes.dependencies import get_help_action_handler, require_staff_session
from app.services.help_action_handler import HelpActionHandler

router = APIRouter(tags=["staff-help"])

@router.get("/help-requests", response_model=list[HelpRequestResponse])
async def list_help_requests(status: HelpRequestStatus | None = None, _: Annotated[None, Depends(require_staff_session)] = None, handler: HelpActionHandler = Depends(get_help_action_handler)) -> list[HelpRequestResponse]:
    return await handler.list_for_staff(status)

@router.put("/help-requests/{request_id}/acknowledgement", response_model=HelpRequestResponse)
async def acknowledge_help_request(request_id: UUID, _: Annotated[None, Depends(require_staff_session)] = None, handler: HelpActionHandler = Depends(get_help_action_handler)) -> HelpRequestResponse:
    return await handler.acknowledge(request_id)
