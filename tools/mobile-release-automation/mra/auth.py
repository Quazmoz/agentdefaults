"""Authentication for each platform.

Each platform authenticates differently and the differences are load-bearing:

* Google Play  - service account (server-to-server, no human consent).
* AdMob        - OAuth user credentials only. The static Desktop OAuth client is
                 resolved from Bitwarden and the refresh token lives in the OS
                 credential store; no authorized-user JSON is persisted locally.
* RevenueCat   - a v2 secret API key sent as a bearer token. App profiles may
                 reference that key in Bitwarden Secrets Manager by UUID.
"""

from __future__ import annotations

import os
from typing import Sequence

from . import admob_credentials, config, keychain, play_credentials
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
    "store a Google Desktop OAuth client JSON in Bitwarden and bind it with "
    "`mra-agent auth bind-admob --secret-id <UUID>`"
)
REVENUECAT_HINT = (
    "configure the app profile with a Bitwarden Secrets Manager UUID, export "
    "REVENUECAT_V2_SECRET_KEY for an unprofiled invocation, or write a legacy "
    f"fallback key to {config.path_for(config.REVENUECAT_KEY)} with chmod 600"
)


def _authorized_session(credentials):
    from google.auth.transport.requests import AuthorizedSession

    session = AuthorizedSession(credentials)
    session.headers["User-Agent"] = "mobile-release-automation/1.4"
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
    """Return an authorized AdMob session without persisting OAuth JSON files.

    The first call requires browser consent from a Google Account with AdMob
    access. The long-lived refresh token is stored in the OS credential store;
    short-lived access credentials are reconstructed in memory for each process.
    """
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    scopes = admob_scopes(include_monetization)
    client = admob_credentials.installed_client_info()
    refresh_token = keychain.admob_refresh_token()

    if refresh_token:
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri=client["token_uri"],
            client_id=client["client_id"],
            client_secret=client["client_secret"],
            scopes=scopes,
        )
        credentials.refresh(Request())
        if credentials.refresh_token and credentials.refresh_token != refresh_token:
            keychain.store_admob_refresh_token(credentials.refresh_token)
        return _authorized_session(credentials)

    if not allow_consent:
        raise config.ConfigError(
            "AdMob is not authorized yet.\n"
            "  fix: run `mra admob login` once to complete browser consent"
        )

    credentials = _run_admob_consent(scopes)
    if not credentials.refresh_token:
        raise config.ConfigError(
            "Google did not return an AdMob refresh token; revoke the existing OAuth grant "
            "for this client and run `mra admob login` again"
        )
    keychain.store_admob_refresh_token(credentials.refresh_token)
    return _authorized_session(credentials)


def _run_admob_consent(scopes: Sequence[str]):
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_config(
        admob_credentials.oauth_client_config(), list(scopes)
    )
    return flow.run_local_server(
        port=0,
        prompt="consent",
        access_type="offline",
    )


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
