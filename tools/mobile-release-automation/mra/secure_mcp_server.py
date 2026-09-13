"""Local MCP surface that keeps vendor credentials behind the tool boundary."""

from __future__ import annotations

from typing import Any

from . import auth, config
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

UNCONFIRMED = (
    "Refused: this changes live platform state. Re-call with confirm=true only "
    "after the operator has approved this exact action."
)


def _profile(slug: str) -> config.Profile:
    profile = config.load_profile(slug)
    if not profile.revenuecat_project_id:
        raise ValueError(f"profile {slug!r} has no revenuecat_project_id")
    if not profile.revenuecat_secret_id:
        raise ValueError(f"profile {slug!r} has no revenuecat_secret_id")
    return profile


def _client(profile: config.Profile) -> rc_module.RevenueCatClient:
    return rc_module.RevenueCatClient(api_key=auth.revenuecat_key(profile))


@server.tool()
def doctor() -> dict[str, Any]:
    """Check Bitwarden bootstrap readiness and list profiles with secret references."""
    profiles = config.load_profiles()
    return {
        "bitwarden": secret_provider.bitwarden_status(),
        "secured_profiles": sorted(
            slug for slug, profile in profiles.items() if profile.revenuecat_secret_id
        ),
    }


@server.tool()
def rc_list_projects(profile: str) -> list[dict]:
    """List RevenueCat projects visible to the selected profile's secret key."""
    resolved = _profile(profile)
    return _client(resolved).list_projects()


@server.tool()
def rc_list_apps(profile: str) -> list[dict]:
    """List apps in the selected profile's RevenueCat project."""
    resolved = _profile(profile)
    return _client(resolved).list_apps(resolved.revenuecat_project_id)


@server.tool()
def rc_list_products(profile: str) -> list[dict]:
    """List products in the selected profile's RevenueCat project."""
    resolved = _profile(profile)
    return _client(resolved).list_products(resolved.revenuecat_project_id)


@server.tool()
def rc_create_play_app(profile: str, name: str, confirm: bool = False) -> dict:
    """Create the profile's Play app in RevenueCat without exposing credentials."""
    if not confirm:
        return {"status": "refused", "detail": UNCONFIRMED}
    resolved = _profile(profile)
    if not resolved.package_name:
        raise ValueError(f"profile {profile!r} has no package_name")
    key_path = config.require_file(config.PLAY_SERVICE_ACCOUNT, auth.PLAY_HINT)
    return _client(resolved).create_play_app(
        resolved.revenuecat_project_id,
        name,
        resolved.package_name,
        key_path.read_text(encoding="utf-8"),
    )


@server.tool()
def rc_create_product(
    profile: str,
    app_id: str,
    store_identifier: str,
    product_type: str,
    display_name: str | None = None,
    confirm: bool = False,
) -> dict:
    """Register a product in the selected profile's RevenueCat project."""
    if not confirm:
        return {"status": "refused", "detail": UNCONFIRMED}
    if product_type not in rc_module.PRODUCT_TYPES:
        raise ValueError(f"unsupported product_type {product_type!r}")
    resolved = _profile(profile)
    return _client(resolved).create_product(
        resolved.revenuecat_project_id,
        app_id,
        store_identifier,
        product_type,
        display_name,
    )


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
