"""Optional Microsoft Agent Framework answer provider with a deterministic fallback."""

from collections.abc import Awaitable, Callable
import inspect
import json
from typing import Protocol

from app.models.guest_session import Language
from app.core.settings import Settings
from app.services.hotel_information_service import HotelInformationService


class HotelAnswerProvider(Protocol):
    async def answer(self, question: str, language: Language) -> str | None: ...


class SyntheticHotelAnswerProvider:
    def __init__(self, information_service: HotelInformationService) -> None:
        self._information_service = information_service

    async def answer(self, question: str, language: Language) -> str | None:
        return self._information_service.answer_question(question, language)


class MicrosoftAgentFrameworkAnswerProvider:
    """Adapter for an injected Microsoft Agent Framework agent.

    The agent is configured by deployment composition, keeping provider packages optional
    for the deterministic local demo and test environment.
    """

    def __init__(self, run_agent: Callable[[str, Language], Awaitable[str | None]]) -> None:
        self._run_agent = run_agent

    async def answer(self, question: str, language: Language) -> str | None:
        return await self._run_agent(question, language)

    @classmethod
    def from_agent_framework_agent(cls, agent: object) -> "MicrosoftAgentFrameworkAnswerProvider":
        """Adapt a configured Microsoft Agent Framework agent without importing it locally."""

        async def run_agent(question: str, language: Language) -> str | None:
            run = getattr(agent, "run", None)
            if not callable(run):
                raise TypeError("The configured Microsoft Agent Framework agent has no run method.")
            result = run(f"Respond in {language.value}. Hotel question: {question}")
            if inspect.isawaitable(result):
                result = await result
            text = getattr(result, "text", result)
            if not isinstance(text, str) or text.strip() == "NO_SUPPORTED_ANSWER":
                return None
            return text

        return cls(run_agent)


class HotelAgent:
    def __init__(self, provider: HotelAnswerProvider) -> None:
        self._provider = provider

    async def answer(self, question: str, language: Language) -> str | None:
        return await self._provider.answer(question, language)


def build_azure_agent_provider(settings: Settings) -> MicrosoftAgentFrameworkAnswerProvider | None:
    """Build the optional Azure-backed Agent Framework provider when configured."""
    if not settings.has_azure_agent_config:
        return None
    try:
        from agent_framework import Agent
        from agent_framework.openai import OpenAIChatClient
    except ImportError:
        return None
    information = HotelInformationService()
    facts = json.dumps(information.facts, ensure_ascii=False)
    chat_client = OpenAIChatClient(
        model=settings.azure_openai_deployment,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
        api_key=settings.azure_openai_api_key.get_secret_value(),
    )
    agent = Agent(
        client=chat_client,
        name="HotelInformationAssistant",
        instructions=(
            "Answer guest questions only using the JSON facts below. "
            "If the facts do not directly answer the question, reply exactly with NO_SUPPORTED_ANSWER. "
            "Do not invent hotel policies, facilities, prices, or services. "
            "Answer in the language requested by the user.\n"
            f"Hotel facts JSON: {facts}"
        ),
    )
    return MicrosoftAgentFrameworkAnswerProvider.from_agent_framework_agent(agent)
