"""Server-side ride booking port and configured synthetic destinations."""

from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path
from typing import Protocol

from app.core.errors import InvalidInputError
from app.models.guest_session import Language


class RideBookingStatus(StrEnum):
    SIMULATED = "simulated"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"


@dataclass(frozen=True)
class DemoDestination:
    id: str
    labels: dict[Language, str]
    sandbox_dropoff_latitude: float
    sandbox_dropoff_longitude: float

    def label_for(self, language: Language) -> str:
        return self.labels.get(language, self.labels[Language.ENGLISH])


@dataclass(frozen=True)
class RideBookingResult:
    status: RideBookingStatus
    provider_reference: str | None = None


class RideBookingAdapter(Protocol):
    async def book(self, destination: DemoDestination) -> RideBookingResult: ...


class RideBookingService:
    def __init__(self, adapter: RideBookingAdapter, destinations: tuple[DemoDestination, ...]) -> None:
        self._adapter = adapter
        self._destinations = {destination.id: destination for destination in destinations}

    def destination_for(self, destination_id: str) -> DemoDestination:
        destination = self._destinations.get(destination_id)
        if destination is None:
            raise InvalidInputError("Choose one of the configured demo destinations.")
        return destination

    async def book(self, destination_id: str) -> tuple[DemoDestination, RideBookingResult]:
        destination = self.destination_for(destination_id)
        return destination, await self._adapter.book(destination)


def load_demo_destinations() -> tuple[DemoDestination, ...]:
    """Load server-controlled labels that are copied into confirmed ride records."""

    data_path = Path(__file__).parent.parent / "data" / "demo_destinations.json"
    raw_destinations = json.loads(data_path.read_text(encoding="utf-8"))
    return tuple(
        DemoDestination(
            id=raw_destination["id"],
            labels={Language(language): label for language, label in raw_destination["labels"].items()},
            sandbox_dropoff_latitude=raw_destination["sandboxDropoff"]["latitude"],
            sandbox_dropoff_longitude=raw_destination["sandboxDropoff"]["longitude"],
        )
        for raw_destination in raw_destinations
    )
