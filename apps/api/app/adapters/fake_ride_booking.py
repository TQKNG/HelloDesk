"""Deterministic local adapter for ride-flow tests and credential-free demos."""

from uuid import NAMESPACE_URL, uuid5

from app.services.ride_booking_service import DemoDestination, RideBookingResult, RideBookingStatus


class FakeRideBookingAdapter:
    async def book(self, destination: DemoDestination) -> RideBookingResult:
        reference = uuid5(NAMESPACE_URL, f"hellodesk:simulated-ride:{destination.id}")
        return RideBookingResult(
            status=RideBookingStatus.SIMULATED,
            provider_reference=f"fake-sandbox-{reference}",
        )
