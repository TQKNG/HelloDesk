"""Pending-action persistence interface and the Supabase implementation."""

from typing import Protocol
from uuid import UUID

from app.models.pending_action import PendingActionRecord
from app.repositories.supabase_postgrest import SupabasePostgrestClient


class PendingActionRepository(Protocol):
    async def create(self, action: PendingActionRecord) -> PendingActionRecord: ...
    async def get(self, action_id: UUID) -> PendingActionRecord | None: ...
    async def update(self, action: PendingActionRecord) -> PendingActionRecord: ...


class SupabasePendingActionRepository:
    def __init__(self, client: SupabasePostgrestClient) -> None:
        self._client = client

    async def create(self, action: PendingActionRecord) -> PendingActionRecord:
        row = await self._client.insert("pending_actions", action.model_dump(mode="json"))
        return PendingActionRecord.model_validate(row)

    async def get(self, action_id: UUID) -> PendingActionRecord | None:
        row = await self._client.select_one("pending_actions", {"id": str(action_id)})
        return PendingActionRecord.model_validate(row) if row else None

    async def update(self, action: PendingActionRecord) -> PendingActionRecord:
        payload = action.model_dump(mode="json", exclude={"id", "session_id"})
        row = await self._client.update("pending_actions", {"id": str(action.id)}, payload)
        return PendingActionRecord.model_validate(row) if row else action
