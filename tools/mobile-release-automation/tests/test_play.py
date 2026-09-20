"""Play edit-lifecycle behaviour, including the failure paths that matter."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

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
    """A Play failure must be classified without asserting an unproven cause.

    An earlier revision told the reader a 403 meant the service account was
    missing a separate monetization grant. Live probing disproved that: the
    same account/identity later returned 200 on convertRegionPrices and 404 on
    the one-time product upsert, so the 403 had been a transient or propagating
    authorization state. Naming one cause sent the reader to the wrong fix.
    """

    def raise_for(self, status_code: int, api_status: str):
        response = FakeResponse(
            status_code, {"error": {"code": status_code, "status": api_status}}
        )
        with self.assertRaises(play.PlayError) as caught:
            play._raise_for_status(response, "upsert one-time product pro")
        return caught.exception

    def test_each_status_gets_its_own_classification(self) -> None:
        for status_code, api_status, expected in (
            (400, "INVALID_ARGUMENT", "malformed_request"),
            (401, "UNAUTHENTICATED", "credential_not_accepted"),
            (403, "PERMISSION_DENIED", "authorization_denied"),
            (404, "NOT_FOUND", "resource_absent"),
            (500, "INTERNAL", "play_api_error"),
        ):
            error = self.raise_for(status_code, api_status)
            self.assertEqual(error.classification, expected)
            self.assertEqual(error.status_code, status_code)
            self.assertEqual(error.api_status, api_status)
            self.assertIn(f"classification: {expected}", str(error))

    def test_authorization_failures_name_the_active_identity(self) -> None:
        # An identity mismatch is the cheapest cause to rule out, so the
        # non-secret client_email must be in the message itself.
        with patch.object(play, "_publisher_identity", return_value="sa@example.iam.gserviceaccount.com"):
            for status_code, api_status in ((401, "UNAUTHENTICATED"), (403, "PERMISSION_DENIED")):
                message = str(self.raise_for(status_code, api_status))
                self.assertIn("active publisher identity: sa@example.iam.gserviceaccount.com", message)

    def test_unreadable_identity_does_not_mask_the_real_error(self) -> None:
        with patch.object(play, "_publisher_identity", return_value=None):
            message = str(self.raise_for(403, "PERMISSION_DENIED"))
        self.assertIn("HTTP 403", message)
        self.assertIn("could not be read", message)

    def test_permission_wording_outranks_the_status_code(self) -> None:
        """Play returns a real authorization failure as 400 INVALID_ARGUMENT.

        Observed verbatim from the live API when creating a one-time product:
        'Can\'t create product. To fix, request billing permission.' Trusting the
        status code alone classified that as malformed_request and told the
        reader access was not involved, which is the opposite of the truth.
        """
        response = FakeResponse(400, {"error": {
            "code": 400,
            "status": "INVALID_ARGUMENT",
            "message": 'Product "pro": Can\'t create product. To fix, request billing permission.',
        }})
        with self.assertRaises(play.PlayError) as caught:
            play._raise_for_status(response, "upsert one-time product pro")
        error = caught.exception
        self.assertEqual(error.classification, "authorization_denied")
        self.assertEqual(error.status_code, 400)
        message = str(error)
        self.assertIn("names a permission", message)
        self.assertIn("active publisher identity", message)
        self.assertNotIn("not the caller's access", message)

    def test_a_400_without_permission_wording_stays_malformed(self) -> None:
        response = FakeResponse(400, {"error": {
            "code": 400, "status": "INVALID_ARGUMENT", "message": "Invalid update_mask: [*]."
        }})
        with self.assertRaises(play.PlayError) as caught:
            play._raise_for_status(response, "upsert one-time product pro")
        self.assertEqual(caught.exception.classification, "malformed_request")
        # It must still refuse to declare access irrelevant.
        self.assertIn("before ruling access out", str(caught.exception))

    def test_permission_phrasings_are_recognized(self) -> None:
        for message in (
            "To fix, request billing permission.",
            "The caller does not have permission",
            "Caller is not authorized to perform this action",
            "permission denied for this package",
            "insufficient permission for monetization",
        ):
            classification, _ = play.classify_play_failure(400, "INVALID_ARGUMENT", message)
            self.assertEqual(classification, "authorization_denied", message)

    def test_403_offers_checks_and_never_asserts_a_missing_grant(self) -> None:
        message = str(self.raise_for(403, "PERMISSION_DENIED"))
        self.assertIn("distinguish before concluding a cause", message)
        # A 403 must be presented as ambiguous, including the transient case.
        self.assertIn("propagating", message)
        for claim in ("may lack", "Users and permissions", "need their own grant"):
            self.assertNotIn(claim, message)

    def test_non_authorization_failures_omit_the_identity_line(self) -> None:
        for status_code, api_status in ((400, "INVALID_ARGUMENT"), (404, "NOT_FOUND")):
            message = str(self.raise_for(status_code, api_status))
            self.assertNotIn("active publisher identity", message)

    def test_404_states_the_caller_was_authorized(self) -> None:
        self.assertIn("authorized", str(self.raise_for(404, "NOT_FOUND")))

    def test_detail_is_still_redacted(self) -> None:
        response = FakeResponse(403, {"error": {"message": "denied for Bearer ya29.CANARYTOKEN"}})
        with self.assertRaises(play.PlayError) as caught:
            play._raise_for_status(response, "read tracks")
        self.assertNotIn("ya29.CANARYTOKEN", str(caught.exception))


class PlayMutationFailureEvidenceTest(unittest.TestCase):
    """An approved mutation that the vendor refuses must keep its approval record."""

    def refuse(self, payload: dict, status_code: int = 400):
        from mra import mcp_play_monetization as monetization

        session = FakeSession(
            {("PATCH", "/onetimeproducts/pro"): lambda **_: FakeResponse(status_code, payload)}
        )
        with patch.object(monetization, "_package", return_value="com.example.app"), \
             patch.object(
                 monetization, "_client",
                 return_value=play.PlayClient("com.example.app", session=session),
             ), \
             patch.object(
                 monetization.human_approval, "request",
                 return_value={"approved": True, "status": "approved"},
             ):
            return monetization.play_upsert_one_time_product(
                "example", "pro", {"listings": []}, "2025/03"
            )

    def test_vendor_refusal_returns_structured_evidence_not_an_exception(self) -> None:
        result = self.refuse({"error": {
            "code": 400, "status": "INVALID_ARGUMENT",
            "message": "Can't create product. To fix, request billing permission.",
        }})
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["http_status"], 400)
        self.assertEqual(result["api_status"], "INVALID_ARGUMENT")
        self.assertEqual(result["classification"], "authorization_denied")
        # The operator did approve; a vendor refusal must not erase that.
        self.assertTrue(result["_mra"]["human_approved"])
        self.assertEqual(result["_mra"]["risk"], "high")

    def test_refusal_detail_is_redacted(self) -> None:
        result = self.refuse({"error": {
            "code": 403, "status": "PERMISSION_DENIED",
            "message": "denied for Bearer ya29.CANARYTOKEN",
        }}, status_code=403)
        self.assertNotIn("ya29.CANARYTOKEN", result["detail"])
