"""Creation and validation of expiring, bearer-token guest sessions."""

import hashlib
import secrets
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.core.errors import SessionExpiredError, UnauthorizedSessionError
from app.core.settings import Settings
from app.models.guest_session import (
    CreateGuestSessionRequest,
    GuestSessionRecord,
    GuestSessionResponse,
    GuestSessionStatus,
)
from app.repositories.guest_session_repository import GuestSessionRepository


def utc_now() -> datetime:
    return datetime.now(UTC)


class GuestSessionService:
    def __init__(
        self,
        repository: GuestSessionRepository,
        settings: Settings,
        now: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._settings = settings
        self._now = now

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def create(self, request: CreateGuestSessionRequest) -> GuestSessionResponse:
        raw_token = secrets.token_urlsafe(32)
        current_time = self._now()
        session = GuestSessionRecord(
            token_hash=self.hash_token(raw_token),
            language=request.language,
            created_at=current_time,
            expires_at=current_time + timedelta(seconds=self._settings.guest_session_ttl_duration_seconds),
        )
        await self._repository.create(session)
        return GuestSessionResponse(
            session_token=raw_token,
            language=session.language,
            expires_at=session.expires_at,
            status=session.status,
        )

    async def require_active_session(self, token: str) -> GuestSessionRecord:
        session = await self._repository.get_by_token_hash(self.hash_token(token))
        if session is None:
            raise UnauthorizedSessionError()
        if session.status is not GuestSessionStatus.ACTIVE or session.expires_at <= self._now():
            if session.status is GuestSessionStatus.ACTIVE:
                session = session.model_copy(update={"status": GuestSessionStatus.EXPIRED})
                await self._repository.update(session)
            raise SessionExpiredError()
        return session

    async def scope_reservation(self, session_id: UUID, reservation_id: UUID) -> GuestSessionRecord:
        """A future reservation repository calls this only after lookup confirmation."""

        for_token_lookup = getattr(self._repository, "get_by_id", None)
        if for_token_lookup is None:
            raise RuntimeError("The configured guest session repository cannot scope reservations.")
        session = await for_token_lookup(session_id)
        if session is None:
            raise UnauthorizedSessionError()
        updated_session = session.model_copy(update={"reservation_id": reservation_id})
        return await self._repository.update(updated_session)
