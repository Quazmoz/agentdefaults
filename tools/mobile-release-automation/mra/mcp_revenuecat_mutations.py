"""RevenueCat mutation tools for the local risk-gated MCP server."""

from __future__ import annotations

from typing import Any

from . import auth, config, human_approval, play_credentials
from . import mcp_revenuecat_management
from . import revenuecat as rc_module


def _profile(slug: str) -> config.Profile:
    profile = config.load_profile(slug)
    if not profile.revenuecat_project_id:
        raise ValueError(f"profile {slug!r} has no revenuecat_project_id")
    return profile


def _client(profile: config.Profile) -> rc_module.RevenueCatClient:
    return rc_module.RevenueCatClient(api_key=auth.revenuecat_key(profile))


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
        "detail": "High-risk action was not executed.",
    }


def rc_create_play_app(profile: str, name: str) -> dict:
    """Create one Play app in RevenueCat. Contained single-app mutation."""
    resolved = _profile(profile)
    package_name = resolved.package_name
    if not package_name:
        raise ValueError(f"profile {profile!r} has no package_name")
    result = _client(resolved).create_play_app(
        resolved.revenuecat_project_id,
        name,
        package_name,
        play_credentials.revenuecat_json(),
    )
    return _tag(result, "contained")


def rc_create_product(
    profile: str,
    app_id: str,
    store_identifier: str,
    product_type: str,
    display_name: str | None = None,
) -> dict:
    """Register an existing store product with RevenueCat. Contained mutation."""
    resolved = _profile(profile)
    result = _client(resolved).create_product(
        resolved.revenuecat_project_id,
        app_id,
        store_identifier,
        product_type,
        display_name,
    )
    return _tag(result, "contained")


def rc_create_entitlement(profile: str, lookup_key: str, display_name: str) -> dict:
    """Create an empty entitlement; attaching products is gated separately."""
    resolved = _profile(profile)
    result = _client(resolved).create_entitlement(
        resolved.revenuecat_project_id, lookup_key, display_name
    )
    return _tag(result, "contained")


def rc_create_offering(
    profile: str,
    lookup_key: str,
    display_name: str,
    is_current: bool = False,
) -> dict:
    """Create an offering. Making it current requires local human approval."""
    resolved = _profile(profile)
    approved = False
    risk = "contained"
    if is_current:
        risk = "high"
        approved, refusal = _gate(
            "Approve current RevenueCat offering",
            f"Profile: {profile}\nProject: {resolved.revenuecat_project_id}\nOffering: {lookup_key}\nSet current: yes",
        )
        if not approved:
            return refusal
    result = _client(resolved).create_offering(
        resolved.revenuecat_project_id,
        lookup_key,
        display_name,
        is_current=is_current,
    )
    return _tag(result, risk, approved)


def rc_create_package(
    profile: str,
    offering_id: str,
    lookup_key: str,
    display_name: str,
    position: int | None = None,
) -> dict:
    """Create an empty package; attaching products is gated separately."""
    resolved = _profile(profile)
    result = _client(resolved).create_package(
        resolved.revenuecat_project_id,
        offering_id,
        lookup_key,
        display_name,
        position,
    )
    return _tag(result, "contained")


def rc_attach_products_to_entitlement(
    profile: str,
    entitlement_id: str,
    product_ids: list[str],
) -> dict:
    """Attach products to an entitlement. Requires local human approval."""
    resolved = _profile(profile)
    approved, refusal = _gate(
        "Approve RevenueCat entitlement change",
        f"Profile: {profile}\nProject: {resolved.revenuecat_project_id}\nEntitlement: {entitlement_id}\nProducts: {', '.join(product_ids)}",
    )
    if not approved:
        return refusal
    result = _client(resolved).attach_products_to_entitlement(
        resolved.revenuecat_project_id, entitlement_id, product_ids
    )
    return _tag(result, "high", True)


def rc_attach_products_to_package(
    profile: str,
    package_id: str,
    products: list[dict],
) -> dict:
    """Attach products to a package. Requires local human approval."""
    resolved = _profile(profile)
    product_ids = [str(item.get("product_id", "?")) for item in products]
    approved, refusal = _gate(
        "Approve RevenueCat package change",
        f"Profile: {profile}\nProject: {resolved.revenuecat_project_id}\nPackage: {package_id}\nProducts: {', '.join(product_ids)}",
    )
    if not approved:
        return refusal
    result = _client(resolved).attach_products_to_package(
        resolved.revenuecat_project_id, package_id, products
    )
    return _tag(result, "high", True)


def rc_create_product_in_store(profile: str, product_id: str) -> dict:
    """Create backing-store state. Requires local human approval."""
    resolved = _profile(profile)
    approved, refusal = _gate(
        "Approve store product creation",
        f"Profile: {profile}\nProject: {resolved.revenuecat_project_id}\nRevenueCat product: {product_id}\nThis will create or update backing-store state.",
    )
    if not approved:
        return refusal
    result = _client(resolved).create_product_in_store(
        resolved.revenuecat_project_id, product_id
    )
    return _tag(result, "high", True)


def register(server) -> None:
    for tool in (
        rc_create_play_app,
        rc_create_product,
        rc_create_entitlement,
        rc_create_offering,
        rc_create_package,
        rc_attach_products_to_entitlement,
        rc_attach_products_to_package,
        rc_create_product_in_store,
    ):
        server.tool()(tool)
    mcp_revenuecat_management.register(server)
