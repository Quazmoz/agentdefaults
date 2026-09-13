"""AdMob OAuth client configuration backed by Bitwarden Secrets Manager."""

from __future__ import annotations

import json

from . import config, keychain
from . import secrets as secret_provider


def _json_object(value: str, label: str) -> dict:
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as error:
        raise config.ConfigError(f"{label} is not valid JSON") from error
    if not isinstance(payload, dict):
        raise config.ConfigError(f"{label} must contain a JSON object")
    return payload


def oauth_client_json() -> str:
    """Return the AdMob Desktop OAuth client JSON without creating a temp file."""
    refs = config.load_secret_refs()
    if refs.admob_oauth_client_secret_id:
        value = secret_provider.bitwarden_secret(refs.admob_oauth_client_secret_id).strip()
        _json_object(value, "AdMob OAuth client credential")
        return value

    path = config.require_file(
        config.ADMOB_OAUTH_CLIENT,
        "bind the AdMob OAuth client from Bitwarden or configure the legacy local file",
    )
    value = path.read_text(encoding="utf-8")
    _json_object(value, str(path))
    return value


def oauth_client_config() -> dict:
    payload = _json_object(oauth_client_json(), "AdMob OAuth client credential")
    installed = payload.get("installed")
    if not isinstance(installed, dict):
        raise config.ConfigError(
            "AdMob OAuth credential must be a Google Desktop app client JSON with an 'installed' object"
        )
    for field in ("client_id", "client_secret", "token_uri"):
        if not installed.get(field):
            raise config.ConfigError(f"AdMob OAuth client is missing {field!r}")
    return payload


def installed_client_info() -> dict:
    return oauth_client_config()["installed"]


def status() -> dict[str, str]:
    refs = config.load_secret_refs()
    info = installed_client_info()
    token_status = keychain.admob_refresh_token_status()
    return {
        "status": "ready" if token_status["status"] == "ready" else "client-ready",
        "client_source": "bitwarden-secrets-manager"
        if refs.admob_oauth_client_secret_id
        else "legacy-local-file",
        "client_id": str(info.get("client_id", "unknown")),
        "project_id": str(info.get("project_id", "unknown")),
        "refresh_token": token_status["status"],
        "token_source": token_status["source"],
    }
