"""Tests for external secret-manager integration."""

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

from mra import auth, config, secure_cli, secrets  # noqa: E402


SECRET_ID = "6f7c12c0-df7b-4a2b-9360-1539a4d13392"
BOOTSTRAP_SECRET_ID = "00000000-0000-0000-0000-000000000099"
PROFILE_SECRET_ID = "00000000-0000-0000-0000-000000000100"


class BitwardenSecretProviderTest(unittest.TestCase):
    def test_secret_token_is_child_environment_only(self) -> None:
        completed = mock.Mock(returncode=0, stdout=json.dumps({"value": "sk_example"}))
        with mock.patch.object(secrets.keychain, "bitwarden_access_token", return_value="bootstrap-token"), \
             mock.patch.object(secrets.shutil, "which", return_value="/usr/local/bin/bws"), \
             mock.patch.object(secrets.subprocess, "run", return_value=completed) as run:
            value = secrets.bitwarden_secret(SECRET_ID)

        self.assertEqual(value, "sk_example")
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


class RevenueCatSecretResolutionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.previous_home = os.environ.get("MRA_HOME")
        self.previous_key = os.environ.pop("REVENUECAT_V2_SECRET_KEY", None)
        os.environ["MRA_HOME"] = self.tempdir.name

    def tearDown(self) -> None:
        if self.previous_home is None:
            os.environ.pop("MRA_HOME", None)
        else:
            os.environ["MRA_HOME"] = self.previous_home
        if self.previous_key is not None:
            os.environ["REVENUECAT_V2_SECRET_KEY"] = self.previous_key
        else:
            os.environ.pop("REVENUECAT_V2_SECRET_KEY", None)
        self.tempdir.cleanup()

    def test_profile_resolves_its_bitwarden_secret(self) -> None:
        profile = config.Profile(slug="motionguard", revenuecat_secret_id=SECRET_ID)
        with mock.patch.object(auth.secret_provider, "bitwarden_secret", return_value="sk_motionguard") as get:
            self.assertEqual(auth.revenuecat_key(profile), "sk_motionguard")
        get.assert_called_once_with(SECRET_ID)

    def test_profile_secret_beats_stale_environment_override(self) -> None:
        os.environ["REVENUECAT_V2_SECRET_KEY"] = "sk_wrong_app"
        profile = config.Profile(slug="motionguard", revenuecat_secret_id=SECRET_ID)
        with mock.patch.object(auth.secret_provider, "bitwarden_secret", return_value="sk_motionguard") as get:
            self.assertEqual(auth.revenuecat_key(profile), "sk_motionguard")
        get.assert_called_once_with(SECRET_ID)

    def test_environment_override_remains_for_unprofiled_legacy_use(self) -> None:
        os.environ["REVENUECAT_V2_SECRET_KEY"] = "sk_ci_override"
        self.assertEqual(auth.revenuecat_key(), "sk_ci_override")

    def test_profile_without_key_inherits_global_bootstrap_reference_in_memory(self) -> None:
        config.save_profile(
            config.Profile(slug="webhookdeck", package_name="com.quazmoz.webhookdeck")
        )
        config.save_secret_refs(
            config.SecretRefs(revenuecat_bootstrap_secret_id=BOOTSTRAP_SECRET_ID)
        )

        persisted = config.load_profiles()["webhookdeck"]
        effective = config.load_profile("webhookdeck")

        self.assertIsNone(persisted.revenuecat_secret_id)
        self.assertEqual(effective.revenuecat_secret_id, BOOTSTRAP_SECRET_ID)
        self.assertEqual(
            auth.revenuecat_credential_source(effective),
            "global-bootstrap-bitwarden",
        )

    def test_bootstrap_key_is_used_when_profile_has_no_project_specific_key(self) -> None:
        config.save_profile(config.Profile(slug="webhookdeck"))
        config.save_secret_refs(
            config.SecretRefs(revenuecat_bootstrap_secret_id=BOOTSTRAP_SECRET_ID)
        )
        profile = config.load_profile("webhookdeck")
        with mock.patch.object(
            auth.secret_provider,
            "bitwarden_secret",
            return_value="sk_bootstrap",
        ) as get:
            self.assertEqual(auth.revenuecat_key(profile), "sk_bootstrap")
        get.assert_called_once_with(BOOTSTRAP_SECRET_ID)

    def test_project_specific_key_beats_global_bootstrap_key(self) -> None:
        config.save_secret_refs(
            config.SecretRefs(revenuecat_bootstrap_secret_id=BOOTSTRAP_SECRET_ID)
        )
        config.save_profile(
            config.Profile(slug="motionguard", revenuecat_secret_id=PROFILE_SECRET_ID)
        )
        profile = config.load_profile("motionguard")
        with mock.patch.object(
            auth.secret_provider,
            "bitwarden_secret",
            return_value="sk_motionguard",
        ) as get:
            self.assertEqual(auth.revenuecat_key(profile), "sk_motionguard")
        get.assert_called_once_with(PROFILE_SECRET_ID)
        self.assertEqual(auth.revenuecat_credential_source(profile), "profile-bitwarden")

    def test_agent_cli_binds_secret_reference_without_value(self) -> None:
        config.save_profile(
            config.Profile(
                slug="motionguard",
                package_name="com.quazmoz.motionguard",
                revenuecat_project_id="proj_example",
            )
        )
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = secure_cli.main(
                ["profile", "bind-revenuecat", "--profile", "motionguard", "--secret-id", SECRET_ID]
            )
        self.assertEqual(result, 0)
        profile = config.load_profile("motionguard")
        self.assertEqual(profile.revenuecat_secret_id, SECRET_ID)
        self.assertNotIn("sk_", stdout.getvalue())

    def test_agent_cli_binds_global_bootstrap_reference_without_value(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = secure_cli.main(
                ["auth", "bind-revenuecat-bootstrap", "--secret-id", BOOTSTRAP_SECRET_ID]
            )
        self.assertEqual(result, 0)
        self.assertEqual(
            config.load_secret_refs().revenuecat_bootstrap_secret_id,
            BOOTSTRAP_SECRET_ID,
        )
        self.assertNotIn("sk_", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
