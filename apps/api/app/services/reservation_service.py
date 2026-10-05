"""Session-scoped synthetic reservation lookup and confirmation."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.core.errors import ConflictError, NotFoundError, RateLimitedError
from app.models.guest_session import GuestSessionRecord
from app.models.reservation import (
    ReservationLookupRequest,
    ReservationLookupResponse,
    ReservationRecord,
    ReservationSummary,
)
from app.repositories.reservation_repository import ReservationRepository
from app.services.guest_session_service import GuestSessionService


class ReservationService:
    def __init__(
        self,
        repository: ReservationRepository,
        guest_session_service: GuestSessionService,
    ) -> None:
        self._repository = repository
        self._guest_session_service = guest_session_service
        self._lookups: dict[UUID, tuple[UUID, UUID]] = {}
        self._failed_lookups: dict[UUID, tuple[datetime, int]] = {}

    async def lookup(
        self,
        session: GuestSessionRecord,
        request: ReservationLookupRequest,
    ) -> ReservationLookupResponse:
        now = datetime.now(UTC)
        window = self._failed_lookups.get(session.id)
        if window and now - window[0] < timedelta(minutes=1) and window[1] >= 5:
            raise RateLimitedError()
        if window and now - window[0] >= timedelta(minutes=1):
            self._failed_lookups.pop(session.id, None)
        reservation = await self._repository.find_by_code(request.reservation_code)
        if reservation is None:
            start, count = self._failed_lookups.get(session.id, (now, 0))
            if now - start >= timedelta(minutes=1):
                start, count = now, 0
            self._failed_lookups[session.id] = (start, count + 1)
            raise NotFoundError("No demo reservation matches that code.")
        self._failed_lookups.pop(session.id, None)
        if reservation.status.value in {"checked_out", "cancelled"}:
            raise ConflictError("This reservation cannot be used for a stay action.")
        lookup_id = uuid4()
        self._lookups[lookup_id] = (session.id, reservation.id)
        return ReservationLookupResponse(lookup_id=lookup_id, reservation=self._summary(reservation))

    async def confirm_lookup(self, session: GuestSessionRecord, lookup_id: UUID) -> GuestSessionRecord:
        lookup = self._lookups.get(lookup_id)
        if lookup is None or lookup[0] != session.id:
            raise NotFoundError("The reservation lookup was not found for this guest session.")
        reservation = await self._repository.find_by_id(lookup[1])
        if reservation is None:
            raise NotFoundError("The reservation is no longer available.")
        if reservation.status.value in {"checked_out", "cancelled"}:
            raise ConflictError("This reservation cannot be associated with the session.")
        updated_session = await self._guest_session_service.scope_reservation(session.id, reservation.id)
        self._lookups.pop(lookup_id, None)
        return updated_session

    async def require_scoped_reservation(self, session: GuestSessionRecord) -> ReservationRecord:
        if session.reservation_id is None:
            raise ConflictError("Confirm a reservation before continuing with a stay action.")
        reservation = await self._repository.find_by_id(session.reservation_id)
        if reservation is None:
            raise NotFoundError("The session reservation was not found.")
        return reservation

    @staticmethod
    def _summary(reservation: ReservationRecord) -> ReservationSummary:
        return ReservationSummary(
            display_name=reservation.guest_display_name,
            arrival_date=reservation.arrival_date,
            departure_date=reservation.departure_date,
            status=reservation.status,
            room_number=reservation.room_number,
        )
