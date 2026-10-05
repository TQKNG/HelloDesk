"""Supabase adapters for reservation and bill data accessed by FastAPI only."""

from uuid import UUID

from app.models.reservation import BillRecord, BillStatus, ReservationRecord, ReservationStatus
from app.repositories.supabase_postgrest import SupabasePostgrestClient


class SupabaseReservationRepository:
    def __init__(self, client: SupabasePostgrestClient) -> None:
        self._client = client

    async def find_by_code(self, reservation_code: str) -> ReservationRecord | None:
        row = await self._client.select_one("reservations", {"reservation_code": reservation_code})
        return ReservationRecord.model_validate(row) if row else None

    async def find_by_id(self, reservation_id: UUID) -> ReservationRecord | None:
        row = await self._client.select_one("reservations", {"id": str(reservation_id)})
        return ReservationRecord.model_validate(row) if row else None

    async def transition(self, reservation_id: UUID, expected_status: ReservationStatus, target_status: ReservationStatus) -> ReservationRecord | None:
        row = await self._client.update(
            "reservations",
            {"id": str(reservation_id), "status": expected_status.value},
            {"status": target_status.value},
        )
        return ReservationRecord.model_validate(row) if row else None


class SupabaseBillRepository:
    def __init__(self, client: SupabasePostgrestClient) -> None:
        self._client = client

    async def find_by_reservation_id(self, reservation_id: UUID) -> BillRecord | None:
        row = await self._client.select_one("bills", {"reservation_id": str(reservation_id)})
        return BillRecord.model_validate(row) if row else None

    async def transition(self, reservation_id: UUID, expected_status: BillStatus, target_status: BillStatus) -> BillRecord | None:
        row = await self._client.update(
            "bills",
            {"reservation_id": str(reservation_id), "status": expected_status.value},
            {"status": target_status.value},
        )
        return BillRecord.model_validate(row) if row else None
