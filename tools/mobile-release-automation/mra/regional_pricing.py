"""Deterministic, approval-bound Google Play regional pricing plans.

The LLM may request a plan, but it never supplies live price values to the apply
path. A plan is derived from authoritative Play state, persisted under MRA_HOME,
hashed, checked for drift, and then applied by plan id only.
"""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any
import hashlib
import json
import os

from . import config
from . import play as play_module

PLAN_SCHEMA_VERSION = 1
POLICY_NAME = "purchasing-power-v1"

# Deliberately narrow first policy. Reference markets such as US/GB are not
# changed. Each factor is applied to the current US reference price, then sent
# through Google's convertRegionPrices endpoint so Play supplies a locally valid
# currency and country-specific price pattern.
POLICIES: dict[str, dict[str, Decimal]] = {
    POLICY_NAME: {
        "IN": Decimal("0.35"),
        "ID": Decimal("0.40"),
        "PH": Decimal("0.45"),
        "TR": Decimal("0.45"),
        "VN": Decimal("0.45"),
        "TH": Decimal("0.50"),
        "BR": Decimal("0.55"),
        "MY": Decimal("0.55"),
        "MX": Decimal("0.60"),
        "ZA": Decimal("0.60"),
    }
}


class PricingError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _plan_dir() -> Path:
    path = config.ensure_home() / "pricing-plans"
    path.mkdir(parents=True, exist_ok=True)
    path.chmod(0o700)
    return path


def _plan_path(plan_id: str) -> Path:
    if not plan_id or any(ch not in "0123456789abcdef" for ch in plan_id) or len(plan_id) != 64:
        raise PricingError("plan_id must be a 64-character lowercase sha256")
    return _plan_dir() / f"{plan_id}.json"


def _money_decimal(money: dict[str, Any]) -> Decimal:
    units = Decimal(str(money.get("units", "0")))
    nanos = Decimal(str(money.get("nanos", 0))) / Decimal("1000000000")
    return units + nanos


def _decimal_money(value: Decimal, currency_code: str) -> dict[str, Any]:
    if value <= 0:
        raise PricingError("reference price after policy adjustment must be positive")
    nanos_total = int(
        (value * Decimal("1000000000")).to_integral_value(rounding=ROUND_HALF_UP)
    )
    units, nanos = divmod(nanos_total, 1_000_000_000)
    result: dict[str, Any] = {
        "currencyCode": currency_code,
        "units": str(units),
    }
    if nanos:
        result["nanos"] = nanos
    return result


def _money_key(money: dict[str, Any] | None) -> tuple[str, str, int] | None:
    if not money:
        return None
    return (
        str(money.get("currencyCode", "")),
        str(money.get("units", "0")),
        int(money.get("nanos", 0)),
    )


def _purchase_option(product: dict[str, Any], purchase_option_id: str) -> dict[str, Any]:
    for option in product.get("purchaseOptions", []):
        if option.get("purchaseOptionId") == purchase_option_id:
            return option
    known = sorted(
        str(item.get("purchaseOptionId"))
        for item in product.get("purchaseOptions", [])
        if item.get("purchaseOptionId")
    )
    raise PricingError(
        f"purchase option {purchase_option_id!r} not found; known: {known or '(none)'}"
    )


def _regions(option: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item["regionCode"]).upper(): item
        for item in option.get("regionalPricingAndAvailabilityConfigs", [])
        if item.get("regionCode")
    }


def _source_fingerprint(product: dict[str, Any]) -> str:
    # Pricing updates replace purchaseOptions as one coherent field. Fingerprint
    # the whole field so unrelated option changes also invalidate an old plan.
    return _sha256(product.get("purchaseOptions", []))


def _policy(name: str) -> dict[str, Decimal]:
    try:
        return POLICIES[name]
    except KeyError as error:
        raise PricingError(
            f"unknown pricing policy {name!r}; known: {', '.join(sorted(POLICIES))}"
        ) from error


def _region_version(conversion: dict[str, Any]) -> str:
    version = conversion.get("regionVersion", {}).get("version")
    if not version:
        raise PricingError("Play convertRegionPrices response had no regionVersion.version")
    return str(version)


def create_one_time_product_plan(
    package_name: str,
    product_id: str,
    purchase_option_id: str,
    *,
    profile: str | None = None,
    policy_name: str = POLICY_NAME,
    reference_region: str = "US",
    target_regions: list[str] | None = None,
    client: play_module.PlayClient | None = None,
) -> dict[str, Any]:
    """Create and persist a reviewable regional-price plan without changing Play."""
    play = client or play_module.PlayClient(package_name)
    product = play.get_one_time_product(product_id)
    option = _purchase_option(product, purchase_option_id)
    current_regions = _regions(option)

    reference_region = reference_region.upper()
    reference = current_regions.get(reference_region)
    if not reference or reference.get("availability") != "AVAILABLE" or not reference.get("price"):
        raise PricingError(
            f"reference region {reference_region} must already be AVAILABLE with a price"
        )
    reference_price = deepcopy(reference["price"])
    currency_code = str(reference_price.get("currencyCode", ""))
    if not currency_code:
        raise PricingError(f"reference region {reference_region} has no currencyCode")

    policy = _policy(policy_name)
    requested = [item.upper() for item in (target_regions or list(policy))]
    unknown = sorted(set(requested) - set(policy))
    if unknown:
        raise PricingError(
            "requested regions are not in the selected policy: " + ", ".join(unknown)
        )
    if reference_region in requested:
        raise PricingError("reference region cannot be changed by this pricing policy")

    eligible: dict[str, dict[str, Any]] = {}
    skipped: list[dict[str, str]] = []
    for region_code in sorted(set(requested)):
        current = current_regions.get(region_code)
        if not current:
            skipped.append({"region_code": region_code, "reason": "not_configured"})
            continue
        if current.get("availability") != "AVAILABLE":
            skipped.append(
                {
                    "region_code": region_code,
                    "reason": f"availability={current.get('availability', 'missing')}",
                }
            )
            continue
        if not current.get("price"):
            skipped.append({"region_code": region_code, "reason": "missing_current_price"})
            continue
        eligible[region_code] = current

    tax_category = (
        product.get("taxAndComplianceSettings", {}).get("productTaxCategoryCode")
    )
    reference_amount = _money_decimal(reference_price)
    conversions: dict[Decimal, dict[str, Any]] = {}
    versions: set[str] = set()

    for factor in sorted({policy[region] for region in eligible}):
        adjusted = _decimal_money(reference_amount * factor, currency_code)
        converted = play.convert_region_prices(adjusted, tax_category)
        conversions[factor] = converted
        versions.add(_region_version(converted))

    if len(versions) > 1:
        raise PricingError(
            "Play changed regionVersion while the plan was being generated; retry planning"
        )

    changes: list[dict[str, Any]] = []
    for region_code, current in sorted(eligible.items()):
        factor = policy[region_code]
        converted = conversions[factor].get("convertedRegionPrices", {}).get(region_code)
        proposed = converted.get("price") if isinstance(converted, dict) else None
        if not proposed:
            skipped.append({"region_code": region_code, "reason": "conversion_missing"})
            continue
        if proposed.get("currencyCode") != current["price"].get("currencyCode"):
            raise PricingError(
                f"currency mismatch for {region_code}: current "
                f"{current['price'].get('currencyCode')} vs proposed "
                f"{proposed.get('currencyCode')}"
            )
        if _money_key(proposed) == _money_key(current["price"]):
            skipped.append({"region_code": region_code, "reason": "already_at_target"})
            continue
        if _money_decimal(proposed) >= _money_decimal(current["price"]):
            skipped.append({"region_code": region_code, "reason": "proposal_not_lower"})
            continue
        changes.append(
            {
                "region_code": region_code,
                "factor": str(factor),
                "availability": current["availability"],
                "current_price": deepcopy(current["price"]),
                "proposed_price": deepcopy(proposed),
            }
        )

    payload: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "profile": profile,
        "package_name": package_name,
        "product_type": "one_time_product",
        "product_id": product_id,
        "purchase_option_id": purchase_option_id,
        "policy_name": policy_name,
        "reference_region": reference_region,
        "reference_price": reference_price,
        "product_tax_category_code": tax_category,
        "source_fingerprint": _source_fingerprint(product),
        "regions_version": next(iter(versions)) if versions else None,
        "changes": changes,
        "skipped": sorted(skipped, key=lambda item: item["region_code"]),
    }
    plan_id = _sha256(payload)
    payload["plan_id"] = plan_id

    path = _plan_path(plan_id)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)

    return {
        **payload,
        "status": "planned" if changes else "no_changes",
        "plan_path": str(path),
    }


def load_plan(plan_id: str) -> dict[str, Any]:
    path = _plan_path(plan_id)
    if not path.is_file():
        raise PricingError(f"pricing plan not found: {plan_id}")
    config._require_private(path)  # noqa: SLF001 - same local sensitive-state policy
    plan = json.loads(path.read_text(encoding="utf-8"))
    if plan.get("plan_id") != plan_id:
        raise PricingError("stored pricing plan id does not match its filename")
    hashed = dict(plan)
    hashed.pop("plan_id", None)
    if _sha256(hashed) != plan_id:
        raise PricingError("stored pricing plan content failed integrity verification")
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise PricingError(
            f"unsupported pricing plan schema {plan.get('schema_version')!r}"
        )
    return plan


def approval_detail(plan: dict[str, Any]) -> str:
    lines = [
        f"App/profile: {plan.get('profile') or '(direct package)'}",
        f"Package: {plan['package_name']}",
        f"Product: {plan['product_id']}",
        f"Purchase option: {plan['purchase_option_id']}",
        f"Plan: {plan['plan_id']}",
        "",
        "Regional price changes:",
    ]
    for change in plan.get("changes", []):
        old = change["current_price"]
        new = change["proposed_price"]
        lines.append(
            f"{change['region_code']}: "
            f"{old.get('currencyCode')} {old.get('units', '0')}.{int(old.get('nanos', 0)):09d} "
            f"-> {new.get('currencyCode')} {new.get('units', '0')}.{int(new.get('nanos', 0)):09d}"
        )
    lines.append("")
    lines.append("No US/GB reference-market price is changed by this plan.")
    return "\n".join(lines)


def _matches_plan(product: dict[str, Any], plan: dict[str, Any], proposed: bool) -> bool:
    source_product = deepcopy(product)
    option = _purchase_option(source_product, plan["purchase_option_id"])
    regions = _regions(option)
    key = "proposed_price" if proposed else "current_price"
    for change in plan.get("changes", []):
        current = regions.get(change["region_code"])
        if not current or _money_key(current.get("price")) != _money_key(change[key]):
            return False
        # Reverse approved prices so the fingerprint also verifies protected
        # prices, availability, and every other purchase-option field.
        current["price"] = deepcopy(change["current_price"])
    return _source_fingerprint(source_product) == plan["source_fingerprint"]


def _current_region_version(
    play: play_module.PlayClient, plan: dict[str, Any]
) -> str:
    converted = play.convert_region_prices(
        plan["reference_price"], plan.get("product_tax_category_code")
    )
    return _region_version(converted)


def apply_one_time_product_plan(
    package_name: str,
    plan_id: str,
    *,
    profile: str | None = None,
    client: play_module.PlayClient | None = None,
) -> dict[str, Any]:
    """Apply exactly one persisted plan, rejecting drift and verifying read-back."""
    plan = load_plan(plan_id)
    if plan["package_name"] != package_name:
        raise PricingError(
            f"plan belongs to {plan['package_name']}, not requested package {package_name}"
        )
    if plan.get("profile") and profile and plan["profile"] != profile:
        raise PricingError(
            f"plan belongs to profile {plan['profile']!r}, not {profile!r}"
        )
    if not plan.get("changes"):
        return {"status": "no_changes", "plan_id": plan_id, "verified": True}

    play = client or play_module.PlayClient(package_name)
    product = play.get_one_time_product(plan["product_id"])

    if _matches_plan(product, plan, proposed=True):
        return {
            "status": "already_applied",
            "plan_id": plan_id,
            "verified": True,
            "changes": plan["changes"],
        }

    if _source_fingerprint(product) != plan["source_fingerprint"]:
        raise PricingError(
            "pricing plan is stale: purchase-option state changed after planning; "
            "generate a new plan and obtain approval again"
        )

    current_version = _current_region_version(play, plan)
    if current_version != plan.get("regions_version"):
        raise PricingError(
            f"pricing plan is stale: Play regionVersion changed from "
            f"{plan.get('regions_version')} to {current_version}; regenerate and re-approve"
        )

    if not _matches_plan(product, plan, proposed=False):
        raise PricingError(
            "pricing plan is stale: one or more source regional prices changed"
        )

    options = deepcopy(product.get("purchaseOptions", []))
    target_option = _purchase_option({"purchaseOptions": options}, plan["purchase_option_id"])
    target_regions = _regions(target_option)
    by_region = {change["region_code"]: change for change in plan["changes"]}
    for region_code, change in by_region.items():
        target_regions[region_code]["price"] = deepcopy(change["proposed_price"])

    # state is output-only and must not be echoed into the patch body.
    for option in options:
        option.pop("state", None)

    play.upsert_one_time_product(
        plan["product_id"],
        {"purchaseOptions": options},
        plan["regions_version"],
        update_mask="purchaseOptions",
        allow_missing=False,
    )

    verified_product = play.get_one_time_product(plan["product_id"])
    if not _matches_plan(verified_product, plan, proposed=True):
        raise PricingError(
            "Play accepted the pricing mutation but read-back did not match the approved plan"
        )

    return {
        "status": "applied",
        "plan_id": plan_id,
        "verified": True,
        "package_name": package_name,
        "product_id": plan["product_id"],
        "purchase_option_id": plan["purchase_option_id"],
        "changes": plan["changes"],
    }
