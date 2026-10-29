"""Google Play listing, tester, review, image, and diagnostics operations.

These endpoints complement the release/monetization operations in ``play.py``.
They use the same Android Publisher authorized session and edit lifecycle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import mimetypes
import struct

from . import play as play_module

# A listing commit must not cancel an unrelated submission already in review,
# which is what Play's default (CANCEL_IN_REVIEW_AND_SUBMIT) does.
LISTING_REVIEW_BEHAVIOR = "ERROR_IF_IN_REVIEW"

# Play screenshot rules: JPEG or 24-bit PNG without alpha, 320-3840 px, long
# side at most twice the short side, up to 8 per device type; Wear OS is 1:1
# and at least 384 px. https://support.google.com/googleplay/android-developer/answer/9866151
SCREENSHOT_TYPES = ("phoneScreenshots", "wearScreenshots")
MAX_SCREENSHOTS = 8


def _image_info(data: bytes) -> tuple[str, int, int]:
    """Return (format, width, height) from a PNG or JPEG header."""
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        width, height = struct.unpack(">II", data[16:24])
        bit_depth, color_type = data[24], data[25]
        if (bit_depth, color_type) != (8, 2) or b"tRNS" in data[: data.find(b"IDAT")]:
            raise play_module.PlayError("PNG must be 24-bit RGB without alpha or transparency")
        return "png", width, height
    if data[:2] == b"\xff\xd8":
        index = 2
        while index + 9 < len(data) and data[index] == 0xFF:
            marker = data[index + 1]
            length = struct.unpack(">H", data[index + 2 : index + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                height, width = struct.unpack(">HH", data[index + 5 : index + 9])
                return "jpeg", width, height
            index += 2 + length
    raise play_module.PlayError("image is not a readable PNG or JPEG")


def local_screenshot_set(image_type: str, image_paths: list[Path]) -> list[dict]:
    """Validate an ordered screenshot set against Play's rules and hash it."""
    if image_type not in SCREENSHOT_TYPES:
        raise play_module.PlayError(f"unsupported screenshot type {image_type!r}")
    paths = [Path(path).expanduser().resolve() for path in image_paths]
    if not 1 <= len(paths) <= MAX_SCREENSHOTS:
        raise play_module.PlayError(f"a screenshot set needs 1-{MAX_SCREENSHOTS} images")
    if [path.name for path in paths] != sorted(path.name for path in paths):
        raise play_module.PlayError("screenshots must be given in filename order")
    items = []
    for path in paths:
        if not path.is_file():
            raise play_module.PlayError(f"image not found: {path}")
        data = path.read_bytes()
        try:
            kind, width, height = _image_info(data)
        except play_module.PlayError as error:
            raise play_module.PlayError(f"{path.name}: {error}") from None
        short, long = sorted((width, height))
        if short < 320 or long > 3840 or long > 2 * short:
            raise play_module.PlayError(f"{path.name}: {width}x{height} is outside Play limits")
        if image_type == "wearScreenshots" and (width != height or width < 384):
            raise play_module.PlayError(f"{path.name}: Wear OS needs square images of at least 384 px")
        items.append({"name": path.name, "path": str(path), "format": kind,
                      "width": width, "height": height,
                      "sha256": hashlib.sha256(data).hexdigest()})
    if len({item["sha256"] for item in items}) != len(items):
        raise play_module.PlayError("screenshot set contains duplicate images")
    return items


def _hashes(images: list[dict]) -> list[str | None]:
    return [image.get("sha256") for image in images]


def _brief(images: list[dict]) -> list[dict]:
    return [{"id": image.get("id"), "sha256": image.get("sha256")} for image in images]


class PlayManagementClient:
    def __init__(self, package_name: str, client: play_module.PlayClient | None = None) -> None:
        self.client = client or play_module.PlayClient(package_name)
        self.package_name = package_name

    # ---- store listings ----------------------------------------------------

    def list_listings(self) -> list[dict]:
        with self.client.edit(commit=False, validate=False) as edit_id:
            payload = self.client._request(  # noqa: SLF001 - shared package client plumbing
                "GET", f"/edits/{edit_id}/listings", "list store listings"
            )
            return payload.get("listings", [])

    def get_listing(self, language: str) -> dict:
        with self.client.edit(commit=False, validate=False) as edit_id:
            return self.client._request(  # noqa: SLF001
                "GET", f"/edits/{edit_id}/listings/{language}", f"get listing {language}"
            )

    def update_listing(
        self,
        language: str,
        *,
        title: str,
        short_description: str,
        full_description: str,
        video: str | None = None,
        dry_run: bool = True,
        expected_current: dict[str, Any] | None = None,
    ) -> dict:
        body: dict[str, Any] = {
            "language": language,
            "title": title,
            "shortDescription": short_description,
            "fullDescription": full_description,
        }
        if video:
            body["video"] = video
        with self.client.edit(
            commit=not dry_run, validate=True, changes_in_review_behavior=LISTING_REVIEW_BEHAVIOR
        ) as edit_id:
            if expected_current is not None:
                current = self.client._request(  # noqa: SLF001
                    "GET", f"/edits/{edit_id}/listings/{language}",
                    f"compare listing {language}",
                )
                fields = ("title", "shortDescription", "fullDescription")
                if any(current.get(field) != expected_current.get(field) for field in fields):
                    raise play_module.PlayError(f"listing {language} drifted before update")
                # Fail closed if an unrecorded promo video would be cleared.
                if current.get("video") != expected_current.get("video"):
                    raise play_module.PlayError(f"listing {language} video drifted before update")
            result = self.client._request(  # noqa: SLF001
                "PUT",
                f"/edits/{edit_id}/listings/{language}",
                f"update listing {language}",
                json=body,
            )
        return {"listing": result, "dry_run": dry_run, "committed": not dry_run}

    def create_listing(
        self,
        language: str,
        *,
        title: str,
        short_description: str,
        full_description: str,
        dry_run: bool = True,
    ) -> dict:
        """Create a missing locale only; never replace existing localized copy.

        The absence check and PUT share a Play edit. Concurrent external edits
        are still governed by Play's commit conflict handling; a failed or
        uncertain commit must be reconciled by reading the locale before retry.
        """
        body = {
            "language": language,
            "title": title,
            "shortDescription": short_description,
            "fullDescription": full_description,
        }
        with self.client.edit(
            commit=not dry_run, validate=True, changes_in_review_behavior=LISTING_REVIEW_BEHAVIOR
        ) as edit_id:
            existing = self.client._request(  # noqa: SLF001
                "GET", f"/edits/{edit_id}/listings", "check existing listing locales"
            ).get("listings")
            if not isinstance(existing, list) or any(
                not isinstance(item, dict) or not isinstance(item.get("language"), str)
                for item in existing
            ):
                raise play_module.PlayError("Play returned an invalid locale inventory; refusing create")
            if any(item["language"] == language for item in existing):
                raise play_module.PlayError(
                    f"listing {language!r} already exists; use drift-protected listing-update"
                )
            result = self.client._request(  # noqa: SLF001
                "PUT",
                f"/edits/{edit_id}/listings/{language}",
                f"create listing {language}",
                json=body,
            )
        return {"listing": result, "dry_run": dry_run, "committed": not dry_run}

    # ---- images ------------------------------------------------------------

    def list_images(self, language: str, image_type: str) -> list[dict]:
        with self.client.edit(commit=False, validate=False) as edit_id:
            payload = self.client._request(  # noqa: SLF001
                "GET",
                f"/edits/{edit_id}/listings/{language}/{image_type}",
                f"list {image_type} images for {language}",
            )
            return payload.get("images", [])

    def _upload(self, edit_id: str, language: str, image_type: str, path: Path) -> dict:
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        upload_url = self.client._url(  # noqa: SLF001
            f"/edits/{edit_id}/listings/{language}/{image_type}",
            base=play_module.UPLOAD_BASE,
        )
        with path.open("rb") as handle:
            response = self.client.session.post(
                upload_url,
                params={"uploadType": "media"},
                headers={"Content-Type": content_type},
                data=handle,
                timeout=play_module.UPLOAD_TIMEOUT_SECONDS,
            )
        play_module._raise_for_status(response, f"upload {image_type} image {path.name}")
        result = response.json() if response.content else {}
        return result.get("image", result)

    def upload_image(
        self,
        language: str,
        image_type: str,
        image_path: Path,
        *,
        dry_run: bool = True,
    ) -> dict:
        path = image_path.expanduser()
        if not path.is_file():
            raise play_module.PlayError(f"image not found: {path}")
        with self.client.edit(
            commit=not dry_run, validate=True, changes_in_review_behavior=LISTING_REVIEW_BEHAVIOR
        ) as edit_id:
            image = self._upload(edit_id, language, image_type, path)
        return {
            "image": image,
            "path": str(path),
            "language": language,
            "image_type": image_type,
            "dry_run": dry_run,
            "committed": not dry_run,
        }

    def replace_image_set(
        self,
        language: str,
        image_type: str,
        image_paths: list[Path],
        *,
        expected_current: list[str] | None = None,
        dry_run: bool = True,
    ) -> dict:
        """Replace one locale's screenshot carousel in a single Play edit.

        ``expected_current`` is the ordered sha256 list of the live set the
        caller reviewed; a commit requires it so a set changed by someone else
        is never overwritten. Every check runs inside the edit, which is
        deleted unless the final commit succeeds, so Play never sees a partial
        set. An identical live set is reported and nothing is written.
        """
        desired = local_screenshot_set(image_type, image_paths)
        want = [item["sha256"] for item in desired]
        if not dry_run and expected_current is None:
            raise play_module.PlayError(
                "a committed image-set replacement requires expected_current"
            )
        summary = {
            "package_name": self.package_name,
            "language": language,
            "image_type": image_type,
            "desired": desired,
            "dry_run": dry_run,
        }

        before = self.list_images(language, image_type)
        if _hashes(before) == want:
            return {**summary, "status": "skipped_identical", "committed": False,
                    "before": _brief(before)}

        with self.client.edit(
            commit=not dry_run, validate=False, changes_in_review_behavior=LISTING_REVIEW_BEHAVIOR
        ) as edit_id:
            listings = self.client._request(  # noqa: SLF001
                "GET", f"/edits/{edit_id}/listings", "check listing locales"
            ).get("listings")
            if not isinstance(listings, list) or language not in {
                item.get("language") for item in listings if isinstance(item, dict)
            }:
                raise play_module.PlayError(
                    f"listing {language!r} does not exist; refusing to create it through images"
                )
            images_path = f"/edits/{edit_id}/listings/{language}/{image_type}"
            current = self.client._request(  # noqa: SLF001
                "GET", images_path, f"read {image_type} for {language}"
            ).get("images", [])
            current_hashes = _hashes(current)
            if expected_current is not None and current_hashes != list(expected_current):
                raise play_module.PlayError(
                    f"{language} {image_type} drifted from expected_current; re-read before retrying"
                )
            deleted = self.client._request(  # noqa: SLF001
                "DELETE", images_path, f"clear {image_type} for {language}"
            ).get("deleted", [])
            if sorted(i.get("id") for i in deleted) != sorted(i.get("id") for i in current):
                raise play_module.PlayError(
                    f"Play deleted a different {image_type} set than was read for {language}"
                )
            for item in desired:
                uploaded = self._upload(edit_id, language, image_type, Path(item["path"]))
                if uploaded.get("sha256") != item["sha256"]:
                    raise play_module.PlayError(f"Play stored a different hash for {item['name']}")
            in_edit = self.client._request(  # noqa: SLF001
                "GET", images_path, f"verify {image_type} for {language}"
            ).get("images", [])
            if _hashes(in_edit) != want:
                raise play_module.PlayError(
                    f"in-edit {image_type} for {language} do not match the desired set and order"
                )
            self.client._request(  # noqa: SLF001
                "POST", f"/edits/{edit_id}:validate", "validate edit"
            )

        result = {**summary, "before": _brief(before), "in_edit": _brief(in_edit),
                  "committed": not dry_run}
        if dry_run:
            return {**result, "status": "validated_dry_run"}
        after = self.list_images(language, image_type)
        matches = _hashes(after) == want
        return {
            **result,
            "read_back": _brief(after),
            "read_back_matches": matches,
            "status": "committed_verified" if matches else "committed_readback_mismatch",
        }

    # ---- testers and availability -----------------------------------------

    def set_data_safety_labels(self, csv_text: str, *, dry_run: bool = True) -> dict:
        """Submit a Data safety CSV declaration.

        Unlike every other write here, this one has no corresponding read, so a
        dry run can only validate locally and the result never claims the state
        was verified.
        """
        if not csv_text.strip():
            raise play_module.PlayError("data safety CSV content is empty")
        summary = {
            "bytes": len(csv_text.encode("utf-8")),
            "rows": csv_text.strip().count("\n") + 1,
            "dry_run": dry_run,
            "read_back": "unsupported_by_api",
        }
        if dry_run:
            return {"submitted": False, **summary}
        self.client.set_data_safety_labels(csv_text)
        return {"submitted": True, **summary}

    def get_testers(self, track: str) -> dict:
        with self.client.edit(commit=False, validate=False) as edit_id:
            return self.client._request(  # noqa: SLF001
                "GET", f"/edits/{edit_id}/testers/{track}", f"get testers for {track}"
            )

    def update_testers(
        self, track: str, google_groups: list[str], *, dry_run: bool = True
    ) -> dict:
        groups = sorted({group.strip() for group in google_groups if group.strip()})
        with self.client.edit(commit=not dry_run, validate=True) as edit_id:
            result = self.client._request(  # noqa: SLF001
                "PUT",
                f"/edits/{edit_id}/testers/{track}",
                f"update testers for {track}",
                json={"googleGroups": groups},
            )
        return {
            "testers": result,
            "track": track,
            "dry_run": dry_run,
            "committed": not dry_run,
        }

    def get_country_availability(self, track: str) -> dict:
        with self.client.edit(commit=False, validate=False) as edit_id:
            return self.client._request(  # noqa: SLF001
                "GET",
                f"/edits/{edit_id}/countryAvailability/{track}",
                f"get country availability for {track}",
            )

    # ---- reviews -----------------------------------------------------------

    def list_reviews(self, *, max_results: int = 100, translation_language: str | None = None) -> list[dict]:
        if not 1 <= max_results <= 100:
            raise play_module.PlayError("max_results must be between 1 and 100")
        reviews: list[dict] = []
        token: str | None = None
        while True:
            params: dict[str, Any] = {"maxResults": max_results}
            if token:
                params["token"] = token
            if translation_language:
                params["translationLanguage"] = translation_language
            payload = self.client._request("GET", "/reviews", "list reviews", params=params)  # noqa: SLF001
            reviews.extend(payload.get("reviews", []))
            token = payload.get("tokenPagination", {}).get("nextPageToken")
            if not token:
                return reviews

    def reply_review(self, review_id: str, reply_text: str) -> dict:
        text = reply_text.strip()
        if not text:
            raise play_module.PlayError("review reply cannot be blank")
        if len(text) > 350:
            raise play_module.PlayError("review reply must be 350 characters or fewer")
        return self.client._request(  # noqa: SLF001
            "POST",
            f"/reviews/{review_id}:reply",
            f"reply to review {review_id}",
            json={"replyText": text},
        )

    # ---- diagnostics artifacts --------------------------------------------

    def upload_deobfuscation_file(
        self,
        version_code: int,
        file_type: str,
        file_path: Path,
        *,
        dry_run: bool = True,
    ) -> dict:
        if file_type not in ("proguard", "nativeCode"):
            raise play_module.PlayError("file_type must be 'proguard' or 'nativeCode'")
        path = file_path.expanduser()
        if not path.is_file():
            raise play_module.PlayError(f"deobfuscation file not found: {path}")
        with self.client.edit(commit=not dry_run, validate=True) as edit_id:
            upload_url = self.client._url(  # noqa: SLF001
                f"/edits/{edit_id}/apks/{version_code}/deobfuscationFiles/{file_type}",
                base=play_module.UPLOAD_BASE,
            )
            with path.open("rb") as handle:
                response = self.client.session.post(
                    upload_url,
                    params={"uploadType": "media"},
                    headers={"Content-Type": "application/octet-stream"},
                    data=handle,
                    timeout=play_module.UPLOAD_TIMEOUT_SECONDS,
                )
            play_module._raise_for_status(response, f"upload {file_type} symbols for {version_code}")
            result = response.json() if response.content else {}
        return {
            "result": result,
            "version_code": version_code,
            "file_type": file_type,
            "path": str(path),
            "dry_run": dry_run,
            "committed": not dry_run,
        }
