"""Guest-owned help request status endpoint."""

from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends
from app.models.guest_session import GuestSessionRecord
from app.models.help_request import HelpRequestResponse
from app.models.help_request import HotelQuestionRequest, HotelQuestionResponse
from app.routes.dependencies import get_help_action_handler, get_hotel_agent, require_guest_session
from app.services.help_action_handler import HelpActionHandler
from app.services.hotel_agent import HotelAgent

router = APIRouter(tags=["guest-help"])

@router.post("/hotel-questions", response_model=HotelQuestionResponse)
async def answer_hotel_question(
    request: HotelQuestionRequest,
    session: Annotated[GuestSessionRecord, Depends(require_guest_session)],
    hotel_agent: Annotated[HotelAgent, Depends(get_hotel_agent)],
) -> HotelQuestionResponse:
    answer = await hotel_agent.answer(request.question, session.language)
    return HotelQuestionResponse(answer=answer, needs_staff_help=answer is None)

@router.get("/help-requests/{request_id}", response_model=HelpRequestResponse)
async def get_guest_help_request(request_id: UUID, session: Annotated[GuestSessionRecord, Depends(require_guest_session)], handler: Annotated[HelpActionHandler, Depends(get_help_action_handler)]) -> HelpRequestResponse:
    return await handler.get_for_guest(request_id, session)
