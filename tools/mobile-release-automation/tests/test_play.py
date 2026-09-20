"""Play edit-lifecycle behaviour, including the failure paths that matter."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import play  # noqa: E402
from tests.fakes import FakeResponse, FakeSession, ok  # noqa: E402

PACKAGE = "com.example.app"


def play_routes(track_payload: dict | None = None) -> dict:
    return {
        ("POST", "/edits"): ok({"id": "edit-1"}),
        ("POST", "/bundles"): ok({"versionCode": 42, "sha1": "s1", "sha256": "s256"}),
        ("PUT", "/tracks/"): ok({"track": "internal"}),
        ("POST", ":commit"): ok({"id": "edit-1"}),
        ("POST", ":validate"): ok({"id": "edit-1"}),
        ("DELETE", "/edits/"): ok({}),
        # Fragments are chosen so the longest match resolves to the right route:
        # "tracks/internal" (read one) is longer than "edit-1/tracks" (list all).
        ("GET", "tracks/internal"): ok(track_payload or {"track": "internal", "releases": []}),
        ("GET", "edit-1/tracks"): ok({"tracks": [{"track": "internal"}]}),
    }


def client(routes: dict) -> tuple[play.PlayClient, FakeSession]:
    session = FakeSession(routes)
    return play.PlayClient(PACKAGE, session=session), session


class PublishBundleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.aab = Path(self.tempdir.name) / "app-release.aab"
        self.aab.write_bytes(b"not-a-real-bundle")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_commits_and_uses_documented_upload_endpoint(self) -> None:
        api, session = client(play_routes())
        result = play.publish_bundle(PACKAGE, self.aab, track="internal", client=api)

        self.assertEqual(result["version_code"], 42)
        self.assertTrue(result["committed"])

        upload = next(call for call in session.calls if "/bundles" in call["url"])
        self.assertIn("/upload/androidpublisher/v3/", upload["url"])
        self.assertEqual(upload["params"], {"uploadType": "media"})
        self.assertEqual(upload["headers"]["Content-Type"], "application/octet-stream")

        self.assertTrue(any(":commit" in url for url in session.urls("POST")))
        self.assertFalse(any("DELETE" == call["method"] for call in session.calls))

    def test_dry_run_validates_discards_and_never_commits(self) -> None:
        api, session = client(play_routes())
        result = play.publish_bundle(
            PACKAGE, self.aab, track="internal", dry_run=True, client=api
        )

        self.assertFalse(result["committed"])
        self.assertTrue(any(":validate" in url for url in session.urls("POST")))
        self.assertFalse(any(":commit" in url for url in session.urls("POST")))
        self.assertTrue(session.urls("DELETE"), "dry-run must discard the edit")

    def test_failed_upload_still_deletes_the_edit(self) -> None:
        routes = play_routes()
        routes[("POST", "/bundles")] = lambda **_: _raise()
        api, session = client(routes)

        with self.assertRaises(RuntimeError):
            play.publish_bundle(PACKAGE, self.aab, track="internal", client=api)

        self.assertTrue(session.urls("DELETE"), "a failed edit must not be left open")

    def test_release_notes_become_language_entries(self) -> None:
        api, session = client(play_routes())
        play.publish_bundle(
            PACKAGE,
            self.aab,
            track="internal",
            release_notes={"en-US": "first", "de-DE": "erste"},
            client=api,
        )
        body = session.body_for("PUT", "/tracks/internal")
        notes = body["releases"][0]["releaseNotes"]
        self.assertEqual([entry["language"] for entry in notes], ["de-DE", "en-US"])

    def test_missing_bundle_fails_before_opening_an_edit(self) -> None:
        api, session = client(play_routes())
        with self.assertRaises(play.PlayError):
            play.publish_bundle(PACKAGE, Path("/nonexistent.aab"), "internal", client=api)
        # The edit is opened first, so it must also be cleaned up.
        self.assertTrue(session.urls("DELETE"))


def _raise():
    raise play.PlayError("upload exploded")


class TrackReleaseValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.api, self.session = client(play_routes())

    def test_rejects_unknown_status(self) -> None:
        with self.assertRaises(play.PlayError):
            self.api.set_track_release("edit-1", "internal", [1], status="shipped")

    def test_in_progress_requires_a_user_fraction(self) -> None:
        with self.assertRaises(play.PlayError):
            self.api.set_track_release("edit-1", "internal", [1], status="inProgress")

    def test_rejects_out_of_range_user_fraction(self) -> None:
        for fraction in (0, 1, 1.5, -0.1):
            with self.assertRaises(play.PlayError):
                self.api.set_track_release(
                    "edit-1", "internal", [1], status="inProgress", user_fraction=fraction
                )

    def test_version_codes_are_sent_as_strings(self) -> None:
        self.api.set_track_release("edit-1", "internal", [42, 43])
        body = self.session.body_for("PUT", "/tracks/internal")
        self.assertEqual(body["releases"][0]["versionCodes"], ["42", "43"])


class PromoteTest(unittest.TestCase):
    def test_derives_version_codes_from_the_source_track(self) -> None:
        routes = play_routes(
            {"track": "internal", "releases": [{"versionCodes": ["42"], "status": "completed"}]}
        )
        api, session = client(routes)
        result = play.promote(PACKAGE, "internal", "alpha", client=api)

        self.assertEqual(result["version_codes"], [42])
        body = session.body_for("PUT", "/tracks/alpha")
        self.assertEqual(body["releases"][0]["versionCodes"], ["42"])

    def test_refuses_to_promote_an_empty_track(self) -> None:
        api, session = client(play_routes({"track": "internal", "releases": []}))
        with self.assertRaises(play.PlayError):
            play.promote(PACKAGE, "internal", "alpha", client=api)
        self.assertTrue(session.urls("DELETE"))


class ReadOnlyTest(unittest.TestCase):
    def test_track_status_does_not_validate_or_commit(self) -> None:
        api, session = client(play_routes())
        play.track_status(PACKAGE, client=api)
        posts = session.urls("POST")
        self.assertFalse(any(":commit" in url for url in posts))
        self.assertFalse(any(":validate" in url for url in posts))
        self.assertTrue(session.urls("DELETE"))


if __name__ == "__main__":
    unittest.main()


class PlayErrorClassificationTest(unittest.TestCase):
    def test_403_explains_the_play_console_permission_split(self) -> None:
        # Read/release access and monetization-write access are granted
        # separately, so a bare PERMISSION_DENIED is not actionable on its own.
        response = FakeResponse(403, {"error": {"code": 403, "status": "PERMISSION_DENIED"}})
        with self.assertRaises(play.PlayError) as caught:
            play._raise_for_status(response, "upsert one-time product pro")
        message = str(caught.exception)
        self.assertIn("HTTP 403", message)
        self.assertIn("Users and permissions", message)

    def test_other_errors_do_not_get_the_permission_hint(self) -> None:
        response = FakeResponse(400, {"error": {"code": 400, "status": "INVALID_ARGUMENT"}})
        with self.assertRaises(play.PlayError) as caught:
            play._raise_for_status(response, "upsert one-time product pro")
        self.assertNotIn("Users and permissions", str(caught.exception))
