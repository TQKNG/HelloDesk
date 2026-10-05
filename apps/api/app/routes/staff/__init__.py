"""Staff API router. Authentication and help workflows follow in the staff story."""

from fastapi import APIRouter

from app.routes.staff import help_requests, sessions

router = APIRouter(prefix="/staff")
router.include_router(sessions.router)
router.include_router(help_requests.router)
