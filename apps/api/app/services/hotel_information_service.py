"""Safe read-only answers from configured synthetic hotel facts."""

import json
from pathlib import Path

from app.models.guest_session import Language


class HotelInformationService:
    def __init__(self, source: Path | None = None) -> None:
        path = source or Path(__file__).parent.parent / "data" / "hotel_information.json"
        self._facts: dict[str, dict[str, str]] = json.loads(path.read_text())

    @property
    def facts(self) -> dict[str, dict[str, str]]:
        return self._facts.copy()

    def answer(self, topic: str, language: Language) -> str | None:
        fact = self._facts.get(topic.strip().lower())
        return fact.get(language.value) if fact else None

    def answer_question(self, question: str, language: Language) -> str | None:
        normalized_question = question.lower()
        for topic in self._facts:
            if topic.replace("_", " ") in normalized_question:
                return self.answer(topic, language)
        return None
