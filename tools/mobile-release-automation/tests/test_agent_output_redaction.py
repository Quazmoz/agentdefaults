"""Regression tests for redaction at agent-facing MRA tool boundaries."""

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from mra import (
    mcp_admob_tools,
    mcp_play_management,
    mcp_play_monetization,
    mcp_play_mutations,
    mcp_revenuecat_management,
    mcp_revenuecat_mutations,
    secure_cli,
    secure_mcp_server,
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
