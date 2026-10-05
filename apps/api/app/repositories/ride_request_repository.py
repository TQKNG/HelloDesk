"""Persistence ports for guest-owned simulated ride records."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from app.models.ride_request import RideRequestRecord
from app.repositories.supabase_postgrest import SupabasePostgrestClient


def utc_now() -> datetime:
    return datetime.now(UTC)


class RideRequestRepository(Protocol):
    async def create(self, request: RideRequestRecord) -> RideRequestRecord: ...
    async def get_owned(self, request_id: UUID, session_id: UUID) -> RideRequestRecord | None: ...


class InMemoryRideRequestRepository:
    def __init__(self, now: Callable[[], datetime] = utc_now) -> None:
        self._now = now
        self._requests: dict[UUID, RideRequestRecord] = {}

    async def create(self, request: RideRequestRecord) -> RideRequestRecord:
        self._requests[request.id] = request
        return request

    async def get_owned(self, request_id: UUID, session_id: UUID) -> RideRequestRecord | None:
        request = self._requests.get(request_id)
        return request if request and request.session_id == session_id else None


class SupabaseRideRequestRepository:
    """Uses the server-only PostgREST client, never a browser Supabase client."""

    def __init__(self, client: SupabasePostgrestClient) -> None:
        self._client = client

    async def create(self, request: RideRequestRecord) -> RideRequestRecord:
        row = await self._client.insert("ride_requests", request.model_dump(mode="json"))
        return RideRequestRecord.model_validate(row)

    async def get_owned(self, request_id: UUID, session_id: UUID) -> RideRequestRecord | None:
        row = await self._client.select_one(
            "ride_requests",
            {"id": str(request_id), "session_id": str(session_id)},
        )
        return RideRequestRecord.model_validate(row) if row else None
