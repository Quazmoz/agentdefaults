"""Google Play Developer API v3 operations.

Reference: https://developers.google.com/android-publisher/api-ref/rest/v3
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Sequence
import json

from . import auth

BASE = "https://androidpublisher.googleapis.com/androidpublisher/v3"
UPLOAD_BASE = "https://androidpublisher.googleapis.com/upload/androidpublisher/v3"

# An upload of a large bundle is slow; Google recommends raising the timeout.
UPLOAD_TIMEOUT_SECONDS = 600
REQUEST_TIMEOUT_SECONDS = 60

RELEASE_STATUSES = ("draft", "inProgress", "halted", "completed")


class PlayError(RuntimeError):
    pass


def _raise_for_status(response, action: str) -> None:
    if response.ok:
        return
    try:
        detail = json.dumps(response.json(), indent=2)
    except ValueError:
        detail = response.text
    raise PlayError(f"{action} failed with HTTP {response.status_code}:\n{detail}")


class PlayClient:
    """Thin client over the Play Developer API for one package."""

    def __init__(self, package_name: str, session=None) -> None:
        self.package_name = package_name
        self.session = session or auth.play_session()

    # ---- plumbing ----------------------------------------------------------

    def _url(self, suffix: str, base: str = BASE) -> str:
        return f"{base}/applications/{self.package_name}{suffix}"

    def _request(self, method: str, suffix: str, action: str, **kwargs) -> Any:
        kwargs.setdefault("timeout", REQUEST_TIMEOUT_SECONDS)
        response = self.session.request(method, self._url(suffix), **kwargs)
        _raise_for_status(response, action)
        return response.json() if response.content else {}

    # ---- edits -------------------------------------------------------------

    @contextmanager
    def edit(
        self,
        commit: bool,
        changes_not_sent_for_review: bool = False,
        validate: bool = True,
    ) -> Iterator[str]:
        """Open a Play edit, and always clean it up.

        An abandoned edit blocks nothing, but leaving them behind makes the
        Console confusing, so a failed or dry-run edit is deleted explicitly.
        """
        created = self._request("POST", "/edits", "create edit")
        edit_id = created["id"]
        committed = False
        try:
            yield edit_id
            if commit:
                params = {}
                if changes_not_sent_for_review:
                    params["changesNotSentForReview"] = "true"
                self._request(
                    "POST",
                    f"/edits/{edit_id}:commit",
                    "commit edit",
                    params=params,
                )
                committed = True
            elif validate:
                self._request("POST", f"/edits/{edit_id}:validate", "validate edit")
        finally:
            if not committed:
                self._delete_edit_quietly(edit_id)

    def _delete_edit_quietly(self, edit_id: str) -> None:
        try:
            self.session.delete(
                self._url(f"/edits/{edit_id}"), timeout=REQUEST_TIMEOUT_SECONDS
            )
        except Exception:  # noqa: BLE001 - cleanup must not mask the real error
            pass

    # ---- bundles and tracks ------------------------------------------------

    def upload_bundle(self, edit_id: str, aab_path: Path) -> dict:
        """Upload an .aab and return the Bundle resource (versionCode, sha1, sha256)."""
        if not aab_path.is_file():
            raise PlayError(f"bundle not found: {aab_path}")
        with aab_path.open("rb") as handle:
            response = self.session.post(
                self._url(f"/edits/{edit_id}/bundles", base=UPLOAD_BASE),
                params={"uploadType": "media"},
                headers={"Content-Type": "application/octet-stream"},
                data=handle,
                timeout=UPLOAD_TIMEOUT_SECONDS,
            )
        _raise_for_status(response, f"upload {aab_path.name}")
        return response.json()

    def get_track(self, edit_id: str, track: str) -> dict:
        return self._request("GET", f"/edits/{edit_id}/tracks/{track}", f"read track {track}")

    def list_tracks(self, edit_id: str) -> list[dict]:
        payload = self._request("GET", f"/edits/{edit_id}/tracks", "list tracks")
        return payload.get("tracks", [])

    def set_track_release(
        self,
        edit_id: str,
        track: str,
        version_codes: Sequence[int],
        status: str = "completed",
        release_notes: dict[str, str] | None = None,
        user_fraction: float | None = None,
        release_name: str | None = None,
    ) -> dict:
        """Assign version codes to a track as a single release."""
        if status not in RELEASE_STATUSES:
            raise PlayError(f"invalid release status {status!r}; expected one of {RELEASE_STATUSES}")
        if status == "inProgress" and user_fraction is None:
            raise PlayError("status 'inProgress' requires a user fraction (staged rollout)")
        if user_fraction is not None and not 0 < user_fraction < 1:
            raise PlayError("user fraction must be strictly between 0 and 1")

        release: dict[str, Any] = {
            "versionCodes": [str(code) for code in version_codes],
            "status": status,
        }
        if release_name:
            release["name"] = release_name
        if user_fraction is not None:
            release["userFraction"] = user_fraction
        if release_notes:
            release["releaseNotes"] = [
                {"language": language, "text": text}
                for language, text in sorted(release_notes.items())
            ]

        return self._request(
            "PUT",
            f"/edits/{edit_id}/tracks/{track}",
            f"update track {track}",
            json={"track": track, "releases": [release]},
        )

    # ---- monetization ------------------------------------------------------

    def create_subscription(self, product_id: str, body: dict, regions_version: str) -> dict:
        return self._request(
            "POST",
            "/subscriptions",
            f"create subscription {product_id}",
            params={"productId": product_id, "regionsVersion.version": regions_version},
            json=body,
        )

    def list_subscriptions(self) -> list[dict]:
        payload = self._request("GET", "/subscriptions", "list subscriptions")
        return payload.get("subscriptions", [])

    def create_in_app_product(self, body: dict) -> dict:
        return self._request(
            "POST", "/inappproducts", "create in-app product", json=body
        )

    def list_in_app_products(self) -> list[dict]:
        payload = self._request("GET", "/inappproducts", "list in-app products")
        return payload.get("inappproduct", [])


# ---- high level operations -------------------------------------------------


def publish_bundle(
    package_name: str,
    aab_path: Path,
    track: str,
    status: str = "completed",
    release_notes: dict[str, str] | None = None,
    user_fraction: float | None = None,
    release_name: str | None = None,
    dry_run: bool = False,
    changes_not_sent_for_review: bool = False,
    client: PlayClient | None = None,
) -> dict:
    """Upload a bundle and assign it to a track in one edit.

    With dry_run the edit is validated and then discarded, so nothing reaches
    testers. Note that the upload itself still happens: validation cannot be
    performed against a bundle Play has not received.
    """
    play = client or PlayClient(package_name)
    result: dict[str, Any] = {
        "package_name": package_name,
        "track": track,
        "dry_run": dry_run,
    }
    with play.edit(commit=not dry_run, changes_not_sent_for_review=changes_not_sent_for_review) as edit_id:
        bundle = play.upload_bundle(edit_id, aab_path)
        result["version_code"] = bundle["versionCode"]
        result["sha256"] = bundle.get("sha256")
        play.set_track_release(
            edit_id,
            track,
            [bundle["versionCode"]],
            status=status,
            release_notes=release_notes,
            user_fraction=user_fraction,
            release_name=release_name,
        )
        result["edit_id"] = edit_id
    result["committed"] = not dry_run
    return result


def promote(
    package_name: str,
    from_track: str,
    to_track: str,
    version_codes: Sequence[int] | None = None,
    status: str = "completed",
    user_fraction: float | None = None,
    release_notes: dict[str, str] | None = None,
    dry_run: bool = False,
    client: PlayClient | None = None,
) -> dict:
    """Promote existing version codes from one track to another.

    Promotion never rebuilds: the artifact Play already qualified on the source
    track is the artifact that moves, preserving build identity.
    """
    play = client or PlayClient(package_name)
    result: dict[str, Any] = {
        "package_name": package_name,
        "from_track": from_track,
        "to_track": to_track,
        "dry_run": dry_run,
    }
    with play.edit(commit=not dry_run) as edit_id:
        codes = list(version_codes or [])
        if not codes:
            source = play.get_track(edit_id, from_track)
            releases = source.get("releases", [])
            if not releases:
                raise PlayError(f"track {from_track!r} has no releases to promote")
            codes = [int(code) for code in releases[0].get("versionCodes", [])]
            if not codes:
                raise PlayError(f"track {from_track!r} newest release has no version codes")
        result["version_codes"] = codes
        play.set_track_release(
            edit_id,
            to_track,
            codes,
            status=status,
            release_notes=release_notes,
            user_fraction=user_fraction,
        )
        result["edit_id"] = edit_id
    result["committed"] = not dry_run
    return result


def track_status(package_name: str, client: PlayClient | None = None) -> list[dict]:
    """Read every track without committing anything."""
    play = client or PlayClient(package_name)
    with play.edit(commit=False, validate=False) as edit_id:
        return play.list_tracks(edit_id)
