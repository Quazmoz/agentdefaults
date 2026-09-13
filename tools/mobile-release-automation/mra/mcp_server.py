"""A local stdio MCP server over the toolkit.

Why local: driving Play and AdMob means handing over a Play Console service
account and an AdMob refresh token. A third-party hosted MCP server would hold
both. This server runs on your machine, reads credentials from your own
credential directory, and talks only to Google's and RevenueCat's API hosts.

RevenueCat publishes a first-party MCP server at https://mcp.revenuecat.ai/mcp.
Prefer it. The RevenueCat tools here cover gaps and unattended scripting only.

Run:  python -m mra.mcp_server

Works with both mcp 1.x (FastMCP) and mcp 2.x (MCPServer).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import admob as admob_module
from . import auth, config
from . import play as play_module
from . import revenuecat as rc_module

# The SDK renamed FastMCP to MCPServer in mcp 2.x. Both expose the same
# name/tool/run surface this server uses, so support either.
try:
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # pragma: no cover - SDK version fallback
    try:
        from mcp.server.fastmcp import FastMCP as _Server
    except ImportError as error:
        raise SystemExit(
            "the MCP server needs the 'mcp' package: pip install 'mcp>=1.2.0'"
        ) from error

server = _Server("mobile-release-automation")

UNCONFIRMED = (
    "Refused: this changes live platform state. Re-call with confirm=true only "
    "after the operator has approved this exact action."
)


def _package(package_name: str | None, profile: str | None) -> str:
    if package_name:
        return package_name
    if profile:
        resolved = config.load_profile(profile).package_name
        if resolved:
            return resolved
        raise ValueError(f"profile {profile!r} has no package_name")
    raise ValueError("pass package_name or profile")


def _project(project_id: str | None, profile: str | None) -> str:
    if project_id:
        return project_id
    if profile:
        resolved = config.load_profile(profile).revenuecat_project_id
        if resolved:
            return resolved
        raise ValueError(f"profile {profile!r} has no revenuecat_project_id")
    raise ValueError("pass project_id or profile")


# ---- diagnostics -----------------------------------------------------------


@server.tool()
def doctor() -> dict:
    """Report which platform credentials are present and usable locally."""
    probes = {
        "play_service_account": lambda: str(
            config.require_file(config.PLAY_SERVICE_ACCOUNT, auth.PLAY_HINT)
        ),
        "revenuecat_key": lambda: f"present ({len(auth.revenuecat_key())} chars)",
        "admob_oauth_client": lambda: str(
            config.require_file(config.ADMOB_OAUTH_CLIENT, auth.ADMOB_CLIENT_HINT)
        ),
    }
    report: dict[str, Any] = {"credential_home": str(config.home()), "checks": {}}
    for name, probe in probes.items():
        try:
            report["checks"][name] = {"status": "ok", "detail": probe()}
        except Exception as error:  # noqa: BLE001 - diagnostics never raise
            report["checks"][name] = {"status": "fail", "detail": str(error)}
    report["admob_token_cached"] = config.path_for(config.ADMOB_TOKEN).is_file()
    report["profiles"] = sorted(config.load_profiles())
    return report


# ---- Google Play -----------------------------------------------------------


@server.tool()
def play_list_tracks(package_name: str | None = None, profile: str | None = None) -> list[dict]:
    """Read every Play track and its current releases. Read-only."""
    return play_module.track_status(_package(package_name, profile))


@server.tool()
def play_list_products(package_name: str | None = None, profile: str | None = None) -> dict:
    """List Play subscriptions and in-app products. Read-only."""
    client = play_module.PlayClient(_package(package_name, profile))
    return {
        "subscriptions": client.list_subscriptions(),
        "in_app_products": client.list_in_app_products(),
    }


@server.tool()
def play_publish_bundle(
    aab_path: str,
    track: str = "internal",
    package_name: str | None = None,
    profile: str | None = None,
    release_notes_en_us: str | None = None,
    status: str = "completed",
    dry_run: bool = True,
    confirm: bool = False,
) -> dict:
    """Upload an .aab and assign it to a Play track.

    Defaults to dry_run, which validates the edit and discards it so nothing
    reaches testers. A real publish requires dry_run=false and confirm=true.
    """
    if not dry_run and not confirm:
        return {"status": "refused", "detail": UNCONFIRMED}
    return play_module.publish_bundle(
        _package(package_name, profile),
        Path(aab_path).expanduser(),
        track=track,
        status=status,
        release_notes={"en-US": release_notes_en_us} if release_notes_en_us else None,
        dry_run=dry_run,
    )


@server.tool()
def play_promote(
    source_track: str,
    target_track: str,
    package_name: str | None = None,
    profile: str | None = None,
    status: str = "completed",
    user_fraction: float | None = None,
    dry_run: bool = True,
    confirm: bool = False,
) -> dict:
    """Promote the newest release from one Play track to another.

    Promotion moves the already-qualified artifact; it never rebuilds.
    """
    if not dry_run and not confirm:
        return {"status": "refused", "detail": UNCONFIRMED}
    return play_module.promote(
        _package(package_name, profile),
        from_track=source_track,
        to_track=target_track,
        status=status,
        user_fraction=user_fraction,
        dry_run=dry_run,
    )


# ---- AdMob -----------------------------------------------------------------


@server.tool()
def admob_probe_access(publisher_id: str | None = None) -> dict:
    """Test whether this AdMob account has monetization access. Creates nothing.

    AdMob's create methods are limited access and are unlocked per account by a
    Google account manager. Run this before promising any AdMob automation.
    """
    return admob_module.AdMobClient(publisher_id).probe_monetization_access()


@server.tool()
def admob_list_apps(publisher_id: str | None = None) -> list[dict]:
    """List AdMob apps. Read-only."""
    return admob_module.AdMobClient(publisher_id).list_apps()


@server.tool()
def admob_list_ad_units(publisher_id: str | None = None) -> list[dict]:
    """List AdMob ad units. Read-only."""
    return admob_module.AdMobClient(publisher_id).list_ad_units()


@server.tool()
def admob_create_app(
    display_name: str,
    platform: str = "ANDROID",
    app_store_id: str | None = None,
    publisher_id: str | None = None,
    confirm: bool = False,
) -> dict:
    """Create an AdMob app, linked to a store listing when app_store_id is given.

    Limited access: may return 403 regardless of scopes or service accounts.
    """
    if not confirm:
        return {"status": "refused", "detail": UNCONFIRMED}
    try:
        return admob_module.AdMobClient(publisher_id).create_app(
            display_name, platform, app_store_id
        )
    except admob_module.AdMobAccessDenied as error:
        return {"status": "access_denied", "detail": str(error)}


@server.tool()
def admob_create_ad_unit(
    app_id: str,
    display_name: str,
    ad_format: str,
    ad_types: list[str] | None = None,
    publisher_id: str | None = None,
    confirm: bool = False,
) -> dict:
    """Create an AdMob ad unit. Limited access: may return 403."""
    if not confirm:
        return {"status": "refused", "detail": UNCONFIRMED}
    try:
        return admob_module.AdMobClient(publisher_id).create_ad_unit(
            app_id, display_name, ad_format, ad_types
        )
    except admob_module.AdMobAccessDenied as error:
        return {"status": "access_denied", "detail": str(error)}


# ---- RevenueCat ------------------------------------------------------------


@server.tool()
def rc_list_projects() -> list[dict]:
    """List RevenueCat projects. Read-only. Prefer the first-party RevenueCat MCP."""
    return rc_module.RevenueCatClient().list_projects()


@server.tool()
def rc_list_apps(project_id: str | None = None, profile: str | None = None) -> list[dict]:
    """List apps in a RevenueCat project. Read-only."""
    return rc_module.RevenueCatClient().list_apps(_project(project_id, profile))


@server.tool()
def rc_create_play_app(
    name: str,
    package_name: str | None = None,
    project_id: str | None = None,
    profile: str | None = None,
    confirm: bool = False,
) -> dict:
    """Create a Play app in RevenueCat, wired to the local Play service account.

    This sends the Play service account key to RevenueCat, which is the
    documented way RevenueCat validates Play purchases.
    """
    if not confirm:
        return {"status": "refused", "detail": UNCONFIRMED}
    key_path = config.require_file(config.PLAY_SERVICE_ACCOUNT, auth.PLAY_HINT)
    return rc_module.RevenueCatClient().create_play_app(
        _project(project_id, profile),
        name,
        _package(package_name, profile),
        key_path.read_text(encoding="utf-8"),
    )


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
