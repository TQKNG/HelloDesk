"""Session-scoped reservation lookup, lookup confirmation, and bill routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.models.guest_session import GuestSessionRecord, GuestSessionStateResponse
from app.models.reservation import BillResponse, ReservationLookupRequest, ReservationLookupResponse
from app.routes.dependencies import (
    get_billing_service,
    get_reservation_service,
    require_guest_session,
)
from app.services.billing_service import BillingService
from app.services.reservation_service import ReservationService

router = APIRouter(tags=["guest-stays"])


@router.post("/reservation-lookups", response_model=ReservationLookupResponse)
async def lookup_reservation(
    request: ReservationLookupRequest,
    session: Annotated[GuestSessionRecord, Depends(require_guest_session)],
    reservation_service: Annotated[ReservationService, Depends(get_reservation_service)],
) -> ReservationLookupResponse:
    return await reservation_service.lookup(session, request)


@router.post("/reservation-lookups/{lookup_id}/confirm", response_model=GuestSessionStateResponse)
async def confirm_reservation_lookup(
    lookup_id: UUID,
    session: Annotated[GuestSessionRecord, Depends(require_guest_session)],
    reservation_service: Annotated[ReservationService, Depends(get_reservation_service)],
) -> GuestSessionStateResponse:
    updated_session = await reservation_service.confirm_lookup(session, lookup_id)
    return GuestSessionStateResponse(
        language=updated_session.language,
        expires_at=updated_session.expires_at,
        status=updated_session.status,
    )


@router.get("/bill", response_model=BillResponse)
async def get_guest_bill(
    session: Annotated[GuestSessionRecord, Depends(require_guest_session)],
    billing_service: Annotated[BillingService, Depends(get_billing_service)],
) -> BillResponse:
    return await billing_service.get_bill(session)
