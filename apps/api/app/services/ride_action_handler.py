"""Confirmed action handler that persists simulated ride outcomes server-side."""

from datetime import UTC, datetime
from uuid import UUID

from app.models.guest_session import GuestSessionRecord
from app.models.pending_action import ActionOutcome, PendingActionRecord
from app.models.ride_request import RideRequestRecord, RideRequestStatus
from app.repositories.ride_request_repository import RideRequestRepository
from app.services.ride_booking_service import RideBookingService, RideBookingStatus


class RideActionHandler:
    def __init__(self, repository: RideRequestRepository, booking_service: RideBookingService) -> None:
        self._repository = repository
        self._booking_service = booking_service

    async def handle(self, action: PendingActionRecord, session: GuestSessionRecord) -> ActionOutcome:
        destination_id = action.details.get("destinationId")
        if not isinstance(destination_id, str):
            raise ValueError("A confirmed ride action needs a configured destination.")
        destination, booking = await self._booking_service.book(destination_id)
        status = RideRequestStatus(booking.status.value)
        now = datetime.now(UTC)
        request = RideRequestRecord(
            session_id=session.id,
            destination_id=destination.id,
            destination_label=destination.label_for(session.language),
            status=status,
            provider_reference=booking.provider_reference,
            created_at=now,
            updated_at=now,
        )
        persisted = await self._repository.create(request)
        if booking.status is RideBookingStatus.SIMULATED:
            return ActionOutcome(
                action_id=action.id,
                status="simulated",
                message="Your simulated ride request is confirmed.",
                result={"rideStatus": "simulated", "rideRequestId": str(persisted.id)},
            )
        message = "The simulated ride service is unavailable." if booking.status is RideBookingStatus.UNAVAILABLE else "The simulated ride request failed."
        return ActionOutcome(
            action_id=action.id,
            status="failed",
            message=message,
            result={"rideStatus": booking.status.value, "rideRequestId": str(persisted.id)},
        )
