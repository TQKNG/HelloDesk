import pytest

from app.auth.staff import StaffAuthService
from app.core.errors import UnauthorizedSessionError
from app.core.settings import Settings


def test_local_demo_staff_sign_in_is_disabled_in_production() -> None:
    service = StaffAuthService(Settings(environment="production"))
    with pytest.raises(UnauthorizedSessionError):
        service.sign_in("admin", "admin")
