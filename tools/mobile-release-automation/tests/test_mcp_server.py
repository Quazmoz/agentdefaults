"""The MCP server's confirmation gate.

An agent reaches these tools directly, so the gate here is the last thing
standing between a model and a live store.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from mra import mcp_server
except SystemExit:  # the mcp package is optional
    mcp_server = None


@unittest.skipIf(mcp_server is None, "the optional 'mcp' package is not installed")
class ConfirmationGateTest(unittest.TestCase):
    def test_real_publish_without_confirm_is_refused(self) -> None:
        result = mcp_server.play_publish_bundle(
            aab_path="app.aab", package_name="com.example.app", dry_run=False
        )
        self.assertEqual(result["status"], "refused")

    def test_promote_without_confirm_is_refused(self) -> None:
        result = mcp_server.play_promote(
            source_track="internal",
            target_track="production",
            package_name="com.example.app",
            dry_run=False,
        )
        self.assertEqual(result["status"], "refused")

    def test_admob_creates_without_confirm_are_refused(self) -> None:
        self.assertEqual(mcp_server.admob_create_app("Example")["status"], "refused")
        self.assertEqual(
            mcp_server.admob_create_ad_unit("ca-app-pub-1~2", "Banner", "BANNER")["status"],
            "refused",
        )

    def test_revenuecat_create_without_confirm_is_refused(self) -> None:
        result = mcp_server.rc_create_play_app(name="Example", project_id="proj_1")
        self.assertEqual(result["status"], "refused")

    def test_publish_defaults_to_dry_run(self) -> None:
        import inspect

        signature = inspect.signature(mcp_server.play_publish_bundle)
        self.assertIs(signature.parameters["dry_run"].default, True)
        self.assertIs(signature.parameters["confirm"].default, False)

    def test_confirm_true_still_requires_native_operator_approval(self) -> None:
        """A model-controlled confirmation cannot bypass the native gate."""
        actions = (
            lambda: mcp_server.play_publish_bundle(
                "example.aab", package_name="com.example.app",
                dry_run=False, confirm=True,
            ),
            lambda: mcp_server.play_promote(
                "internal", "production", package_name="com.example.app",
                dry_run=False, confirm=True,
            ),
            lambda: mcp_server.admob_create_app("Example", confirm=True),
            lambda: mcp_server.admob_create_ad_unit(
                "ca-app-pub-1~2", "Banner", "BANNER", confirm=True,
            ),
            lambda: mcp_server.rc_create_play_app(
                "Example", package_name="com.example.app",
                project_id="proj_1", confirm=True,
            ),
        )
        with (
            patch.object(
                mcp_server.human_approval, "request",
                return_value={"approved": False, "status": "cancelled"},
            ) as approval,
            patch.object(mcp_server.play_module, "publish_bundle") as publish,
            patch.object(mcp_server.play_module, "promote") as promote,
            patch.object(mcp_server.admob_module, "AdMobClient") as admob,
            patch.object(mcp_server.rc_module, "RevenueCatClient") as revenuecat,
            patch.object(mcp_server.play_credentials, "revenuecat_json") as credential,
        ):
            for index, action in enumerate(actions):
                with self.subTest(action=index):
                    self.assertEqual(action()["status"], "refused")
            self.assertEqual(approval.call_count, len(actions))
            publish.assert_not_called()
            promote.assert_not_called()
            admob.assert_not_called()
            revenuecat.assert_not_called()
            credential.assert_not_called()

    def test_approved_legacy_revenuecat_uses_dedicated_google_credentials(self) -> None:
        with (
            patch.object(
                mcp_server.human_approval, "request",
                return_value={"approved": True, "status": "approved"},
            ),
            patch.object(
                mcp_server.play_credentials, "revenuecat_json",
                return_value="dedicated-canary-credential",
            ) as dedicated,
            patch.object(
                mcp_server.play_credentials, "publisher_json",
            ) as publisher,
            patch.object(mcp_server.rc_module, "RevenueCatClient") as client,
        ):
            client.return_value.create_play_app.return_value = {
                "id": "app-1", "client_secret": "vendor-canary"
            }
            result = mcp_server.rc_create_play_app(
                "Example", package_name="com.example.app",
                project_id="proj_1", confirm=True,
            )
        dedicated.assert_called_once_with()
        publisher.assert_not_called()
        client.return_value.create_play_app.assert_called_once_with(
            "proj_1", "Example", "com.example.app", "dedicated-canary-credential"
        )
        self.assertEqual(result["id"], "app-1")
        self.assertEqual(result["client_secret"], "<redacted>")

    def test_confirmed_legacy_publish_masks_vendor_tokens(self) -> None:
        with (
            patch.object(
                mcp_server.human_approval, "request",
                return_value={"approved": True, "status": "approved"},
            ),
            patch.object(
                mcp_server.play_module, "publish_bundle",
                return_value={"status": "published", "refreshToken": "token-canary"},
            ),
        ):
            result = mcp_server.play_publish_bundle(
                "example.aab", package_name="com.example.app",
                dry_run=False, confirm=True,
            )
        self.assertEqual(result, {"status": "published", "refreshToken": "<redacted>"})

    def test_every_mutating_tool_defaults_confirm_to_false(self) -> None:
        import inspect

        mutating = [
            mcp_server.play_publish_bundle,
            mcp_server.play_promote,
            mcp_server.admob_create_app,
            mcp_server.admob_create_ad_unit,
            mcp_server.rc_create_play_app,
        ]
        for tool in mutating:
            with self.subTest(tool=tool.__name__):
                self.assertIs(
                    inspect.signature(tool).parameters["confirm"].default, False
                )


if __name__ == "__main__":
    unittest.main()
