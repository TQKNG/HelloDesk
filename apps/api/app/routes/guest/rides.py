"""Guest-owned simulated ride status routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.errors import NotFoundError
from app.models.guest_session import GuestSessionRecord
from app.models.ride_request import RideRequestResponse
from app.repositories.ride_request_repository import RideRequestRepository
from app.routes.dependencies import get_ride_request_repository, require_guest_session

router = APIRouter(tags=["guest-rides"])


@router.get("/ride-requests/{request_id}", response_model=RideRequestResponse)
async def get_guest_ride_request(
    request_id: UUID,
    session: Annotated[GuestSessionRecord, Depends(require_guest_session)],
    repository: Annotated[RideRequestRepository, Depends(get_ride_request_repository)],
) -> RideRequestResponse:
    request = await repository.get_owned(request_id, session.id)
    if request is None:
        raise NotFoundError("The ride request was not found for this guest session.")
    return RideRequestResponse(
        id=request.id,
        destination_label=request.destination_label,
        status=request.status,
        created_at=request.created_at,
    )
