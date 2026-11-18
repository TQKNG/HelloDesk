"""Explicit, single-use confirmation gate for all consequential guest actions."""

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from app.core.errors import ActionExpiredError, ConflictError, InvalidInputError, NotFoundError
from app.core.settings import Settings
from app.models.guest_session import GuestSessionRecord
from app.models.pending_action import (
    ActionOutcome,
    PendingActionKind,
    PendingActionRecord,
    PendingActionResponse,
    PendingActionStatus,
    PrepareActionRequest,
)
from app.repositories.confirmation_repository import PendingActionRepository

ActionHandler = Callable[[PendingActionRecord, GuestSessionRecord], Awaitable[ActionOutcome]]


def utc_now() -> datetime:
    return datetime.now(UTC)


class ConfirmationService:
    """Stores local pending actions until a repository implementation is supplied."""

    def __init__(self, settings: Settings, now: Callable[[], datetime] = utc_now, repository: PendingActionRepository | None = None) -> None:
        self._settings = settings
        self._now = now
        self._actions: dict[UUID, PendingActionRecord] = {}
        self._lock = asyncio.Lock()
        self._handlers: dict[PendingActionKind, ActionHandler] = {}
        self._repository = repository

    def register_handler(self, kind: PendingActionKind, handler: ActionHandler) -> None:
        self._handlers[kind] = handler

    async def prepare(
        self,
        session: GuestSessionRecord,
        request: PrepareActionRequest,
    ) -> PendingActionResponse:
        summary = self._localized_summary(session, request)
        action = PendingActionRecord(
            session_id=session.id,
            kind=request.kind,
            summary=summary,
            details=request.details.model_dump(by_alias=True, exclude_none=True),
            expires_at=self._now() + timedelta(seconds=self._settings.pending_action_ttl_seconds),
        )
        async with self._lock:
            self._actions[action.id] = action
            if self._repository:
                action = await self._repository.create(action)
        return self._response(action)

    async def confirm(
        self,
        session: GuestSessionRecord,
        action_id: UUID,
        request_id: UUID,
        confirmed: bool,
    ) -> ActionOutcome:
        if not confirmed:
            raise InvalidInputError("Guest confirmation must be explicit.")
        async with self._lock:
            action = await self._owned_action(session, action_id)
            self._reject_expired(action)
            if action.request_id is not None:
                if action.request_id != request_id:
                    raise ConflictError("This action has already been submitted.")
                if action.outcome is None:
                    raise ConflictError("This action is already being confirmed.")
                return ActionOutcome.model_validate(action.outcome)
            if action.status is not PendingActionStatus.PENDING:
                raise ConflictError("This action is no longer pending.")
            action = action.model_copy(update={"request_id": request_id})
            self._actions[action.id] = action
            if self._repository:
                action = await self._repository.update(action)

        handler = self._handlers.get(action.kind)
        if handler is None:
            async with self._lock:
                self._actions[action.id] = action.model_copy(update={"status": PendingActionStatus.FAILED})
                if self._repository:
                    await self._repository.update(self._actions[action.id])
            raise ConflictError("This action type is not available.")
        try:
            outcome = await handler(action, session)
        except Exception:
            async with self._lock:
                self._actions[action.id] = action.model_copy(update={"status": PendingActionStatus.FAILED})
                if self._repository:
                    await self._repository.update(self._actions[action.id])
            raise

        async with self._lock:
            confirmed_action = action.model_copy(
                update={
                    "status": PendingActionStatus.CONFIRMED,
                    "outcome": outcome.model_dump(mode="json"),
                }
            )
            self._actions[action.id] = confirmed_action
            if self._repository:
                await self._repository.update(confirmed_action)
        return outcome

    async def cancel(self, session: GuestSessionRecord, action_id: UUID) -> PendingActionResponse:
        async with self._lock:
            action = await self._owned_action(session, action_id)
            self._reject_expired(action)
            if action.status is not PendingActionStatus.PENDING:
                raise ConflictError("This action can no longer be cancelled.")
            action = action.model_copy(update={"status": PendingActionStatus.CANCELLED})
            self._actions[action.id] = action
            if self._repository:
                await self._repository.update(action)
        return self._response(action)

    async def _owned_action(self, session: GuestSessionRecord, action_id: UUID) -> PendingActionRecord:
        action = self._actions.get(action_id)
        if action is None and self._repository:
            action = await self._repository.get(action_id)
        if action is None or action.session_id != session.id:
            raise NotFoundError("The pending action was not found for this guest session.")
        return action

    def _reject_expired(self, action: PendingActionRecord) -> None:
        if action.expires_at > self._now():
            return
        self._actions[action.id] = action.model_copy(update={"status": PendingActionStatus.EXPIRED})
        raise ActionExpiredError()

    @staticmethod
    def _response(action: PendingActionRecord) -> PendingActionResponse:
        return PendingActionResponse(
            action_id=action.id,
            kind=action.kind,
            summary=action.summary,
            status=action.status,
            expires_at=action.expires_at,
        )

    @staticmethod
    def _localized_summary(session: GuestSessionRecord, request: PrepareActionRequest) -> str:
        supplied_summary = request.details.summary
        if request.kind is PendingActionKind.STAFF_HELP:
            if not supplied_summary:
                raise InvalidInputError("A staff-help request needs a summary for review.")
            return supplied_summary
        if request.kind is PendingActionKind.UBER_RIDE:
            if not request.details.destination_id:
                raise InvalidInputError("A ride request needs a configured destination.")
            return supplied_summary or f"Review the simulated ride to {request.details.destination_id}."
        action_name = "Check in" if request.kind is PendingActionKind.CHECK_IN else "Check out"
        if session.language.value == "vi":
            action_name = "Nhận phòng" if request.kind is PendingActionKind.CHECK_IN else "Trả phòng"
        return supplied_summary or f"{action_name}: please confirm this action."
