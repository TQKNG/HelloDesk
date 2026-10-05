from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from app.models.help_request import HelpRequestRecord, HelpRequestStatus
from app.repositories.supabase_postgrest import SupabasePostgrestClient


class HelpRequestRepository(Protocol):
    async def create(self, request: HelpRequestRecord) -> HelpRequestRecord: ...
    async def get(self, request_id: UUID) -> HelpRequestRecord | None: ...
    async def list(self, status: HelpRequestStatus | None = None) -> list[HelpRequestRecord]: ...
    async def acknowledge(self, request_id: UUID) -> HelpRequestRecord | None: ...


class InMemoryHelpRequestRepository:
    def __init__(self) -> None:
        self._requests: dict[UUID, HelpRequestRecord] = {}

    async def create(self, request: HelpRequestRecord) -> HelpRequestRecord:
        self._requests[request.id] = request
        return request

    async def get(self, request_id: UUID) -> HelpRequestRecord | None:
        return self._requests.get(request_id)

    async def list(self, status: HelpRequestStatus | None = None) -> list[HelpRequestRecord]:
        return [request for request in self._requests.values() if status is None or request.status is status]

    async def acknowledge(self, request_id: UUID) -> HelpRequestRecord | None:
        request = self._requests.get(request_id)
        if request is None:
            return None
        updated = request.model_copy(update={"status": HelpRequestStatus.ACKNOWLEDGED, "acknowledged_at": datetime.now(UTC)})
        self._requests[request_id] = updated
        return updated


class SupabaseHelpRequestRepository:
    def __init__(self, client: SupabasePostgrestClient) -> None:
        self._client = client

    async def create(self, request: HelpRequestRecord) -> HelpRequestRecord:
        row = await self._client.insert("help_requests", request.model_dump(mode="json"))
        return HelpRequestRecord.model_validate(row)

    async def get(self, request_id: UUID) -> HelpRequestRecord | None:
        row = await self._client.select_one("help_requests", {"id": str(request_id)})
        return HelpRequestRecord.model_validate(row) if row else None

    async def list(self, status: HelpRequestStatus | None = None) -> list[HelpRequestRecord]:
        rows = await self._client.select("help_requests", {"status": status.value} if status else None)
        return [HelpRequestRecord.model_validate(row) for row in rows]

    async def acknowledge(self, request_id: UUID) -> HelpRequestRecord | None:
        row = await self._client.update(
            "help_requests",
            {"id": str(request_id), "status": HelpRequestStatus.PENDING.value},
            {"status": HelpRequestStatus.ACKNOWLEDGED.value, "acknowledged_at": datetime.now(UTC).isoformat()},
        )
        return HelpRequestRecord.model_validate(row) if row else None
