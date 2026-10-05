import json

import httpx
import pytest
from pydantic import SecretStr

from app.adapters.fake_ride_booking import FakeRideBookingAdapter
from app.adapters.uber_guest_rides_sandbox import SANDBOX_RUN_PATH, UberGuestRidesSandboxAdapter
from app.core.settings import Settings
from app.models.guest_session import Language
from app.services.ride_booking_service import DemoDestination, RideBookingStatus


DESTINATION = DemoDestination(
    id="demo-union-square",
    labels={Language.ENGLISH: "Union Square, San Francisco", Language.VIETNAMESE: "Quảng trường Union, San Francisco"},
    sandbox_dropoff_latitude=37.75203,
    sandbox_dropoff_longitude=-122.422065,
)


@pytest.mark.asyncio
async def test_fake_adapter_returns_a_deterministic_simulated_outcome() -> None:
    adapter = FakeRideBookingAdapter()

    first = await adapter.book(DESTINATION)
    second = await adapter.book(DESTINATION)

    assert first.status is RideBookingStatus.SIMULATED
    assert first.provider_reference == second.provider_reference
    assert first.provider_reference is not None
    assert first.provider_reference.startswith("fake-sandbox-")


@pytest.mark.asyncio
async def test_sandbox_adapter_reports_unavailable_without_sandbox_configuration() -> None:
    adapter = UberGuestRidesSandboxAdapter(Settings())

    result = await adapter.book(DESTINATION)

    assert result.status is RideBookingStatus.UNAVAILABLE
    assert result.provider_reference is None


def test_sandbox_adapter_rejects_the_uber_production_host() -> None:
    with pytest.raises(ValueError, match="sandbox endpoint"):
        UberGuestRidesSandboxAdapter(
            Settings(
                uber_guest_rides_base_url="https://api.uber.com",
                uber_sandbox_token=SecretStr("sandbox-token"),
                uber_sandbox_parent_product_type_id="sandbox-product",
            )
        )


@pytest.mark.asyncio
async def test_sandbox_adapter_calls_only_the_sandbox_run_endpoint() -> None:
    observed: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed["url"] = str(request.url)
        observed["authorization"] = request.headers["Authorization"]
        observed["body"] = json.loads(request.content)
        return httpx.Response(201, json={"run_id": "sandbox-run-id"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = UberGuestRidesSandboxAdapter(
            Settings(
                uber_sandbox_token=SecretStr("sandbox-token"),
                uber_sandbox_parent_product_type_id="sandbox-product",
            ),
            client=client,
        )
        result = await adapter.book(DESTINATION)

    assert result.status is RideBookingStatus.SIMULATED
    assert result.provider_reference == "sandbox-run-id"
    assert observed["url"] == f"https://sandbox-api.uber.com{SANDBOX_RUN_PATH}"
    assert observed["authorization"] == "Bearer sandbox-token"
    assert observed["body"] == {
        "driver_locations": [{}],
        "pickup_location": {"latitude": 37.766192, "longitude": -122.400745},
        "dropoff_location": {"latitude": 37.75203, "longitude": -122.422065},
        "parent_product_type_id": "sandbox-product",
        "preferences": {"auto_accept_trip": True},
    }
