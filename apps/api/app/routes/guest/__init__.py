"""Guest API router. Story-specific routes are registered as they are built."""

from fastapi import APIRouter

from app.routes.guest import actions, help, rides, stays

router = APIRouter(prefix="/guest")
router.include_router(actions.router)
router.include_router(stays.router)
router.include_router(help.router)
router.include_router(rides.router)
