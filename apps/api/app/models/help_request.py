from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class HelpRequestStatus(StrEnum):
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"


class HelpRequestRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    reservation_id: UUID | None = None
    summary: str = Field(min_length=1, max_length=500)
    status: HelpRequestStatus = HelpRequestStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    acknowledged_at: datetime | None = None


class HelpRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    summary: str
    status: HelpRequestStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    acknowledged_at: datetime | None = Field(default=None, serialization_alias="acknowledgedAt")


class HotelQuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class HotelQuestionResponse(BaseModel):
    answer: str | None = None
    needs_staff_help: bool = Field(serialization_alias="needsStaffHelp")
