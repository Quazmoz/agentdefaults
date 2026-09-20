"""Tests for the official RevenueCat CLI OAuth transport."""

from __future__ import annotations

from pathlib import Path
from unittest import mock
import json
import os
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import config, revenuecat_cli  # noqa: E402


class RevenueCatCliOAuthTest(unittest.TestCase):
    def completed(self, payload: dict, returncode: int = 0, stderr: str = ""):
        return mock.Mock(
            returncode=returncode,
            stdout=json.dumps(payload),
            stderr=stderr,
        )

    def test_auth_status_requires_oauth(self) -> None:
        payload = {
            "data": {
                "authenticated": True,
                "method": "oauth",
                "account_email": "dev@example.com",
            }
        }
        with mock.patch.object(revenuecat_cli.shutil, "which", return_value="/usr/local/bin/rc"), \
             mock.patch.object(
                 revenuecat_cli.subprocess,
                 "run",
                 return_value=self.completed(payload),
             ) as run:
            status = revenuecat_cli.auth_status()

        self.assertEqual(status["status"], "ready")
        self.assertEqual(status["method"], "oauth")
        self.assertEqual(status["source"], "official-revenuecat-cli-oauth")
        self.assertIn("auth", run.call_args.args[0])
        self.assertIn("status", run.call_args.args[0])

    def test_auth_status_accepts_cli_decorated_oauth_method(self) -> None:
        payload = {
            "data": {
                "authenticated": True,
                "auth_origin": "oauth_login",
                "credential_source": "oauth",
                "method": "oauth (expires 2026-09-18 19:04)",
                "profile": "default",
                "token_can_refresh": True,
                "token_status": "valid",
            }
        }
        with mock.patch.object(revenuecat_cli.shutil, "which", return_value="/opt/homebrew/bin/rc"), \
             mock.patch.object(
                 revenuecat_cli.subprocess,
                 "run",
                 return_value=self.completed(payload),
             ):
            status = revenuecat_cli.auth_status()

        self.assertEqual(status["status"], "ready")
        self.assertEqual(status["method"], "oauth")
        self.assertEqual(status["source"], "official-revenuecat-cli-oauth")

    def test_api_key_login_is_rejected(self) -> None:
        payload = {"data": {"authenticated": True, "method": "api_key"}}
        with mock.patch.object(revenuecat_cli.shutil, "which", return_value="/usr/local/bin/rc"), \
             mock.patch.object(
                 revenuecat_cli.subprocess,
                 "run",
                 return_value=self.completed(payload),
             ):
            with self.assertRaises(config.ConfigError) as caught:
                revenuecat_cli.auth_status()
        self.assertIn("API key, not OAuth", str(caught.exception))

    def test_credential_source_outranks_oauth_looking_method(self) -> None:
        """credential_source is the stable discriminator, so it must decide."""
        payload = {
            "data": {
                "authenticated": True,
                "credential_source": "api_key",
                "method": "oauth (expires 2026-09-18 19:04)",
            }
        }
        with mock.patch.object(revenuecat_cli.shutil, "which", return_value="/usr/local/bin/rc"), \
             mock.patch.object(
                 revenuecat_cli.subprocess,
                 "run",
                 return_value=self.completed(payload),
             ):
            with self.assertRaises(config.ConfigError) as caught:
                revenuecat_cli.auth_status()
        self.assertIn("API key, not OAuth", str(caught.exception))

    def test_environment_api_key_overrides_are_removed(self) -> None:
        payload = {"data": {"authenticated": True, "method": "oauth"}}
        api_payload = {"items": []}
        previous_rc = os.environ.get("RC_API_KEY")
        previous_legacy = os.environ.get("REVENUECAT_V2_SECRET_KEY")
        os.environ["RC_API_KEY"] = "sk_should_not_escape"
        os.environ["REVENUECAT_V2_SECRET_KEY"] = "sk_legacy_should_not_escape"
        try:
            with mock.patch.object(revenuecat_cli.shutil, "which", return_value="/usr/local/bin/rc"), \
                 mock.patch.object(
                     revenuecat_cli.subprocess,
                     "run",
                     side_effect=[self.completed(payload), self.completed(api_payload)],
                 ) as run:
                result = revenuecat_cli.api_call("GET", "/projects")

            self.assertEqual(result, api_payload)
            child_env = run.call_args_list[-1].kwargs["env"]
            self.assertNotIn("RC_API_KEY", child_env)
            self.assertNotIn("REVENUECAT_V2_SECRET_KEY", child_env)
        finally:
            if previous_rc is None:
                os.environ.pop("RC_API_KEY", None)
            else:
                os.environ["RC_API_KEY"] = previous_rc
            if previous_legacy is None:
                os.environ.pop("REVENUECAT_V2_SECRET_KEY", None)
            else:
                os.environ["REVENUECAT_V2_SECRET_KEY"] = previous_legacy

    def test_api_body_uses_stdin_not_command_line(self) -> None:
        auth_payload = {"data": {"authenticated": True, "method": "oauth"}}
        created = {"id": "proj_new", "name": "WebHookDeck"}
        body = {"name": "WebHookDeck"}
        with mock.patch.object(revenuecat_cli.shutil, "which", return_value="/usr/local/bin/rc"), \
             mock.patch.object(
                 revenuecat_cli.subprocess,
                 "run",
                 side_effect=[self.completed(auth_payload), self.completed(created)],
             ) as run:
            result = revenuecat_cli.api_call("POST", "/projects", body=body)

        self.assertEqual(result, created)
        argv = run.call_args_list[-1].args[0]
        self.assertIn("@-", argv)
        self.assertNotIn("WebHookDeck", argv)
        self.assertEqual(json.loads(run.call_args_list[-1].kwargs["input"]), body)

    def test_missing_cli_has_actionable_error(self) -> None:
        with mock.patch.object(revenuecat_cli.shutil, "which", return_value=None):
            with self.assertRaises(config.ConfigError) as caught:
                revenuecat_cli.auth_status()
        self.assertIn("brew install RevenueCat/tap/rc", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
