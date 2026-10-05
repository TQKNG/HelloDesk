"""Retrieves a bill only for the reservation scoped to the active guest session."""

from app.core.errors import ConflictError, NotFoundError
from app.models.guest_session import GuestSessionRecord
from app.models.reservation import BillResponse, ReservationStatus
from app.repositories.bill_repository import BillRepository
from app.services.reservation_service import ReservationService


class BillingService:
    def __init__(self, repository: BillRepository, reservation_service: ReservationService) -> None:
        self._repository = repository
        self._reservation_service = reservation_service

    async def get_bill(self, session: GuestSessionRecord) -> BillResponse:
        reservation = await self._reservation_service.require_scoped_reservation(session)
        if reservation.status is not ReservationStatus.CHECKED_IN:
            raise ConflictError("A bill is available only for an active checked-in stay.")
        bill = await self._repository.find_by_reservation_id(reservation.id)
        if bill is None:
            raise NotFoundError("No bill was found for this reservation.")
        return BillResponse(
            items=bill.items,
            currency=bill.currency,
            total_amount_minor=bill.total_amount_minor,
            status=bill.status,
        )
