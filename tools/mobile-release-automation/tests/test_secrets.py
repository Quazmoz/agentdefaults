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
        self.tempdir.cleanup()

    def test_profile_resolves_its_bitwarden_secret(self) -> None:
        profile = config.Profile(slug="motionguard", revenuecat_secret_id=SECRET_ID)
        with mock.patch.object(auth.secret_provider, "bitwarden_secret", return_value="sk_motionguard") as get:
            self.assertEqual(auth.revenuecat_key(profile), "sk_motionguard")
        get.assert_called_once_with(SECRET_ID)

    def test_environment_override_still_wins(self) -> None:
        os.environ["REVENUECAT_V2_SECRET_KEY"] = "sk_ci_override"
        profile = config.Profile(slug="motionguard", revenuecat_secret_id=SECRET_ID)
        with mock.patch.object(auth.secret_provider, "bitwarden_secret") as get:
            self.assertEqual(auth.revenuecat_key(profile), "sk_ci_override")
        get.assert_not_called()

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


if __name__ == "__main__":
    unittest.main()
