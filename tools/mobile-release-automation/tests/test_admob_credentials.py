"""Tests for Bitwarden-backed AdMob OAuth and keychain token storage."""

from __future__ import annotations

from pathlib import Path
from unittest import mock
import contextlib
import io
import json
import os
import sys
import tempfile
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import admob_credentials, config, keychain, secure_cli  # noqa: E402

SECRET_ID = "7c1f10c4-7ac6-4b87-a2fe-f4a5b88f452e"

CLIENT = {
    "installed": {
        "client_id": "example.apps.googleusercontent.com",
        "project_id": "mra-admob",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_secret": "example-client-secret",
        "redirect_uris": ["http://localhost"],
    }
}


class AdMobCredentialTest(unittest.TestCase):
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

    def test_client_resolves_from_bitwarden_uuid(self) -> None:
        config.save_secret_refs(config.SecretRefs(admob_oauth_client_secret_id=SECRET_ID))
        with mock.patch.object(
            admob_credentials.secret_provider,
            "bitwarden_secret",
            return_value=json.dumps(CLIENT),
        ) as get:
            info = admob_credentials.installed_client_info()
        self.assertEqual(info["client_id"], CLIENT["installed"]["client_id"])
        get.assert_called_once_with(SECRET_ID)

    def test_non_desktop_oauth_json_is_rejected(self) -> None:
        config.save_secret_refs(config.SecretRefs(admob_oauth_client_secret_id=SECRET_ID))
        with mock.patch.object(
            admob_credentials.secret_provider,
            "bitwarden_secret",
            return_value=json.dumps({"web": CLIENT["installed"]}),
        ):
            with self.assertRaises(config.ConfigError):
                admob_credentials.oauth_client_config()

    def test_agent_cli_binds_uuid_without_secret_value(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = secure_cli.main(["auth", "bind-admob", "--secret-id", SECRET_ID])
        self.assertEqual(result, 0)
        self.assertEqual(config.load_secret_refs().admob_oauth_client_secret_id, SECRET_ID)
        self.assertNotIn("client_secret", stdout.getvalue())

    def test_refresh_token_uses_keyring_backend(self) -> None:
        fake = types.SimpleNamespace(
            get_password=mock.Mock(return_value="refresh-example"),
            set_password=mock.Mock(),
        )
        with mock.patch.dict(sys.modules, {"keyring": fake}):
            self.assertEqual(keychain.admob_refresh_token(), "refresh-example")
            keychain.store_admob_refresh_token("refresh-new")

        fake.get_password.assert_called_once_with(
            keychain.ADMOB_KEYCHAIN_SERVICE,
            keychain.ADMOB_REFRESH_TOKEN_ACCOUNT,
        )
        fake.set_password.assert_called_once_with(
            keychain.ADMOB_KEYCHAIN_SERVICE,
            keychain.ADMOB_REFRESH_TOKEN_ACCOUNT,
            "refresh-new",
        )


if __name__ == "__main__":
    unittest.main()
