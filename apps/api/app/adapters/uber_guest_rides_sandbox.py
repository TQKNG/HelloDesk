"""Uber Guest Rides sandbox adapter that rejects every non-sandbox endpoint."""

from urllib.parse import urlparse

import httpx

from app.core.settings import Settings
from app.services.ride_booking_service import DemoDestination, RideBookingResult, RideBookingStatus

SANDBOX_HOST = "sandbox-api.uber.com"
SANDBOX_RUN_PATH = "/v1/guests/sandbox/run"
SANDBOX_PICKUP = {"latitude": 37.766192, "longitude": -122.400745}


class UberGuestRidesSandboxAdapter:
    """Creates an ephemeral sandbox run after confirmation and never dispatches a live trip."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        parsed_url = urlparse(settings.uber_guest_rides_base_url)
        if parsed_url.scheme != "https" or parsed_url.hostname != SANDBOX_HOST:
            raise ValueError("Uber Guest Rides must use the HTTPS sandbox endpoint.")
        self._base_url = settings.uber_guest_rides_base_url.rstrip("/")
        self._token = settings.uber_sandbox_token
        self._parent_product_type_id = settings.uber_sandbox_parent_product_type_id
        self._client = client

    async def book(self, _destination: DemoDestination) -> RideBookingResult:
        if self._token is None or not self._parent_product_type_id:
            return RideBookingResult(status=RideBookingStatus.UNAVAILABLE)

        headers = {
            "Authorization": f"Bearer {self._token.get_secret_value()}",
            "Content-Type": "application/json",
        }
        payload = {
            "driver_locations": [{}],
            "pickup_location": SANDBOX_PICKUP,
            "dropoff_location": {
                "latitude": _destination.sandbox_dropoff_latitude,
                "longitude": _destination.sandbox_dropoff_longitude,
            },
            "parent_product_type_id": self._parent_product_type_id,
            "preferences": {"auto_accept_trip": True},
        }
        try:
            if self._client is not None:
                response = await self._client.post(f"{self._base_url}{SANDBOX_RUN_PATH}", headers=headers, json=payload)
            else:
                async with httpx.AsyncClient(timeout=20) as client:
                    response = await client.post(f"{self._base_url}{SANDBOX_RUN_PATH}", headers=headers, json=payload)
            if response.status_code in {401, 403}:
                return RideBookingResult(status=RideBookingStatus.UNAVAILABLE)
            response.raise_for_status()
        except httpx.HTTPError:
            return RideBookingResult(status=RideBookingStatus.FAILED)

        run_id = response.json().get("run_id")
        if not isinstance(run_id, str) or not run_id:
            return RideBookingResult(status=RideBookingStatus.FAILED)
        return RideBookingResult(status=RideBookingStatus.SIMULATED, provider_reference=run_id)
