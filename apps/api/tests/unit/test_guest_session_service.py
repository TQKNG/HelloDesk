from datetime import UTC, datetime, timedelta

import pytest

from app.core.errors import SessionExpiredError, UnauthorizedSessionError
from app.core.settings import Settings
from app.models.guest_session import CreateGuestSessionRequest, Language
from app.repositories.guest_session_repository import InMemoryGuestSessionRepository
from app.services.guest_session_service import GuestSessionService


@pytest.mark.asyncio
async def test_sessions_are_isolated_by_unique_bearer_token() -> None:
    now = datetime(2026, 10, 4, tzinfo=UTC)
    repository = InMemoryGuestSessionRepository(lambda: now)
    service = GuestSessionService(repository, Settings(), now=lambda: now)
    first = await service.create(CreateGuestSessionRequest(language=Language.ENGLISH))
    second = await service.create(CreateGuestSessionRequest(language=Language.VIETNAMESE))

    first_session = await service.require_active_session(first.session_token)
    second_session = await service.require_active_session(second.session_token)

    assert first_session.id != second_session.id
    assert first_session.language is Language.ENGLISH
    assert second_session.language is Language.VIETNAMESE
    with pytest.raises(UnauthorizedSessionError):
        await service.require_active_session("a-token-from-another-session")


@pytest.mark.asyncio
async def test_expired_session_is_rejected_and_marked_expired() -> None:
    created_at = datetime(2026, 10, 4, tzinfo=UTC)
    clock = [created_at]
    repository = InMemoryGuestSessionRepository(lambda: clock[0])
    service = GuestSessionService(
        repository,
        Settings(guest_session_ttl_seconds=60),
        now=lambda: clock[0],
    )
    response = await service.create(CreateGuestSessionRequest(language=Language.ENGLISH))
    clock[0] = created_at + timedelta(seconds=61)

    with pytest.raises(SessionExpiredError):
        await service.require_active_session(response.session_token)


def test_unsupported_language_is_rejected() -> None:
    with pytest.raises(ValueError):
        CreateGuestSessionRequest.model_validate({"language": "fr"})
