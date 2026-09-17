"""Google Play listing, tester, review, image, and diagnostics MCP tools."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import config, human_approval
from . import play_management


def _package(profile: str) -> str:
    package_name = config.load_profile(profile).package_name
    if not package_name:
        raise ValueError(f"profile {profile!r} has no package_name")
    return package_name


def _client(profile: str) -> play_management.PlayManagementClient:
    return play_management.PlayManagementClient(_package(profile))


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
        "detail": "High-risk Google Play action was not executed.",
    }


def play_list_listings(profile: str) -> list[dict]:
    """List every localized Play Store listing for a profile."""
    return _client(profile).list_listings()


def play_get_listing(profile: str, language: str = "en-US") -> dict:
    """Read one localized Play Store listing."""
    return _client(profile).get_listing(language)


def play_list_images(profile: str, language: str, image_type: str) -> list[dict]:
    """List Play Store images/screenshots for one locale and image type."""
    return _client(profile).list_images(language, image_type)


def play_get_testers(profile: str, track: str = "internal") -> dict:
    """Read Google Groups configured as testers for a Play track."""
    return _client(profile).get_testers(track)


def play_country_availability(profile: str, track: str = "production") -> dict:
    """Read country availability for a Play track."""
    return _client(profile).get_country_availability(track)


def play_list_reviews(
    profile: str,
    max_results: int = 100,
    translation_language: str | None = None,
) -> list[dict]:
    """List Play reviews with rating, app version, language and device metadata."""
    return _client(profile).list_reviews(
        max_results=max_results,
        translation_language=translation_language,
    )


def play_update_listing(
    profile: str,
    language: str,
    title: str,
    short_description: str,
    full_description: str,
    video: str | None = None,
    dry_run: bool = True,
) -> dict:
    """Create/update localized store copy; a real public change requires approval."""
    if not dry_run:
        approved, refusal = _gate(
            "Approve Google Play listing update",
            f"Profile: {profile}\nLanguage: {language}\nTitle: {title}\n"
            "This changes public Play Store metadata.",
        )
        if not approved:
            return refusal
    else:
        approved = False
    result = _client(profile).update_listing(
        language,
        title=title,
        short_description=short_description,
        full_description=full_description,
        video=video,
        dry_run=dry_run,
    )
    return _tag(result, "observe" if dry_run else "high", approved)


def play_upload_image(
    profile: str,
    language: str,
    image_type: str,
    image_path: str,
    dry_run: bool = True,
) -> dict:
    """Upload a Play Store image; a committed public asset change requires approval."""
    if not dry_run:
        approved, refusal = _gate(
            "Approve Google Play image update",
            f"Profile: {profile}\nLanguage: {language}\nType: {image_type}\n"
            f"Path: {Path(image_path).expanduser()}",
        )
        if not approved:
            return refusal
    else:
        approved = False
    result = _client(profile).upload_image(
        language,
        image_type,
        Path(image_path),
        dry_run=dry_run,
    )
    return _tag(result, "observe" if dry_run else "high", approved)


def play_update_testers(
    profile: str,
    track: str,
    google_groups: list[str],
    dry_run: bool = True,
) -> dict:
    """Update track testers. API supports Google Groups, not Console email lists."""
    if not dry_run:
        approved, refusal = _gate(
            "Approve Google Play tester update",
            f"Profile: {profile}\nTrack: {track}\nGoogle Groups: {', '.join(google_groups)}",
        )
        if not approved:
            return refusal
    else:
        approved = False
    result = _client(profile).update_testers(track, google_groups, dry_run=dry_run)
    return _tag(result, "observe" if dry_run else "high", approved)


def play_reply_review(profile: str, review_id: str, reply_text: str) -> dict:
    """Reply publicly to a Play review after local human approval."""
    approved, refusal = _gate(
        "Approve Google Play review reply",
        f"Profile: {profile}\nReview: {review_id}\nReply:\n{reply_text}",
    )
    if not approved:
        return refusal
    result = _client(profile).reply_review(review_id, reply_text)
    return _tag(result, "high", True)


def play_upload_deobfuscation_file(
    profile: str,
    version_code: int,
    file_type: str,
    file_path: str,
    dry_run: bool = True,
) -> dict:
    """Attach ProGuard/R8 mapping or native symbols to a Play artifact."""
    result = _client(profile).upload_deobfuscation_file(
        version_code,
        file_type,
        Path(file_path),
        dry_run=dry_run,
    )
    return _tag(result, "observe" if dry_run else "contained")


def register(server) -> None:
    for tool in (
        play_list_listings,
        play_get_listing,
        play_list_images,
        play_get_testers,
        play_country_availability,
        play_list_reviews,
        play_update_listing,
        play_upload_image,
        play_update_testers,
        play_reply_review,
        play_upload_deobfuscation_file,
    ):
        server.tool()(tool)
