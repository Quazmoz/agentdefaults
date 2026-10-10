"""One-approval, hash-bound Play listing and regional-price execution batch.

The operator reviews one complete proposal and explicitly authorizes its exact
manifest SHA-256. This module cannot see a Codex conversation or prove its
approval; only the operator-facing CLI may invoke apply, with --yes and the
already-approved SHA. MCP high-risk per-action dialogs remain unchanged.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import re

from . import config, play as play_module, play_management, regional_pricing

MAX_ACTIONS = 50
TEXT_FIELDS = ("title", "shortDescription", "fullDescription")
TEXT_LIMITS = {"title": 30, "shortDescription": 80, "fullDescription": 4000}
ALLOWED_KINDS = {"listing-create", "listing-update", "pricing-apply"}
SHA256_RE = re.compile(r"[a-f0-9]{64}\Z")
LOCALE_RE = re.compile(r"[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*\Z")


class BatchError(ValueError):
    """Invalid, stale or unauthorized-by-scope batch configuration."""


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _parse_datetime(value: Any) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise BatchError("batch timestamps must be UTC RFC3339 values ending in Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise BatchError("invalid batch timestamp") from error
    return parsed


def _listing(payload: Any, language: str, *, allow_video: bool = False) -> dict:
    if not isinstance(payload, dict):
        raise BatchError("listing snapshot must be an object")
    fields = {"language", *TEXT_FIELDS}
    if allow_video:
        fields.add("video")
    if set(payload) - fields or not all(f in payload for f in TEXT_FIELDS):
        raise BatchError("listing must contain exact title/shortDescription/fullDescription fields")
    if payload.get("language", language) != language:
        raise BatchError("listing language does not match the action locale")
    result = {"language": language}
    for field in TEXT_FIELDS:
        value = payload[field]
        if not isinstance(value, str):
            raise BatchError(f"listing {field} must be a string")
        count = len(value.encode("utf-16-le")) // 2
        if not value.strip() or count > TEXT_LIMITS[field]:
            raise BatchError(f"invalid listing {field}: {count} UTF-16 units")
        result[field] = value
    if "video" in payload:
        video = payload["video"]
        if video is not None and not isinstance(video, str):
            raise BatchError("listing video must be a string or null")
        result["video"] = video
    return result


def _validate_action(action: Any) -> dict:
    if not isinstance(action, dict) or action.get("kind") not in ALLOWED_KINDS:
        raise BatchError("unsupported batch action kind")
    kind = action["kind"]
    expected_keys = {"kind", "profile", "package_name"}
    expected_keys |= {"plan_id"} if kind == "pricing-apply" else {"language", "desired"}
    if kind == "listing-update":
        expected_keys.add("expected_current")
    if set(action) != expected_keys:
        raise BatchError(f"{kind} action fields must match its exact schema")
    for field in ("profile", "package_name"):
        if not isinstance(action[field], str) or not action[field].strip():
            raise BatchError(f"action missing {field}")
    if kind == "pricing-apply":
        if not isinstance(action["plan_id"], str) or not SHA256_RE.fullmatch(action["plan_id"]):
            raise BatchError("pricing action must identify an exact SHA-256 plan_id")
    else:
        locale = action["language"]
        if not isinstance(locale, str) or not LOCALE_RE.fullmatch(locale):
            raise BatchError("invalid listing locale")
        _listing(action["desired"], locale)
        if kind == "listing-update":
            _listing(action["expected_current"], locale, allow_video=True)
    return action


def load_manifest(path_value: str, approved_sha256: str) -> dict:
    """Validate digest before parsing; never silently expand approved actions."""
    if not SHA256_RE.fullmatch(approved_sha256):
        raise BatchError("--sha256 must be the 64-character lowercase manifest digest")
    path = Path(path_value).expanduser()
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise BatchError(f"cannot read batch manifest: {error}") from error
    if len(raw) > 300_000:
        raise BatchError("batch manifest exceeds 300 KB")
    if _digest(raw) != approved_sha256:
        raise BatchError("batch manifest bytes differ from the approved SHA-256")
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise BatchError("batch manifest must be UTF-8 JSON") from error
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema_version", "created_at", "expires_at", "actions"
    } or manifest["schema_version"] != 1:
        raise BatchError("unsupported batch manifest schema")
    created = _parse_datetime(manifest["created_at"])
    expires = _parse_datetime(manifest["expires_at"])
    now = datetime.now(timezone.utc)
    if not created <= now + timedelta(minutes=5) or not now < expires:
        raise BatchError("batch manifest is not yet valid or has expired")
    if not created < expires <= created + timedelta(days=7):
        raise BatchError("batch validity window must be at most seven days")
    actions = manifest["actions"]
    if not isinstance(actions, list) or not 1 <= len(actions) <= MAX_ACTIONS:
        raise BatchError("batch must contain between 1 and 50 explicit actions")
    keys: set[tuple] = set()
    pricing_products: set[tuple[str, str]] = set()
    for action in actions:
        _validate_action(action)
        key = (
            action["package_name"],
            action["kind"] == "pricing-apply",
            action.get("plan_id") if action["kind"] == "pricing-apply" else action["language"],
        )
        if key in keys:
            raise BatchError("same package and locale/plan cannot occur twice in a batch")
        keys.add(key)
        if action["kind"] == "pricing-apply":
            plan = regional_pricing.load_plan(action["plan_id"])
            product = (action["package_name"], plan["product_id"])
            if product in pricing_products:
                raise BatchError("multiple plans for one Play product must be combined and reapproved")
            pricing_products.add(product)
    return manifest


def _match_listing(live: dict, snapshot: dict) -> bool:
    return all(live.get(k) == snapshot[k] for k in TEXT_FIELDS) and (
        "video" not in snapshot or live.get("video") == snapshot["video"]
    )


def _resolve_package(action: dict) -> None:
    profile = config.load_profile(action["profile"])
    if profile.package_name != action["package_name"]:
        raise BatchError(f"profile/package mismatch: {action['profile']!r}")


def _inspect_action(action: dict) -> dict:
    _resolve_package(action)
    kind = action["kind"]
    package = action["package_name"]
    if kind == "pricing-apply":
        plan = regional_pricing.load_plan(action["plan_id"])
        if (plan.get("package_name") != package or plan.get("profile") != action["profile"]
                or not plan.get("changes")):
            raise BatchError("pricing plan does not match approved action scope")
        client = play_module.PlayClient(package)
        current = client.get_one_time_product(plan["product_id"])
        if regional_pricing._matches_plan(current, plan, proposed=True):  # noqa: SLF001
            status = "already_applied"
        elif regional_pricing._source_fingerprint(current) != plan["source_fingerprint"]:  # noqa: SLF001
            raise BatchError("pricing plan source has drifted")
        elif regional_pricing._current_region_version(client, plan) != plan["regions_version"]:  # noqa: SLF001
            raise BatchError("pricing plan region version has drifted")
        else:
            status = "ready"
        return {"kind": kind, "package_name": package, "plan_id": plan["plan_id"],
                "product_id": plan["product_id"], "purchase_option_id": plan["purchase_option_id"],
                "changes": plan["changes"], "status": status}

    manager = play_management.PlayManagementClient(package)
    listings = manager.list_listings()
    if not isinstance(listings, list) or any(
        not isinstance(item, dict) or not isinstance(item.get("language"), str)
        for item in listings
    ):
        raise BatchError("invalid live Play locale inventory")
    language = action["language"]
    present = language in {item["language"] for item in listings}
    if not present:
        if kind == "listing-update":
            raise BatchError(f"expected locale {language} is absent")
        status = "ready"
    else:
        current = manager.get_listing(language)
        if kind == "listing-create":
            if not _match_listing(current, action["desired"]) or current.get("video"):
                raise BatchError(f"locale {language} already exists with different metadata")
            status = "already_applied"
        elif _match_listing(current, action["desired"]) and (
            current.get("video") == action["expected_current"].get("video")
        ):
            status = "already_applied"
        elif _match_listing(current, action["expected_current"]):
            # A proposed text-only update must preserve a known promo video.
            if current.get("video") and "video" not in action["expected_current"]:
                raise BatchError("expected-current must include live promotional video")
            status = "ready"
        else:
            raise BatchError(f"locale {language} has drifted from approved before/after")
    return {"kind": kind, "package_name": package,
            "language": language, "status": status,
            "desired": action["desired"]}


def preflight(manifest: dict) -> list[dict]:
    """Check the entire batch before the first external write."""
    return [_inspect_action(action) for action in manifest["actions"]]


def _apply_action(action: dict) -> dict:
    snapshot = _inspect_action(action)  # recheck immediately before each write
    if snapshot["status"] == "already_applied":
        return {**snapshot, "status": "already_applied", "verified": True}
    kind = action["kind"]
    if kind == "pricing-apply":
        result = regional_pricing.apply_one_time_product_plan(
            action["package_name"], action["plan_id"], profile=action["profile"]
        )
        return {**snapshot, "status": result["status"], "verified": result["verified"]}

    manager = play_management.PlayManagementClient(action["package_name"])
    desired = action["desired"]
    fields = {"title": desired["title"], "short_description": desired["shortDescription"],
              "full_description": desired["fullDescription"], "dry_run": False}
    if kind == "listing-create":
        manager.create_listing(action["language"], **fields)
    else:
        # This check takes place again within the same Play edit as the PUT.
        expected = action["expected_current"]
        manager.update_listing(
            action["language"], **fields, expected_current=expected,
            **({"video": expected["video"]} if expected.get("video") else {}),
        )
    actual = manager.get_listing(action["language"])
    if not _match_listing(actual, desired):
        raise BatchError("Play committed listing text but exact read-back differs")
    if kind == "listing-update" and "video" in action["expected_current"]:
        if actual.get("video") != action["expected_current"]["video"]:
            raise BatchError("listing promotional video changed unexpectedly")
    return {**snapshot, "status": "applied", "verified": True}


def apply(manifest: dict) -> dict:
    """All-or-stop. Partial successes remain applied; never blindly roll back."""
    preflight(manifest)
    results = []
    for index, action in enumerate(manifest["actions"]):
        try:
            results.append({"index": index, **_apply_action(action)})
        except (BatchError, play_module.PlayError, regional_pricing.PricingError,
                config.ConfigError) as error:
            return {"status": "partial_failure", "stopped_at": index,
                    "results": results,
                    "error": str(error),
                    "remaining": len(manifest["actions"]) - index,
                    "recovery": "Read live state, fix drift, re-plan and re-approve any changed payload. "
                                "Never blindly retry uncertain commits."}
    return {"status": "verified", "results": results,
            "publication_state": "not_verified_by_api"}
