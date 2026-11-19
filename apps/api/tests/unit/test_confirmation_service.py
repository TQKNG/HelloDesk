from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.core.errors import ActionExpiredError, ConflictError, InvalidInputError
from app.core.settings import Settings
from app.models.guest_session import GuestSessionRecord, Language
from app.models.pending_action import ActionOutcome, PendingActionKind, PrepareActionRequest
from app.services.confirmation_service import ConfirmationService


def active_session(now: datetime) -> GuestSessionRecord:
    return GuestSessionRecord(
        token_hash="hash",
        language=Language.ENGLISH,
        created_at=now,
        expires_at=now + timedelta(minutes=15),
    )


@pytest.mark.asyncio
async def test_pending_action_requires_explicit_confirmation() -> None:
    now = datetime(2026, 10, 4, tzinfo=UTC)
    service = ConfirmationService(Settings(), now=lambda: now)
    session = active_session(now)
    action = await service.prepare(session, PrepareActionRequest(kind=PendingActionKind.CHECK_IN))

    with pytest.raises(InvalidInputError):
        await service.confirm(session, action.action_id, uuid4(), confirmed=False)


@pytest.mark.asyncio
async def test_confirmation_is_idempotent_but_cannot_be_replayed_with_another_key() -> None:
    now = datetime(2026, 10, 4, tzinfo=UTC)
    service = ConfirmationService(Settings(), now=lambda: now)

    async def handle_check_in(action, _session):
        return ActionOutcome(action_id=action.id, status="completed", message="Check-in complete.")

    service.register_handler(PendingActionKind.CHECK_IN, handle_check_in)
    session = active_session(now)
    action = await service.prepare(session, PrepareActionRequest(kind=PendingActionKind.CHECK_IN))
    request_id = uuid4()

    first = await service.confirm(session, action.action_id, request_id, confirmed=True)
    repeated = await service.confirm(session, action.action_id, request_id, confirmed=True)

    assert repeated == first
    with pytest.raises(ConflictError):
        await service.confirm(session, action.action_id, uuid4(), confirmed=True)


@pytest.mark.asyncio
async def test_expired_action_cannot_be_confirmed() -> None:
    created_at = datetime(2026, 10, 4, tzinfo=UTC)
    clock = [created_at]
    service = ConfirmationService(Settings(pending_action_ttl_seconds=15), now=lambda: clock[0])
    session = active_session(created_at)
    action = await service.prepare(session, PrepareActionRequest(kind=PendingActionKind.CHECK_IN))
    clock[0] = created_at + timedelta(seconds=16)

    with pytest.raises(ActionExpiredError):
        await service.confirm(session, action.action_id, uuid4(), confirmed=True)
