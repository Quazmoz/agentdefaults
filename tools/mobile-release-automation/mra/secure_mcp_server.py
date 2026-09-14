"""Risk-gated local MCP surface with vendor credentials behind the tool boundary."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from . import admob_credentials, auth, config, human_approval, play_credentials
from . import mcp_admob_tools, mcp_play_mutations, mcp_revenuecat_mutations
from . import play as play_module
from . import revenuecat as rc_module
from . import secrets as secret_provider

try:
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # pragma: no cover - SDK version fallback
    try:
        from mcp.server.fastmcp import FastMCP as _Server
    except ImportError as error:
        raise SystemExit(
            "the MCP server needs the 'mcp' package: pip install 'mcp>=1.2.0'"
        ) from error

server = _Server("mobile-release-automation-agent")


def _profile(slug: str) -> config.Profile:
    profile = config.load_profile(slug)
    if not profile.revenuecat_project_id:
        raise ValueError(f"profile {slug!r} has no revenuecat_project_id")
    if not profile.revenuecat_secret_id:
        raise ValueError(f"profile {slug!r} has no revenuecat_secret_id")
    return profile


def _package(slug: str) -> str:
    package_name = config.load_profile(slug).package_name
    if not package_name:
        raise ValueError(f"profile {slug!r} has no package_name")
    return package_name


def _client(profile: config.Profile) -> rc_module.RevenueCatClient:
    return rc_module.RevenueCatClient(api_key=auth.revenuecat_key(profile))


def _probe(probe) -> dict:
    try:
        return probe()
    except config.ConfigError as error:
        return {"status": "not-ready", "detail": str(error)}


def _error_payload(error: Exception, *, platform: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": "error",
        "error_type": type(error).__name__,
        "detail": str(error),
    }
    if platform:
        payload["platform"] = platform
    return payload


def _safe_read(operation: Callable[[], Any]) -> Any:
    """Keep expected read/config failures visible to MCP clients instead of opaque."""
    try:
        return operation()
    except (config.ConfigError, ValueError) as error:
        return _error_payload(error)


def _rc_read(
    profile: str,
    operation: Callable[[rc_module.RevenueCatClient, config.Profile], Any],
    *,
    required_permissions: list[str],
) -> Any:
    """Run a RevenueCat read while preserving vendor error detail for agents.

    Successful responses retain their historical shape. Expected configuration or
    RevenueCat failures return a structured object so the MCP transport does not
    collapse them into the generic ``Error executing tool`` message.
    """
    try:
        resolved = _profile(profile)
        return operation(_client(resolved), resolved)
    except (config.ConfigError, ValueError, rc_module.RevenueCatError) as error:
        payload = _error_payload(error, platform="revenuecat")
        payload["required_permissions"] = required_permissions
        if isinstance(error, rc_module.RevenueCatError) and "HTTP 403" in str(error):
            payload["hint"] = (
                "RevenueCat denied this API v2 operation. Check that the profile's "
                "secret key includes the listed permission(s)."
            )
        return payload


@server.tool()
def doctor() -> dict[str, Any]:
    """Check credential bindings, approval capability, and secured profiles."""
    profiles = config.load_profiles()
    return {
        "bitwarden": secret_provider.bitwarden_status(),
        "google_play_publisher": _probe(play_credentials.publisher_status),
        "revenuecat_google_play": _probe(play_credentials.revenuecat_status),
        "admob": _probe(admob_credentials.status),
        "human_approval": human_approval.status(),
        "secured_profiles": sorted(
            slug for slug, profile in profiles.items() if profile.revenuecat_secret_id
        ),
        "platform_mutations": "risk-gated",
    }


@server.tool()
def approval_policy() -> dict[str, Any]:
    """Describe the MCP risk policy before mutation-heavy work."""
    return {
        "observe": ["reads", "diagnostics", "Play dry-runs"],
        "contained": [
            "internal Play releases",
            "single RevenueCat object creation that does not change live entitlement wiring",
            "single AdMob app or ad-unit creation where supported",
            "local reconciliation of verified non-secret app identifiers",
        ],
        "high": [
            "non-internal Play releases or promotions",
            "making a RevenueCat offering current",
            "attaching products to entitlements or packages",
            "creating RevenueCat products in the backing store",
            "future destructive, financial, or broad multi-app mutations",
        ],
        "gate": human_approval.status(),
        "rule": "High-risk actions fail closed unless the local operator approves the exact action.",
    }


@server.tool()
def profile_get(profile: str) -> Any:
    """Read only non-secret identifiers for one MRA app profile."""
    return _safe_read(lambda: config.public_profile(config.load_profile(profile)))


@server.tool()
def profile_update_identifiers(
    profile: str,
    package_name: str | None = None,
    admob_app_id: str | None = None,
    admob_publisher_id: str | None = None,
    revenuecat_project_id: str | None = None,
    revenuecat_app_id: str | None = None,
) -> dict[str, Any]:
    """Reconcile verified non-secret identifiers without exposing profile secrets.

    This is a local contained mutation. It cannot change secret bindings and it
    refuses to create a new partial profile accidentally.
    """
    updated = config.update_profile_identifiers(
        profile,
        package_name=package_name,
        admob_app_id=admob_app_id,
        admob_publisher_id=admob_publisher_id,
        revenuecat_project_id=revenuecat_project_id,
        revenuecat_app_id=revenuecat_app_id,
    )
    return {
        "profile": config.public_profile(updated),
        "_mra": {"risk": "contained-local", "human_approved": False},
    }


@server.tool()
def play_list_tracks(profile: str) -> list[dict]:
    """List Google Play tracks for a configured app profile."""
    return play_module.track_status(_package(profile))


@server.tool()
def play_list_products(profile: str) -> dict:
    """List Google Play subscriptions and one-time products for a profile."""
    client = play_module.PlayClient(_package(profile))
    return {
        "subscriptions": client.list_subscriptions(),
        "in_app_products": client.list_in_app_products(),
    }


@server.tool()
def rc_list_projects(profile: str) -> Any:
    """List RevenueCat projects visible to the selected profile's key."""
    return _rc_read(
        profile,
        lambda client, resolved: client.list_projects(),
        required_permissions=["project_configuration:projects:read"],
    )


@server.tool()
def rc_list_apps(profile: str) -> Any:
    """List apps in the selected RevenueCat project."""
    return _rc_read(
        profile,
        lambda client, resolved: client.list_apps(resolved.revenuecat_project_id),
        required_permissions=["project_configuration:apps:read"],
    )


@server.tool()
def rc_list_products(profile: str) -> Any:
    """List products in the selected RevenueCat project."""
    return _rc_read(
        profile,
        lambda client, resolved: client.list_products(resolved.revenuecat_project_id),
        required_permissions=["project_configuration:products:read"],
    )


@server.tool()
def rc_list_entitlements(profile: str) -> Any:
    """List entitlements in the selected RevenueCat project."""
    return _rc_read(
        profile,
        lambda client, resolved: client.list_entitlements(resolved.revenuecat_project_id),
        required_permissions=["project_configuration:entitlements:read"],
    )


@server.tool()
def rc_list_entitlement_products(profile: str, entitlement_id: str) -> Any:
    """List products currently attached to one RevenueCat entitlement."""
    return _rc_read(
        profile,
        lambda client, resolved: client.list_entitlement_products(
            resolved.revenuecat_project_id, entitlement_id
        ),
        required_permissions=["project_configuration:entitlements:read"],
    )


@server.tool()
def rc_list_offerings(profile: str) -> Any:
    """List offerings in the selected RevenueCat project."""
    return _rc_read(
        profile,
        lambda client, resolved: client.list_offerings(resolved.revenuecat_project_id),
        required_permissions=["project_configuration:offerings:read"],
    )


@server.tool()
def rc_list_packages(profile: str, offering_id: str) -> Any:
    """List packages currently attached to one RevenueCat offering."""
    return _rc_read(
        profile,
        lambda client, resolved: client.list_packages(
            resolved.revenuecat_project_id, offering_id
        ),
        required_permissions=["project_configuration:packages:read"],
    )


@server.tool()
def rc_list_package_products(profile: str, package_id: str) -> Any:
    """List products currently attached to one RevenueCat package."""
    return _rc_read(
        profile,
        lambda client, resolved: client.list_package_products(
            resolved.revenuecat_project_id, package_id
        ),
        required_permissions=["project_configuration:packages:read"],
    )


@server.tool()
def rc_inspect_wiring(profile: str) -> Any:
    """Read complete offering/package/product and entitlement/product wiring."""
    return _rc_read(
        profile,
        lambda client, resolved: client.inspect_wiring(resolved.revenuecat_project_id),
        required_permissions=[
            "project_configuration:offerings:read",
            "project_configuration:packages:read",
            "project_configuration:entitlements:read",
        ],
    )


mcp_play_mutations.register(server)
mcp_revenuecat_mutations.register(server)
mcp_admob_tools.register(server)


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
