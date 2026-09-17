"""Play listing, tester, review, and diagnostic-management behaviour."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import play, play_management  # noqa: E402
from tests.fakes import FakeSession, ok  # noqa: E402

PACKAGE = "com.example.app"


def routes() -> dict:
    return {
        ("POST", "/edits"): ok({"id": "edit-1"}),
        ("POST", ":commit"): ok({"id": "edit-1"}),
        ("POST", ":validate"): ok({"id": "edit-1"}),
        ("DELETE", "/edits/"): ok({}),
        ("GET", "/listings"): ok({"listings": [{"language": "en-US", "title": "Old"}]}),
        ("PUT", "/listings/en-US"): ok({"language": "en-US", "title": "New"}),
        ("GET", "/testers/internal"): ok({"googleGroups": ["qa@example.com"]}),
        ("PUT", "/testers/internal"): ok({"googleGroups": ["qa@example.com"]}),
        ("GET", "/countryAvailability/production"): ok({"countries": [{"countryCode": "US"}]}),
        ("GET", "/reviews"): ok({"reviews": [{"reviewId": "review-1"}]}),
        ("POST", "/reviews/review-1:reply"): ok({"result": {"replyText": "Thanks"}}),
        ("GET", "/phoneScreenshots"): ok({"images": [{"id": "img-1"}]}),
        ("POST", "/phoneScreenshots"): ok({"image": {"id": "img-2"}}),
        ("POST", "/deobfuscationFiles/proguard"): ok({"deobfuscationFile": {"symbolType": "proguard"}}),
    }


def management() -> tuple[play_management.PlayManagementClient, FakeSession]:
    session = FakeSession(routes())
    base = play.PlayClient(PACKAGE, session=session)
    return play_management.PlayManagementClient(PACKAGE, client=base), session


class ListingTest(unittest.TestCase):
    def test_list_is_read_only_and_discards_edit(self) -> None:
        api, session = management()
        self.assertEqual(api.list_listings()[0]["language"], "en-US")
        self.assertFalse(any(":commit" in url for url in session.urls("POST")))
        self.assertFalse(any(":validate" in url for url in session.urls("POST")))
        self.assertTrue(session.urls("DELETE"))

    def test_dry_run_listing_update_validates_and_discards(self) -> None:
        api, session = management()
        result = api.update_listing(
            "en-US",
            title="New",
            short_description="Short",
            full_description="Full",
            dry_run=True,
        )
        self.assertFalse(result["committed"])
        body = session.body_for("PUT", "/listings/en-US")
        self.assertEqual(body["title"], "New")
        self.assertTrue(any(":validate" in url for url in session.urls("POST")))
        self.assertTrue(session.urls("DELETE"))


class TesterAndAvailabilityTest(unittest.TestCase):
    def test_tester_groups_are_trimmed_deduplicated_and_sorted(self) -> None:
        api, session = management()
        api.update_testers(
            "internal", [" b@example.com ", "a@example.com", "b@example.com"], dry_run=True
        )
        body = session.body_for("PUT", "/testers/internal")
        self.assertEqual(body["googleGroups"], ["a@example.com", "b@example.com"])

    def test_country_availability_is_readable(self) -> None:
        api, _ = management()
        result = api.get_country_availability("production")
        self.assertEqual(result["countries"][0]["countryCode"], "US")


class ReviewTest(unittest.TestCase):
    def test_reviews_are_readable(self) -> None:
        api, _ = management()
        self.assertEqual(api.list_reviews()[0]["reviewId"], "review-1")

    def test_reply_limit_is_checked_before_api_call(self) -> None:
        api, session = management()
        before = len(session.calls)
        with self.assertRaises(play.PlayError):
            api.reply_review("review-1", "x" * 351)
        self.assertEqual(len(session.calls), before)

    def test_valid_reply_is_sent(self) -> None:
        api, session = management()
        api.reply_review("review-1", "Thanks")
        self.assertEqual(session.body_for("POST", "/reviews/review-1:reply"), {"replyText": "Thanks"})


class AssetTest(unittest.TestCase):
    def test_image_upload_uses_upload_endpoint_and_dry_run_cleanup(self) -> None:
        api, session = management()
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "shot.png"
            image.write_bytes(b"png")
            result = api.upload_image("en-US", "phoneScreenshots", image, dry_run=True)
        self.assertFalse(result["committed"])
        upload = next(call for call in session.calls if "/phoneScreenshots" in call["url"] and call["method"] == "POST")
        self.assertIn("/upload/androidpublisher/v3/", upload["url"])
        self.assertEqual(upload["params"], {"uploadType": "media"})
        self.assertTrue(session.urls("DELETE"))

    def test_deobfuscation_type_is_validated_before_edit(self) -> None:
        api, session = management()
        before = len(session.calls)
        with tempfile.TemporaryDirectory() as directory:
            symbols = Path(directory) / "symbols.txt"
            symbols.write_text("x", encoding="utf-8")
            with self.assertRaises(play.PlayError):
                api.upload_deobfuscation_file(42, "mystery", symbols)
        self.assertEqual(len(session.calls), before)


if __name__ == "__main__":
    unittest.main()
