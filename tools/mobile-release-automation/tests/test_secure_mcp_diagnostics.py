"""Structured diagnostics for the secure MCP read surface."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from mra import config
    from mra import revenuecat as rc_module
    from mra import secure_mcp_server as secure_mcp
except SystemExit:  # pragma: no cover - optional MCP dependency
    secure_mcp = None


@unittest.skipIf(secure_mcp is None, "the optional 'mcp' package is not installed")
class SecureMcpDiagnosticsTest(unittest.TestCase):
    def test_profile_read_returns_structured_configuration_error(self) -> None:
        with patch.object(
            secure_mcp.config,
            "load_profile",
            side_effect=config.ConfigError("unknown profile 'missing'"),
        ):
            result = secure_mcp._safe_read(
                lambda: secure_mcp.config.public_profile(
                    secure_mcp.config.load_profile("missing")
                )
            )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "ConfigError")
        self.assertIn("unknown profile", result["detail"])

    def test_revenuecat_read_surfaces_http_detail_and_required_permission(self) -> None:
        profile = config.Profile(
            slug="motionguard",
            package_name="com.example.app",
            revenuecat_project_id="proj_1",
            revenuecat_secret_id="secret-ref",
        )
        client = Mock()
        client.list_packages.side_effect = rc_module.RevenueCatError(
            "list packages in offering ofrng_1 failed with HTTP 403:\n"
            '{"message":"Access denied"}'
        )

        with patch.object(secure_mcp, "_profile", return_value=profile), patch.object(
            secure_mcp, "_client", return_value=client
        ):
            result = secure_mcp._rc_read(
                "motionguard",
                lambda resolved_client, resolved_profile: resolved_client.list_packages(
                    resolved_profile.revenuecat_project_id, "ofrng_1"
                ),
                required_permissions=["project_configuration:packages:read"],
            )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["platform"], "revenuecat")
        self.assertEqual(result["error_type"], "RevenueCatError")
        self.assertIn("HTTP 403", result["detail"])
        self.assertEqual(
            result["required_permissions"],
            ["project_configuration:packages:read"],
        )

    def test_successful_revenuecat_read_keeps_existing_result_shape(self) -> None:
        profile = config.Profile(
            slug="motionguard",
            revenuecat_project_id="proj_1",
            revenuecat_secret_id="secret-ref",
        )
        client = Mock()
        client.list_packages.return_value = [{"id": "pkge_1"}]

        with patch.object(secure_mcp, "_profile", return_value=profile), patch.object(
            secure_mcp, "_client", return_value=client
        ):
            result = secure_mcp._rc_read(
                "motionguard",
                lambda resolved_client, resolved_profile: resolved_client.list_packages(
                    resolved_profile.revenuecat_project_id, "ofrng_1"
                ),
                required_permissions=["project_configuration:packages:read"],
            )

        self.assertEqual(result, [{"id": "pkge_1"}])


if __name__ == "__main__":
    unittest.main()
