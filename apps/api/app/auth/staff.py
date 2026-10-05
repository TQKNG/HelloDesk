import secrets
from datetime import UTC, datetime, timedelta

from app.core.errors import UnauthorizedSessionError
from app.core.settings import Settings


class StaffAuthService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._tokens: dict[str, datetime] = {}

    def sign_in(self, username: str, password: str) -> tuple[str, datetime]:
        if self._settings.is_production:
            raise UnauthorizedSessionError("Local demo staff sign-in is disabled in production.")
        if not secrets.compare_digest(username, self._settings.staff_demo_username) or not secrets.compare_digest(password, self._settings.staff_demo_password.get_secret_value()):
            raise UnauthorizedSessionError("Invalid local demo staff credentials.")
        expires_at = datetime.now(UTC) + timedelta(hours=8)
        token = secrets.token_urlsafe(32)
        self._tokens[token] = expires_at
        return token, expires_at

    def require(self, token: str | None) -> None:
        if token is None or self._tokens.get(token, datetime.now(UTC)) <= datetime.now(UTC):
            raise UnauthorizedSessionError("A valid staff session is required.")
