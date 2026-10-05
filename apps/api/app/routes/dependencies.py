"""FastAPI dependencies for authenticated guest sessions and services."""

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import UnauthorizedSessionError
from app.models.guest_session import GuestSessionRecord
from app.services.confirmation_service import ConfirmationService
from app.services.guest_session_service import GuestSessionService
from app.services.voice_session_service import VoiceSessionBroker
from app.services.reservation_service import ReservationService
from app.services.billing_service import BillingService
from app.repositories.ride_request_repository import RideRequestRepository
from app.services.help_action_handler import HelpActionHandler
from app.auth.staff import StaffAuthService
from app.services.hotel_agent import HotelAgent

GUEST_BEARER = HTTPBearer(auto_error=False)


def get_guest_session_service(request: Request) -> GuestSessionService:
    return request.app.state.guest_session_service


def get_confirmation_service(request: Request) -> ConfirmationService:
    return request.app.state.confirmation_service


def get_voice_session_broker(request: Request) -> VoiceSessionBroker:
    return request.app.state.voice_session_broker


def get_reservation_service(request: Request) -> ReservationService:
    return request.app.state.reservation_service


def get_billing_service(request: Request) -> BillingService:
    return request.app.state.billing_service


def get_ride_request_repository(request: Request) -> RideRequestRepository:
    return request.app.state.ride_request_repository

def get_help_action_handler(request: Request) -> HelpActionHandler:
    return request.app.state.help_action_handler

def get_staff_auth_service(request: Request) -> StaffAuthService:
    return request.app.state.staff_auth_service

def get_hotel_agent(request: Request) -> HotelAgent:
    return request.app.state.hotel_agent

async def require_staff_session(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(GUEST_BEARER)],
    auth_service: Annotated[StaffAuthService, Depends(get_staff_auth_service)],
) -> None:
    auth_service.require(credentials.credentials if credentials and credentials.scheme.lower() == "bearer" else None)


async def require_guest_session(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(GUEST_BEARER)],
    service: Annotated[GuestSessionService, Depends(get_guest_session_service)],
) -> GuestSessionRecord:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedSessionError()
    return await service.require_active_session(credentials.credentials)
