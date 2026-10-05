"""Runtime configuration loaded exclusively from process environment."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    environment: str = Field(default="development", validation_alias="API_ENV")
    api_prefix: str = "/api/v1"
    guest_session_ttl_seconds: int = Field(
        default=900,
        ge=60,
        le=86_400,
        validation_alias="GUEST_SESSION_TTL_SECONDS",
    )
    guest_session_ttl_minutes: int | None = Field(default=None, ge=1, le=1_440, validation_alias="GUEST_SESSION_TTL_MINUTES")
    pending_action_ttl_seconds: int = Field(default=120, ge=15, le=3_600, validation_alias="PENDING_ACTION_TTL_SECONDS")
    cors_origins: str = Field(default="http://localhost:3000", validation_alias="API_CORS_ORIGINS")
    supabase_url: str | None = Field(default=None, validation_alias="SUPABASE_URL")
    supabase_service_role_key: SecretStr | None = Field(default=None, validation_alias="SUPABASE_SERVICE_ROLE_KEY")
    staff_demo_username: str = Field(default="admin", validation_alias="STAFF_DEMO_USERNAME")
    staff_demo_password: SecretStr = Field(default=SecretStr("admin"), validation_alias="STAFF_DEMO_PASSWORD")
    azure_openai_endpoint: str | None = Field(default=None, validation_alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: SecretStr | None = Field(default=None, validation_alias="AZURE_OPENAI_API_KEY")
    azure_openai_deployment: str | None = Field(default=None, validation_alias="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_version: str | None = Field(default=None, validation_alias="AZURE_OPENAI_API_VERSION")
    azure_agent_enabled: bool = Field(default=False, validation_alias="AZURE_AGENT_ENABLED")
    uber_guest_rides_base_url: str = Field(
        default="https://sandbox-api.uber.com",
        validation_alias="UBER_GUEST_RIDES_BASE_URL",
    )
    uber_sandbox_token: SecretStr | None = Field(default=None, validation_alias="UBER_SANDBOX_TOKEN")
    uber_sandbox_parent_product_type_id: str | None = Field(
        default=None,
        validation_alias="UBER_SANDBOX_PARENT_PRODUCT_TYPE_ID",
    )

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def azure_voice_sdp_endpoint(self) -> str | None:
        if not self.azure_openai_endpoint:
            return None
        return f"{self.azure_openai_endpoint.rstrip('/')}/openai/v1/live/sessions"

    @property
    def guest_session_ttl_duration_seconds(self) -> int:
        return self.guest_session_ttl_minutes * 60 if self.guest_session_ttl_minutes is not None else self.guest_session_ttl_seconds

    @property
    def parsed_cors_origins(self) -> tuple[str, ...]:
        return tuple(origin.strip() for origin in self.cors_origins.split(",") if origin.strip())

    @property
    def has_supabase_service_role(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)

    @property
    def has_azure_agent_config(self) -> bool:
        return bool(self.azure_agent_enabled and self.azure_openai_endpoint and self.azure_openai_api_key and self.azure_openai_deployment)

    def redacted_values(self) -> dict[str, str | int | tuple[str, ...] | None]:
        """Expose settings safe to include in startup diagnostics."""

        return {
            "environment": self.environment,
            "api_prefix": self.api_prefix,
            "guest_session_ttl_seconds": self.guest_session_ttl_duration_seconds,
            "pending_action_ttl_seconds": self.pending_action_ttl_seconds,
            "cors_origins": self.parsed_cors_origins,
            "supabase_url": self.supabase_url,
            "supabase_service_role_key": "[configured]" if self.supabase_service_role_key else None,
            "azure_openai_endpoint": self.azure_openai_endpoint,
            "azure_openai_deployment": self.azure_openai_deployment,
            "azure_openai_api_version": self.azure_openai_api_version,
            "azure_openai_api_key": "[configured]" if self.azure_openai_api_key else None,
            "azure_agent_enabled": self.azure_agent_enabled,
            "uber_guest_rides_base_url": self.uber_guest_rides_base_url,
            "uber_sandbox_token": "[configured]" if self.uber_sandbox_token else None,
            "uber_sandbox_parent_product_type_id": self.uber_sandbox_parent_product_type_id,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
