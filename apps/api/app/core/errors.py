"""Consistent public API errors that do not expose provider or internal details."""

from enum import StrEnum

from fastapi import Request
from fastapi.responses import JSONResponse


class ErrorCode(StrEnum):
    INVALID_INPUT = "invalid_input"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    SESSION_EXPIRED = "session_expired"
    ACTION_EXPIRED = "action_expired"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    RATE_LIMITED = "rate_limited"


class ApiError(Exception):
    def __init__(self, code: ErrorCode, message: str, status_code: int) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidInputError(ApiError):
    def __init__(self, message: str = "The request is invalid.") -> None:
        super().__init__(ErrorCode.INVALID_INPUT, message, 400)


class UnauthorizedSessionError(ApiError):
    def __init__(self, message: str = "A valid guest session is required.") -> None:
        super().__init__(ErrorCode.UNAUTHORIZED, message, 401)


class NotFoundError(ApiError):
    def __init__(self, message: str = "The requested resource was not found.") -> None:
        super().__init__(ErrorCode.NOT_FOUND, message, 404)


class ConflictError(ApiError):
    def __init__(self, message: str) -> None:
        super().__init__(ErrorCode.CONFLICT, message, 409)


class SessionExpiredError(ApiError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.SESSION_EXPIRED, "This guest session has expired.", 409)


class ActionExpiredError(ApiError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.ACTION_EXPIRED, "This action has expired.", 409)


class ProviderUnavailableError(ApiError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.PROVIDER_UNAVAILABLE, "The voice provider is temporarily unavailable.", 502)


class RateLimitedError(ApiError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.RATE_LIMITED, "Too many unsuccessful reservation lookups. Try again later.", 429)


async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code.value, "message": exc.message},
    )
