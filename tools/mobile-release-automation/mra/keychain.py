"""Local OS credential-store helpers.

Only the Bitwarden Secrets Manager machine-account access token is bootstrapped
from the OS keychain. Vendor credentials remain in Bitwarden itself.
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
