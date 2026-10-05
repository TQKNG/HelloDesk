"""Pending action models for explicit guest confirmation."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class PendingActionKind(StrEnum):
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"
    STAFF_HELP = "staff_help"
    UBER_RIDE = "uber_ride"


class PendingActionStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    FAILED = "failed"


class PrepareActionDetails(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    summary: str | None = Field(default=None, max_length=500)
    destination_id: str | None = Field(default=None, max_length=64, alias="destinationId")


class PrepareActionRequest(BaseModel):
    kind: PendingActionKind
    details: PrepareActionDetails = Field(default_factory=PrepareActionDetails)


class ConfirmActionRequest(BaseModel):
    confirmed: bool


class PendingActionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    kind: PendingActionKind
    summary: str
    details: dict[str, Any]
    status: PendingActionStatus = PendingActionStatus.PENDING
    expires_at: datetime
    request_id: UUID | None = None
    outcome: dict[str, Any] | None = None


class PendingActionResponse(BaseModel):
    action_id: UUID = Field(serialization_alias="actionId")
    kind: PendingActionKind
    summary: str
    status: PendingActionStatus
    expires_at: datetime = Field(serialization_alias="expiresAt")


class ActionOutcome(BaseModel):
    action_id: UUID = Field(serialization_alias="actionId")
    status: str
    message: str
    result: dict[str, Any] | None = None
