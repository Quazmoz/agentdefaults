"""Defensive redaction for any vendor payload or error exposed to an agent.

This is not a substitute for keeping secrets behind the tool boundary. It is a
last-line guard for vendor responses/errors that unexpectedly echo credentials.
"""

from __future__ import annotations

from typing import Any
import re

REDACTED = "<redacted>"

_SENSITIVE_KEYS = {
    "authorization",
    "authorization_header",
    "access_token",
    "refresh_token",
    "id_token",
    "client_secret",
    "private_key",
    "private_key_id",
    "signing_secret",
    "api_key",
    "apikey",
    "password",
}

# Conservative string patterns for the credential formats this toolkit handles.
_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,}\]]+"),
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"\bsk_[A-Za-z0-9._-]{8,}\b"),
    re.compile(r"-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----", re.DOTALL),
    re.compile(
        r'(?i)("(?:access_token|refresh_token|client_secret|private_key|signing_secret|api_key)"\s*:\s*")[^"]*(")'
    ),
    # Same keys in bare key=value form. An OAuth token endpoint echoing its
    # form-encoded request body is the realistic leak shape here, and the
    # JSON-quoted pattern above does not match it.
    re.compile(
        r"(?i)\b((?:access_token|refresh_token|client_secret|private_key|signing_secret|api_key)\s*=\s*)[^\s&,;}\]]+"
    ),
)


def _key_is_sensitive(key: object) -> bool:
    normalized = str(key).strip().lower().replace("-", "_")
    return normalized in _SENSITIVE_KEYS or normalized.endswith("_password")


def redact_text(text: str) -> str:
    value = text
    for pattern in _PATTERNS:
        if pattern.groups >= 2:
            value = pattern.sub(rf"\1{REDACTED}\2", value)
        elif pattern.groups == 1:
            value = pattern.sub(rf"\1{REDACTED}", value)
        else:
            value = pattern.sub(REDACTED, value)
    return value


def redact(value: Any) -> Any:
    """Recursively redact common credential fields while preserving useful shape."""
    if isinstance(value, dict):
        return {
            key: REDACTED if _key_is_sensitive(key) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    if isinstance(value, str):
        return redact_text(value)
    return value
