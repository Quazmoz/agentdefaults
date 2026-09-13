"""AdMob API v1beta operations.

Reference: https://developers.google.com/admob/api/reference/rest

Two constraints shape everything here and neither can be engineered around:

1. The AdMob API accepts OAuth user credentials only. Service accounts are not
   supported by any AdMob endpoint.
2. `accounts.apps.create` and `accounts.adUnits.create` are documented as
   limited access: "This method has limited access. If you see a 403 permission
   denied error, please reach out to your account manager for access." That gate
   is applied by Google per AdMob account. Granting yourself the
   `admob.monetization` scope does not lift it.

So creation may legitimately be unavailable. This module reports that state
plainly instead of pretending the call succeeded.
"""

from __future__ import annotations

from typing import Any, Iterator
import json

from . import auth

BASE = "https://admob.googleapis.com/v1beta"
REQUEST_TIMEOUT_SECONDS = 60

AD_FORMATS = (
    "BANNER",
    "INTERSTITIAL",
    "NATIVE",
    "REWARDED",
    "REWARDED_INTERSTITIAL",
    "APP_OPEN",
)
AD_TYPES = ("RICH_MEDIA", "VIDEO")
PLATFORMS = ("ANDROID", "IOS")

LIMITED_ACCESS_EXPLANATION = (
    "AdMob returned 403 for a limited-access method. Per Google's own reference "
    "documentation this method is gated per AdMob account and is unlocked only by "
    "an AdMob account manager. No scope, IAM role, or service account changes this. "
    "Treat AdMob creation as unavailable and use the reviewed manual path."
)


class AdMobError(RuntimeError):
    pass


class AdMobAccessDenied(AdMobError):
    """Raised when AdMob refuses a limited-access method."""


def _raise_for_status(response, action: str) -> None:
    if response.ok:
        return
    try:
        detail = json.dumps(response.json(), indent=2)
    except ValueError:
        detail = response.text
    if response.status_code == 403:
        raise AdMobAccessDenied(
            f"{action} denied with HTTP 403.\n{LIMITED_ACCESS_EXPLANATION}\n{detail}"
        )
    raise AdMobError(f"{action} failed with HTTP {response.status_code}:\n{detail}")


class AdMobClient:
    def __init__(self, publisher_id: str | None = None, session=None) -> None:
        self.session = session or auth.admob_session()
        self._publisher_id = publisher_id

    # ---- plumbing ----------------------------------------------------------

    def _request(self, method: str, path: str, action: str, **kwargs) -> Any:
        kwargs.setdefault("timeout", REQUEST_TIMEOUT_SECONDS)
        response = self.session.request(method, f"{BASE}/{path}", **kwargs)
        _raise_for_status(response, action)
        return response.json() if response.content else {}

    def _paginate(self, path: str, action: str, key: str) -> Iterator[dict]:
        page_token = None
        while True:
            params = {"pageSize": 100}
            if page_token:
                params["pageToken"] = page_token
            payload = self._request("GET", path, action, params=params)
            yield from payload.get(key, [])
            page_token = payload.get("nextPageToken")
            if not page_token:
                return

    # ---- account -----------------------------------------------------------

    def list_accounts(self) -> list[dict]:
        payload = self._request("GET", "accounts", "list AdMob accounts")
        return payload.get("account", [])

    @property
    def publisher_id(self) -> str:
        if self._publisher_id:
            return self._publisher_id
        accounts = self.list_accounts()
        if not accounts:
            raise AdMobError(
                "the authenticated Google Account has no AdMob account. "
                "Re-run `mra admob login` signed in as the AdMob account owner."
            )
        if len(accounts) > 1:
            names = ", ".join(account.get("publisherId", "?") for account in accounts)
            raise AdMobError(f"multiple AdMob accounts visible ({names}); pass --publisher-id")
        self._publisher_id = accounts[0]["publisherId"]
        return self._publisher_id

    # ---- inventory ---------------------------------------------------------

    def list_apps(self) -> list[dict]:
        return list(
            self._paginate(f"accounts/{self.publisher_id}/apps", "list apps", "apps")
        )

    def list_ad_units(self) -> list[dict]:
        return list(
            self._paginate(
                f"accounts/{self.publisher_id}/adUnits", "list ad units", "adUnits"
            )
        )

    def create_app(
        self, display_name: str, platform: str, app_store_id: str | None = None
    ) -> dict:
        """Create an AdMob app. Limited access: may return 403.

        Passing app_store_id links the AdMob app to the published store listing
        (the Play package name for Android). Without it the app is created as a
        manual, unlinked entry.
        """
        if platform not in PLATFORMS:
            raise AdMobError(f"invalid platform {platform!r}; expected one of {PLATFORMS}")
        body: dict[str, Any] = {"platform": platform}
        if app_store_id:
            body["linkedAppInfo"] = {"appStoreId": app_store_id, "displayName": display_name}
        else:
            body["manualAppInfo"] = {"displayName": display_name}
        return self._request(
            "POST", f"accounts/{self.publisher_id}/apps", "create AdMob app", json=body
        )

    def create_ad_unit(
        self,
        app_id: str,
        display_name: str,
        ad_format: str,
        ad_types: list[str] | None = None,
    ) -> dict:
        """Create an ad unit. Limited access: may return 403."""
        if ad_format not in AD_FORMATS:
            raise AdMobError(f"invalid ad format {ad_format!r}; expected one of {AD_FORMATS}")
        for ad_type in ad_types or []:
            if ad_type not in AD_TYPES:
                raise AdMobError(f"invalid ad type {ad_type!r}; expected one of {AD_TYPES}")
        body: dict[str, Any] = {
            "appId": app_id,
            "displayName": display_name,
            "adFormat": ad_format,
        }
        if ad_types:
            body["adTypes"] = ad_types
        return self._request(
            "POST",
            f"accounts/{self.publisher_id}/adUnits",
            "create AdMob ad unit",
            json=body,
        )

    # ---- access probe ------------------------------------------------------

    def probe_monetization_access(self) -> dict:
        """Test monetization access without creating anything.

        `mediationGroups.list` requires the same `admob.monetization` scope as the
        create methods and mutates nothing, so it is the safest available signal.
        It is an indicator, not a guarantee: the create methods carry their own
        per-account gate and can still return 403 after this probe succeeds.
        """
        result: dict[str, Any] = {"publisher_id": None, "probe": "mediationGroups.list"}
        try:
            result["publisher_id"] = self.publisher_id
        except AdMobError as error:
            result["monetization_access"] = "unknown"
            result["detail"] = str(error)
            return result

        try:
            self._request(
                "GET",
                f"accounts/{result['publisher_id']}/mediationGroups",
                "probe mediation groups",
                params={"pageSize": 1},
            )
        except AdMobAccessDenied as error:
            result["monetization_access"] = "denied"
            result["detail"] = str(error)
            return result
        except AdMobError as error:
            result["monetization_access"] = "unknown"
            result["detail"] = str(error)
            return result

        result["monetization_access"] = "likely"
        result["detail"] = (
            "The monetization scope is accepted for this account. Creation is still "
            "separately gated; confirm with one real create before relying on it."
        )
        return result
