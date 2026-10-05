"""FastAPI application assembly for the server-only hotel API."""

from datetime import timedelta

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.errors import ApiError, api_error_handler
from app.core.logging import get_logger
from app.core.settings import Settings, get_settings
from app.repositories.guest_session_repository import InMemoryGuestSessionRepository
from app.repositories.bill_repository import InMemoryBillRepository
from app.repositories.reservation_repository import InMemoryReservationRepository
from app.repositories.guest_session_repository import SupabaseGuestSessionRepository
from app.repositories.supabase_postgrest import SupabasePostgrestClient
from app.repositories.supabase_stay_repositories import SupabaseBillRepository, SupabaseReservationRepository
from app.repositories.confirmation_repository import SupabasePendingActionRepository
from app.routes import guest_sessions, voice
from app.routes.guest import router as guest_router
from app.routes.staff import router as staff_router
from app.services.confirmation_service import ConfirmationService
from app.services.guest_session_service import GuestSessionService, utc_now
from app.services.billing_service import BillingService
from app.services.reservation_service import ReservationService
from app.services.stay_action_handler import StayActionHandler
from app.services.voice_session_service import AzureVoiceSessionService, VoiceSessionBroker
from app.models.pending_action import PendingActionKind
from app.models.reservation import BillItem, BillRecord, ReservationRecord, ReservationStatus
from app.repositories.help_request_repository import InMemoryHelpRequestRepository, SupabaseHelpRequestRepository
from app.services.help_action_handler import HelpActionHandler
from app.auth.staff import StaffAuthService
from app.adapters.fake_ride_booking import FakeRideBookingAdapter
from app.adapters.uber_guest_rides_sandbox import UberGuestRidesSandboxAdapter
from app.repositories.ride_request_repository import InMemoryRideRequestRepository, SupabaseRideRequestRepository
from app.services.ride_action_handler import RideActionHandler
from app.services.ride_booking_service import RideBookingService, load_demo_destinations
from app.services.hotel_agent import HotelAgent, HotelAnswerProvider, SyntheticHotelAnswerProvider, build_azure_agent_provider
from app.services.hotel_information_service import HotelInformationService


def create_app(
    settings: Settings | None = None,
    voice_session_broker: VoiceSessionBroker | None = None,
    hotel_answer_provider: HotelAnswerProvider | None = None,
) -> FastAPI:
    runtime_settings = settings or get_settings()
    app = FastAPI(title="Hotel Voice Receptionist API", version="1.0.0")
    logger = get_logger(__name__)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(runtime_settings.parsed_cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    )
    app.add_exception_handler(ApiError, api_error_handler)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_, __: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"code": "invalid_input", "message": "The request is invalid."},
        )

    now = utc_now()
    today = now.date()
    guest_session_repository = InMemoryGuestSessionRepository(utc_now)
    checked_in_reservation = ReservationRecord(
        reservation_code="DEMO-CHECKED-IN",
        guest_display_name="Jordan Demo",
        arrival_date=today - timedelta(days=1),
        departure_date=today + timedelta(days=1),
        room_number="303",
        status=ReservationStatus.CHECKED_IN,
        created_at=now,
        updated_at=now,
    )
    reservation_repository = InMemoryReservationRepository(
        [
            ReservationRecord(
                reservation_code="DEMO-EN-1001",
                guest_display_name="Alex Demo",
                arrival_date=today,
                departure_date=today + timedelta(days=2),
                room_number="101",
                status=ReservationStatus.RESERVED,
                created_at=now,
                updated_at=now,
            ),
            checked_in_reservation,
        ],
        utc_now,
    )
    bill_repository = InMemoryBillRepository(
        [
            BillRecord(
                reservation_id=checked_in_reservation.id,
                items=(BillItem(description="Demo room night", quantity=1, unit_amount_minor=12500, line_total_minor=12500),),
                currency="CAD",
                total_amount_minor=12500,
                updated_at=now,
            )
        ],
        utc_now,
    )
    ride_request_repository = InMemoryRideRequestRepository()
    help_request_repository = InMemoryHelpRequestRepository()
    pending_action_repository = None
    if runtime_settings.has_supabase_service_role:
        postgrest_client = SupabasePostgrestClient(runtime_settings)
        guest_session_repository = SupabaseGuestSessionRepository(postgrest_client)
        reservation_repository = SupabaseReservationRepository(postgrest_client)
        bill_repository = SupabaseBillRepository(postgrest_client)
        pending_action_repository = SupabasePendingActionRepository(postgrest_client)
        ride_request_repository = SupabaseRideRequestRepository(postgrest_client)
        help_request_repository = SupabaseHelpRequestRepository(postgrest_client)
    guest_session_service = GuestSessionService(guest_session_repository, runtime_settings)
    reservation_service = ReservationService(reservation_repository, guest_session_service)
    billing_service = BillingService(bill_repository, reservation_service)
    app.state.guest_session_service = guest_session_service
    app.state.reservation_service = reservation_service
    app.state.billing_service = billing_service
    app.state.confirmation_service = ConfirmationService(runtime_settings, repository=pending_action_repository)
    stay_action_handler = StayActionHandler(reservation_repository, bill_repository, reservation_service)
    app.state.confirmation_service.register_handler(PendingActionKind.CHECK_IN, stay_action_handler.handle)
    app.state.confirmation_service.register_handler(PendingActionKind.CHECK_OUT, stay_action_handler.handle)
    app.state.help_action_handler = HelpActionHandler(help_request_repository)
    app.state.confirmation_service.register_handler(PendingActionKind.STAFF_HELP, app.state.help_action_handler.handle)
    app.state.staff_auth_service = StaffAuthService(runtime_settings)
    agent_provider = hotel_answer_provider or build_azure_agent_provider(runtime_settings)
    app.state.hotel_agent = HotelAgent(agent_provider or SyntheticHotelAnswerProvider(HotelInformationService()))
    ride_booking_adapter = FakeRideBookingAdapter()
    if runtime_settings.uber_sandbox_token and runtime_settings.uber_sandbox_parent_product_type_id:
        ride_booking_adapter = UberGuestRidesSandboxAdapter(runtime_settings)
    ride_booking_service = RideBookingService(ride_booking_adapter, load_demo_destinations())
    app.state.ride_request_repository = ride_request_repository
    app.state.confirmation_service.register_handler(
        PendingActionKind.UBER_RIDE,
        RideActionHandler(ride_request_repository, ride_booking_service).handle,
    )
    app.state.voice_session_broker = voice_session_broker or AzureVoiceSessionService(runtime_settings)

    app.include_router(guest_sessions.router, prefix=runtime_settings.api_prefix)
    app.include_router(guest_router, prefix=runtime_settings.api_prefix)
    app.include_router(voice.router, prefix=runtime_settings.api_prefix)
    app.include_router(staff_router, prefix=runtime_settings.api_prefix)

    logger.info("API configured", extra={"settings": runtime_settings.redacted_values()})
    return app


app = create_app()
