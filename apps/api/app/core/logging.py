"""Structured logging with defensive redaction for voice and secret data."""

import logging
from collections.abc import Mapping
import re
from typing import Any

SENSITIVE_KEYS = frozenset(
    {
        "authorization",
        "token",
        "session_token",
        "api_key",
        "client_secret",
        "secret",
        "password",
        "audio",
        "sdp",
        "transcript",
        "provider_reference",
    }
)
REDACTED = "[redacted]"


def redact_value(value: Any, key: str | None = None) -> Any:
    """Return a recursively safe representation suitable for logs."""

    if key:
        normalized_key = re.sub(r"[^a-z0-9]", "", key.lower())
        normalized_sensitive_keys = {re.sub(r"[^a-z0-9]", "", item) for item in SENSITIVE_KEYS}
        if any(sensitive_key in normalized_key for sensitive_key in normalized_sensitive_keys):
            return REDACTED
    if isinstance(value, Mapping):
        return {item_key: redact_value(item_value, item_key) for item_key, item_value in value.items()}
    if isinstance(value, list | tuple):
        return [redact_value(item) for item in value]
    return value


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
