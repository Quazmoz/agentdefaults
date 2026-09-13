"""Authentication for each platform.

Each platform authenticates differently and the differences are load-bearing:

* Google Play  - service account (server-to-server, no human consent).
* AdMob        - OAuth user credentials only. Google documents that "All requests
                 to the AdMob API must be authorized by an authenticated user"
                 and that "No other authorization protocols are supported".
                 A service account will NOT work, regardless of IAM roles.
* RevenueCat   - a v2 secret API key sent as a bearer token. App profiles may
                 reference that key in Bitwarden Secrets Manager by UUID.
"""

from __future__ import annotations

import os
from typing import Sequence

from . import config
from . import secrets as secret_provider

PLAY_SCOPES = ("https://www.googleapis.com/auth/androidpublisher",)

ADMOB_READ_SCOPES = (
    "https://www.googleapis.com/auth/admob.readonly",
    "https://www.googleapis.com/auth/admob.report",
)
ADMOB_MONETIZATION_SCOPE = "https://www.googleapis.com/auth/admob.monetization"

PLAY_HINT = (
    "create a GCP service account, enable the Google Play Android Developer API, "
    "download its JSON key, invite it under Play Console > Users and permissions, "
    f"then place the key at {config.path_for(config.PLAY_SERVICE_ACCOUNT)} with chmod 600"
)
ADMOB_CLIENT_HINT = (
    "in GCP create an OAuth client of type 'Desktop app', download the client JSON, "
    f"and place it at {config.path_for(config.ADMOB_OAUTH_CLIENT)} with chmod 600"
)
REVENUECAT_HINT = (
    "configure the app profile with --revenuecat-secret-id for a Bitwarden Secrets "
    "Manager secret, export REVENUECAT_V2_SECRET_KEY, or write a legacy fallback "
    f"key to {config.path_for(config.REVENUECAT_KEY)} with chmod 600"
)


def _authorized_session(credentials):
    from google.auth.transport.requests import AuthorizedSession

    session = AuthorizedSession(credentials)
    session.headers["User-Agent"] = "mobile-release-automation/1.0"
    return session


def play_session():
    """Return an authorized session for the Google Play Developer API."""
    from google.oauth2 import service_account

    key_path = config.require_file(config.PLAY_SERVICE_ACCOUNT, PLAY_HINT)
    credentials = service_account.Credentials.from_service_account_file(
        str(key_path), scopes=list(PLAY_SCOPES)
    )
    return _authorized_session(credentials)


def admob_scopes(include_monetization: bool = True) -> list[str]:
    scopes = list(ADMOB_READ_SCOPES)
    if include_monetization:
        scopes.append(ADMOB_MONETIZATION_SCOPE)
    return scopes


def admob_session(include_monetization: bool = True, allow_consent: bool = False):
    """Return an authorized session for the AdMob API.

    The first call requires a browser consent from a Google Account that has
    access to the AdMob publisher account. The resulting refresh token is cached
    locally so later calls are non-interactive.
    """
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    scopes = admob_scopes(include_monetization)
    token_path = config.path_for(config.ADMOB_TOKEN)

    credentials = None
    if token_path.is_file():
        config._require_private(token_path)
        credentials = Credentials.from_authorized_user_file(str(token_path), scopes)

    if credentials and credentials.valid:
        return _authorized_session(credentials)

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        _persist_admob_token(credentials)
        return _authorized_session(credentials)

    if not allow_consent:
        raise config.ConfigError(
            "no usable AdMob token cached.\n"
            "  fix: run `mra admob login` once to complete browser consent"
        )

    credentials = _run_admob_consent(scopes)
    _persist_admob_token(credentials)
    return _authorized_session(credentials)


def _run_admob_consent(scopes: Sequence[str]):
    from google_auth_oauthlib.flow import InstalledAppFlow

    client_path = config.require_file(config.ADMOB_OAUTH_CLIENT, ADMOB_CLIENT_HINT)
    flow = InstalledAppFlow.from_client_secrets_file(str(client_path), list(scopes))
    return flow.run_local_server(port=0, prompt="consent")


def _persist_admob_token(credentials) -> None:
    config.ensure_home()
    token_path = config.path_for(config.ADMOB_TOKEN)
    token_path.write_text(credentials.to_json(), encoding="utf-8")
    token_path.chmod(0o600)


def revenuecat_key(profile: config.Profile | None = None) -> str:
    """Return the RevenueCat API v2 secret key for the selected app profile.

    Precedence is intentional:
      1. REVENUECAT_V2_SECRET_KEY for CI/emergency override.
      2. The profile's Bitwarden Secrets Manager UUID.
      3. The legacy owner-only local fallback file.
    """
    environment_value = os.environ.get("REVENUECAT_V2_SECRET_KEY", "").strip()
    if environment_value:
        return environment_value

    if profile and profile.revenuecat_secret_id:
        value = secret_provider.bitwarden_secret(profile.revenuecat_secret_id).strip()
        if not value:
            raise config.ConfigError(
                f"Bitwarden secret for profile {profile.slug!r} is empty"
            )
        return value

    return config.require_file(config.REVENUECAT_KEY, REVENUECAT_HINT).read_text(
        encoding="utf-8"
    ).strip()
