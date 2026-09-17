"""Cross-platform desired-state planning, verification, and portfolio auditing.

The reconciler is intentionally declarative and secret-free. Desired state may
contain immutable ``*_secret_id`` references, but literal credentials are
rejected before any vendor call is made.
"""

from __future__ import annotations

from typing import Any

from . import admob, auth, config, play, play_management
from . import revenuecat as rc_module
from . import revenuecat_management


class ReconcileError(RuntimeError):
    pass


_FORBIDDEN_DESIRED_KEYS = {
    "authorization",
    "authorization_header",
    "access_token",
    "refresh_token",
    "client_secret",
    "private_key",
    "signing_secret",
    "api_key",
    "password",
}


def validate_desired_state(desired: dict[str, Any]) -> None:
    if not isinstance(desired, dict):
        raise ReconcileError("desired_state must be a JSON object")

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                normalized = str(key).strip().lower().replace("-", "_")
                if normalized in _FORBIDDEN_DESIRED_KEYS:
                    raise ReconcileError(
                        f"desired_state contains secret-like field {path + '.' if path else ''}{key!s}; "
                        "store the value in Bitwarden and pass a *_secret_id reference instead"
                    )
                walk(item, f"{path}.{key}" if path else str(key))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")

    walk(desired, "")


def _safe(call) -> dict[str, Any]:
    try:
        return {"status": "ready", "data": call()}
    except Exception as error:  # noqa: BLE001 - audit must continue across platforms
        return {
            "status": "error",
            "error_type": type(error).__name__,
            "detail": str(error),
        }


def _rc_client(profile: config.Profile) -> rc_module.RevenueCatClient:
    return rc_module.RevenueCatClient(api_key=auth.revenuecat_key(profile))


def snapshot_profile(profile_slug: str, *, include_reviews: bool = False) -> dict[str, Any]:
    """Collect authoritative current state without mutating any vendor."""
    profile = config.load_profile(profile_slug)
    snapshot: dict[str, Any] = {
        "profile": config.public_profile(profile),
        "play": {"status": "not_configured"},
        "revenuecat": {"status": "not_configured"},
        "admob": {"status": "not_configured"},
    }

    if profile.package_name:
        def play_state() -> dict[str, Any]:
            base = play.PlayClient(profile.package_name)
            management = play_management.PlayManagementClient(profile.package_name, client=base)
            state = {
                "tracks": play.track_status(profile.package_name, client=base),
                "subscriptions": base.list_subscriptions(),
                "one_time_products": base.list_in_app_products(),
                "listings": management.list_listings(),
            }
            if include_reviews:
                state["reviews"] = management.list_reviews(max_results=100)
            return state
        snapshot["play"] = _safe(play_state)

    if profile.revenuecat_secret_id:
        def rc_state() -> dict[str, Any]:
            client = _rc_client(profile)
            state: dict[str, Any] = {"projects": client.list_projects()}
            if profile.revenuecat_project_id:
                project_id = profile.revenuecat_project_id
                state.update(
                    {
                        "apps": client.list_apps(project_id),
                        "products": client.list_products(project_id),
                        "entitlements": client.list_entitlements(project_id),
                        "offerings": client.list_offerings(project_id),
                        "wiring": client.inspect_wiring(project_id),
                        "webhooks": revenuecat_management.RevenueCatManagementClient(
                            client
                        ).list_webhooks(project_id),
                    }
                )
            return state
        snapshot["revenuecat"] = _safe(rc_state)

    if profile.admob_publisher_id or profile.admob_app_id or profile.package_name:
        def admob_state() -> dict[str, Any]:
            client = admob.AdMobClient(profile.admob_publisher_id)
            return {
                "apps": client.list_apps(),
                "ad_units": client.list_ad_units(),
                "approval": client.app_approval_summary(),
                "capabilities": client.capability_matrix(),
            }
        snapshot["admob"] = _safe(admob_state)

    return snapshot


def _data(snapshot: dict[str, Any], platform: str) -> dict[str, Any] | None:
    entry = snapshot.get(platform, {})
    if entry.get("status") != "ready":
        return None
    data = entry.get("data")
    return data if isinstance(data, dict) else None


def _action(
    action_id: str,
    platform: str,
    operation: str,
    status: str,
    risk: str,
    params: dict[str, Any],
    detail: str,
) -> dict[str, Any]:
    return {
        "id": action_id,
        "platform": platform,
        "operation": operation,
        "status": status,
        "risk": risk,
        "params": params,
        "detail": detail,
    }


def plan_profile(
    profile_slug: str,
    desired: dict[str, Any],
    *,
    snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare desired state with vendor state and return a deterministic plan."""
    validate_desired_state(desired)
    profile = config.load_profile(profile_slug)
    current = snapshot or snapshot_profile(profile_slug)
    actions: list[dict[str, Any]] = []

    # Google Play ------------------------------------------------------------
    play_desired = desired.get("play") or {}
    play_current = _data(current, "play")
    listing = play_desired.get("listing")
    if listing:
        language = listing.get("language", "en-US")
        existing = None
        if play_current:
            existing = next(
                (item for item in play_current.get("listings", []) if item.get("language") == language),
                None,
            )
        expected = {
            "title": listing.get("title"),
            "shortDescription": listing.get("short_description"),
            "fullDescription": listing.get("full_description"),
            "video": listing.get("video"),
        }
        matches = existing is not None and all(
            value is None or existing.get(key) == value for key, value in expected.items()
        )
        actions.append(
            _action(
                f"play.listing.{language}",
                "play",
                "update_listing",
                "satisfied" if matches else ("needed" if play_current else "blocked"),
                "high",
                dict(listing),
                "localized store listing already matches" if matches else "localized store listing differs or is missing",
            )
        )

    for tester in play_desired.get("testers", []):
        track = tester.get("track", "internal")
        # Tester state is fetched lazily because it is not part of the base snapshot.
        if profile.package_name and play_current:
            tester_read = _safe(
                lambda track=track: play_management.PlayManagementClient(
                    profile.package_name
                ).get_testers(track)
            )
        else:
            tester_read = {"status": "error"}
        desired_groups = sorted(set(tester.get("google_groups", [])))
        actual_groups = sorted(set((tester_read.get("data") or {}).get("googleGroups", [])))
        matches = tester_read.get("status") == "ready" and desired_groups == actual_groups
        actions.append(
            _action(
                f"play.testers.{track}",
                "play",
                "update_testers",
                "satisfied" if matches else ("needed" if tester_read.get("status") == "ready" else "blocked"),
                "high",
                {"track": track, "google_groups": desired_groups},
                "tester groups already match" if matches else "tester groups differ or could not be read",
            )
        )

    # RevenueCat -------------------------------------------------------------
    rc_desired = desired.get("revenuecat") or {}
    rc_current = _data(current, "revenuecat")
    project_spec = rc_desired.get("project")
    if project_spec:
        project_name = project_spec.get("name")
        project_exists = bool(profile.revenuecat_project_id)
        actions.append(
            _action(
                "revenuecat.project",
                "revenuecat",
                "create_project",
                "satisfied" if project_exists else ("needed" if profile.revenuecat_secret_id else "blocked"),
                "contained",
                {"name": project_name},
                "profile already has a RevenueCat project" if project_exists else "profile has no RevenueCat project id",
            )
        )

    rc_apps = (rc_current or {}).get("apps", [])
    app_spec = rc_desired.get("app")
    if app_spec and profile.revenuecat_project_id:
        package_name = app_spec.get("package_name") or profile.package_name
        existing_app = next(
            (
                app
                for app in rc_apps
                if app.get("play_store", {}).get("package_name") == package_name
                or app.get("package_name") == package_name
            ),
            None,
        )
        actions.append(
            _action(
                "revenuecat.app",
                "revenuecat",
                "create_play_app",
                "satisfied" if existing_app else ("needed" if rc_current else "blocked"),
                "contained",
                {"name": app_spec.get("name"), "package_name": package_name},
                "RevenueCat Play app exists" if existing_app else "RevenueCat Play app is missing",
            )
        )

    rc_products = (rc_current or {}).get("products", [])
    for product in rc_desired.get("products", []):
        store_id = product.get("store_identifier")
        existing = next(
            (item for item in rc_products if item.get("store_identifier") == store_id), None
        )
        actions.append(
            _action(
                f"revenuecat.product.{store_id}",
                "revenuecat",
                "create_product",
                "satisfied" if existing else ("needed" if rc_current else "blocked"),
                "contained",
                dict(product),
                "RevenueCat product exists" if existing else "RevenueCat product is missing",
            )
        )

    rc_entitlements = (rc_current or {}).get("entitlements", [])
    for entitlement in rc_desired.get("entitlements", []):
        lookup_key = entitlement.get("lookup_key")
        existing = next(
            (item for item in rc_entitlements if item.get("lookup_key") == lookup_key), None
        )
        actions.append(
            _action(
                f"revenuecat.entitlement.{lookup_key}",
                "revenuecat",
                "create_entitlement",
                "satisfied" if existing else ("needed" if rc_current else "blocked"),
                "contained",
                dict(entitlement),
                "RevenueCat entitlement exists" if existing else "RevenueCat entitlement is missing",
            )
        )

    rc_offerings = (rc_current or {}).get("offerings", [])
    for offering in rc_desired.get("offerings", []):
        lookup_key = offering.get("lookup_key")
        existing = next(
            (item for item in rc_offerings if item.get("lookup_key") == lookup_key), None
        )
        current_match = not offering.get("is_current") or bool(existing and existing.get("is_current"))
        satisfied = existing is not None and current_match
        risk = "high" if offering.get("is_current") else "contained"
        actions.append(
            _action(
                f"revenuecat.offering.{lookup_key}",
                "revenuecat",
                "create_offering",
                "satisfied" if satisfied else ("needed" if rc_current else "blocked"),
                risk,
                dict(offering),
                "RevenueCat offering matches" if satisfied else "RevenueCat offering is missing or not current",
            )
        )

    rc_webhooks = (rc_current or {}).get("webhooks", [])
    for webhook in rc_desired.get("webhooks", []):
        name = webhook.get("name")
        existing = next((item for item in rc_webhooks if item.get("name") == name), None)
        comparable = ("url", "environment", "app_id")
        matches = existing is not None and all(
            webhook.get(key) is None or existing.get(key) == webhook.get(key) for key in comparable
        )
        actions.append(
            _action(
                f"revenuecat.webhook.{name}",
                "revenuecat",
                "create_or_update_webhook",
                "satisfied" if matches else ("needed" if rc_current else "blocked"),
                "high",
                dict(webhook),
                "RevenueCat webhook matches" if matches else "RevenueCat webhook is missing or differs",
            )
        )

    # AdMob ------------------------------------------------------------------
    admob_desired = desired.get("admob") or {}
    admob_current = _data(current, "admob")
    admob_apps = (admob_current or {}).get("apps", [])
    app_spec = admob_desired.get("app")
    matched_admob_app = None
    if app_spec:
        linked_package = app_spec.get("linked_package") or profile.package_name
        display_name = app_spec.get("display_name")
        matched_admob_app = next(
            (
                app
                for app in admob_apps
                if app.get("linkedAppInfo", {}).get("appStoreId") == linked_package
                or app.get("manualAppInfo", {}).get("displayName") == display_name
                or (profile.admob_app_id and app.get("appId") == profile.admob_app_id)
            ),
            None,
        )
        actions.append(
            _action(
                "admob.app",
                "admob",
                "create_app",
                "satisfied" if matched_admob_app else ("needed" if admob_current else "blocked"),
                "high" if linked_package else "contained",
                {
                    "display_name": display_name,
                    "platform": app_spec.get("platform", "ANDROID"),
                    "app_store_id": linked_package,
                },
                "AdMob app exists" if matched_admob_app else "AdMob app is missing; API creation will be attempted and may be account-gated",
            )
        )

    admob_units = (admob_current or {}).get("ad_units", [])
    app_id = (matched_admob_app or {}).get("appId") or profile.admob_app_id
    for unit in admob_desired.get("ad_units", []):
        name = unit.get("display_name")
        existing = next(
            (
                item
                for item in admob_units
                if item.get("displayName") == name and (not app_id or item.get("appId") == app_id)
            ),
            None,
        )
        status = "satisfied" if existing else ("needed" if admob_current and app_id else "blocked")
        actions.append(
            _action(
                f"admob.ad_unit.{name}",
                "admob",
                "create_ad_unit",
                status,
                "contained",
                {**dict(unit), "app_id": app_id},
                "AdMob ad unit exists" if existing else (
                    "AdMob ad unit is missing; API creation may be account-gated"
                    if app_id else "AdMob app id is required before the ad unit can be created"
                ),
            )
        )

    counts: dict[str, int] = {}
    for item in actions:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    return {
        "profile": profile_slug,
        "actions": actions,
        "summary": counts,
        "converged": all(item["status"] == "satisfied" for item in actions),
        "snapshot_errors": {
            platform: entry
            for platform, entry in current.items()
            if platform in ("play", "revenuecat", "admob") and entry.get("status") == "error"
        },
    }


def verify_profile(profile_slug: str, desired: dict[str, Any]) -> dict[str, Any]:
    """Re-read all vendors and report whether desired state has converged."""
    plan = plan_profile(profile_slug, desired)
    remaining = [item for item in plan["actions"] if item["status"] != "satisfied"]
    return {
        "profile": profile_slug,
        "converged": not remaining and not plan["snapshot_errors"],
        "remaining": remaining,
        "summary": plan["summary"],
        "snapshot_errors": plan["snapshot_errors"],
    }


def audit_profile(profile_slug: str) -> dict[str, Any]:
    """Audit one app across profile, Play, RevenueCat, and AdMob state."""
    profile = config.load_profile(profile_slug)
    snapshot = snapshot_profile(profile_slug, include_reviews=True)
    findings: list[dict[str, Any]] = []

    def finding(severity: str, code: str, platform: str, detail: str, **extra: Any) -> None:
        findings.append(
            {"severity": severity, "code": code, "platform": platform, "detail": detail, **extra}
        )

    if not profile.package_name:
        finding("error", "profile_missing_package", "profile", "No Android package name is configured.")

    for platform in ("play", "revenuecat", "admob"):
        entry = snapshot.get(platform, {})
        if entry.get("status") == "error":
            finding(
                "error",
                f"{platform}_read_failed",
                platform,
                entry.get("detail", "vendor read failed"),
            )

    play_state = _data(snapshot, "play") or {}
    for review in play_state.get("reviews", []):
        comments = review.get("comments", [])
        user_comments = [item.get("userComment") for item in comments if item.get("userComment")]
        developer_comments = [
            item.get("developerComment") for item in comments if item.get("developerComment")
        ]
        if user_comments:
            rating = user_comments[-1].get("starRating")
            if isinstance(rating, int) and rating <= 2 and not developer_comments:
                finding(
                    "warning",
                    "unanswered_low_review",
                    "play",
                    f"Review {review.get('reviewId', '?')} has {rating} stars and no developer reply.",
                    review_id=review.get("reviewId"),
                    star_rating=rating,
                )

    rc_state = _data(snapshot, "revenuecat") or {}
    if profile.revenuecat_project_id and rc_state:
        package = profile.package_name
        apps = rc_state.get("apps", [])
        matching = [
            app
            for app in apps
            if app.get("play_store", {}).get("package_name") == package
            or app.get("package_name") == package
        ]
        if package and not matching:
            finding(
                "warning",
                "revenuecat_app_missing",
                "revenuecat",
                f"No RevenueCat Play app matches {package}.",
            )
        if rc_state.get("products") and not any(
            offering.get("is_current") for offering in rc_state.get("offerings", [])
        ):
            finding(
                "warning",
                "revenuecat_no_current_offering",
                "revenuecat",
                "RevenueCat has products but no current offering was observed.",
            )

    admob_state = _data(snapshot, "admob") or {}
    approval = admob_state.get("approval", {})
    for app in approval.get("action_required", []):
        finding(
            "warning",
            "admob_action_required",
            "admob",
            f"AdMob app {app.get('appId', '?')} requires action.",
            app_id=app.get("appId"),
        )
    for app in approval.get("in_review", []):
        finding(
            "info",
            "admob_in_review",
            "admob",
            f"AdMob app {app.get('appId', '?')} is still in review.",
            app_id=app.get("appId"),
        )

    if profile.package_name and admob_state:
        matching_apps = [
            app
            for app in admob_state.get("apps", [])
            if app.get("linkedAppInfo", {}).get("appStoreId") == profile.package_name
            or (profile.admob_app_id and app.get("appId") == profile.admob_app_id)
        ]
        if profile.admob_app_id and not matching_apps:
            finding(
                "warning",
                "admob_profile_app_not_found",
                "admob",
                f"Configured AdMob app id {profile.admob_app_id} was not found in account inventory.",
            )
        if matching_apps:
            app_ids = {item.get("appId") for item in matching_apps}
            units = [u for u in admob_state.get("ad_units", []) if u.get("appId") in app_ids]
            if not units:
                finding(
                    "info",
                    "admob_no_ad_units",
                    "admob",
                    "The matched AdMob app currently has no ad units.",
                )

    severities: dict[str, int] = {}
    for item in findings:
        severities[item["severity"]] = severities.get(item["severity"], 0) + 1
    return {
        "profile": profile_slug,
        "profile_identifiers": config.public_profile(profile),
        "findings": findings,
        "summary": severities,
        "snapshot": snapshot,
    }


def audit_portfolio() -> dict[str, Any]:
    """Audit all configured MRA profiles while isolating failures per app."""
    results: dict[str, Any] = {}
    totals: dict[str, int] = {}
    for slug in sorted(config.load_profiles()):
        try:
            result = audit_profile(slug)
        except Exception as error:  # noqa: BLE001
            result = {
                "profile": slug,
                "findings": [
                    {
                        "severity": "error",
                        "code": "audit_failed",
                        "platform": "mra",
                        "detail": str(error),
                    }
                ],
                "summary": {"error": 1},
            }
        results[slug] = result
        for severity, count in result.get("summary", {}).items():
            totals[severity] = totals.get(severity, 0) + count
    return {
        "profiles": results,
        "summary": {
            "profile_count": len(results),
            "findings": totals,
        },
    }
