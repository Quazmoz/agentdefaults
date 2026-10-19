"""Regression tests for redaction at agent-facing MRA tool boundaries."""

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from mra import (
    cli,
    mcp_admob_tools,
    mcp_play_management,
    mcp_play_monetization,
    mcp_play_mutations,
    mcp_revenuecat_management,
    mcp_revenuecat_mutations,
    secure_cli,
    secure_mcp_server,
    redaction,
)


class AgentOutputRedactionTest(unittest.TestCase):
    @staticmethod
    def vendor_payload() -> dict:
        return {
            "id": "object-123",
            "authorization_header": "webhook-secret-canary",
            "nested": {
                "private_key": "private-key-canary",
                "refresh_token": "refresh-canary",
            },
            "description": "Authorization: Bearer abcdefghijklmnopqrstuvwxyz",
        }

    def assert_redacted(self, result: object) -> None:
        rendered = json.dumps(result)
        for secret in (
            "webhook-secret-canary",
            "private-key-canary",
            "refresh-canary",
            "abcdefghijklmnopqrstuvwxyz",
        ):
            self.assertNotIn(secret, rendered)
        self.assertIn("object-123", rendered)
        self.assertIn("<redacted>", rendered)

    def test_extended_snake_and_camel_case_secret_fields(self) -> None:
        payload = {
            "id": "object-123",
            "play_service_account_credentials_json": "service-account-canary",
            "serviceAccountCredentialsJson": "json-canary",
            "credentials": {"token": "nested-canary"},
            "refreshToken": "refresh-camel-canary",
            "clientSecret": "client-camel-canary",
            "authorizationHeader": "header-camel-canary",
            "signingPassword": "signing-canary",
            "secret_id": "uuid-reference-unchanged",
            "passwords_ready": True,
            "token_source": "macOS-keychain",
        }
        result = redaction.redact(payload)
        for field in (
            "play_service_account_credentials_json",
            "serviceAccountCredentialsJson",
            "credentials",
            "refreshToken",
            "clientSecret",
            "authorizationHeader",
            "signingPassword",
        ):
            self.assertEqual(result[field], "<redacted>")
        self.assertEqual(result["id"], "object-123")
        self.assertEqual(result["secret_id"], "uuid-reference-unchanged")
        self.assertTrue(result["passwords_ready"])
        self.assertEqual(result["token_source"], "macOS-keychain")

    def test_string_redaction_uses_structured_secret_names(self) -> None:
        payload = (
            'HTTP 400: {"refreshToken":"refresh-canary","clientSecret":"client-canary"} '
            "Authorization: Basic YWxhZGRpbjpvcGVuc2VzYW1l "
            "'apiKey': 'api-canary' "
            "BWS_ACCESS_TOKEN=machine-account-canary "
            "not-secret=keep"
        )
        result = redaction.redact_text(payload)
        for secret in (
            "refresh-canary", "client-canary", "YWxhZGRpbjpvcGVuc2VzYW1l",
            "api-canary", "machine-account-canary",
        ):
            self.assertNotIn(secret, result)
        self.assertIn("HTTP 400", result)
        self.assertIn("not-secret=keep", result)

    def test_private_key_pem_variants_are_redacted(self) -> None:
        for kind in ("RSA ", "EC ", "OPENSSH ", ""):
            with self.subTest(kind=kind):
                pem = (
                    f"-----BEGIN {kind}PRIVATE KEY-----\\n"
                    "key-body-canary\\n"
                    f"-----END {kind}PRIVATE KEY-----"
                )
                self.assertNotIn("key-body-canary", redaction.redact_text(pem))

    def test_operator_cli_redacts_output_and_error_messages(self) -> None:
        output = io.StringIO()
        errors = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                cli.emit({"id": "object-123", "clientSecret": "cli-canary"}), 0
            )
        from contextlib import redirect_stderr
        with redirect_stderr(errors):
            cli.note("Authorization: Bearer cli-error-canary-token")
            secure_cli.note("refresh_token=secure-error-canary")
        self.assertNotIn("cli-canary", output.getvalue())
        self.assertNotIn("cli-error-canary-token", errors.getvalue())
        self.assertNotIn("secure-error-canary", errors.getvalue())
        self.assertIn("object-123", output.getvalue())

    def test_all_vendor_mutation_taggers_redact_responses(self) -> None:
        taggers = (
            mcp_admob_tools._tag,
            mcp_play_management._tag,
            mcp_play_monetization._tag,
            mcp_play_mutations._tag,
            mcp_revenuecat_management._tag,
            mcp_revenuecat_mutations._tag,
        )
        for tagger in taggers:
            with self.subTest(module=tagger.__module__):
                result = tagger(self.vendor_payload(), "contained")
                self.assert_redacted(result)
                self.assertEqual(result["_mra"]["risk"], "contained")
                self.assertFalse(result["_mra"]["human_approved"])

    def test_vendor_read_wrappers_redact_successful_responses(self) -> None:
        for read in (mcp_admob_tools._read, mcp_play_management._read):
            with self.subTest(module=read.__module__):
                result = read(self.vendor_payload)
                self.assert_redacted(result)
                self.assertEqual(result["id"], "object-123")

    def test_direct_play_tracks_read_redacts_response(self) -> None:
        with (
            patch.object(secure_mcp_server, "_package", return_value="com.example.app"),
            patch.object(
                secure_mcp_server.play_module,
                "track_status",
                return_value=self.vendor_payload(),
            ),
        ):
            result = secure_mcp_server.play_list_tracks("test-profile")
        self.assert_redacted(result)

    def test_agent_cli_emits_only_redacted_provider_output(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(secure_cli.emit(self.vendor_payload()), 0)
        result = json.loads(output.getvalue())
        self.assert_redacted(result)
        self.assertEqual(result["id"], "object-123")


if __name__ == "__main__":
    unittest.main()
