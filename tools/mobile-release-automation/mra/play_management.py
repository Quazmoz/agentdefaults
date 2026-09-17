"""Google Play listing, tester, review, image, and diagnostics operations.

These endpoints complement the release/monetization operations in ``play.py``.
They use the same Android Publisher authorized session and edit lifecycle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import mimetypes

from . import play as play_module


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
    ) -> dict:
        body: dict[str, Any] = {
            "language": language,
            "title": title,
            "shortDescription": short_description,
            "fullDescription": full_description,
        }
        if video:
            body["video"] = video
        with self.client.edit(commit=not dry_run, validate=True) as edit_id:
            result = self.client._request(  # noqa: SLF001
                "PUT",
                f"/edits/{edit_id}/listings/{language}",
                f"update listing {language}",
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
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        with self.client.edit(commit=not dry_run, validate=True) as edit_id:
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
        return {
            "image": result.get("image", result),
            "path": str(path),
            "language": language,
            "image_type": image_type,
            "dry_run": dry_run,
            "committed": not dry_run,
        }

    # ---- testers and availability -----------------------------------------

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
