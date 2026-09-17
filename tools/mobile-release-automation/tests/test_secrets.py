"""Tests for external secret-manager integration and RevenueCat key migration."""

from __future__ import annotations

from pathlib import Path
from unittest import mock
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import config, secure_cli, secrets  # noqa: E402


SECRET_ID = "6f7c12c0-df7b-4a2b-9360-1539a4d13392"
LEGACY_BOOTSTRAP_SECRET_ID = "00000000-0000-0000-0000-000000000099"
LEGACY_PROFILE_SECRET_ID = "00000000-0000-0000-0000-000000000100"


class BitwardenSecretProviderTest(unittest.TestCase):
    def test_secret_token_is_child_environment_only(self) -> None:
        completed = mock.Mock(returncode=0, stdout=json.dumps({"value": "secret-example"}))
        with mock.patch.object(secrets.keychain, "bitwarden_access_token", return_value="bootstrap-token"), \
             mock.patch.object(secrets.shutil, "which", return_value="/usr/local/bin/bws"), \
             mock.patch.object(secrets.subprocess, "run", return_value=completed) as run:
            value = secrets.bitwarden_secret(SECRET_ID)

        self.assertEqual(value, "secret-example")
        argv = run.call_args.args[0]
        self.assertNotIn("bootstrap-token", argv)
        self.assertEqual(run.call_args.kwargs["env"]["BWS_ACCESS_TOKEN"], "bootstrap-token")

    def test_invalid_uuid_is_rejected_before_provider_call(self) -> None:
        with mock.patch.object(secrets.subprocess, "run") as run:
            with self.assertRaises(config.ConfigError):
                secrets.bitwarden_secret("not-a-uuid")
        run.assert_not_called()

    def test_provider_failure_does_not_echo_provider_output(self) -> None:
        completed = mock.Mock(returncode=1, stdout="sensitive-output", stderr="sensitive-error")
        with mock.patch.object(secrets.keychain, "bitwarden_access_token", return_value="token"), \
             mock.patch.object(secrets.shutil, "which", return_value="/usr/local/bin/bws"), \
             mock.patch.object(secrets.subprocess, "run", return_value=completed):
            with self.assertRaises(config.ConfigError) as caught:
                secrets.bitwarden_secret(SECRET_ID)
        self.assertNotIn("sensitive-output", str(caught.exception))
        self.assertNotIn("sensitive-error", str(caught.exception))


class RevenueCatOAuthMigrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.previous_home = os.environ.get("MRA_HOME")
        os.environ["MRA_HOME"] = self.tempdir.name

    def tearDown(self) -> None:
        if self.previous_home is None:
            os.environ.pop("MRA_HOME", None)
        else:
            os.environ["MRA_HOME"] = self.previous_home
        self.tempdir.cleanup()

    def test_profile_without_legacy_key_gets_nonsecret_oauth_marker_in_memory(self) -> None:
        config.save_profile(
            config.Profile(slug="webhookdeck", package_name="com.quazmoz.webhookdeck")
        )
        persisted = config.load_profiles()["webhookdeck"]
        effective = config.load_profile("webhookdeck")

        self.assertIsNone(persisted.revenuecat_secret_id)
        self.assertEqual(effective.revenuecat_secret_id, config.REVENUECAT_OAUTH_MARKER)

    def test_oauth_marker_is_never_persisted(self) -> None:
        config.save_profile(config.Profile(slug="webhookdeck"))
        config.save_profile(
            config.Profile(
                slug="webhookdeck",
                revenuecat_secret_id=config.REVENUECAT_OAUTH_MARKER,
                revenuecat_project_id="proj_example",
            )
        )
        persisted = config.load_profiles()["webhookdeck"]
        self.assertIsNone(persisted.revenuecat_secret_id)
        self.assertEqual(persisted.revenuecat_project_id, "proj_example")

    def test_legacy_bootstrap_reference_still_loads_but_is_not_inherited(self) -> None:
        config.save_profile(config.Profile(slug="webhookdeck"))
        config.save_secret_refs(
            config.SecretRefs(revenuecat_bootstrap_secret_id=LEGACY_BOOTSTRAP_SECRET_ID)
        )
        effective = config.load_profile("webhookdeck")
        self.assertEqual(effective.revenuecat_secret_id, config.REVENUECAT_OAUTH_MARKER)
        self.assertEqual(
            config.load_secret_refs().revenuecat_bootstrap_secret_id,
            LEGACY_BOOTSTRAP_SECRET_ID,
        )

    def test_legacy_profile_key_remains_loadable_for_migration(self) -> None:
        config.save_profile(
            config.Profile(slug="motionguard", revenuecat_secret_id=LEGACY_PROFILE_SECRET_ID)
        )
        self.assertEqual(
            config.load_profile("motionguard").revenuecat_secret_id,
            LEGACY_PROFILE_SECRET_ID,
        )

    def test_agent_cli_revenuecat_key_bind_commands_are_deprecated_noops(self) -> None:
        config.save_profile(config.Profile(slug="motionguard"))
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = secure_cli.main(
                ["profile", "bind-revenuecat", "--profile", "motionguard", "--secret-id", SECRET_ID]
            )
        self.assertEqual(result, 0)
        self.assertIn("deprecated", stdout.getvalue())
        self.assertIsNone(config.load_profiles()["motionguard"].revenuecat_secret_id)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = secure_cli.main(
                ["auth", "bind-revenuecat-bootstrap", "--secret-id", LEGACY_BOOTSTRAP_SECRET_ID]
            )
        self.assertEqual(result, 0)
        self.assertIn("deprecated", stdout.getvalue())
        self.assertIsNone(config.load_secret_refs().revenuecat_bootstrap_secret_id)


if __name__ == "__main__":
    unittest.main()
