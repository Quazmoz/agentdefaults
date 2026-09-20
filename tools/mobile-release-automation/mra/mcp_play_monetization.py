"""Modern Google Play monetization tools for the risk-gated MCP surface."""

from __future__ import annotations

from typing import Any

from . import config, human_approval
from . import play as play_module


def _package(profile: str) -> str:
    package_name = config.load_profile(profile).package_name
    if not package_name:
        raise ValueError(f"profile {profile!r} has no package_name")
    return package_name


def _client(profile: str) -> play_module.PlayClient:
    return play_module.PlayClient(_package(profile))


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
        "detail": "High-risk Google Play monetization action was not executed.",
    }


def play_convert_region_prices(
    profile: str,
    currency_code: str,
    units: str = "0",
    nanos: int = 0,
    product_tax_category_code: str | None = None,
) -> dict:
    """Convert a tax-exclusive price and return Google's current regionVersion."""
    price = {"currencyCode": currency_code, "units": str(units), "nanos": nanos}
    return _client(profile).convert_region_prices(price, product_tax_category_code)


def play_create_subscription(
    profile: str,
    product_id: str,
    body: dict,
    regions_version: str,
) -> dict:
    """Create a Play subscription in draft state after local approval."""
    approved, refusal = _gate(
        "Approve Google Play subscription creation",
        f"Profile: {profile}\nPackage: {_package(profile)}\nProduct: {product_id}\n"
        f"Regions version: {regions_version}\n"
        "This creates monetization catalog state in Google Play. Base plans remain draft until activated.",
    )
    if not approved:
        return refusal
    result = _client(profile).create_subscription(product_id, body, regions_version)
    return _tag(result, "high", True)


def play_activate_base_plan(
    profile: str,
    product_id: str,
    base_plan_id: str,
) -> dict:
    """Activate a subscription base plan after local approval."""
    approved, refusal = _gate(
        "Approve Google Play base-plan activation",
        f"Profile: {profile}\nPackage: {_package(profile)}\n"
        f"Subscription: {product_id}\nBase plan: {base_plan_id}\n"
        "Activation makes this base plan available to new subscribers.",
    )
    if not approved:
        return refusal
    result = _client(profile).activate_base_plan(product_id, base_plan_id)
    return _tag(result, "high", True)


def play_upsert_one_time_product(
    profile: str,
    product_id: str,
    body: dict,
    regions_version: str,
    update_mask: str | None = None,
    allow_missing: bool = True,
) -> dict:
    """Create/update a modern Play OneTimeProduct after local approval."""
    approved, refusal = _gate(
        "Approve Google Play one-time-product upsert",
        f"Profile: {profile}\nPackage: {_package(profile)}\nProduct: {product_id}\n"
        f"Update mask: {update_mask or 'derived from supplied fields'}\nAllow create if missing: {allow_missing}\n"
        f"Regions version: {regions_version}",
    )
    if not approved:
        return refusal
    result = _client(profile).upsert_one_time_product(
        product_id,
        body,
        regions_version,
        update_mask=update_mask,
        allow_missing=allow_missing,
    )
    return _tag(result, "high", True)


def play_set_purchase_option_active(
    profile: str,
    product_id: str,
    purchase_option_id: str,
    active: bool = True,
) -> dict:
    """Activate/deactivate a one-time-product purchase option after approval."""
    verb = "activate" if active else "deactivate"
    approved, refusal = _gate(
        f"Approve Google Play purchase-option {verb}",
        f"Profile: {profile}\nPackage: {_package(profile)}\n"
        f"Product: {product_id}\nPurchase option: {purchase_option_id}\n"
        f"Requested state: {'ACTIVE' if active else 'INACTIVE'}",
    )
    if not approved:
        return refusal
    result = _client(profile).set_purchase_option_active(
        product_id, purchase_option_id, active=active
    )
    return _tag(result, "high", True)


def register(server) -> None:
    for tool in (
        play_convert_region_prices,
        play_create_subscription,
        play_activate_base_plan,
        play_upsert_one_time_product,
        play_set_purchase_option_active,
    ):
        server.tool()(tool)
