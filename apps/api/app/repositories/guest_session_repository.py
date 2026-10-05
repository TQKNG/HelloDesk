"""Guest session persistence seam with a local in-memory implementation."""

from collections.abc import Callable
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.models.guest_session import GuestSessionRecord
from app.repositories.supabase_postgrest import SupabasePostgrestClient


class GuestSessionRepository(Protocol):
    async def create(self, session: GuestSessionRecord) -> GuestSessionRecord: ...
    async def get_by_token_hash(self, token_hash: str) -> GuestSessionRecord | None: ...
    async def get_by_id(self, session_id: UUID) -> GuestSessionRecord | None: ...
    async def update(self, session: GuestSessionRecord) -> GuestSessionRecord: ...


class InMemoryGuestSessionRepository:
    """Local demo repository. Replace through the protocol for Supabase storage."""

    def __init__(self, now: Callable[[], datetime]) -> None:
        self._now = now
        self._sessions_by_id: dict[UUID, GuestSessionRecord] = {}
        self._session_ids_by_token_hash: dict[str, UUID] = {}

    async def create(self, session: GuestSessionRecord) -> GuestSessionRecord:
        self._sessions_by_id[session.id] = session
        self._session_ids_by_token_hash[session.token_hash] = session.id
        return session

    async def get_by_token_hash(self, token_hash: str) -> GuestSessionRecord | None:
        session_id = self._session_ids_by_token_hash.get(token_hash)
        return self._sessions_by_id.get(session_id) if session_id else None

    async def get_by_id(self, session_id: UUID) -> GuestSessionRecord | None:
        return self._sessions_by_id.get(session_id)

    async def update(self, session: GuestSessionRecord) -> GuestSessionRecord:
        self._sessions_by_id[session.id] = session
        return session


class SupabaseGuestSessionRepository:
    """Service-role persistence adapter for `public.guest_sessions`."""

    def __init__(self, client: SupabasePostgrestClient) -> None:
        self._client = client

    async def create(self, session: GuestSessionRecord) -> GuestSessionRecord:
        row = await self._client.insert("guest_sessions", session.model_dump(mode="json"))
        return GuestSessionRecord.model_validate(row)

    async def get_by_token_hash(self, token_hash: str) -> GuestSessionRecord | None:
        row = await self._client.select_one("guest_sessions", {"token_hash": token_hash})
        return GuestSessionRecord.model_validate(row) if row else None

    async def get_by_id(self, session_id: UUID) -> GuestSessionRecord | None:
        row = await self._client.select_one("guest_sessions", {"id": str(session_id)})
        return GuestSessionRecord.model_validate(row) if row else None

    async def update(self, session: GuestSessionRecord) -> GuestSessionRecord:
        payload = session.model_dump(mode="json", exclude={"id", "created_at"})
        row = await self._client.update("guest_sessions", {"id": str(session.id)}, payload)
        return GuestSessionRecord.model_validate(row) if row else session
