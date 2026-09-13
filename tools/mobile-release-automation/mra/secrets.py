"""External secret provider integrations.

Profiles contain only immutable secret references. Secret values are retrieved at
runtime and returned directly to the caller; this module never prints them.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid

from . import config, keychain

BWS_ACCESS_TOKEN_ENV = "BWS_ACCESS_TOKEN"
BWS_BINARY_ENV = "MRA_BWS_BIN"


class SecretProviderError(config.ConfigError):
    """Raised when an external secret provider cannot satisfy a request."""


def _bws_binary() -> str:
    configured = os.environ.get(BWS_BINARY_ENV, "").strip()
    if configured:
        return configured
    discovered = shutil.which("bws")
    if not discovered:
        raise SecretProviderError(
            "Bitwarden Secrets Manager CLI (`bws`) is not installed or not on PATH"
        )
    return discovered


def bitwarden_status() -> dict[str, str]:
    """Check Bitwarden bootstrap prerequisites without retrieving a vault secret."""
    binary = _bws_binary()
    keychain.bitwarden_access_token()
    source = "environment" if os.environ.get(BWS_ACCESS_TOKEN_ENV, "").strip() else "macOS-keychain"
    return {
        "provider": "bitwarden-secrets-manager",
        "status": "ready",
        "bws": binary,
        "token_source": source,
    }


def bitwarden_secret(secret_id: str) -> str:
    """Retrieve exactly one Bitwarden Secrets Manager secret by UUID."""
    try:
        normalized_id = str(uuid.UUID(secret_id))
    except (ValueError, AttributeError) as error:
        raise SecretProviderError(
            f"invalid Bitwarden secret id {secret_id!r}; expected a UUID"
        ) from error

    access_token = keychain.bitwarden_access_token()
    child_environment = os.environ.copy()
    child_environment[BWS_ACCESS_TOKEN_ENV] = access_token

    result = subprocess.run(
        [_bws_binary(), "secret", "get", normalized_id, "--output", "json"],
        capture_output=True,
        text=True,
        env=child_environment,
        check=False,
    )
    if result.returncode != 0:
        raise SecretProviderError(
            f"Bitwarden could not retrieve secret {normalized_id}; "
            "check the secret id and machine-account read access"
        )

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise SecretProviderError(
            f"Bitwarden returned invalid JSON for secret {normalized_id}"
        ) from error

    if isinstance(payload, list):
        if len(payload) != 1:
            raise SecretProviderError(
                f"Bitwarden returned {len(payload)} objects for secret {normalized_id}"
            )
        payload = payload[0]

    value = payload.get("value") if isinstance(payload, dict) else None
    if not isinstance(value, str):
        raise SecretProviderError(
            f"Bitwarden response for secret {normalized_id} had no string value"
        )
    return value
