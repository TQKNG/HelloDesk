"""Guest session domain models.

Raw bearer tokens are deliberately excluded from persisted session records.
"""

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Language(StrEnum):
    ENGLISH = "en"
    VIETNAMESE = "vi"


class GuestSessionStatus(StrEnum):
    ACTIVE = "active"
    ENDED = "ended"
    EXPIRED = "expired"


class CreateGuestSessionRequest(BaseModel):
    language: Language


class GuestSessionRecord(BaseModel):
    """The durable portion of a guest session."""

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    token_hash: str
    language: Language
    reservation_id: UUID | None = None
    created_at: datetime
    expires_at: datetime
    status: GuestSessionStatus = GuestSessionStatus.ACTIVE


class GuestSessionResponse(BaseModel):
    """The only response that contains the raw token, at creation time."""

    session_token: str = Field(serialization_alias="sessionToken")
    language: Language
    expires_at: datetime = Field(serialization_alias="expiresAt")
    status: GuestSessionStatus


class GuestSessionStateResponse(BaseModel):
    """Post-creation session state that intentionally excludes the bearer token."""

    language: Language
    expires_at: datetime = Field(serialization_alias="expiresAt")
    status: GuestSessionStatus
