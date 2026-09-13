"""The MCP server's confirmation gate.

An agent reaches these tools directly, so the gate here is the last thing
standing between a model and a live store.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

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
