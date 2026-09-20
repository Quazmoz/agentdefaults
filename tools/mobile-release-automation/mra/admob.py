"""AdMob API operations with capability-aware access handling.

References:
- https://developers.google.com/admob/api/reference/rest
- https://developers.google.com/admob/api/reference/rest/v1/accounts.networkReport/generate
- https://developers.google.com/admob/api/reference/rest/v1/accounts.mediationReport/generate

AdMob has two materially different API surfaces:

* read/reporting operations that are broadly available with normal OAuth grants;
* v1beta monetization mutations and some mediation reads that are limited-access
  per AdMob account.

The module never treats every HTTP 403 as an allowlist failure. Limited-access
errors are raised only for endpoints Google explicitly documents as gated; other
401/403 responses remain authentication/permission errors so agents can diagnose
revoked grants, missing scopes, the wrong account, or disabled API access.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Iterator
import json

from . import auth

BETA_BASE = "https://admob.googleapis.com/v1beta"
V1_BASE = "https://admob.googleapis.com/v1"
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
    "AdMob returned 403 for a limited-access method. Google's reference "
    "documentation says this capability is enabled per AdMob account and a "
    "publisher must contact its AdMob account manager for access. OAuth scopes, "
    "IAM roles, and service accounts do not bypass this account gate."
)


class AdMobError(RuntimeError):
    pass


class AdMobConfigurationError(AdMobError):
    """Local MRA profile/credential configuration is missing or unusable.

    AdMob was never contacted. This is an operator-fixable setup mistake, not a
    vendor response, and it must not be reported as an AdMob permission problem.
    """


class AdMobAuthenticationError(AdMobError):
    """The OAuth credential was rejected or is no longer usable."""


class AdMobPermissionDenied(AdMobError):
    """The credential is authenticated but lacks permission/scope/access."""


class AdMobAccessDenied(AdMobPermissionDenied):
    """A Google-documented limited-access AdMob method is not enabled."""


def _response_detail(response) -> str:
    try:
        return json.dumps(response.json(), indent=2)
    except ValueError:
        return response.text


def _raise_for_status(response, action: str, *, limited_access: bool = False) -> None:
    if response.ok:
        return
    detail = _response_detail(response)
    if response.status_code == 401:
        raise AdMobAuthenticationError(
            f"{action} failed with HTTP 401. Re-authorize AdMob OAuth and retry.\n{detail}"
        )
    if response.status_code == 403:
        if limited_access:
            raise AdMobAccessDenied(
                f"{action} denied with HTTP 403 for a limited-access method.\n"
                f"{LIMITED_ACCESS_EXPLANATION}\n{detail}"
            )
        raise AdMobPermissionDenied(
            f"{action} failed with HTTP 403. Check OAuth scopes, AdMob account access, "
            f"and whether the AdMob API is enabled for the OAuth project.\n{detail}"
        )
    raise AdMobError(f"{action} failed with HTTP {response.status_code}:\n{detail}")


def _date_value(value: str | date) -> dict[str, int]:
    parsed = value if isinstance(value, date) else date.fromisoformat(value)
    return {"year": parsed.year, "month": parsed.month, "day": parsed.day}


class AdMobClient:
    def __init__(self, publisher_id: str | None = None, session=None) -> None:
        self.session = session or auth.admob_session()
        self._publisher_id = publisher_id

    # ---- plumbing ----------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        action: str,
        *,
        base: str = BETA_BASE,
        limited_access: bool = False,
        **kwargs,
    ) -> Any:
        kwargs.setdefault("timeout", REQUEST_TIMEOUT_SECONDS)
        response = self.session.request(method, f"{base}/{path}", **kwargs)
        _raise_for_status(response, action, limited_access=limited_access)
        return response.json() if response.content else {}

    def _paginate(
        self,
        path: str,
        action: str,
        key: str,
        *,
        page_size: int = 100,
        limited_access: bool = False,
        params: dict[str, Any] | None = None,
    ) -> Iterator[dict]:
        page_token = None
        while True:
            request_params = dict(params or {})
            request_params["pageSize"] = page_size
            if page_token:
                request_params["pageToken"] = page_token
            payload = self._request(
                "GET",
                path,
                action,
                params=request_params,
                limited_access=limited_access,
            )
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
                "the authenticated Google Account has no visible AdMob account. "
                "Re-run `mra admob login` signed in as the intended AdMob account."
            )
        if len(accounts) > 1:
            names = ", ".join(account.get("publisherId", "?") for account in accounts)
            raise AdMobError(f"multiple AdMob accounts visible ({names}); pass --publisher-id")
        self._publisher_id = accounts[0]["publisherId"]
        return self._publisher_id

    # ---- inventory ---------------------------------------------------------

    def list_apps(self) -> list[dict]:
        return list(self._paginate(f"accounts/{self.publisher_id}/apps", "list apps", "apps"))

    def list_ad_units(self) -> list[dict]:
        return list(
            self._paginate(
                f"accounts/{self.publisher_id}/adUnits", "list ad units", "adUnits"
            )
        )

    def list_ad_sources(self) -> list[dict]:
        return list(
            self._paginate(
                f"accounts/{self.publisher_id}/adSources",
                "list ad sources",
                "adSources",
                page_size=10000,
            )
        )

    def list_adapters(self, ad_source_id: str) -> list[dict]:
        return list(
            self._paginate(
                f"accounts/{self.publisher_id}/adSources/{ad_source_id}/adapters",
                f"list adapters for ad source {ad_source_id}",
                "adapters",
                page_size=10000,
            )
        )

    def list_mediation_groups(self, filter_expression: str | None = None) -> list[dict]:
        params = {"filter": filter_expression} if filter_expression else None
        return list(
            self._paginate(
                f"accounts/{self.publisher_id}/mediationGroups",
                "list mediation groups",
                "mediationGroups",
                page_size=10000,
                limited_access=True,
                params=params,
            )
        )

    def list_ad_unit_mappings(
        self, ad_unit_id: str, filter_expression: str | None = None
    ) -> list[dict]:
        params = {"filter": filter_expression} if filter_expression else None
        return list(
            self._paginate(
                f"accounts/{self.publisher_id}/adUnits/{ad_unit_id}/adUnitMappings",
                f"list mappings for ad unit {ad_unit_id}",
                "adUnitMappings",
                page_size=10000,
                limited_access=True,
                params=params,
            )
        )

    def app_approval_summary(self) -> dict[str, Any]:
        apps = self.list_apps()
        by_state: dict[str, list[dict]] = {}
        for app in apps:
            state = app.get("appApprovalState", "APP_APPROVAL_STATE_UNSPECIFIED")
            by_state.setdefault(state, []).append(app)
        return {
            "publisher_id": self.publisher_id,
            "total_apps": len(apps),
            "states": {key: len(value) for key, value in sorted(by_state.items())},
            "action_required": by_state.get("ACTION_REQUIRED", []),
            "in_review": by_state.get("IN_REVIEW", []),
        }

    # ---- reporting ---------------------------------------------------------

    def _generate_report(self, kind: str, report_spec: dict, *, beta: bool = False) -> Any:
        base = BETA_BASE if beta else V1_BASE
        return self._request(
            "POST",
            f"accounts/{self.publisher_id}/{kind}:generate",
            f"generate AdMob {kind}",
            base=base,
            json={"reportSpec": report_spec},
        )

    def generate_network_report(self, report_spec: dict) -> Any:
        return self._generate_report("networkReport", report_spec)

    def generate_mediation_report(self, report_spec: dict) -> Any:
        return self._generate_report("mediationReport", report_spec)

    def generate_campaign_report(self, report_spec: dict) -> Any:
        return self._generate_report("campaignReport", report_spec, beta=True)

    def monetization_health_report(
        self,
        start_date: str | date,
        end_date: str | date,
        *,
        app_ids: list[str] | None = None,
        currency_code: str = "USD",
    ) -> Any:
        """Generate a portfolio-friendly network health report.

        The report exposes app/version/SDK/serving-restriction signals and the
        request->match->show funnel so an agent can detect regressions without
        scraping the AdMob UI.
        """
        spec: dict[str, Any] = {
            "dateRange": {
                "startDate": _date_value(start_date),
                "endDate": _date_value(end_date),
            },
            "dimensions": [
                "DATE",
                "APP",
                "APP_VERSION_NAME",
                "GMA_SDK_VERSION",
                "SERVING_RESTRICTION",
                "FORMAT",
            ],
            "metrics": [
                "AD_REQUESTS",
                "MATCHED_REQUESTS",
                "MATCH_RATE",
                "IMPRESSIONS",
                "SHOW_RATE",
                "CLICKS",
                "ESTIMATED_EARNINGS",
                "IMPRESSION_RPM",
            ],
            "localizationSettings": {"currencyCode": currency_code, "languageCode": "en-US"},
            "maxReportRows": 100000,
        }
        if app_ids:
            spec["dimensionFilters"] = [
                {
                    "dimension": "APP",
                    "matchesAny": {"values": [{"value": app_id} for app_id in app_ids]},
                }
            ]
        return self.generate_network_report(spec)

    # ---- limited-access creation/mutation ---------------------------------

    def create_app(
        self, display_name: str, platform: str, app_store_id: str | None = None
    ) -> dict:
        """Create an AdMob app. Limited access; linking is irreversible.

        Google documents ``linkedAppInfo.displayName`` as output-only. For a
        linked Android app only ``appStoreId`` is supplied; AdMob resolves the
        store display name itself.
        """
        if platform not in PLATFORMS:
            raise AdMobError(f"invalid platform {platform!r}; expected one of {PLATFORMS}")
        body: dict[str, Any] = {"platform": platform}
        if app_store_id:
            body["linkedAppInfo"] = {"appStoreId": app_store_id}
        else:
            body["manualAppInfo"] = {"displayName": display_name}
        return self._request(
            "POST",
            f"accounts/{self.publisher_id}/apps",
            "create AdMob app",
            json=body,
            limited_access=True,
        )

    def create_ad_unit(
        self,
        app_id: str,
        display_name: str,
        ad_format: str,
        ad_types: list[str] | None = None,
    ) -> dict:
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
            limited_access=True,
        )

    def create_mediation_group(self, body: dict) -> dict:
        return self._request(
            "POST",
            f"accounts/{self.publisher_id}/mediationGroups",
            "create mediation group",
            json=body,
            limited_access=True,
        )

    def patch_mediation_group(self, resource_name: str, update_mask: str, body: dict) -> dict:
        expected_prefix = f"accounts/{self.publisher_id}/mediationGroups/"
        if not resource_name.startswith(expected_prefix):
            raise AdMobError(
                f"mediation group name must start with {expected_prefix!r}; got {resource_name!r}"
            )
        return self._request(
            "PATCH",
            resource_name,
            "update mediation group",
            params={"updateMask": update_mask},
            json=body,
            limited_access=True,
        )

    def create_ad_unit_mapping(self, ad_unit_id: str, body: dict) -> dict:
        return self._request(
            "POST",
            f"accounts/{self.publisher_id}/adUnits/{ad_unit_id}/adUnitMappings",
            "create ad unit mapping",
            json=body,
            limited_access=True,
        )

    def batch_create_ad_unit_mappings(self, requests: list[dict]) -> dict:
        if not 1 <= len(requests) <= 100:
            raise AdMobError("AdMob batch mapping creation requires 1-100 requests")
        return self._request(
            "POST",
            f"accounts/{self.publisher_id}/adUnitMappings:batchCreate",
            "batch create ad unit mappings",
            json={"requests": requests},
            limited_access=True,
        )

    def create_mediation_experiment(self, mediation_group_id: str, body: dict) -> dict:
        return self._request(
            "POST",
            f"accounts/{self.publisher_id}/mediationGroups/{mediation_group_id}/mediationAbExperiments",
            "create mediation A/B experiment",
            json=body,
            limited_access=True,
        )

    def stop_mediation_experiment(self, experiment_name: str, variant_choice: str) -> dict:
        expected_prefix = f"accounts/{self.publisher_id}/mediationGroups/"
        if not experiment_name.startswith(expected_prefix):
            raise AdMobError(
                f"experiment name must start with {expected_prefix!r}; got {experiment_name!r}"
            )
        return self._request(
            "POST",
            f"{experiment_name}:stop",
            "stop mediation A/B experiment",
            json={"variantChoice": variant_choice},
            limited_access=True,
        )

    # ---- capability discovery ---------------------------------------------

    def probe_monetization_access(self) -> dict:
        """Probe one documented limited-access read without mutating anything."""
        result: dict[str, Any] = {"publisher_id": None, "probe": "mediationGroups.list"}
        try:
            result["publisher_id"] = self.publisher_id
        except AdMobError as error:
            result["monetization_access"] = "unknown"
            result["detail"] = str(error)
            return result

        try:
            self.list_mediation_groups()
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
            "This account can read the limited-access mediation surface. App/ad-unit "
            "creation remains separately gated and must be confirmed by an actual "
            "create when one is genuinely needed."
        )
        return result

    def capability_matrix(self) -> dict[str, Any]:
        """Return documented support plus non-mutating observations for this account."""
        capabilities: dict[str, str] = {
            "admob.inventory.read": "unknown",
            "admob.approval_state.read": "unknown",
            "admob.reporting.network": "supported_by_public_api",
            "admob.reporting.mediation": "supported_by_public_api",
            "admob.reporting.campaign": "supported_by_public_api",
            "admob.ad_sources.read": "unknown",
            "admob.adapters.read": "supported_by_public_api",
            "admob.mediation.read": "unknown",
            "admob.apps.create": "account_gated_unknown",
            "admob.adunits.create": "account_gated_unknown",
            "admob.mediation.write": "account_gated_unknown",
            "admob.mappings.write": "account_gated_unknown",
            "admob.mediation_experiments.write": "account_gated_unknown",
        }
        observations: list[dict[str, str]] = []

        try:
            self.list_apps()
            capabilities["admob.inventory.read"] = "ready"
            capabilities["admob.approval_state.read"] = "ready"
        except AdMobError as error:
            capabilities["admob.inventory.read"] = "error"
            capabilities["admob.approval_state.read"] = "error"
            observations.append({"capability": "admob.inventory.read", "detail": str(error)})

        try:
            self.list_ad_sources()
            capabilities["admob.ad_sources.read"] = "ready"
        except AdMobError as error:
            capabilities["admob.ad_sources.read"] = "error"
            observations.append({"capability": "admob.ad_sources.read", "detail": str(error)})

        try:
            self.list_mediation_groups()
            capabilities["admob.mediation.read"] = "ready"
        except AdMobAccessDenied as error:
            capabilities["admob.mediation.read"] = "denied_by_account"
            capabilities["admob.mediation.write"] = "denied_by_account_or_separately_gated"
            capabilities["admob.mappings.write"] = "denied_by_account_or_separately_gated"
            capabilities["admob.mediation_experiments.write"] = "denied_by_account_or_separately_gated"
            observations.append({"capability": "admob.mediation.read", "detail": str(error)})
        except AdMobError as error:
            capabilities["admob.mediation.read"] = "error"
            observations.append({"capability": "admob.mediation.read", "detail": str(error)})

        return {
            "publisher_id": self.publisher_id,
            "capabilities": capabilities,
            "observations": observations,
            "note": (
                "Creation/write gates are intentionally not probed with dummy objects. "
                "A real required mutation is the only safe way to turn an unknown write "
                "capability into ready or denied_by_account."
            ),
        }
