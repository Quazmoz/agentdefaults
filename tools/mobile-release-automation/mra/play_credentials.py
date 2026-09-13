"""Google Play credential references backed by Bitwarden Secrets Manager."""

from __future__ import annotations

import json

from . import config
from . import secrets as secret_provider


def _json_object(value: str, label: str) -> dict:
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as error:
        raise config.ConfigError(f"{label} is not valid JSON") from error
    if not isinstance(payload, dict):
        raise config.ConfigError(f"{label} must contain a JSON object")
    return payload


def publisher_json() -> str:
    """Return the Play publisher credential without creating a temporary file."""
    refs = config.load_secret_refs()
    if refs.play_service_account_secret_id:
        value = secret_provider.bitwarden_secret(refs.play_service_account_secret_id).strip()
        _json_object(value, "Google Play publisher credential")
        return value
    path = config.require_file(
        config.PLAY_SERVICE_ACCOUNT,
        "bind the publisher credential from Bitwarden or configure the legacy local file",
    )
    value = path.read_text(encoding="utf-8")
    _json_object(value, str(path))
    return value


def publisher_info() -> dict:
    return _json_object(publisher_json(), "Google Play publisher credential")


def publisher_status() -> dict[str, str]:
    refs = config.load_secret_refs()
    info = publisher_info()
    return {
        "status": "ready",
        "source": "bitwarden-secrets-manager"
        if refs.play_service_account_secret_id
        else "legacy-local-file",
        "client_email": str(info.get("client_email", "unknown")),
    }


def revenuecat_json() -> str:
    """Return the dedicated Play credential that may be handed to RevenueCat."""
    refs = config.load_secret_refs()
    secret_id = refs.revenuecat_play_service_account_secret_id
    if not secret_id:
        raise config.ConfigError(
            "RevenueCat Play credential is not configured; bind its Bitwarden secret UUID first"
        )
    value = secret_provider.bitwarden_secret(secret_id).strip()
    _json_object(value, "RevenueCat Google Play credential")
    return value


def revenuecat_status() -> dict[str, str]:
    refs = config.load_secret_refs()
    if not refs.revenuecat_play_service_account_secret_id:
        return {"status": "not-configured", "source": "bitwarden-secrets-manager"}
    info = _json_object(revenuecat_json(), "RevenueCat Google Play credential")
    return {
        "status": "ready",
        "source": "bitwarden-secrets-manager",
        "client_email": str(info.get("client_email", "unknown")),
    }
