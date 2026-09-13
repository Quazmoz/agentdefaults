"""Read-only local MCP surface with vendor credentials behind the tool boundary."""

from __future__ import annotations

from typing import Any

from . import auth, config, play_credentials
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
    profile = config.load_profile(slug)
    if not profile.package_name:
        raise ValueError(f"profile {slug!r} has no package_name")
    return profile.package_name


def _client(profile: config.Profile) -> rc_module.RevenueCatClient:
    return rc_module.RevenueCatClient(api_key=auth.revenuecat_key(profile))


def _probe(probe) -> dict:
    try:
        return probe()
    except config.ConfigError as error:
        return {"status": "not-ready", "detail": str(error)}


@server.tool()
def doctor() -> dict[str, Any]:
    """Check local credential bindings without returning credential values."""
    profiles = config.load_profiles()
    return {
        "bitwarden": secret_provider.bitwarden_status(),
        "google_play_publisher": _probe(play_credentials.publisher_status),
        "revenuecat_google_play": _probe(play_credentials.revenuecat_status),
        "secured_profiles": sorted(
            slug for slug, profile in profiles.items() if profile.revenuecat_secret_id
        ),
        "platform_mutations": "disabled",
    }


@server.tool()
def play_list_tracks(profile: str) -> list[dict]:
    """List Google Play tracks for a configured app profile."""
    return play_module.track_status(_package(profile))


@server.tool()
def play_list_products(profile: str) -> dict:
    """List Google Play subscriptions and in-app products for a profile."""
    client = play_module.PlayClient(_package(profile))
    return {
        "subscriptions": client.list_subscriptions(),
        "in_app_products": client.list_in_app_products(),
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


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
