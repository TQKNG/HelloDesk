from app.core.errors import NotFoundError
from app.models.guest_session import GuestSessionRecord
from app.models.help_request import HelpRequestRecord, HelpRequestResponse
from app.models.pending_action import ActionOutcome, PendingActionRecord
from app.repositories.help_request_repository import HelpRequestRepository


class HelpActionHandler:
    def __init__(self, repository: HelpRequestRepository) -> None:
        self._repository = repository

    async def handle(self, action: PendingActionRecord, session: GuestSessionRecord) -> ActionOutcome:
        request = await self._repository.create(
            HelpRequestRecord(session_id=session.id, reservation_id=session.reservation_id, summary=action.summary)
        )
        return ActionOutcome(action_id=action.id, status="completed", message="Staff help has been requested.", result={"helpRequestId": str(request.id)})

    async def get_for_guest(self, request_id, session: GuestSessionRecord) -> HelpRequestResponse:
        request = await self._repository.get(request_id)
        if request is None or request.session_id != session.id:
            raise NotFoundError("The help request was not found for this guest session.")
        return HelpRequestResponse.model_validate(request)

    async def list_for_staff(self, status=None) -> list[HelpRequestResponse]:
        return [HelpRequestResponse.model_validate(request) for request in await self._repository.list(status)]

    async def acknowledge(self, request_id) -> HelpRequestResponse:
        request = await self._repository.acknowledge(request_id)
        if request is None:
            raise NotFoundError("The help request was not found.")
        return HelpRequestResponse.model_validate(request)
