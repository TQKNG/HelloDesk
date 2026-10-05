"""Reservation persistence port and deterministic in-memory demo adapter."""

from collections.abc import Callable
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.models.reservation import ReservationRecord, ReservationStatus


class ReservationRepository(Protocol):
    async def find_by_code(self, reservation_code: str) -> ReservationRecord | None: ...
    async def find_by_id(self, reservation_id: UUID) -> ReservationRecord | None: ...
    async def transition(
        self,
        reservation_id: UUID,
        expected_status: ReservationStatus,
        target_status: ReservationStatus,
    ) -> ReservationRecord | None: ...


class InMemoryReservationRepository:
    def __init__(self, records: list[ReservationRecord], now: Callable[[], datetime]) -> None:
        self._records = {record.id: record for record in records}
        self._ids_by_code = {record.reservation_code: record.id for record in records}
        self._now = now

    async def find_by_code(self, reservation_code: str) -> ReservationRecord | None:
        reservation_id = self._ids_by_code.get(reservation_code)
        return self._records.get(reservation_id) if reservation_id else None

    async def find_by_id(self, reservation_id: UUID) -> ReservationRecord | None:
        return self._records.get(reservation_id)

    async def transition(
        self,
        reservation_id: UUID,
        expected_status: ReservationStatus,
        target_status: ReservationStatus,
    ) -> ReservationRecord:
        reservation = self._records.get(reservation_id)
        if reservation is None or reservation.status is not expected_status:
            return None
        updated = reservation.model_copy(update={"status": target_status, "updated_at": self._now()})
        self._records[reservation_id] = updated
        return updated
