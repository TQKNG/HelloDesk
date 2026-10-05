"""Bill persistence port and deterministic in-memory demo adapter."""

from collections.abc import Callable
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.models.reservation import BillRecord, BillStatus


class BillRepository(Protocol):
    async def find_by_reservation_id(self, reservation_id: UUID) -> BillRecord | None: ...
    async def transition(
        self,
        reservation_id: UUID,
        expected_status: BillStatus,
        target_status: BillStatus,
    ) -> BillRecord | None: ...


class InMemoryBillRepository:
    def __init__(self, records: list[BillRecord], now: Callable[[], datetime]) -> None:
        self._records_by_reservation_id = {record.reservation_id: record for record in records}
        self._now = now

    async def find_by_reservation_id(self, reservation_id: UUID) -> BillRecord | None:
        return self._records_by_reservation_id.get(reservation_id)

    async def transition(
        self,
        reservation_id: UUID,
        expected_status: BillStatus,
        target_status: BillStatus,
    ) -> BillRecord | None:
        bill = self._records_by_reservation_id.get(reservation_id)
        if bill is None or bill.status is not expected_status:
            return None
        updated = bill.model_copy(update={"status": target_status, "updated_at": self._now()})
        self._records_by_reservation_id[reservation_id] = updated
        return updated
