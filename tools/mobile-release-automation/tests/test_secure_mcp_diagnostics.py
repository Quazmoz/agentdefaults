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
    def test_every_mcp_tool_module_reaches_the_served_surface(self) -> None:
        """An mcp_* module with register() but no call site silently drops its tools.

        mcp_play_monetization was orphaned this way: Play one-time product upsert
        and purchase-option activation were implemented and risk-gated but
        unreachable from every agent surface.
        """
        import asyncio
        import importlib
        import pkgutil

        from mra import __path__ as mra_path

        served = {tool.name for tool in asyncio.run(secure_mcp.server.list_tools())}
        unreachable: dict[str, list[str]] = {}
        for info in pkgutil.iter_modules(list(mra_path)):
            if not info.name.startswith("mcp_"):
                continue
            register = getattr(importlib.import_module(f"mra.{info.name}"), "register", None)
            if register is None:
                continue
            declared: list[str] = []

            class Recorder:
                def tool(self):
                    def decorate(fn):
                        declared.append(fn.__name__)
                        return fn

                    return decorate

            register(Recorder())
            gap = sorted(set(declared) - served)
            if gap:
                unreachable[info.name] = gap

        self.assertEqual(unreachable, {}, f"mcp modules whose tools are not served: {unreachable}")

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

    def test_revenuecat_error_detail_redacts_canary_secret(self) -> None:
        profile = config.Profile(
            slug="motionguard",
            revenuecat_project_id="proj_1",
            revenuecat_secret_id="secret-ref",
        )
        client = Mock()
        client.list_packages.side_effect = rc_module.RevenueCatError(
            "failed with HTTP 403: Authorization: Bearer secret-canary-1234567890 "
            "sk_1234567890abcdef"
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

        self.assertNotIn("secret-canary-1234567890", result["detail"])
        self.assertNotIn("sk_1234567890abcdef", result["detail"])
        self.assertIn("<redacted>", result["detail"])

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

    def test_successful_read_redacts_sensitive_fields_without_changing_shape(self) -> None:
        result = secure_mcp._safe_read(
            lambda: {
                "id": "wh_1",
                "signing_secret": "signing-canary",
                "nested": {"client_secret": "client-canary"},
            }
        )

        self.assertEqual(result["id"], "wh_1")
        self.assertEqual(result["signing_secret"], "<redacted>")
        self.assertEqual(result["nested"]["client_secret"], "<redacted>")


if __name__ == "__main__":
    unittest.main()
