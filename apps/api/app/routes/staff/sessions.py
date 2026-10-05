"""Local demo staff sign-in route."""

from typing import Annotated
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from app.auth.staff import StaffAuthService
from app.routes.dependencies import get_staff_auth_service

router = APIRouter(tags=["staff-sessions"])

class StaffCredentials(BaseModel):
    username: str
    password: str

@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_staff_session(credentials: StaffCredentials, auth: Annotated[StaffAuthService, Depends(get_staff_auth_service)]) -> dict[str, str]:
    token, expires_at = auth.sign_in(credentials.username, credentials.password)
    return {"sessionToken": token, "expiresAt": expires_at.isoformat()}
