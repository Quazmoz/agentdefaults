"""RevenueCat project and webhook tools for the risk-gated MCP surface."""

from __future__ import annotations

from typing import Any

from . import config, human_approval
from . import revenuecat as rc_module
from . import revenuecat_management
from . import secrets as secret_provider


def _auth_profile(slug: str) -> config.Profile:
    """Load an app profile; RevenueCat account auth is provided by CLI OAuth."""
    return config.load_profile(slug)


def _project_profile(slug: str) -> config.Profile:
    profile = _auth_profile(slug)
    if not profile.revenuecat_project_id:
        raise ValueError(f"profile {slug!r} has no revenuecat_project_id")
    return profile


def _client(profile: config.Profile) -> revenuecat_management.RevenueCatManagementClient:
    del profile
    return revenuecat_management.RevenueCatManagementClient(rc_module.RevenueCatClient())


def _tag(result: dict, risk: str, approved: bool = False) -> dict:
    return {**result, "_mra": {"risk": risk, "human_approved": approved}}


def _gate(title: str, detail: str) -> tuple[bool, dict[str, Any]]:
    decision = human_approval.request(title, detail)
    if decision.get("approved"):
        return True, decision
    return False, {
        "status": "human_approval_required",
        "risk": "high",
        "approval": decision,
        "detail": "High-risk RevenueCat action was not executed.",
    }


def _authorization_header(secret_id: str | None) -> str | None:
    if not secret_id:
        return None
    value = secret_provider.bitwarden_secret(secret_id).strip()
    if not value:
        raise config.ConfigError("webhook authorization-header secret is empty")
    return value


def rc_create_project(profile: str, name: str) -> dict:
    """Create one RevenueCat project using the authenticated account OAuth session."""
    resolved = _auth_profile(profile)
    result = _client(resolved).create_project(name)
    return _tag(result, "contained")


def rc_update_offering(
    profile: str,
    offering_id: str,
    display_name: str | None = None,
    is_current: bool | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """Update an offering; changing current offering requires local approval."""
    resolved = _project_profile(profile)
    approved = False
    risk = "contained"
    if is_current is not None:
        risk = "high"
        approved, refusal = _gate(
            "Approve RevenueCat current offering change",
            f"Profile: {profile}\nProject: {resolved.revenuecat_project_id}\n"
            f"Offering: {offering_id}\nSet current: {is_current}",
        )
        if not approved:
            return refusal
    result = _client(resolved).update_offering(
        resolved.revenuecat_project_id,
        offering_id,
        display_name=display_name,
        is_current=is_current,
        metadata=metadata,
    )
    return _tag(result, risk, approved)


def rc_list_webhooks(profile: str) -> list[dict]:
    """List webhook integrations without exposing signing secrets."""
    resolved = _project_profile(profile)
    return _client(resolved).list_webhooks(resolved.revenuecat_project_id)


def rc_get_webhook(profile: str, webhook_id: str) -> dict:
    """Read one webhook integration with secret fields redacted."""
    resolved = _project_profile(profile)
    return _client(resolved).get_webhook(resolved.revenuecat_project_id, webhook_id)


def rc_create_webhook(
    profile: str,
    name: str,
    url: str,
    authorization_header_secret_id: str | None = None,
    environment: str | None = None,
    event_types: list[str] | None = None,
    app_id: str | None = None,
) -> dict:
    """Create a live webhook after local approval.

    The optional authorization header is addressed by Bitwarden UUID; its value
    is resolved only inside the MCP process and is never an agent argument/output.
    """
    resolved = _project_profile(profile)
    approved, refusal = _gate(
        "Approve RevenueCat webhook creation",
        f"Profile: {profile}\nProject: {resolved.revenuecat_project_id}\n"
        f"Name: {name}\nURL: {url}\nEnvironment: {environment or 'all'}\n"
        f"App: {app_id or 'all'}\nEvents: {', '.join(event_types or []) or 'all'}\n"
        f"Authorization header configured: {'yes' if authorization_header_secret_id else 'no'}",
    )
    if not approved:
        return refusal
    result = _client(resolved).create_webhook(
        resolved.revenuecat_project_id,
        name=name,
        url=url,
        authorization_header=_authorization_header(authorization_header_secret_id),
        environment=environment,
        event_types=event_types,
        app_id=app_id,
    )
    return _tag(result, "high", True)


def rc_update_webhook(
    profile: str,
    webhook_id: str,
    name: str | None = None,
    url: str | None = None,
    authorization_header_secret_id: str | None = None,
    environment: str | None = None,
    event_types: list[str] | None = None,
    app_id: str | None = None,
    clear_authorization_header: bool = False,
    clear_environment: bool = False,
    clear_event_types: bool = False,
    clear_app_id: bool = False,
) -> dict:
    """Partially update a webhook after local approval."""
    resolved = _project_profile(profile)
    approved, refusal = _gate(
        "Approve RevenueCat webhook update",
        f"Profile: {profile}\nProject: {resolved.revenuecat_project_id}\nWebhook: {webhook_id}\n"
        f"URL change: {url or '(unchanged)'}\nAuthorization change: "
        f"{'set from secret' if authorization_header_secret_id else ('clear' if clear_authorization_header else 'unchanged')}",
    )
    if not approved:
        return refusal
    result = _client(resolved).update_webhook(
        resolved.revenuecat_project_id,
        webhook_id,
        name=name,
        url=url,
        authorization_header=_authorization_header(authorization_header_secret_id),
        environment=environment,
        event_types=event_types,
        app_id=app_id,
        clear_authorization_header=clear_authorization_header,
        clear_environment=clear_environment,
        clear_event_types=clear_event_types,
        clear_app_id=clear_app_id,
    )
    return _tag(result, "high", True)


def rc_delete_webhook(profile: str, webhook_id: str) -> dict:
    """Permanently delete a webhook after local approval."""
    resolved = _project_profile(profile)
    approved, refusal = _gate(
        "Approve RevenueCat webhook deletion",
        f"Profile: {profile}\nProject: {resolved.revenuecat_project_id}\nWebhook: {webhook_id}\n"
        "Deletion stops event delivery and is destructive.",
    )
    if not approved:
        return refusal
    result = _client(resolved).delete_webhook(resolved.revenuecat_project_id, webhook_id)
    return _tag(result, "high", True)


def register(server) -> None:
    for tool in (
        rc_create_project,
        rc_update_offering,
        rc_list_webhooks,
        rc_get_webhook,
        rc_create_webhook,
        rc_update_webhook,
        rc_delete_webhook,
    ):
        server.tool()(tool)
