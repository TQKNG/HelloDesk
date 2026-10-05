"""Confirmed check-in and checkout writes for the approved guest session."""

import base64
from uuid import UUID

from app.core.errors import ConflictError
from app.models.guest_session import GuestSessionRecord
from app.models.pending_action import ActionOutcome, PendingActionKind, PendingActionRecord
from app.models.reservation import BillStatus, ReservationStatus
from app.repositories.bill_repository import BillRepository
from app.repositories.reservation_repository import ReservationRepository
from app.services.reservation_service import ReservationService


class StayActionHandler:
    def __init__(
        self,
        reservation_repository: ReservationRepository,
        bill_repository: BillRepository,
        reservation_service: ReservationService,
    ) -> None:
        self._reservation_repository = reservation_repository
        self._bill_repository = bill_repository
        self._reservation_service = reservation_service

    async def handle(self, action: PendingActionRecord, session: GuestSessionRecord) -> ActionOutcome:
        reservation = await self._reservation_service.require_scoped_reservation(session)
        if action.kind is PendingActionKind.CHECK_IN:
            return await self._check_in(action, reservation.id, reservation.status)
        if action.kind is PendingActionKind.CHECK_OUT:
            return await self._check_out(action, reservation.id, reservation.status)
        raise ConflictError("This handler only processes stay actions.")

    async def _check_in(
        self,
        action: PendingActionRecord,
        reservation_id: UUID,
        current_status: ReservationStatus,
    ) -> ActionOutcome:
        if current_status is ReservationStatus.CANCELLED:
            raise ConflictError("A cancelled reservation cannot be checked in.")
        updated = await self._reservation_repository.transition(
            reservation_id,
            ReservationStatus.RESERVED,
            ReservationStatus.CHECKED_IN,
        )
        if updated is None or updated.room_number is None:
            raise ConflictError("This reservation is not eligible for check-in.")
        barcode = base64.urlsafe_b64encode(f"demo-room:{updated.id}:{updated.room_number}".encode()).decode().rstrip("=")
        return ActionOutcome(
            action_id=action.id,
            status="completed",
            message="Check-in is complete.",
            result={"roomNumber": updated.room_number, "roomBarcodePayload": barcode},
        )

    async def _check_out(
        self,
        action: PendingActionRecord,
        reservation_id: UUID,
        current_status: ReservationStatus,
    ) -> ActionOutcome:
        if current_status is not ReservationStatus.CHECKED_IN:
            raise ConflictError("Only an active checked-in stay can check out.")
        updated = await self._reservation_repository.transition(
            reservation_id,
            ReservationStatus.CHECKED_IN,
            ReservationStatus.CHECKED_OUT,
        )
        if updated is None:
            raise ConflictError("The stay could not be checked out.")
        bill = await self._bill_repository.transition(reservation_id, BillStatus.OPEN, BillStatus.CLOSED)
        if bill is None:
            await self._reservation_repository.transition(
                reservation_id,
                ReservationStatus.CHECKED_OUT,
                ReservationStatus.CHECKED_IN,
            )
            raise ConflictError("The bill is not available for checkout.")
        return ActionOutcome(action_id=action.id, status="completed", message="Checkout is complete.")
