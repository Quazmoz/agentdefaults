"""Local OS credential-store helpers.

The Bitwarden machine token is bootstrapped from macOS Keychain. Dynamic OAuth
refresh tokens also live in the OS credential store rather than local files.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

from . import config

BITWARDEN_TOKEN_ENV = "BWS_ACCESS_TOKEN"
BITWARDEN_KEYCHAIN_SERVICE = "com.quazmoz.mobile-release-automation.bitwarden"
BITWARDEN_KEYCHAIN_ACCOUNT = "mra-machine-account"

ADMOB_KEYCHAIN_SERVICE = "com.quazmoz.mobile-release-automation.admob"
ADMOB_REFRESH_TOKEN_ACCOUNT = "oauth-refresh-token"


def bitwarden_access_token() -> str:
    """Return the BWS access token from an ephemeral env override or macOS Keychain."""
    value = os.environ.get(BITWARDEN_TOKEN_ENV, "").strip()
    if value:
        return value

    if sys.platform != "darwin":
        raise config.ConfigError(
            "BWS_ACCESS_TOKEN is not set and macOS Keychain is unavailable"
        )

    security = shutil.which("security")
    if not security:
        raise config.ConfigError("macOS `security` command was not found")

    result = subprocess.run(
        [
            security,
            "find-generic-password",
            "-a",
            BITWARDEN_KEYCHAIN_ACCOUNT,
            "-s",
            BITWARDEN_KEYCHAIN_SERVICE,
            "-w",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise config.ConfigError(
            "Bitwarden machine-account token is missing from macOS Keychain"
        )
    return result.stdout.strip()


def admob_refresh_token() -> str | None:
    """Return the AdMob OAuth refresh token from the OS credential store."""
    try:
        import keyring
        value = keyring.get_password(ADMOB_KEYCHAIN_SERVICE, ADMOB_REFRESH_TOKEN_ACCOUNT)
    except Exception as error:  # noqa: BLE001 - normalize backend failures
        raise config.ConfigError("could not read the AdMob refresh token from Keychain") from error
    return value.strip() if value and value.strip() else None


def store_admob_refresh_token(value: str) -> None:
    """Persist the AdMob refresh token in the OS credential store."""
    token = value.strip()
    if not token:
        raise config.ConfigError("refusing to store an empty AdMob refresh token")
    try:
        import keyring
        keyring.set_password(ADMOB_KEYCHAIN_SERVICE, ADMOB_REFRESH_TOKEN_ACCOUNT, token)
    except Exception as error:  # noqa: BLE001 - normalize backend failures
        raise config.ConfigError("could not store the AdMob refresh token in Keychain") from error


def admob_refresh_token_status() -> dict[str, str]:
    return {
        "status": "ready" if admob_refresh_token() else "not-authorized",
        "source": "os-keychain",
    }
