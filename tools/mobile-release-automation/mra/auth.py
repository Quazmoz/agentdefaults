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
from . import play_credentials
from . import secrets as secret_provider

PLAY_SCOPES = ("https://www.googleapis.com/auth/androidpublisher",)

ADMOB_READ_SCOPES = (
    "https://www.googleapis.com/auth/admob.readonly",
    "https://www.googleapis.com/auth/admob.report",
)
ADMOB_MONETIZATION_SCOPE = "https://www.googleapis.com/auth/admob.monetization"

PLAY_HINT = (
    "bind the Google Play publisher credential from Bitwarden with "
    "`mra-agent auth bind-play --secret-id <UUID>`"
)
ADMOB_CLIENT_HINT = (
    "in GCP create an OAuth client of type 'Desktop app', download the client JSON, "
    f"and place it at {config.path_for(config.ADMOB_OAUTH_CLIENT)} with chmod 600"
)
REVENUECAT_HINT = (
    "configure the app profile with a Bitwarden Secrets Manager UUID, export "
    "REVENUECAT_V2_SECRET_KEY for an unprofiled invocation, or write a legacy "
    f"fallback key to {config.path_for(config.REVENUECAT_KEY)} with chmod 600"
)


def _authorized_session(credentials):
    from google.auth.transport.requests import AuthorizedSession

    session = AuthorizedSession(credentials)
    session.headers["User-Agent"] = "mobile-release-automation/1.2"
    return session


def play_session():
    """Return an authorized session for the Google Play Developer API."""
    from google.oauth2 import service_account

    credentials = service_account.Credentials.from_service_account_info(
        play_credentials.publisher_info(), scopes=list(PLAY_SCOPES)
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
    """Return the RevenueCat API v2 key for a profile or legacy invocation."""
    if profile and profile.revenuecat_secret_id:
        value = secret_provider.bitwarden_secret(profile.revenuecat_secret_id).strip()
        if not value:
            raise config.ConfigError(
                f"Bitwarden secret for profile {profile.slug!r} is empty"
            )
        return value

    environment_value = os.environ.get("REVENUECAT_V2_SECRET_KEY", "").strip()
    if environment_value:
        return environment_value

    return config.require_file(config.REVENUECAT_KEY, REVENUECAT_HINT).read_text(
        encoding="utf-8"
    ).strip()
