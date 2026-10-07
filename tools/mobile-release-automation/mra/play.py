"""Google Play Developer API v3 operations.

Reference: https://developers.google.com/android-publisher/api-ref/rest/v3
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Sequence
import json
import re

from . import auth, redaction

BASE = "https://androidpublisher.googleapis.com/androidpublisher/v3"
UPLOAD_BASE = "https://androidpublisher.googleapis.com/upload/androidpublisher/v3"

# An upload of a large bundle is slow; Google recommends raising the timeout.
UPLOAD_TIMEOUT_SECONDS = 600
REQUEST_TIMEOUT_SECONDS = 60

RELEASE_STATUSES = ("draft", "inProgress", "halted", "completed")


class PlayError(RuntimeError):
    pass


def _publisher_identity() -> str | None:
    """Return the active non-secret service-account email, or None.

    Only the client_email is read. It is an identity, not a credential, and it
    is the fastest way to rule an identity mismatch in or out.
    """
    try:
        from . import play_credentials

        return play_credentials.publisher_info().get("client_email")
    except Exception:  # noqa: BLE001 - diagnostics must not mask the real error
        return None


# Play states an authorization problem in prose, and not only on a 403. A
# monetization create can come back as 400 INVALID_ARGUMENT carrying
# "To fix, request billing permission.", so the status code alone cannot
# separate authorization from a malformed request.
_PERMISSION_LANGUAGE = re.compile(
    r"(?i)(request\s+\w*\s*permission|billing permission|does not have permission"
    r"|no(?:t)? authori[sz]ed|permission denied|insufficient permission)"
)


def classify_play_failure(
    status_code: int,
    api_status: str | None = None,
    api_message: str | None = None,
) -> tuple[str, list[str]]:
    """Name the failure class and the checks that would separate its causes.

    This deliberately does not assert a cause. A Play 403 is consistent with
    several distinct conditions, and naming one of them as "the" reason sends the
    reader to the wrong fix. Report the class, then the checks that discriminate.

    The API message outranks the status code, because Play reports at least one
    authorization failure as 400 INVALID_ARGUMENT.
    """
    if api_message and _PERMISSION_LANGUAGE.search(api_message):
        return "authorization_denied", [
            f"Play returned HTTP {status_code}"
            + (f"/{api_status}" if api_status else "")
            + " but its message names a permission, so treat this as an"
            " authorization failure rather than a malformed request",
            "read the message verbatim: it usually names the permission Play wants",
            "confirm the active publisher identity reported above is the Play"
            " Console user that holds that permission",
            "a monetization write and a read can differ in what they require, so"
            " succeeding reads do not establish that this write is permitted",
        ]
    if status_code == 400:
        return "malformed_request", [
            "no permission wording was found in the message, so this most likely"
            " concerns the request contents rather than the caller's access",
            "for a one-time product, updateMask must be explicit field paths and"
            " every masked field must be present in the body",
            "re-read the verbatim message before ruling access out: Play can"
            " report an authorization problem as 400 INVALID_ARGUMENT",
        ]
    if status_code == 401:
        return "credential_not_accepted", [
            "the service-account credential was not accepted at all",
            "confirm which binding is active and that its key is current",
        ]
    if status_code == 403:
        return "authorization_denied", [
            "confirm the active publisher identity reported above is the same Play"
            " Console user that holds the grant you are relying on",
            "confirm that user's Play Console permissions cover this operation",
            "retry: Play authorization can be transient or still propagating, so a"
            " single 403 is not evidence of a permanently missing grant",
            "if reads succeed and only this operation fails, run the same call"
            " against another package to separate an account-level cause from a"
            " package-level one",
        ]
    if status_code == 404:
        return "resource_absent", [
            "the caller was authorized; the addressed resource does not exist",
            "an upsert with allowMissing=false refuses to create it",
        ]
    return "play_api_error", []


def _raise_for_status(response, action: str) -> None:
    if response.ok:
        return
    try:
        payload = response.json()
    except ValueError:
        payload = None
    detail = json.dumps(payload, indent=2) if payload is not None else response.text
    api_status = None
    if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
        api_status = payload["error"].get("status")

    api_message = None
    if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
        api_message = payload["error"].get("message")

    classification, checks = classify_play_failure(
        response.status_code, api_status, api_message
    )
    lines = [
        f"{action} failed with HTTP {response.status_code}:",
        redaction.redact_text(detail),
        f"classification: {classification}",
    ]
    if classification in ("authorization_denied", "credential_not_accepted"):
        identity = _publisher_identity()
        lines.append(
            f"active publisher identity: {identity}"
            if identity
            else "active publisher identity: could not be read"
        )
    if checks:
        lines.append("distinguish before concluding a cause:")
        lines.extend(f"  - {check}" for check in checks)
    error = PlayError("\n".join(lines))
    error.status_code = response.status_code
    error.api_status = api_status
    error.api_message = api_message
    error.classification = classification
    raise error


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

    def _list_paginated(self, suffix: str, field: str, action: str) -> list[dict]:
        """Read every page from a Play catalog list endpoint."""
        items: list[dict] = []
        page_token: str | None = None
        while True:
            params: dict[str, Any] = {"pageSize": 1000}
            if page_token:
                params["pageToken"] = page_token
            payload = self._request("GET", suffix, action, params=params)
            page_items = payload.get(field, [])
            if not isinstance(page_items, list):
                raise PlayError(f"{action} returned non-list field {field!r}")
            items.extend(page_items)
            page_token = payload.get("nextPageToken")
            if not page_token:
                return items

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

    def convert_region_prices(
        self,
        price: dict[str, Any],
        product_tax_category_code: str | None = None,
    ) -> dict:
        """Convert one tax-exclusive price and return current regionVersion.

        Besides localized prices, Google's response contains the RegionsVersion
        required by subscription and one-time-product mutation APIs. This avoids
        hard-coding a region-version value in automation.
        """
        body: dict[str, Any] = {"price": price}
        if product_tax_category_code:
            body["productTaxCategoryCode"] = product_tax_category_code
        return self._request(
            "POST",
            "/pricing:convertRegionPrices",
            "convert regional prices",
            json=body,
        )

    def create_subscription(
        self,
        product_id: str,
        body: dict[str, Any],
        regions_version: str,
    ) -> dict:
        payload = dict(body)
        payload["packageName"] = self.package_name
        payload["productId"] = product_id
        return self._request(
            "POST",
            "/subscriptions",
            f"create subscription {product_id}",
            params={"productId": product_id, "regionsVersion.version": regions_version},
            json=payload,
        )

    def list_subscriptions(self) -> list[dict]:
        return self._list_paginated(
            "/subscriptions", "subscriptions", "list subscriptions"
        )

    def activate_base_plan(self, product_id: str, base_plan_id: str) -> dict:
        return self._request(
            "POST",
            f"/subscriptions/{product_id}/basePlans/{base_plan_id}:activate",
            f"activate base plan {product_id}:{base_plan_id}",
            json={},
        )

    def upsert_one_time_product(
        self,
        product_id: str,
        body: dict[str, Any],
        regions_version: str,
        *,
        update_mask: str | None = None,
        allow_missing: bool = True,
    ) -> dict:
        """Create or update a modern OneTimeProduct with the current API."""
        payload = dict(body)
        payload["packageName"] = self.package_name
        payload["productId"] = product_id
        # This field is output-only on the resource; the query parameter carries
        # the version used for the mutation.
        payload.pop("regionsVersion", None)
        if not update_mask:
            # Google requires fully qualified field names here and rejects "*"
            # with 400 "Invalid update_mask: [*]". Derive the mask from the
            # fields actually supplied, so a caller can neither send a field
            # that is silently ignored nor mask a field it never sent, which
            # would clear it.
            update_mask = ",".join(
                key
                for key in body
                if key not in ("packageName", "productId", "regionsVersion")
            )
        if not update_mask:
            raise PlayError(
                f"upsert one-time product {product_id} needs at least one updatable field"
            )
        return self._request(
            "PATCH",
            f"/onetimeproducts/{product_id}",
            f"upsert one-time product {product_id}",
            params={
                "updateMask": update_mask,
                "regionsVersion.version": regions_version,
                "allowMissing": "true" if allow_missing else "false",
            },
            json=payload,
        )

    def set_data_safety_labels(self, safety_labels_csv: str) -> dict:
        """Write the app's Safety Labels declaration from Data safety CSV content.

        Google publishes no read method for safety labels, so a successful write
        cannot be confirmed by reading it back through this API.
        """
        return self._request(
            "POST",
            "/dataSafety",
            "write data safety labels",
            json={"safetyLabels": safety_labels_csv},
        )

    def list_in_app_products(self) -> list[dict]:
        """List one-time products using the current monetization publishing API."""
        return self._list_paginated(
            "/oneTimeProducts", "oneTimeProducts", "list one-time products"
        )

    def get_one_time_product(self, product_id: str) -> dict:
        """Read one modern OneTimeProduct, including purchase-option regional prices."""
        return self._request(
            "GET",
            f"/oneTimeProducts/{product_id}",
            f"get one-time product {product_id}",
        )

    def set_purchase_option_active(
        self,
        product_id: str,
        purchase_option_id: str,
        *,
        active: bool,
    ) -> dict:
        transition = "activatePurchaseOptionRequest" if active else "deactivatePurchaseOptionRequest"
        body = {
            "requests": [
                {
                    transition: {
                        "packageName": self.package_name,
                        "productId": product_id,
                        "purchaseOptionId": purchase_option_id,
                    }
                }
            ]
        }
        verb = "activate" if active else "deactivate"
        return self._request(
            "POST",
            f"/oneTimeProducts/{product_id}/purchaseOptions:batchUpdateStates",
            f"{verb} purchase option {product_id}:{purchase_option_id}",
            json=body,
        )

    def create_in_app_product(self, body: dict) -> dict:
        """Legacy inappproducts path retained only for migration compatibility.

        New automation must prefer ``upsert_one_time_product`` because the modern
        OneTimeProduct model supports purchase options, offers, and current
        regional pricing semantics.
        """
        return self._request(
            "POST", "/inappproducts", "create legacy in-app product", json=body
        )


# ---- high level operations -------------------------------------------------


def publish_bundles(
    package_name: str,
    aab_paths: Sequence[Path],
    track: str,
    status: str = "completed",
    release_notes: dict[str, str] | None = None,
    user_fraction: float | None = None,
    release_name: str | None = None,
    dry_run: bool = False,
    changes_not_sent_for_review: bool = False,
    client: PlayClient | None = None,
) -> dict:
    """Upload one or more AABs and assign all version codes in one Play edit.

    Phone and Wear apps that share one package are one multi-artifact Play
    release. Publishing their AABs in separate track edits can cause the second
    track write to replace the first release's version-code set.
    """
    paths = [Path(path).expanduser() for path in aab_paths]
    if not paths:
        raise PlayError("publish requires at least one app bundle")

    play = client or PlayClient(package_name)
    result: dict[str, Any] = {
        "package_name": package_name,
        "track": track,
        "dry_run": dry_run,
    }
    with play.edit(
        commit=not dry_run,
        changes_not_sent_for_review=changes_not_sent_for_review,
    ) as edit_id:
        uploaded: list[dict[str, Any]] = []
        version_codes: list[int] = []
        for path in paths:
            bundle = play.upload_bundle(edit_id, path)
            version_code = int(bundle["versionCode"])
            uploaded.append(
                {
                    "path": str(path),
                    "version_code": version_code,
                    "sha1": bundle.get("sha1"),
                    "sha256": bundle.get("sha256"),
                }
            )
            version_codes.append(version_code)

        if len(set(version_codes)) != len(version_codes):
            raise PlayError(
                "uploaded bundles resolved to duplicate versionCodes; "
                "multi-artifact releases require unique versionCodes"
            )

        play.set_track_release(
            edit_id,
            track,
            version_codes,
            status=status,
            release_notes=release_notes,
            user_fraction=user_fraction,
            release_name=release_name,
        )
        result["edit_id"] = edit_id
        result["bundles"] = uploaded
        result["version_codes"] = version_codes
        if len(uploaded) == 1:
            result["version_code"] = uploaded[0]["version_code"]
            result["sha256"] = uploaded[0]["sha256"]

    result["committed"] = not dry_run
    return result


def publish_track_bundles(
    package_name: str,
    track_aab_paths: dict[str, Sequence[Path]],
    status: str = "completed",
    release_notes: dict[str, str] | None = None,
    user_fraction: float | None = None,
    release_name: str | None = None,
    dry_run: bool = False,
    changes_not_sent_for_review: bool = False,
    client: PlayClient | None = None,
) -> dict:
    """Publish multiple form-factor track releases in one package edit.

    Google Play manages dedicated form factors such as Wear OS on prefixed
    tracks. A phone AAB may belong on internal while its Wear companion belongs
    on wear:internal. Upload every artifact and update every target track inside
    one edit so validation and commit are atomic.
    """
    normalized: dict[str, list[Path]] = {}
    seen_paths: set[Path] = set()
    for raw_track, raw_paths in track_aab_paths.items():
        track = raw_track.strip()
        if not track:
            raise PlayError("track name cannot be blank")
        paths = [Path(path).expanduser() for path in raw_paths]
        if not paths:
            raise PlayError(f"track {track!r} requires at least one app bundle")
        for path in paths:
            resolved = path.resolve()
            if resolved in seen_paths:
                raise PlayError(
                    f"bundle {path} was assigned to more than one track; "
                    "each uploaded versionCode must have one target track in this release set"
                )
            seen_paths.add(resolved)
        normalized[track] = paths

    if not normalized:
        raise PlayError("publish-track-set requires at least one track")

    play = client or PlayClient(package_name)
    result: dict[str, Any] = {
        "package_name": package_name,
        "tracks": list(normalized),
        "dry_run": dry_run,
    }
    with play.edit(
        commit=not dry_run,
        changes_not_sent_for_review=changes_not_sent_for_review,
    ) as edit_id:
        all_version_codes: list[int] = []
        releases: dict[str, dict[str, Any]] = {}

        for track, paths in normalized.items():
            uploaded: list[dict[str, Any]] = []
            version_codes: list[int] = []
            for path in paths:
                bundle = play.upload_bundle(edit_id, path)
                version_code = int(bundle["versionCode"])
                uploaded.append(
                    {
                        "path": str(path),
                        "version_code": version_code,
                        "sha1": bundle.get("sha1"),
                        "sha256": bundle.get("sha256"),
                    }
                )
                version_codes.append(version_code)
                all_version_codes.append(version_code)

            releases[track] = {
                "version_codes": version_codes,
                "bundles": uploaded,
            }

        if len(set(all_version_codes)) != len(all_version_codes):
            raise PlayError(
                "uploaded track-set bundles resolved to duplicate versionCodes; "
                "every artifact in one package edit must use a unique versionCode"
            )

        for track, release in releases.items():
            play.set_track_release(
                edit_id,
                track,
                release["version_codes"],
                status=status,
                release_notes=release_notes,
                user_fraction=user_fraction,
                release_name=release_name,
            )

        result["edit_id"] = edit_id
        result["releases"] = releases
        result["version_codes"] = all_version_codes

    result["committed"] = not dry_run
    return result


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
    """Backward-compatible single-bundle wrapper around publish_bundles."""
    return publish_bundles(
        package_name,
        [aab_path],
        track=track,
        status=status,
        release_notes=release_notes,
        user_fraction=user_fraction,
        release_name=release_name,
        dry_run=dry_run,
        changes_not_sent_for_review=changes_not_sent_for_review,
        client=client,
    )


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
