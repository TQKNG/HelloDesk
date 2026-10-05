"""Reservation and bill models for synthetic hotel stays."""

from datetime import date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReservationStatus(StrEnum):
    RESERVED = "reserved"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"


class BillStatus(StrEnum):
    OPEN = "open"
    REVIEWED = "reviewed"
    CLOSED = "closed"


class ReservationRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    reservation_code: str
    guest_display_name: str
    arrival_date: date
    departure_date: date
    room_number: str | None = None
    status: ReservationStatus = ReservationStatus.RESERVED
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def check_stay_details(self) -> "ReservationRecord":
        if self.departure_date <= self.arrival_date:
            raise ValueError("Departure must be after arrival.")
        if self.status in {ReservationStatus.CHECKED_IN, ReservationStatus.CHECKED_OUT} and not self.room_number:
            raise ValueError("A checked-in or checked-out reservation needs a room number.")
        return self


class BillItem(BaseModel):
    description: str
    quantity: int = Field(gt=0)
    unit_amount_minor: int = Field(ge=0, serialization_alias="unitAmountMinor")
    line_total_minor: int = Field(ge=0, serialization_alias="lineTotalMinor")

    @model_validator(mode="after")
    def check_line_total(self) -> "BillItem":
        if self.quantity * self.unit_amount_minor != self.line_total_minor:
            raise ValueError("The bill item total must match quantity times unit amount.")
        return self


class BillRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    reservation_id: UUID
    items: tuple[BillItem, ...]
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    total_amount_minor: int = Field(ge=0, serialization_alias="totalAmountMinor")
    status: BillStatus = BillStatus.OPEN
    updated_at: datetime

    @model_validator(mode="after")
    def check_total(self) -> "BillRecord":
        if sum(item.line_total_minor for item in self.items) != self.total_amount_minor:
            raise ValueError("The bill total must equal its line totals.")
        return self


class ReservationLookupRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    reservation_code: str = Field(min_length=4, max_length=32, alias="reservationCode")


class ReservationSummary(BaseModel):
    display_name: str = Field(serialization_alias="displayName")
    arrival_date: date = Field(serialization_alias="arrivalDate")
    departure_date: date = Field(serialization_alias="departureDate")
    status: ReservationStatus
    room_number: str | None = Field(default=None, serialization_alias="roomNumber")


class ReservationLookupResponse(BaseModel):
    lookup_id: UUID = Field(serialization_alias="lookupId")
    reservation: ReservationSummary
    requires_confirmation: bool = Field(default=True, serialization_alias="requiresConfirmation")


class BillResponse(BaseModel):
    items: tuple[BillItem, ...]
    currency: str
    total_amount_minor: int = Field(serialization_alias="totalAmountMinor")
    status: BillStatus
