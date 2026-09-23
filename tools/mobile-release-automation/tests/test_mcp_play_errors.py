"""Play MCP tools must return Play's actionable failure, not crash the tool call.

An escaping PlayError reaches the MCP host only as "Error executing tool", which
hid Play's AD_ID declaration rejection during a real WebHookDeck release.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import mcp_play_management, mcp_play_mutations, play  # noqa: E402

AD_ID_MESSAGE = (
    "This release includes the com.google.android.gms.permission.AD_ID permission "
    "but your declaration on Play Console says your app doesn't use advertising ID."
)


class _Response:
    ok = False
    status_code = 400
    text = ""

    def json(self) -> dict:
        return {"error": {"code": 400, "message": AD_ID_MESSAGE, "status": "INVALID_ARGUMENT"}}


def _play_error() -> play.PlayError:
    try:
        play._raise_for_status(_Response(), "validate edit")
    except play.PlayError as error:
        return error
    raise AssertionError("expected PlayError")


PROFILE = SimpleNamespace(package_name="com.example.app")


class PlayMcpErrorTest(unittest.TestCase):
    def test_publish_dry_run_returns_vendor_message(self) -> None:
        with patch.object(mcp_play_mutations.config, "load_profile", return_value=PROFILE), patch.object(
            mcp_play_mutations.play_module, "publish_bundle", side_effect=_play_error()
        ):
            result = mcp_play_mutations.play_publish_bundle("example", "app.aab", dry_run=True)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["http_status"], 400)
        self.assertEqual(result["api_status"], "INVALID_ARGUMENT")
        self.assertIn("AD_ID permission", result["detail"])
        self.assertIn("validate edit failed", result["detail"])
        self.assertEqual(result["_mra"], {"risk": "observe", "human_approved": False})

    def test_approved_listing_write_keeps_approval_on_failure(self) -> None:
        client = SimpleNamespace(update_listing=lambda *a, **k: (_ for _ in ()).throw(_play_error()))
        with patch.object(mcp_play_management, "_gate", return_value=(True, {})), patch.object(
            mcp_play_management, "_client", return_value=client
        ):
            result = mcp_play_management.play_update_listing(
                "example", "en-US", "T", "S", "F", dry_run=False
            )
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["_mra"], {"risk": "high", "human_approved": True})

    def test_read_returns_vendor_message(self) -> None:
        client = SimpleNamespace(list_listings=lambda: (_ for _ in ()).throw(_play_error()))
        with patch.object(mcp_play_management, "_client", return_value=client):
            result = mcp_play_management.play_list_listings("example")
        self.assertIn("AD_ID permission", result["detail"])


if __name__ == "__main__":
    unittest.main()
