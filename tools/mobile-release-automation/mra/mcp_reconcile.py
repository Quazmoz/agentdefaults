"""Cross-platform plan/apply/verify and portfolio-audit MCP tools."""

from __future__ import annotations

from typing import Any

from . import admob, auth, config, human_approval, play_credentials, play_management
from . import reconcile, redaction
from . import revenuecat as rc_module
from . import revenuecat_management
from . import secrets as secret_provider


def _tag(result: Any, risk: str, approved: bool = False) -> dict[str, Any]:
    return {
        "result": redaction.redact(result),
        "_mra": {"risk": risk, "human_approved": approved},
    }


def _gate(title: str, detail: str) -> tuple[bool, dict[str, Any]]:
    decision = human_approval.request(title, detail)
    if decision.get("approved"):
        return True, decision
    return False, {
        "status": "human_approval_required",
        "risk": "high",
        "approval": decision,
        "detail": "High-risk reconciliation action was not executed.",
    }


def _rc_client(profile: config.Profile) -> rc_module.RevenueCatClient:
    if not profile.revenuecat_secret_id:
        raise reconcile.ReconcileError(
            f"profile {profile.slug!r} has no RevenueCat secret binding"
        )
    return rc_module.RevenueCatClient(api_key=auth.revenuecat_key(profile))


def _rc_management(profile: config.Profile) -> revenuecat_management.RevenueCatManagementClient:
    return revenuecat_management.RevenueCatManagementClient(_rc_client(profile))


def _secret(secret_id: str | None) -> str | None:
    if not secret_id:
        return None
    value = secret_provider.bitwarden_secret(secret_id).strip()
    if not value:
        raise reconcile.ReconcileError("referenced Bitwarden secret is empty")
    return value


def _execute(profile_slug: str, action: dict[str, Any]) -> dict[str, Any]:
    """Execute one planned action. Every high-risk path gates locally."""
    profile = config.load_profile(profile_slug)
    operation = action["operation"]
    params = action.get("params", {})

    # Google Play ------------------------------------------------------------
    if action["platform"] == "play":
        if not profile.package_name:
            raise reconcile.ReconcileError("Google Play action requires package_name")
        client = play_management.PlayManagementClient(profile.package_name)
        if operation == "update_listing":
            approved, refusal = _gate(
                "Approve reconciled Google Play listing",
                f"Profile: {profile_slug}\nLanguage: {params.get('language', 'en-US')}\n"
                f"Title: {params.get('title')}\nThis changes public Play Store metadata.",
            )
            if not approved:
                return refusal
            result = client.update_listing(
                params.get("language", "en-US"),
                title=params["title"],
                short_description=params["short_description"],
                full_description=params["full_description"],
                video=params.get("video"),
                dry_run=False,
            )
            return _tag(result, "high", True)
        if operation == "update_testers":
            approved, refusal = _gate(
                "Approve reconciled Google Play testers",
                f"Profile: {profile_slug}\nTrack: {params['track']}\n"
                f"Google Groups: {', '.join(params.get('google_groups', []))}",
            )
            if not approved:
                return refusal
            result = client.update_testers(
                params["track"], params.get("google_groups", []), dry_run=False
            )
            return _tag(result, "high", True)

    # RevenueCat -------------------------------------------------------------
    if action["platform"] == "revenuecat":
        if operation == "create_project":
            result = _rc_management(profile).create_project(params["name"])
            project_id = result.get("id")
            if project_id:
                config.update_profile_identifiers(
                    profile_slug, revenuecat_project_id=str(project_id)
                )
            return _tag(result, "contained")

        if not profile.revenuecat_project_id:
            raise reconcile.ReconcileError("RevenueCat action requires revenuecat_project_id")
        project_id = profile.revenuecat_project_id
        client = _rc_client(profile)
        management = revenuecat_management.RevenueCatManagementClient(client)

        if operation == "create_play_app":
            package_name = params.get("package_name") or profile.package_name
            if not package_name:
                raise reconcile.ReconcileError("RevenueCat Play app requires package_name")
            result = client.create_play_app(
                project_id,
                params["name"],
                package_name,
                play_credentials.revenuecat_json(),
            )
            app_id = result.get("id")
            if app_id:
                config.update_profile_identifiers(profile_slug, revenuecat_app_id=str(app_id))
            return _tag(result, "contained")

        if operation == "create_product":
            app_id = params.get("app_id") or profile.revenuecat_app_id
            if not app_id:
                return {
                    "status": "blocked",
                    "detail": "RevenueCat product creation needs revenuecat_app_id; reconcile the app first.",
                }
            result = client.create_product(
                project_id,
                app_id,
                params["store_identifier"],
                params["type"],
                params.get("display_name"),
            )
            return _tag(result, "contained")

        if operation == "create_entitlement":
            result = client.create_entitlement(
                project_id, params["lookup_key"], params["display_name"]
            )
            return _tag(result, "contained")

        if operation == "attach_products_to_entitlement":
            approved, refusal = _gate(
                "Approve reconciled RevenueCat entitlement wiring",
                f"Profile: {profile_slug}\nProject: {project_id}\n"
                f"Entitlement: {params.get('entitlement_id')}\n"
                f"Products: {', '.join(params.get('store_identifiers', []))}",
            )
            if not approved:
                return refusal
            result = client.attach_products_to_entitlement(
                project_id,
                params["entitlement_id"],
                params["product_ids"],
            )
            return _tag(result, "high", True)

        if operation == "create_offering":
            is_current = bool(params.get("is_current"))
            approved = False
            if is_current:
                approved, refusal = _gate(
                    "Approve reconciled current RevenueCat offering",
                    f"Profile: {profile_slug}\nProject: {project_id}\n"
                    f"Offering: {params.get('lookup_key')}\nCreate and set current: yes",
                )
                if not approved:
                    return refusal
            result = client.create_offering(
                project_id,
                params["lookup_key"],
                params["display_name"],
                is_current=is_current,
            )
            return _tag(result, "high" if is_current else "contained", approved)

        if operation == "update_offering":
            approved, refusal = _gate(
                "Approve reconciled current RevenueCat offering",
                f"Profile: {profile_slug}\nProject: {project_id}\n"
                f"Offering: {params.get('lookup_key')}\nSet current: {params.get('is_current')}",
            )
            if not approved:
                return refusal
            result = management.update_offering(
                project_id,
                params["offering_id"],
                display_name=params.get("display_name"),
                is_current=params.get("is_current"),
            )
            return _tag(result, "high", True)

        if operation == "create_package":
            offering_id = params.get("offering_id")
            if not offering_id:
                return {
                    "status": "blocked",
                    "detail": "RevenueCat package creation needs offering_id; reconcile the offering first.",
                }
            result = client.create_package(
                project_id,
                offering_id,
                params["lookup_key"],
                params["display_name"],
                params.get("position"),
            )
            return _tag(result, "contained")

        if operation == "attach_products_to_package":
            approved, refusal = _gate(
                "Approve reconciled RevenueCat package wiring",
                f"Profile: {profile_slug}\nProject: {project_id}\n"
                f"Package: {params.get('package_id')}\n"
                f"Products: {', '.join(params.get('store_identifiers', []))}",
            )
            if not approved:
                return refusal
            result = client.attach_products_to_package(
                project_id,
                params["package_id"],
                params["products"],
            )
            return _tag(result, "high", True)

        if operation == "create_or_update_webhook":
            existing = next(
                (
                    item
                    for item in management.list_webhooks(project_id)
                    if item.get("name") == params.get("name")
                ),
                None,
            )
            approved, refusal = _gate(
                "Approve reconciled RevenueCat webhook",
                f"Profile: {profile_slug}\nProject: {project_id}\nName: {params.get('name')}\n"
                f"URL: {params.get('url')}\nExisting: {'yes' if existing else 'no'}\n"
                f"Authorization header configured: {'yes' if params.get('authorization_header_secret_id') else 'no'}",
            )
            if not approved:
                return refusal
            auth_header = _secret(params.get("authorization_header_secret_id"))
            if existing:
                result = management.update_webhook(
                    project_id,
                    existing["id"],
                    url=params.get("url"),
                    authorization_header=auth_header,
                    environment=params.get("environment"),
                    event_types=params.get("event_types"),
                    app_id=params.get("app_id"),
                )
            else:
                result = management.create_webhook(
                    project_id,
                    name=params["name"],
                    url=params["url"],
                    authorization_header=auth_header,
                    environment=params.get("environment"),
                    event_types=params.get("event_types"),
                    app_id=params.get("app_id"),
                )
            return _tag(result, "high", True)

    # AdMob ------------------------------------------------------------------
    if action["platform"] == "admob":
        client = admob.AdMobClient(profile.admob_publisher_id)
        if operation == "create_app":
            linked = params.get("app_store_id")
            approved = False
            if linked:
                approved, refusal = _gate(
                    "Approve reconciled AdMob app linking",
                    f"Profile: {profile_slug}\nStore ID: {linked}\n"
                    "AdMob store linking is irreversible.",
                )
                if not approved:
                    return refusal
            try:
                result = client.create_app(
                    params["display_name"], params.get("platform", "ANDROID"), linked
                )
            except admob.AdMobAccessDenied as error:
                return {
                    "status": "manual_required",
                    "platform": "admob",
                    "detail": redaction.redact_text(str(error)),
                    "manual_action": (
                        "Create/link this app in the AdMob console, then rerun mra_verify. "
                        "The API account gate cannot be bypassed by OAuth scope changes."
                    ),
                }
            updates: dict[str, str] = {}
            if result.get("appId"):
                updates["admob_app_id"] = str(result["appId"])
            try:
                updates["admob_publisher_id"] = client.publisher_id
            except admob.AdMobError:
                pass
            if updates:
                config.update_profile_identifiers(profile_slug, **updates)
            return _tag(result, "high" if linked else "contained", approved)

        if operation == "create_ad_unit":
            app_id = params.get("app_id") or profile.admob_app_id
            if not app_id:
                return {
                    "status": "blocked",
                    "detail": "AdMob ad-unit creation needs admob_app_id; reconcile the app first.",
                }
            try:
                result = client.create_ad_unit(
                    app_id,
                    params["display_name"],
                    params["format"],
                    params.get("ad_types"),
                )
            except admob.AdMobAccessDenied as error:
                return {
                    "status": "manual_required",
                    "platform": "admob",
                    "detail": redaction.redact_text(str(error)),
                    "manual_action": (
                        f"Create ad unit {params.get('display_name')!r} for {app_id} in AdMob, "
                        "then rerun mra_verify."
                    ),
                }
            return _tag(result, "contained")

    raise reconcile.ReconcileError(
        f"unsupported reconciliation operation {action['platform']}.{operation}"
    )


def mra_plan(profile: str, desired_state: dict[str, Any]) -> dict[str, Any]:
    """Diff secret-free desired state against Play, RevenueCat, and AdMob."""
    return redaction.redact(reconcile.plan_profile(profile, desired_state))


def mra_apply(profile: str, desired_state: dict[str, Any]) -> dict[str, Any]:
    """Apply planned changes, re-planning after each mutation until no progress remains."""
    reconcile.validate_desired_state(desired_state)
    attempted: set[str] = set()
    results: list[dict[str, Any]] = []

    # Re-plan after every attempted action because creates may unblock later
    # resources and may reconcile newly returned vendor identifiers locally.
    for _ in range(100):
        plan = reconcile.plan_profile(profile, desired_state)
        candidate = next(
            (
                item
                for item in plan["actions"]
                if item["status"] == "needed" and item["id"] not in attempted
            ),
            None,
        )
        if candidate is None:
            break
        attempted.add(candidate["id"])
        try:
            outcome = _execute(profile, candidate)
        except Exception as error:  # noqa: BLE001 - preserve partial reconciliation
            outcome = {
                "status": "error",
                "error_type": type(error).__name__,
                "detail": redaction.redact_text(str(error)),
            }
        results.append(
            {
                "action": candidate,
                "outcome": redaction.redact(outcome),
            }
        )

    verification = reconcile.verify_profile(profile, desired_state)
    return {
        "profile": profile,
        "executions": results,
        "verification": redaction.redact(verification),
        "converged": verification["converged"],
    }


def mra_verify(profile: str, desired_state: dict[str, Any]) -> dict[str, Any]:
    """Re-read authoritative vendor state and report remaining drift."""
    return redaction.redact(reconcile.verify_profile(profile, desired_state))


def mra_audit_profile(profile: str) -> dict[str, Any]:
    """Audit one configured app across Play, RevenueCat, AdMob, and reviews."""
    return redaction.redact(reconcile.audit_profile(profile))


def mra_audit_portfolio() -> dict[str, Any]:
    """Audit every configured MRA profile and isolate failures per app."""
    return redaction.redact(reconcile.audit_portfolio())


def register(server) -> None:
    for tool in (
        mra_plan,
        mra_apply,
        mra_verify,
        mra_audit_profile,
        mra_audit_portfolio,
    ):
        server.tool()(tool)
