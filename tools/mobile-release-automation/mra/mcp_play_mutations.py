"""Google Play mutation tools for the local risk-gated MCP server."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import config, human_approval
from . import mcp_play_management, mcp_reconcile
from . import play as play_module


def _package(profile: str) -> str:
    package_name = config.load_profile(profile).package_name
    if not package_name:
        raise ValueError(f"profile {profile!r} has no package_name")
    return package_name


def _is_internal(track: str) -> bool:
    normalized = track.strip().lower()
    return normalized == "internal" or normalized.endswith(":internal")


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


def play_publish_bundle(
    profile: str,
    aab_path: str,
    track: str = "internal",
    release_notes_en_us: str | None = None,
    status: str = "completed",
    dry_run: bool = True,
) -> dict:
    """Publish an AAB; non-internal real releases require human approval."""
    package_name = _package(profile)
    approved = False
    risk = "observe" if dry_run else "contained"
    if not dry_run and not _is_internal(track):
        risk = "high"
        approved, refusal = _gate(
            "Approve Google Play release",
            f"Profile: {profile}\nPackage: {package_name}\nTrack: {track}\nStatus: {status}\nAAB: {Path(aab_path).expanduser()}",
        )
        if not approved:
            return refusal

    result = play_module.publish_bundle(
        package_name,
        Path(aab_path).expanduser(),
        track=track,
        status=status,
        release_notes={"en-US": release_notes_en_us} if release_notes_en_us else None,
        dry_run=dry_run,
    )
    return _tag(result, risk, approved)


def play_promote(
    profile: str,
    source_track: str,
    target_track: str,
    status: str = "completed",
    user_fraction: float | None = None,
    dry_run: bool = True,
) -> dict:
    """Promote a release; non-internal real targets require human approval."""
    package_name = _package(profile)
    approved = False
    risk = "observe" if dry_run else "contained"
    if not dry_run and not _is_internal(target_track):
        risk = "high"
        approved, refusal = _gate(
            "Approve Google Play promotion",
            f"Profile: {profile}\nPackage: {package_name}\nFrom: {source_track}\nTo: {target_track}\nStatus: {status}\nUser fraction: {user_fraction}",
        )
        if not approved:
            return refusal

    result = play_module.promote(
        package_name,
        from_track=source_track,
        to_track=target_track,
        status=status,
        user_fraction=user_fraction,
        dry_run=dry_run,
    )
    return _tag(result, risk, approved)


def register(server) -> None:
    server.tool()(play_publish_bundle)
    server.tool()(play_promote)
    mcp_play_management.register(server)
    mcp_reconcile.register(server)
