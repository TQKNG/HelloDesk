"""Guest-owned simulated ride request models."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class RideRequestStatus(StrEnum):
    PENDING = "pending"
    SIMULATED = "simulated"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RideRequestRecord(BaseModel):
    """Durable, server-owned state for one confirmed simulated ride."""

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    destination_id: str
    destination_label: str
    status: RideRequestStatus
    provider_reference: str | None = None
    created_at: datetime
    updated_at: datetime


class RideRequestResponse(BaseModel):
    id: UUID
    destination_label: str = Field(serialization_alias="destinationLabel")
    status: RideRequestStatus
    created_at: datetime = Field(serialization_alias="createdAt")
