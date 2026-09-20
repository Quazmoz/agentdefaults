"""Credential hygiene and the mutation confirmation gate.

These are the tests that matter most: they are what stops an agent from leaking
a key or changing a live store without authorization.
"""

from __future__ import annotations

from pathlib import Path
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import cli, config  # noqa: E402


class CredentialHygieneTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.previous = os.environ.get("MRA_HOME")
        os.environ["MRA_HOME"] = self.tempdir.name

    def tearDown(self) -> None:
        if self.previous is None:
            os.environ.pop("MRA_HOME", None)
        else:
            os.environ["MRA_HOME"] = self.previous
        self.tempdir.cleanup()

    def _write(self, name: str, mode: int, content: str = "{}") -> Path:
        path = Path(self.tempdir.name) / name
        path.write_text(content, encoding="utf-8")
        path.chmod(mode)
        return path

    def test_rejects_group_or_world_readable_credentials(self) -> None:
        self._write(config.PLAY_SERVICE_ACCOUNT, 0o644)
        with self.assertRaises(config.ConfigError) as caught:
            config.require_file(config.PLAY_SERVICE_ACCOUNT, "hint")
        self.assertIn("chmod 600", str(caught.exception))

    def test_accepts_owner_only_credentials(self) -> None:
        expected = self._write(config.PLAY_SERVICE_ACCOUNT, 0o600)
        self.assertEqual(config.require_file(config.PLAY_SERVICE_ACCOUNT, "hint"), expected)

    def test_missing_credential_reports_the_remediation_hint(self) -> None:
        with self.assertRaises(config.ConfigError) as caught:
            config.require_file(config.PLAY_SERVICE_ACCOUNT, "do the thing")
        self.assertIn("do the thing", str(caught.exception))

    def test_environment_variable_wins_over_file(self) -> None:
        self._write(config.REVENUECAT_KEY, 0o600, "from-file")
        os.environ["RC_TEST_KEY"] = "from-env"
        try:
            self.assertEqual(
                config.read_secret(config.REVENUECAT_KEY, "RC_TEST_KEY", "hint"), "from-env"
            )
        finally:
            os.environ.pop("RC_TEST_KEY")

    def test_profiles_merge_instead_of_overwriting(self) -> None:
        config.save_profile(config.Profile(slug="app", package_name="com.example.app"))
        config.save_profile(config.Profile(slug="app", revenuecat_project_id="proj_1"))
        profile = config.load_profile("app")
        self.assertEqual(profile.package_name, "com.example.app")
        self.assertEqual(profile.revenuecat_project_id, "proj_1")

    def test_profile_file_is_written_owner_only(self) -> None:
        path = config.save_profile(config.Profile(slug="app", package_name="com.example.app"))
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_unknown_profile_key_is_rejected(self) -> None:
        path = Path(self.tempdir.name) / config.PROFILES
        path.write_text(json.dumps({"app": {"secret_token": "oops"}}), encoding="utf-8")
        with self.assertRaises(config.ConfigError):
            config.load_profiles()

    def test_unknown_profile_slug_lists_known_slugs(self) -> None:
        config.save_profile(config.Profile(slug="known", package_name="com.example.app"))
        with self.assertRaises(config.ConfigError) as caught:
            config.load_profile("missing")
        self.assertIn("known", str(caught.exception))


class ConfirmationGateTest(unittest.TestCase):
    """Every mutating command must refuse to run without --yes."""

    MUTATING_COMMANDS = [
        ["play", "publish", "--package", "com.example.app", "--aab", "app.aab"],
        ["play", "promote", "--package", "com.example.app", "--source", "internal", "--target", "production"],
        ["play", "create-subscription", "--package", "com.example.app", "--product-id", "p", "--body", "b.json"],
        ["admob", "create-app", "--name", "Example"],
        ["admob", "create-adunit", "--app-id", "ca-app-pub-1~2", "--name", "n", "--format", "BANNER"],
        ["rc", "create-play-app", "--project", "proj_1", "--name", "Example"],
        ["rc", "create-product", "--project", "proj_1", "--app-id", "a", "--store-identifier", "s", "--type", "subscription"],
    ]

    def test_mutating_commands_refuse_without_yes(self) -> None:
        for argv in self.MUTATING_COMMANDS:
            with self.subTest(command=" ".join(argv)):
                with self.assertRaises(SystemExit) as caught:
                    cli.main(argv)
                self.assertIn("--yes", str(caught.exception))

    def test_dry_run_publish_does_not_need_yes(self) -> None:
        argv = [
            "play", "publish", "--package", "com.example.app",
            "--aab", "app.aab", "--dry-run",
        ]
        # It must get past the gate; it then fails on credentials, not on --yes.
        # cli.main reports that failure on stderr, which is noise here.
        with contextlib.redirect_stderr(io.StringIO()):
            try:
                cli.main(argv)
            except SystemExit as error:  # pragma: no cover - defensive
                self.assertNotIn("--yes", str(error))
            except Exception:  # noqa: BLE001 - any later failure proves the gate passed
                pass


class AdMobErrorEvidenceTest(unittest.TestCase):
    """A failed vendor call must stay both redacted and audit-truthful."""

    def payload(self, message: str, approved: bool = True) -> dict:
        from mra import admob, mcp_admob_tools

        return mcp_admob_tools._access_payload(
            admob.AdMobAccessDenied(message), "high", approved
        )

    def test_operator_approval_survives_a_vendor_failure(self) -> None:
        # The approval of an irreversible action is the audit trail; a later
        # 403 must not rewrite it into "nobody approved this".
        self.assertTrue(self.payload("denied")["_mra"]["human_approved"])
        self.assertFalse(self.payload("denied", approved=False)["_mra"]["human_approved"])

    def test_error_detail_is_redacted_but_still_diagnostic(self) -> None:
        detail = self.payload(
            "403 denied; refresh_token=1//0gCANARY&client_secret=GOCSPX-canary; "
            "Bearer ya29.CANARYTOKEN"
        )["detail"]
        for canary in ("1//0gCANARY", "GOCSPX-canary", "ya29.CANARYTOKEN"):
            self.assertNotIn(canary, detail)
        self.assertIn("403 denied", detail)


class RedactionPatternTest(unittest.TestCase):
    def test_bare_key_value_credentials_are_redacted(self) -> None:
        from mra import redaction

        # Form-encoded/query-string shape, as an OAuth token endpoint echoes it.
        redacted = redaction.redact_text(
            "grant_type=refresh_token&refresh_token=1//0gCANARY&client_secret=GOCSPX-canary"
        )
        self.assertNotIn("1//0gCANARY", redacted)
        self.assertNotIn("GOCSPX-canary", redacted)
        self.assertIn("grant_type=refresh_token", redacted)

    def test_json_quoted_credentials_are_still_redacted(self) -> None:
        from mra import redaction

        redacted = redaction.redact_text('{"refresh_token": "1//0gCANARY", "ok": true}')
        self.assertNotIn("1//0gCANARY", redacted)
        self.assertIn('"ok": true', redacted)


class NotesParsingTest(unittest.TestCase):
    def test_parses_language_assignments(self) -> None:
        self.assertEqual(
            cli.parse_notes(["en-US=Hello", "de-DE=Hallo"]),
            {"en-US": "Hello", "de-DE": "Hallo"},
        )

    def test_keeps_equals_signs_inside_the_text(self) -> None:
        self.assertEqual(cli.parse_notes(["en-US=a=b"]), {"en-US": "a=b"})

    def test_rejects_notes_without_a_language(self) -> None:
        with self.assertRaises(SystemExit):
            cli.parse_notes(["no-language-here"])

    def test_no_notes_is_none(self) -> None:
        self.assertIsNone(cli.parse_notes(None))


if __name__ == "__main__":
    unittest.main()
