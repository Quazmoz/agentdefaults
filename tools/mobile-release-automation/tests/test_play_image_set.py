"""Atomic screenshot-set replacement against a stateful in-memory Play double."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import copy
import hashlib
import re
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import mcp_play_management, play, play_management  # noqa: E402
from tests.fakes import FakeResponse, FakeSession  # noqa: E402

PACKAGE = "com.example.app"
LANG, WEAR = "en-US", "wearScreenshots"


def png(width: int, height: int, seed: str, color_type: int = 2) -> bytes:
    def chunk(kind: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", seed.encode()) + chunk(b"IEND", b""))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FakePlay:
    """Committed listing images plus per-edit copies, committed only on :commit."""

    PATH = re.compile(r"/applications/[^/]+/edits(?:/(?P<edit>[^/:]+))?(?P<rest>[^?]*)")

    def __init__(self, images: dict[tuple[str, str], list[bytes]]) -> None:
        self.committed = {key: [self._image(i, data) for i, data in enumerate(value)]
                          for key, value in images.items()}
        self.languages = ["en-US", "de-DE"]
        self.edits: dict[str, dict] = {}
        self.fail: dict[str, FakeResponse] = {}
        self.fail_upload_at: int | None = None
        self.uploads = 0
        self.session = FakeSession({
            ("POST", "/edits"): self.post,
            ("GET", "/edits/"): self.get,
            ("DELETE", "/edits/"): self.delete,
        })

    @staticmethod
    def _image(index: int, data: bytes) -> dict:
        return {"id": f"old-{index}-{sha(data)[:6]}", "sha256": sha(data)}

    def _parse(self, url: str) -> tuple[str | None, list[str]]:
        match = self.PATH.search(url)
        return match["edit"], [part for part in match["rest"].split("/") if part]

    def post(self, url: str, **kwargs) -> FakeResponse:
        edit, rest = self._parse(url)
        if edit is None:
            edit_id = f"edit-{len(self.edits) + 1}"
            self.edits[edit_id] = copy.deepcopy(self.committed)
            return FakeResponse(200, {"id": edit_id})
        if edit not in self.edits:
            return FakeResponse(400, {"error": {"message": "This Edit has been deleted."}})
        if url.endswith(":validate"):
            return self.fail.get("validate") or FakeResponse(200, {"id": edit})
        if ":commit" in url:
            if "commit" in self.fail:
                return self.fail["commit"]
            self.committed = self.edits.pop(edit)
            return FakeResponse(200, {"id": edit})
        # upload: /listings/<lang>/<type>
        self.uploads += 1
        if self.fail_upload_at == self.uploads:
            return FakeResponse(500, {"error": {"message": "backend error"}})
        data = kwargs["data"].read()
        image = {"id": f"new-{self.uploads}", "sha256": sha(data)}
        self.edits[edit].setdefault((rest[1], rest[2]), []).append(image)
        return FakeResponse(200, {"image": image})

    def get(self, url: str, **_) -> FakeResponse:
        edit, rest = self._parse(url)
        if rest == ["listings"]:
            return FakeResponse(200, {"listings": [{"language": lang} for lang in self.languages]})
        return FakeResponse(200, {"images": self.edits[edit].get((rest[1], rest[2]), [])})

    def delete(self, url: str, **_) -> FakeResponse:
        edit, rest = self._parse(url)
        if not rest:
            self.edits.pop(edit, None)
            return FakeResponse(200, {})
        deleted = self.edits[edit].pop((rest[1], rest[2]), [])
        return FakeResponse(200, {"deleted": deleted})

    def hashes(self, key=(LANG, WEAR)) -> list[str]:
        return [image["sha256"] for image in self.committed.get(key, [])]

    def commits(self) -> list[dict]:
        return [call for call in self.session.calls if ":commit" in call["url"]]


class ImageSetCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.old = [png(454, 454, f"old{i}") for i in range(3)]
        self.other_phone = [png(1080, 1920, "phone")]
        self.other_locale = [png(454, 454, "de")]
        self.fake = FakePlay({
            (LANG, WEAR): self.old,
            (LANG, "phoneScreenshots"): self.other_phone,
            ("de-DE", WEAR): self.other_locale,
        })
        self.api = play_management.PlayManagementClient(
            PACKAGE, client=play.PlayClient(PACKAGE, session=self.fake.session)
        )
        self.paths = self.write([png(454, 454, f"new{i}") for i in range(8)])

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, blobs: list[bytes], prefix: str = "") -> list[Path]:
        paths = []
        for index, blob in enumerate(blobs, start=1):
            path = self.dir / f"{prefix}{index:02d}-shot.png"
            path.write_bytes(blob)
            paths.append(path)
        return paths

    def want(self) -> list[str]:
        return [sha(path.read_bytes()) for path in self.paths]

    def replace(self, **kwargs) -> dict:
        kwargs.setdefault("expected_current", [sha(data) for data in self.old])
        kwargs.setdefault("dry_run", False)
        return self.api.replace_image_set(LANG, WEAR, self.paths, **kwargs)

    def assert_untouched(self) -> None:
        self.assertEqual(self.fake.hashes(), [sha(data) for data in self.old])
        self.assertEqual(self.fake.edits, {}, "edit must be deleted")


class SuccessTest(ImageSetCase):
    def test_full_set_is_replaced_in_one_commit_and_read_back(self) -> None:
        result = self.replace()
        self.assertEqual(result["status"], "committed_verified")
        self.assertTrue(result["read_back_matches"])
        self.assertEqual(self.fake.hashes(), self.want())
        commits = self.fake.commits()
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0]["params"], {"changesInReviewBehavior": "ERROR_IF_IN_REVIEW"})
        self.assertTrue(any(":validate" in url for url in self.fake.session.urls("POST")))

    def test_order_follows_filenames(self) -> None:
        self.replace()
        self.assertEqual(self.fake.hashes(), self.want())
        reversed_paths = list(reversed(self.paths))
        with self.assertRaisesRegex(play.PlayError, "filename order"):
            self.api.replace_image_set(LANG, WEAR, reversed_paths, expected_current=[])

    def test_no_other_listing_text_or_image_type_changes(self) -> None:
        self.replace()
        self.assertEqual(self.fake.hashes((LANG, "phoneScreenshots")), [sha(self.other_phone[0])])
        self.assertEqual(self.fake.hashes(("de-DE", WEAR)), [sha(self.other_locale[0])])
        methods = {call["method"] for call in self.fake.session.calls}
        self.assertTrue(methods <= {"GET", "POST", "DELETE"}, methods)
        for call in self.fake.session.calls:
            if call["method"] == "POST" and "/listings/" in call["url"] or (
                call["method"] == "DELETE" and "/listings/" in call["url"]
            ):
                self.assertTrue(call["url"].endswith(f"/listings/{LANG}/{WEAR}"), call["url"])


class DryRunAndSkipTest(ImageSetCase):
    def test_dry_run_validates_without_commit(self) -> None:
        result = self.replace(dry_run=True, expected_current=None)
        self.assertEqual(result["status"], "validated_dry_run")
        self.assertEqual(result["in_edit"][0]["sha256"], self.want()[0])
        self.assertEqual(self.fake.commits(), [])
        self.assert_untouched()

    def test_identical_set_is_skipped_without_mutation(self) -> None:
        self.paths = self.write(self.old, prefix="same-")
        result = self.api.replace_image_set(
            LANG, WEAR, self.paths, expected_current=self.want(), dry_run=False
        )
        self.assertEqual(result["status"], "skipped_identical")
        self.assertEqual(self.fake.commits(), [])
        self.assertEqual(self.fake.uploads, 0)
        self.assertNotIn("DELETE", {c["method"] for c in self.fake.session.calls if "/listings/" in c["url"]})

    def test_commit_requires_expected_snapshot(self) -> None:
        with self.assertRaisesRegex(play.PlayError, "expected_current"):
            self.replace(expected_current=None)
        self.assertEqual(self.fake.session.calls, [])


class FailureTest(ImageSetCase):
    def test_drift_from_expected_snapshot_aborts(self) -> None:
        with self.assertRaisesRegex(play.PlayError, "drifted"):
            self.replace(expected_current=[sha(self.old[0])])
        self.assertEqual(self.fake.uploads, 0)
        self.assert_untouched()

    def test_partial_upload_failure_discards_edit(self) -> None:
        self.fake.fail_upload_at = 3
        with self.assertRaises(play.PlayError):
            self.replace()
        self.assertEqual(self.fake.commits(), [])
        self.assert_untouched()

    def test_validation_failure_discards_edit(self) -> None:
        self.fake.fail["validate"] = FakeResponse(400, {"error": {"message": "screenshot rejected"}})
        with self.assertRaisesRegex(play.PlayError, "validate edit"):
            self.replace()
        self.assertEqual(self.fake.commits(), [])
        self.assert_untouched()

    def test_concurrent_edit_invalidation_is_classified(self) -> None:
        self.fake.fail["commit"] = FakeResponse(400, {"error": {"message": "This Edit has been deleted."}})
        with self.assertRaises(play.PlayError) as caught:
            self.replace()
        self.assertEqual(caught.exception.classification, "edit_invalidated")
        self.assert_untouched()

    def test_changes_in_review_is_never_cancelled(self) -> None:
        self.fake.fail["commit"] = FakeResponse(
            400, {"error": {"message": "CHANGES_ALREADY_IN_REVIEW", "status": "FAILED_PRECONDITION"}}
        )
        with self.assertRaises(play.PlayError) as caught:
            self.replace()
        self.assertEqual(caught.exception.classification, "changes_in_review")
        self.assertEqual(self.fake.commits()[0]["params"]["changesInReviewBehavior"], "ERROR_IF_IN_REVIEW")
        self.assertNotIn("changesNotSentForReview", self.fake.commits()[0]["params"])
        self.assert_untouched()

    def test_missing_locale_is_not_created(self) -> None:
        with self.assertRaisesRegex(play.PlayError, "does not exist"):
            self.api.replace_image_set("fr-FR", WEAR, self.paths, expected_current=[], dry_run=False)
        self.assertEqual(self.fake.uploads, 0)
        self.assertEqual(self.fake.commits(), [])


class LocalValidationTest(ImageSetCase):
    def refused(self, paths, pattern, image_type=WEAR) -> None:
        with self.assertRaisesRegex(play.PlayError, pattern):
            self.api.replace_image_set(LANG, image_type, paths, expected_current=[], dry_run=False)
        self.assertEqual(self.fake.session.calls, [], "nothing may reach Play")

    def test_duplicate_path_or_content(self) -> None:
        self.refused([self.paths[0], self.paths[0]], "filename order|duplicate")
        twin = self.write([self.paths[0].read_bytes()], prefix="z-")
        self.refused([self.paths[0], *twin], "duplicate")

    def test_invalid_images(self) -> None:
        self.refused(self.write([png(454, 454, "a", color_type=6)], "alpha-"), "without alpha")
        self.refused(self.write([png(454, 400, "b")], "rect-"), "square")
        self.refused(self.write([png(300, 300, "c")], "tiny-"), "outside Play limits")
        self.refused(self.write([b"not an image"], "junk-"), "PNG or JPEG")
        self.refused([self.dir / "missing.png"], "not found")

    def test_count_and_type(self) -> None:
        self.refused(self.write([png(454, 454, f"n{i}") for i in range(9)], "nine-"), "1-8")
        self.refused([], "1-8")
        self.refused(self.paths, "unsupported screenshot type", image_type="featureGraphic")

    def test_jpeg_dimensions_skip_leading_segments(self) -> None:
        app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + bytes(9)
        sof0 = b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, 1920, 1080, 3) + bytes(6)
        self.assertEqual(play_management._image_info(b"\xff\xd8" + app0 + sof0), ("jpeg", 1080, 1920))

    def test_phone_aspect_cap(self) -> None:
        self.refused(self.write([png(400, 1000, "tall")], "tall-"), "outside Play limits", "phoneScreenshots")


class McpToolTest(ImageSetCase):
    def test_wrong_package_is_refused_before_approval(self) -> None:
        profile = SimpleNamespace(package_name="com.other.app")
        with patch.object(mcp_play_management.config, "load_profile", return_value=profile), patch.object(
            mcp_play_management, "_gate"
        ) as gate:
            result = mcp_play_management.play_replace_image_set(
                "example", PACKAGE, LANG, WEAR, [str(p) for p in self.paths], dry_run=False
            )
        self.assertEqual(result["status"], "refused")
        gate.assert_not_called()

    def test_denied_approval_never_reaches_play(self) -> None:
        profile = SimpleNamespace(package_name=PACKAGE)
        with patch.object(mcp_play_management.config, "load_profile", return_value=profile), patch.object(
            mcp_play_management, "_gate", return_value=(False, {"status": "human_approval_required"})
        ), patch.object(mcp_play_management, "_client") as client:
            result = mcp_play_management.play_replace_image_set(
                "example", PACKAGE, LANG, WEAR, [str(p) for p in self.paths],
                expected_current=[sha(d) for d in self.old], dry_run=False,
            )
        self.assertEqual(result["status"], "human_approval_required")
        client.assert_not_called()

    def test_approved_commit_is_tagged_high_risk(self) -> None:
        profile = SimpleNamespace(package_name=PACKAGE)
        with patch.object(mcp_play_management.config, "load_profile", return_value=profile), patch.object(
            mcp_play_management, "_gate", return_value=(True, {})
        ), patch.object(mcp_play_management, "_client", return_value=self.api):
            result = mcp_play_management.play_replace_image_set(
                "example", PACKAGE, LANG, WEAR, [str(p) for p in self.paths],
                expected_current=[sha(d) for d in self.old], dry_run=False,
            )
        self.assertEqual(result["status"], "committed_verified")
        self.assertEqual(result["_mra"], {"risk": "high", "human_approved": True})


if __name__ == "__main__":
    unittest.main()
