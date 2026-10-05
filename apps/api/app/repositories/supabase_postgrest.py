"""Small server-only PostgREST client used by production repository adapters."""

from typing import Any

import httpx

from app.core.errors import ProviderUnavailableError
from app.core.settings import Settings


class SupabasePostgrestClient:
    """Uses only the server service-role key and never exposes it to a route response."""

    def __init__(self, settings: Settings) -> None:
        if not settings.has_supabase_service_role:
            raise ValueError("Supabase server credentials are required.")
        self._base_url = f"{settings.supabase_url.rstrip('/')}/rest/v1"
        secret = settings.supabase_service_role_key.get_secret_value()
        self._headers = {"apikey": secret, "Authorization": f"Bearer {secret}"}

    async def select_one(self, table: str, filters: dict[str, str]) -> dict[str, Any] | None:
        result = await self._request("GET", table, params={key: f"eq.{value}" for key, value in filters.items()})
        return result[0] if result else None

    async def select(self, table: str, filters: dict[str, str] | None = None) -> list[dict[str, Any]]:
        params = {key: f"eq.{value}" for key, value in (filters or {}).items()}
        return await self._request("GET", table, params=params)

    async def insert(self, table: str, payload: dict[str, Any]) -> dict[str, Any]:
        result = await self._request("POST", table, json=payload, prefer="return=representation")
        return result[0]

    async def update(self, table: str, filters: dict[str, str], payload: dict[str, Any]) -> dict[str, Any] | None:
        result = await self._request(
            "PATCH",
            table,
            params={key: f"eq.{value}" for key, value in filters.items()},
            json=payload,
            prefer="return=representation",
        )
        return result[0] if result else None

    async def _request(self, method: str, table: str, **kwargs: Any) -> list[dict[str, Any]]:
        headers = {**self._headers, "Accept": "application/json"}
        if prefer := kwargs.pop("prefer", None):
            headers["Prefer"] = prefer
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.request(method, f"{self._base_url}/{table}", headers=headers, **kwargs)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError() from exc
        return response.json() if response.content else []
