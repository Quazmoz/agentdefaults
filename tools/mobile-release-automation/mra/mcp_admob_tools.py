"""AdMob read and contained-create tools for the local MCP server."""

from __future__ import annotations

from . import admob as admob_module
from . import config


def _publisher_id(profile: str | None, publisher_id: str | None) -> str | None:
    if publisher_id:
        return publisher_id
    if profile:
        return config.load_profile(profile).admob_publisher_id
    return None


def _tag(result: dict, risk: str = "contained") -> dict:
    return {**result, "_mra": {"risk": risk, "human_approved": False}}


def admob_probe_access(profile: str | None = None, publisher_id: str | None = None) -> dict:
    """Probe whether the account can use AdMob monetization creation APIs."""
    return admob_module.AdMobClient(_publisher_id(profile, publisher_id)).probe_monetization_access()


def admob_list_apps(profile: str | None = None, publisher_id: str | None = None) -> list[dict]:
    """List AdMob apps."""
    return admob_module.AdMobClient(_publisher_id(profile, publisher_id)).list_apps()


def admob_list_ad_units(profile: str | None = None, publisher_id: str | None = None) -> list[dict]:
    """List AdMob ad units."""
    return admob_module.AdMobClient(_publisher_id(profile, publisher_id)).list_ad_units()


def admob_create_app(
    display_name: str,
    platform: str = "ANDROID",
    app_store_id: str | None = None,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> dict:
    """Create one AdMob app. This is a contained single-object mutation."""
    try:
        result = admob_module.AdMobClient(_publisher_id(profile, publisher_id)).create_app(
            display_name, platform, app_store_id
        )
        return _tag(result)
    except admob_module.AdMobAccessDenied as error:
        return {"status": "access_denied", "detail": str(error), "risk": "contained"}


def admob_create_ad_unit(
    app_id: str,
    display_name: str,
    ad_format: str,
    ad_types: list[str] | None = None,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> dict:
    """Create one AdMob ad unit. This is a contained single-object mutation."""
    try:
        result = admob_module.AdMobClient(_publisher_id(profile, publisher_id)).create_ad_unit(
            app_id, display_name, ad_format, ad_types
        )
        return _tag(result)
    except admob_module.AdMobAccessDenied as error:
        return {"status": "access_denied", "detail": str(error), "risk": "contained"}


def register(server) -> None:
    for tool in (
        admob_probe_access,
        admob_list_apps,
        admob_list_ad_units,
        admob_create_app,
        admob_create_ad_unit,
    ):
        server.tool()(tool)
